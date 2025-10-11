from __future__ import annotations
import os, re, io, zipfile, json, datetime, threading, queue, contextlib, traceback, time
from typing import List, Dict, Any, Tuple, Optional
import builtins
from dataclasses import dataclass

import gradio as gr
import pandas as pd
from PIL import Image

from nasa_cmr_data_acquisition_agent import create_nasa_cmr_agent

# -------------------- constants & regex --------------------

# 1) Path + bare file name (both types are recognized) (png/jpg/jpeg/csv/json)
PATH_OR_FILE_RE = re.compile(
    r"(?i)(?:"
    r"([A-Za-z]:[^\s]+?\.(?:png|jpg|jpeg|csv|json))|"      # Windows absolute path
    r"(\.[^\s]+?\.(?:png|jpg|jpeg|csv|json))|"             # Relative paths (starting with .)
    r"([A-Za-z0-9._\-]+?\.(?:png|jpg|jpeg|csv|json))"      # Bare file name
    r")"
)

# 2) ReAct key line (for plain text fallback)
ACTION_LINE_RE       = re.compile(r'(?m)^\s*Action:\s*(.+?)\s*$')
ACTION_INPUT_LINE_RE = re.compile(r'(?m)^\s*Action Input:\s*(.*)\s*$')
OBS_LINE_RE          = re.compile(r'(?m)^\s*Observation\s*:\s*', re.IGNORECASE)
FINAL_LINE_RE        = re.compile(r'(?m)^\s*Final Answer\s*:', re.IGNORECASE)
INPUT_PROMPT = ">>> Your response:"
ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
# 3) Product list/prompt (text fallback)
GEN_PLOTS_RE         = re.compile(r'(?m)^\s*Generated plots\s*:\s*$', re.IGNORECASE)
AVAIL_FILES_RE       = re.compile(r'(?m)^\s*Available data files\s*:\s*$', re.IGNORECASE)
BULLET_FILE_RE       = re.compile(r'^\s*[-•*]?\s*([A-Za-z0-9._\-\/\\]+?\.(?:png|jpg|jpeg|csv|json))\s*$', re.IGNORECASE)
SAVED_LINE_RE        = re.compile(r'(?i)\b(saved(?:\s+to|\s+as)?|generated|wrote|created)\b[: ]+([^\s]+?\.(?:png|jpg|jpeg|csv|json))')

EXECUTE_TOOL_NAMES   = {"execute_python_code", "execute_code", "run_python"}

IMG_EXT = (".png", ".jpg", ".jpeg")

# -------------------- agent singleton ----------------------
AGENT = None
def get_agent():
    global AGENT
    if AGENT is None:
        AGENT = create_nasa_cmr_agent()
    return AGENT
def restart_agent():
    global AGENT
    AGENT = None
    return True

# -------------------- helpers ------------------------------
def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s or "")

def clean_text(s: str) -> str:
    """Desaturate + Collapse > 2 consecutive empty lines into 1"""
    s = strip_ansi(s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s

def find_paths_or_files(text: str, cwd: str) -> List[str]:
    """Extract a path or bare file name from text, mapping it to a usable actual path"""
    hits: List[str] = []
    for m in PATH_OR_FILE_RE.finditer(text or ""):
        cand = next(g for g in m.groups() if g)  # Take the first non-empty group
        # Specification & Parsing
        paths = [cand]
        if not os.path.isabs(cand):
            paths.append(os.path.join(cwd, cand))
        for p in paths:
            if os.path.exists(p):
                if p not in hits:
                    hits.append(p)
                break
    return hits

def render_artifacts(artifacts: List[str]) -> Tuple[List[Image.Image], str]:
    images, html = [], ""
    for p in artifacts or []:
        try:
            if p.lower().endswith(IMG_EXT):
                images.append(Image.open(p))
            elif p.lower().endswith(".csv"):
                df = pd.read_csv(p).head(5)
                html += f"<h4>{os.path.basename(p)}</h4>" + df.to_html(index=False)
            elif p.lower().endswith(".json"):
                df = pd.read_json(p).head(5)
                html += f"<h4>{os.path.basename(p)}</h4>" + df.to_html(index=False)
        except Exception:
            pass
    return images, html

def make_zip(artifacts: List[str]):
    if not artifacts: return None
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in artifacts:
            if os.path.exists(p):
                try: zf.write(p, arcname=os.path.basename(p))
                except Exception: pass
    buf.seek(0)
    return buf

class QueueWriter:
    def __init__(self, q: "queue.Queue[str]"): self.q = q
    def write(self, s: str):
        s = strip_ansi(s)
        if s: self.q.put(s)
    def flush(self): pass

class RunState:
    def __init__(self):
        self.running = False
        self.awaiting = False
        self.stdin_q: "queue.Queue[str]" = None
        self.stdout_q: "queue.Queue[str]" = None
        self.thread: threading.Thread = None

# -------------------- Event model --------------------------
@dataclass
class StreamEvent:
    type: str            # "token" | "tool_start" | "tool_log" | "artifact" | "needs_input" | "final"
    payload: dict | str  # dict for structured, str for raw text

def try_parse_evt(line: str) -> Optional[dict]:
    """Recognizes [EVT]{json} event rows; returns None on failure."""
    line = line.strip("\n")
    if not line.startswith("[EVT]"):
        return None
    try:
        return json.loads(line[5:])
    except Exception:
        return None

def iter_events_from_chunk(chunk: str, cwd: str, state: dict) -> List[StreamEvent]:
    """
    Converts a stdout chunk (possibly containing multiple lines) into a sequence of events;
    - Parses [EVT]{...} first
    - Then makes it compatible with plain text ReAct (Action/Action Input/Observation/Final)
    - Enters "code fence mode" after the Action Input of execute_python_code
    """
    events: List[StreamEvent] = []
    chunk = chunk.replace("\r", "\n")
    for raw_line in chunk.splitlines(keepends=True):

        # 1) Event Channel (Priority)
        evt = try_parse_evt(raw_line)
        if evt:
            t = evt.get("type")
            p = evt.get("payload") or {}
            if t == "token":
                events.append(StreamEvent("token", p.get("text","")))
            elif t == "tool_start":
                state["current_tool"] = p.get("name","tool")
                # close code fences when switching tools
                if state.get("code_on"):
                    events.append(StreamEvent("token", "\n```\n"))
                    state["code_on"] = False
                events.append(StreamEvent("tool_start", {"name": state["current_tool"]}))
            elif t == "tool_log":
                events.append(StreamEvent("token", p.get("text","")))
            elif t == "artifact":
                path = p.get("path")
                if path:
                    events.append(StreamEvent("artifact", {"path": path, "kind": p.get("kind")}))
            elif t == "needs_input":
                events.append(StreamEvent("needs_input", {"reason": p.get("reason","")}))
            elif t == "final":
                # Close the code fence before ending
                if state.get("code_on"):
                    events.append(StreamEvent("token", "\n```\n"))
                    state["code_on"] = False
                events.append(StreamEvent("final", p.get("text","")))
            continue

        # 2) Plain text fallback: ReAct key line
        line = raw_line

        # Action:
        m_act = ACTION_LINE_RE.match(line)
        if m_act:
            tool = m_act.group(1).strip()
            # close code fences when switching tools
            if state.get("code_on"):
                events.append(StreamEvent("token", "\n```\n"))
                state["code_on"] = False
            state["current_tool"] = tool
            events.append(StreamEvent("tool_start", {"name": tool}))
            continue

        # Action Input:
        m_in = ACTION_INPUT_LINE_RE.match(line)
        if m_in:
            # Enable code fencing only for code execution tools
            if (state.get("current_tool","").lower() in EXECUTE_TOOL_NAMES) and not state.get("code_on"):
                events.append(StreamEvent("token", "\n<small><code>Action Input</code></small>\n```python\n"))
                state["code_on"] = True
            # Keep this line (Agent puts the first line of code right after Action Input)
            tail = m_in.group(1)
            events.append(StreamEvent("token", tail + ("\n" if not tail.endswith("\n") else "")))
            continue

        # Observation: or Final Answer: appears → Close the code fence
        if OBS_LINE_RE.match(line) or FINAL_LINE_RE.match(line):
            if state.get("code_on"):
                events.append(StreamEvent("token", "\n```\n"))
                state["code_on"] = False
            events.append(StreamEvent("token", line))
            if FINAL_LINE_RE.match(line):
                events.append(StreamEvent("final", ""))  # Let the upper layer finish
            continue

        # List header (product)
        if GEN_PLOTS_RE.match(line) or AVAIL_FILES_RE.match(line):
            state["list_mode"] = "files" # Borrowing the same process
            events.append(StreamEvent("token", line))
            continue

        # List Item → artifact
        if state.get("list_mode"):
            mb = BULLET_FILE_RE.match(line)
            if mb:
                name = mb.group(1).strip()
                # Parse to real path
                for cand in (name, os.path.join(cwd, name)):
                    if os.path.exists(cand):
                        events.append(StreamEvent("artifact", {"path": cand, "kind": None}))
                        break
                events.append(StreamEvent("token", line))
                continue
            if line.strip() == "" or line.lower().lstrip().startswith("final"):
                state["list_mode"] = None  # end list

        # Saved to / Generated ...
        ms = SAVED_LINE_RE.search(line)
        if ms:
            fname = ms.group(2).strip()
            for cand in (fname, os.path.join(cwd, fname)):
                if os.path.exists(cand):
                    events.append(StreamEvent("artifact", {"path": cand, "kind": None}))
                    break
            events.append(StreamEvent("token", line))
            continue

        # Normal text: If currently in a code fence, enter the code block directly; otherwise normal text
        events.append(StreamEvent("token", line))

    return events

# -------------------- streaming consumer -------------------
def consume_stream(stdout_q: "queue.Queue[str]",
                   history: List[Dict[str, str]],
                   artifacts: List[str],
                   rs: RunState):
    """
    Reads the stdout queue and performs event-based rendering; automatically fences after the Action Input of execute_python_code.
    """
    acc = history[-1]["content"] if history else ""
    text_buf: List[str] = []
    last_flush = time.time()
    FLUSH_EVERY = 0.08  # 80ms
    # Parsing status (across chunks)
    state = {"current_tool": None, "code_on": False, "list_mode": None}

    while True:
        try:
            chunk = stdout_q.get(timeout=0.1)
        except queue.Empty:
            chunk = None

        if chunk == "__<<DONE>>__":
            rs.running = False
            break

        if chunk:
            # Event Parsing
            events = iter_events_from_chunk(chunk, os.getcwd(), state)
            for ev in events:
                if ev.type == "token":
                    text_buf.append(ev.payload if isinstance(ev.payload, str) else str(ev.payload))
                elif ev.type == "tool_start":
                    name = ev.payload.get("name","tool")
                    text_buf.append(f"\n### 🛠️ Action: `{name}`\n")
                elif ev.type == "artifact":
                    path = ev.payload.get("path")
                    if path and os.path.exists(path) and path not in artifacts:
                        artifacts.append(path)
                elif ev.type == "needs_input":
                    rs.awaiting = True
                elif ev.type == "final":

                    pass

            # Path/bare file name in text (double insurance)
            for p in find_paths_or_files(chunk, os.getcwd()):
                if p not in artifacts:
                    artifacts.append(p)

        # Combined frame refresh (with content or heartbeat timeout)
        now = time.time()
        if text_buf and (now - last_flush >= FLUSH_EVERY or chunk is None):
            acc += "".join(text_buf)
            text_buf.clear()
            history[-1]["content"] = clean_text(acc)
            yield history, artifacts, gr.update(value=history), rs
            last_flush = now

        # Compatible with old prompt trigger
        if chunk and (INPUT_PROMPT in chunk):
            rs.awaiting = True

        # Once input is required, return immediately to make the input box available
        if rs.awaiting and chunk is not None:
            if text_buf:
                acc += "".join(text_buf)
                text_buf.clear()
                history[-1]["content"] = clean_text(acc)
            yield history, artifacts, gr.update(value=history), rs
            return

    # Ending fallback: close the unclosed code fence
    if state.get("code_on"):
        acc += "\n```\n"
        state["code_on"] = False
    if text_buf:
        acc += "".join(text_buf)
    if not acc.strip():
        acc = "_No output captured._"
    history[-1]["content"] = clean_text(acc)
    yield history, artifacts, gr.update(value=history), rs

# -------------------- UI bits ------------------------------
def ui_enable(rs: RunState):
    if rs.awaiting:
        return gr.update(interactive=True, placeholder=INPUT_PROMPT), gr.update(interactive=True)
    if rs.running:
        return gr.update(interactive=False, placeholder="Agent is running…"), gr.update(interactive=False)
    return gr.update(interactive=True, placeholder="Ask the agent…"), gr.update(interactive=True)

def refresh_side(arts: List[str]):
    imgs, html = render_artifacts(arts)
    return imgs, html, arts

def do_restart():
    restart_agent()
    return [], [], [], [{"role": "assistant", "content": "🔄 Agent restarted. Memory cleared. Ready for a NEW case."}], RunState()

# -------------------- core chat (generator) -----------------------
def handle_chat(user_text: str,
                history: List[Dict[str, str]],
                artifacts: List[str],
                rs: RunState):
    if not user_text or not user_text.strip():
        yield history, artifacts, gr.update(value=history), rs
        return

    if rs.running and not rs.awaiting:
        tip = "_Agent is still thinking. Please wait until you see an input request._"
        history = history + [{"role": "user", "content": user_text},
                             {"role": "assistant", "content": tip}]
        yield history, artifacts, gr.update(value=history), rs
        return

    # Write user message + reserve assistant
    history = history + [{"role": "user", "content": user_text}]
    history = history + [{"role": "assistant", "content": "…"}]
    yield history, artifacts, gr.update(value=history), rs

    # -------- Waiting for clarification branch --------
    if rs.awaiting and rs.running and rs.stdin_q is not None:
        rs.stdin_q.put(user_text.strip())
        rs.awaiting = False
        for out in consume_stream(rs.stdout_q, history, artifacts, rs):
            yield out
        return

    # -------- New round of branches --------
    stdin_q: "queue.Queue[str]" = queue.Queue()
    stdout_q: "queue.Queue[str]" = queue.Queue()

    def bridged_input(prompt: str = "") -> str:
        if prompt: stdout_q.put(prompt)
        return stdin_q.get()

    def worker(first_message: str):
        old_input = builtins.input
        builtins.input = bridged_input
        try:
            agent = get_agent()
            writer = QueueWriter(stdout_q)
            # Capture stdout + stderr at the same time to avoid blank
            with contextlib.redirect_stdout(writer), contextlib.redirect_stderr(writer):
                print("▶️ Agent started")
                res = agent.invoke({"input": first_message})
                # Some agents only return but do not print → also write back a copy
                try:
                    if isinstance(res, dict):
                        txt = res.get("output") or res.get("final") or json.dumps(res, ensure_ascii=False, indent=2)
                    else:
                        txt = str(res)
                    if txt and txt.strip():
                        print("\n—— Agent return value ——")
                        print(txt)
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

    for out in consume_stream(stdout_q, history, artifacts, rs):
        yield out

# ------------------------------ UI -------------------------------
with gr.Blocks(
    title="NASA CMR Agent — Chat",
    css=r"""
            /* Global: light gray background, uniform rounded corners, no hard border */
            :root{
              --bg: #f5f6f8;
              --card: #ffffff;
              --radius: 16px;
              --shadow: 0 10px 24px rgba(0,0,0,.06);
            }
            html, body { background: var(--bg); }
            .gradio-container {
              max-width: 100% !important;
              padding: 0 24px 28px;
              background: var(--bg);
            }
            
            /* Top title: centered + top adsorption + slight shadow */
            #page-title-wrap{
              position: sticky; top: 0; z-index: 5;
              display: flex; justify-content: center; align-items: center;
              background: var(--bg);
              padding: 14px 0 10px;
              box-shadow: 0 1px 0 rgba(0,0,0,.04);
              margin-bottom: 10px;
            }
            #page-title{
              margin: 0; padding: 0;
              font-size: 20px; font-weight: 650; letter-spacing:.2px;
              color: #0f172a; text-align: center;
            }
            
            /* Set the maximum width of the main column and center it*/
            #chat_wrap, #results { max-width: 1200px; margin: 0 auto; }
            
            /* Chatbot: white card + rounded corners + soft shadow + no hard border */
            #chat_wrap .gr-chatbot{
              height: calc(100vh - 260px);
              background: var(--card);
              border: none !important;
              border-radius: var(--radius);
              box-shadow: var(--shadow);
            }
            
            /* Input line: same height as button; remove label; rounded corners, no hard border */
            #controls .gr-textbox, #controls .gr-textbox *{
              border: none !important;
            }
            #controls .gr-textbox textarea{
              background: var(--card);
              min-height: 48px; max-height: 48px;
              resize: none;
              border-radius: var(--radius);
              box-shadow: var(--shadow);
              padding-top: 12px;     /* Make the text vertically centered more naturally */
            }
            
            /* Send button */
            #send_btn{
              height: 48px;
              border-radius: 14px;
              font-weight: 700;
              font-size: 16px;     
              padding: 0 18px;     
              min-width: 120px;   
              box-shadow: var(--shadow);
            }
            
            /* Result area */
            #results .gr-accordion{
              background: var(--card);
              border: none !important;
              border-radius: var(--radius);
              box-shadow: var(--shadow);
            }
            #results .gr-accordion .gr-accordion-header{ background: var(--card); }
            #results .gr-accordion .gr-accordion-content{ overflow: visible; }
            
            /* Gallery */
            #results .gr-gallery{ background: transparent; }
            #results .gr-gallery div.thumbnail-item{
              border-radius: 14px; overflow: hidden; border: none;
              box-shadow: 0 6px 18px rgba(0,0,0,.05);
            }
            #results .gr-gallery img{ object-fit: contain !important; }
            
            /* Files / HTML Output container */
            #results .gr-file, #results .gr-html{
              background: var(--card);
              border: none !important;
              border-radius: var(--radius);
              box-shadow: var(--shadow);
            }
            
            /* All buttons have the same rounded corner style */
            .gr-button{ border-radius: 14px; }
            
            /* Rounded corners of message bubbles */
            #chat_wrap .wrap .message{ border-radius: 12px; }
            """,
        ) as demo:
            gr.HTML('<div id="page-title-wrap"><h1 id="page-title">Welcome to AutoClimDS Chat</h2></div>')

            with gr.Column(elem_id="chat_wrap"):
                chatbot = gr.Chatbot(
                    height=620,
                    show_copy_button=True,
                    type="messages",
                    render_markdown=False,
                )
                with gr.Row(elem_id="controls"):
                    # Remove the "Textbox" tag and make the height consistent with Send button
                    msg  = gr.Textbox(placeholder="Ask the agent…", show_label=False, scale=8)
                    # Send has a larger font and shorter length (configured in CSS with #send_btn )
                    send = gr.Button("Send", variant="primary", scale=2, elem_id="send_btn")

                # Place ZIP / Notebook / Restart right below the input box, dividing it into three equal parts.
                with gr.Row(elem_id="tool_row"):
                    btn_zip = gr.Button("📦  ZIP all", scale=1)
                    btn_nb  = gr.Button("📓  Notebook", scale=1)
                    btn_restart = gr.Button("↻  Restart", scale=1, variant="secondary")

            # Results Area
            with gr.Accordion("Results", open=True, elem_id="results"):
                gallery = gr.Gallery(label="Images", columns=3, height=620, show_label=False)
                table_html = gr.HTML()
                files_list = gr.Files(label="Artifacts", interactive=False)

            # states
            history_state   = gr.State([])
            artifacts_state = gr.State([])
            run_state       = gr.State(RunState())

            # events
            for trigger in (msg.submit, send.click):
                trigger(
                    handle_chat,
                    inputs=[msg, history_state, artifacts_state, run_state],
                    outputs=[history_state, artifacts_state, chatbot, run_state],
                ).then(
                    refresh_side, inputs=[artifacts_state], outputs=[gallery, table_html, files_list],
                ).then(
                    ui_enable, inputs=[run_state], outputs=[msg, send],
                ).then(lambda: "", None, [msg])

            # # Download & Export
            # btn_zip.click(make_zip, [artifacts_state], [file_zip])
            # btn_nb.click(lambda h, a: make_notebook(h, a), [history_state, artifacts_state], [file_nb])

            # restart
            btn_restart.click(
                do_restart, None, [artifacts_state, gallery, files_list, history_state, run_state]
            ).then(lambda: "", None, [table_html]
                   ).then(ui_enable, inputs=[run_state], outputs=[msg, send])


if __name__ == "__main__":
    print("Starting NASA CMR Agent WebUI (Gradio)…")
    demo.queue()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, show_api=False)
