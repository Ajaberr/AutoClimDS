from __future__ import annotations
import builtins
from contextlib import contextmanager
import pandas as pd
import gradio as gr, threading, queue, contextlib, traceback, json, os, html
from typing import List, Dict
from .agents import AGENTS, CURRENT_AGENT_KEY, switch_agent, get_agent, restart_agent
from .stream import QueueWriter, RunState, consume_stream
from .artifacts import render_artifacts, build_images_html, preview_markdown_for_path, find_paths_or_files
from .export import summarize_tools, refresh_chat_csv, build_notebook_path

# ---- UI helper callbacks (thin wrappers only) ----
INPUT_PROMPT = ">>> Your response:"

def ui_enable(rs: RunState):
    if rs.awaiting:
        return gr.update(interactive=True, placeholder=INPUT_PROMPT), gr.update(interactive=True)
    if rs.running:
        return gr.update(interactive=False, placeholder="Agent is running…"), gr.update(interactive=False)
    return gr.update(interactive=True, placeholder="Ask the agent…"), gr.update(interactive=True)

def refresh_side(arts: List[str]):
    img_paths, html_tables = render_artifacts(arts)  # imgs 这里还是 PIL 图像列表？把 render_artifacts 改返回路径
    img_html = build_images_html(img_paths)
    return img_html, html_tables, arts

def on_switch(sel: str, history: list):
    switch_agent(sel)
    rs = RunState()
    new_history = (history or []) + [{"role":"assistant","content": f"🔁 Switched to **{sel}**"}]
    return new_history, rs, gr.update(value=new_history)

def do_restart():
    restart_agent()
    rs = RunState()
    return [], [], gr.update(value=[]), rs, "", gr.update(value=None), []  # 最后 [] = events_state

def summarize_tools_or_empty(evs):
    df = summarize_tools(evs)
    if df.empty:
        return pd.DataFrame([["(no tool events)", 0, 0, 0, None, ""]],
                            columns=["tool","count","ok","fail","avg_ms","last_error"])
    return df

# ---- Core chat (generator) ----
def handle_chat(agent_selector, user_text, history, artifacts, rs, evs):

    if not user_text or not user_text.strip():
        yield history, artifacts, gr.update(value=history), rs, evs
        return
    if rs.running and not rs.awaiting:
        tip = "_Agent is still thinking. Please wait until you see an input request._"
        history = history + [{"role":"user","content":user_text},
                             {"role":"assistant","content":tip}]
        yield history, artifacts, gr.update(value=history), rs, evs
        return

    history = history + [{"role":"user","content":user_text}, {"role":"assistant","content":"…"}]
    yield history, artifacts, gr.update(value=history), rs, evs

    # waiting-for-input branch
    if rs.awaiting and rs.running and rs.stdin_q is not None:
        rs.stdin_q.put(user_text.strip()); rs.awaiting=False
        for h, a, rs2, evs2 in consume_stream(
                rs.stdout_q, history, artifacts, rs, evs,
                preview_markdown_for_path, find_paths_or_files):
            yield h, a, gr.update(value=h), rs2, evs2
        return

    # new run
    stdin_q: "queue.Queue[str]" = queue.Queue()
    stdout_q: "queue.Queue[str]" = queue.Queue()

    def bridged_input(prompt: str="") -> str:
        if prompt: stdout_q.put(prompt)
        return stdin_q.get()

    @contextmanager
    def patched_input(fn):
        old = builtins.input
        builtins.input = fn
        try:
            yield
        finally:
            builtins.input = old

    def worker(first_message: str):
        with patched_input(bridged_input):
            old_input = builtins.input
            builtins.input = bridged_input
            try:
                agent = get_agent()
                writer = QueueWriter(stdout_q)
                with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                    print(f" 🧠 Active agent: {agent_selector}")
                    res = agent.invoke({"input": first_message})
                    # echo return value
                    try:
                        if isinstance(res, dict):
                            txt = res.get("output") or res.get("final") or json.dumps(res, ensure_ascii=False, indent=2)
                        else: txt = str(res)
                        if txt and txt.strip():
                            print("\n—— Agent return value ——\n" + txt)
                    except Exception:
                        pass
            except Exception:
                stdout_q.put("\n**[Agent Error]**\n```\n" + traceback.format_exc() + "\n```\n")
            finally:
                builtins.input = old_input
                stdout_q.put("__<<DONE>>__")

    t = threading.Thread(target=worker, args=(user_text.strip(),), daemon=True)
    rs.running, rs.awaiting = True, False
    rs.stdin_q, rs.stdout_q, rs.thread = stdin_q, stdout_q, t
    t.start()

    for h, a, rs2, evs2 in consume_stream(
            rs.stdout_q, history, artifacts, rs, evs,
            preview_markdown_for_path, find_paths_or_files):
        yield h, a, gr.update(value=h), rs2, evs2


# ---- Build UI (same layout as you have) ----
def build_ui():
    here = os.path.dirname(__file__)           # The directory where the current file is located
    path = os.path.join(here, "style.css")
    with open(path, "r", encoding="utf-8") as f:
        css_content =  f.read()

    with gr.Blocks(title="AutoClimDS Chat", css=css_content) as demo:
        gr.HTML('<div id="page-title-wrap"><h1 id="page-title">Welcome to AutoClimDS Chat</h2></div>')

        with gr.Column(elem_id="chat_wrap"):
            chatbot = gr.Chatbot(
                height=620,
                show_copy_button=True,
                type="messages",
                render_markdown=True,
            )

            # UI Snippet
            with gr.Row(elem_id="input_row"):
                msg = gr.Textbox(
                    placeholder="Ask the agent…",
                    show_label=False,
                    elem_id="msg",
                    scale=8
                )
                send = gr.Button("Send", elem_id="send_btn", variant="primary", scale=1)

                agent_selector = gr.Dropdown(
                    choices=list(AGENTS.keys()),
                    value=CURRENT_AGENT_KEY,
                    show_label=False,
                    elem_id="agent_sel",
                    scale=2
                )

            # tool calling part
            with gr.Row(elem_id="tool_row"):
                btn_zip = gr.DownloadButton("📦 ZIP all", elem_id="tool_btn")
                btn_nb = gr.DownloadButton("📓 Notebook", elem_id="tool_btn")
                btn_restart = gr.Button("🌀 Restart", elem_id="tool_btn")
                switch_btn = gr.Button("🔁 Switch", elem_id="tool_btn")

        # Results Area
        with gr.Accordion("Results", open=True, elem_id="results"):
            images_html = gr.HTML()
            table_html = gr.HTML()
            tools_df = gr.Dataframe(headers=["tool", "count", "ok", "fail", "avg_ms", "last_error"],
                                    row_count=(1, "dynamic"), wrap=True)
            files_list = gr.Files(label="Artifacts", interactive=False)

        # states
        history_state = gr.State([])
        artifacts_state = gr.State([])
        run_state = gr.State(RunState())
        events_state = gr.State([])
        nb_path_state = gr.State("")
        # events
        for trigger in (msg.submit, send.click):
            trigger(
                handle_chat,
                inputs=[agent_selector, msg, history_state, artifacts_state, run_state, events_state],
                outputs=[history_state, artifacts_state, chatbot, run_state, events_state],
            ).then(
                refresh_side, inputs=[artifacts_state], outputs=[images_html, table_html, files_list],
            ).then(
                ui_enable, inputs=[run_state], outputs=[msg, send],
            ).then(
                refresh_chat_csv, inputs=[history_state], outputs=[btn_zip], queue=False
            ).then(
                summarize_tools_or_empty, inputs=[events_state], outputs=[tools_df], queue=False
            ).then(
                build_notebook_path, inputs=[events_state], outputs=[btn_nb], queue=False  # ⬅️ 新增
            ).then(lambda: "", None, [msg])

        # Download & Export
        btn_nb.click(
            build_notebook_path,
            inputs=[events_state],
            outputs=[btn_nb],
            queue=False
        )

        switch_btn.click(
            on_switch,
            inputs=[agent_selector, history_state],
            outputs=[history_state, run_state, chatbot],
        ).then(
            ui_enable, inputs=[run_state], outputs=[msg, send],
        )

        # restart
        btn_restart.click(
            do_restart,
            inputs=None,
            outputs=[history_state, artifacts_state, chatbot, run_state, msg, btn_zip, events_state]
        ).then(
            refresh_side, inputs=[artifacts_state], outputs=[images_html, table_html, files_list],
        ).then(
            ui_enable, inputs=[run_state], outputs=[msg, send],
        ).then(summarize_tools_or_empty, inputs=[events_state], outputs=[tools_df], queue=False)

    return demo

if __name__ == "__main__":
    demo = build_ui()
    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, show_api=False)
