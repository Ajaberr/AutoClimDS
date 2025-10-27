from __future__ import annotations
import os, re, queue, time, html, json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


# Regex / constants
# 1) ReAct key line (for plain text fallback)
ACTION_LINE_RE = re.compile(r'(?m)^\s*Action:\s*(.+?)\s*$')
ACTION_INPUT_LINE_RE = re.compile(r'(?m)^\s*Action Input:\s*(.*)\s*$')
OBS_LINE_RE = re.compile(r'(?m)^\s*Observation\s*:\s*', re.IGNORECASE)
FINAL_LINE_RE = re.compile(r'(?m)^\s*Final Answer\s*:', re.IGNORECASE)
INPUT_PROMPT = ">>> Your response:"
ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
# 2) Product list/prompt (text fallback)
GEN_PLOTS_RE = re.compile(r'(?m)^\s*Generated plots\s*:\s*$', re.IGNORECASE)
AVAIL_FILES_RE = re.compile(r'(?m)^\s*Available data files\s*:\s*$', re.IGNORECASE)
BULLET_FILE_RE = re.compile(r'^\s*[-•*]?\s*([A-Za-z0-9._\-\/\\]+?\.(?:png|jpg|jpeg|csv|json))\s*$', re.IGNORECASE)
SAVED_LINE_RE = re.compile(r'(?i)\b(saved(?:\s+to|\s+as)?|generated|wrote|created)\b[: ]+([^\s]+?\.(?:png|jpg|jpeg|csv|json))')

EXECUTE_TOOL_NAMES = {"execute_python_code", "execute_code", "run_python"}
IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp")
UPPER_TOOL_HINT_RE = re.compile(r'^\s*(DOWNLOAD|LOADING|PROCESSING|VALIDAT(ING|ION)|SEARCHING|SAV(ING|E))\b', re.I)
MD_SPECIAL = r"\`*_{}[]()#+-.!|>~"

FENCE_RE = re.compile(r'^\s*```')
OUTPUT_NOISE_RE = re.compile(
    r'^\s*(📝|🔍|📊|✅|❌|⚠️|Output:|Full traceback:|Traceback|Error|Exception|Observation:|Final Answer:)\b',
    re.IGNORECASE
)

# Boundaries of code collection
FENCE_TICKS_RE     = re.compile(r'^\s*```')                           # ``` any fence
EVT_PREFIX_RE      = re.compile(r'^\[EVT\]')                          # [EVT]{...}
EXEC_BANNER_RE     = re.compile(r'^\s*[🐍]|^\s*EXECUTING', re.I)       # 🐍 EXECUTING...
OUTPUT_HEADER_RE   = re.compile(r'^\s*(📊|Output:|Full traceback:|Traceback)', re.I)
SECTION_BAR_RE     = re.compile(r'^\s*=+\s*$')                        # ====== Delimiter
# Cleaning the captured Action Input code: removing delimiters/noise lines.
NOISE_LINE_RE      = re.compile(r'^\s*(```|📊|📝|🔍|✅|❌|⚠️|Output:|Full traceback:|Traceback)\b', re.I)



# Models Setup
@dataclass
class StreamEvent:
    """A small event used by the UI stream renderer."""
    type: str  # "token" | "tool_start" | "artifact" | "needs_input" | "final"
    payload: dict | str

class QueueWriter:
    """File-like writer that forwards writes to a Queue (for stdout/stderr capture)."""
    def __init__(self, q: "queue.Queue[str]"): self.q = q
    def write(self, s: str):
        if s: self.q.put(s)
    def flush(self): pass

class RunState:
    """Runtime state for a single run (thread and IO queues)."""
    def __init__(self):
        self.running = False
        self.awaiting = False
        self.stdin_q: "queue.Queue[str]" = None
        self.stdout_q: "queue.Queue[str]" = None
        self.thread = None

# Helpers kept local to stream
def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s or "")

def clean_text(s: str) -> str:
    """Desaturate + Collapse > 2 consecutive empty lines into 1"""
    s = strip_ansi(s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s

def try_parse_evt(line: str) -> Optional[dict]:
    """
    Recognizes [EVT]{json} event rows. Supports both legacy {'type','payload'} and
    new v1 schema {'type','ts','run_id','step_id','seq', ...}.
    Returns a dict with unified keys: {'type':..., 'data':{...}}.
    """
    line = line.strip("\n")
    if not line.startswith("[EVT]"):
        return None
    try:
        raw = json.loads(line[5:])
        t = raw.get("type")
        if not t:
            return None
        # unify to {'type':..., 'data':{...}}
        if "payload" in raw and isinstance(raw["payload"], dict):
            data = raw["payload"]
        else:
            # v1: Put all fields except 'type' into 'data'.
            data = {k: v for k, v in raw.items() if k != "type"}
        return {"type": t, "data": data}
    except Exception:
        return None

def clean_code_for_notebook(src: str) -> str:
    """Strip fences/banners/tracebacks/empty edges from captured code."""
    lines = src.splitlines()
    keep = []
    for ln in lines:
        if FENCE_RE.match(ln):
            continue
        if OUTPUT_NOISE_RE.match(ln):
            continue
        if re.match(r'^\s*---.*---\s*$', ln):
            continue
        keep.append(ln.rstrip())
    # trim leading/trailing blanks
    while keep and keep[0] == "":
        keep.pop(0)
    while keep and keep[-1] == "":
        keep.pop()
    return ("\n".join(keep) + ("\n" if keep else ""))


def _clean_action_input_code(src: str) -> str:
    """Remove fences/banners/noise lines from collected Action Input code."""
    lines = src.splitlines()
    keep = []
    for ln in lines:
        if FENCE_TICKS_RE.match(ln):
            continue
        if NOISE_LINE_RE.match(ln):
            continue
        if SECTION_BAR_RE.match(ln):
            continue
        keep.append(ln.rstrip())
    # trim leading/trailing blanks
    while keep and keep[0] == "":
        keep.pop(0)
    while keep and keep[-1] == "":
        keep.pop()
    return ("\n".join(keep) + ("\n" if keep else ""))



def iter_events_from_chunk(chunk: str, cwd: str, state: dict) -> List[StreamEvent]:
    """
    Parse stdout chunk to structured stream events.

    Priority: [EVT]{...} → ReAct fallback (Action/Action Input/Observation/Final).
    Fences:
      - Execute tools: whole block is fenced as ```python and verbatim_on=True
      - Other tools: whole block is fenced as ```text and verbatim_on=True
      - We also record raw code lines into state["_code_buf"] while in python fence.
    """
    events: List[StreamEvent] = []
    chunk = chunk.replace("\r", "\n")
    state.setdefault("_collect_code", False)
    state.setdefault("_code_buf", "")

    def inject_code_buf_to_raw_events():
        buf = state.get("_code_buf", "")
        if state.get("_code_rec") and buf and buf.strip():
            cleaned = clean_code_for_notebook(buf)
            if cleaned.strip():
                state.setdefault("_raw_events", []).append({
                    "type": "code_start", "lang": "python", "source": cleaned
                })
        state["_code_rec"] = False
        state["_code_buf"] = ""

    def close_any_fence():
        "Close code/text fence and turn off verbatim/exec flags; also flush code buffer."
        # buffer the code injection firstly
        inject_code_buf_to_raw_events()

        if state.get("code_on") or state.get("fence_on"):
            events.append(StreamEvent("token", "\n```\n"))
            state["code_on"] = False
            state["fence_on"] = False
        events.append(StreamEvent("mode", {"verbatim": False}))
        state["exec_mode"] = False

    def open_fence(lang: str):
        "Open fence and turn on verbatim mode."
        events.append(StreamEvent("mode", {"verbatim": True, "lang": lang}))
        events.append(StreamEvent("token", f"```{lang}\n"))
        if lang == "python":
            state["code_on"] = True
            state["fence_on"] = False
        else:
            state["code_on"] = False
            state["fence_on"] = True

    for raw_line in chunk.splitlines(keepends=True):
        # 1) EVT channel
        evt = try_parse_evt(raw_line)
        if evt:
            t = evt["type"]
            p = evt["data"] or {}
            state.setdefault("_raw_events", []).append({"type": t, **p})

            if t == "token":
                events.append(StreamEvent("token", p.get("text", "")))
                continue

            if t == "tool_start":
                name = p.get("name", p.get("tool", "tool"))
                state["current_tool"] = name
                close_any_fence()  # Finishing up the old fence + writing code for buffering
                events.append(StreamEvent("token", f"\n### 🛠️ Action: `{name}`\n"))
                is_exec = (name or "").lower() in EXECUTE_TOOL_NAMES
                if is_exec:
                    open_fence("python")
                    state["_code_rec"] = True
                    state["_code_buf"] = ""
                    state["exec_mode"] = True
                else:
                    open_fence("text")
                    state["exec_mode"] = False
                continue
            # 1) Filter each row
            if t == "tool_end":
                # Final step: Inject the recorded code as `code_start`, then close the fence.
                inject_code_buf_to_raw_events()
                close_any_fence()
                # Keep statistics completion
                name = p.get("name") or p.get("tool") or state.get("current_tool") or "tool"
                state.setdefault("_raw_events", []).append({
                    "type": "tool_end",
                    "name": name,
                    "ok": bool(p.get("ok", True)),
                    "duration_ms": p.get("duration_ms"),
                    "error": p.get("error")
                })
                continue
            # 2) EVT tool_log/stdout
            if t in ("tool_log", "stdout"):
                msg = p.get("text", p.get("msg", ""))
                if msg:
                    line = msg if msg.endswith("\n") else msg + "\n"
                    events.append(StreamEvent("token", line))

                continue

            if t in ("artifact", "file"):
                path = p.get("path")
                if path:
                    events.append(StreamEvent("artifact", {"path": path, "kind": p.get("purpose") or p.get("kind")}))
                continue

            if t == "needs_input":
                events.append(StreamEvent("needs_input", {"reason": p.get("reason", "")}))
                continue

            if t == "code_start":
                if not state.get("code_on"):
                    open_fence(p.get("lang", "python"))
                src = p.get("source", "")
                if src:
                    line = src if src.endswith("\n") else src + "\n"
                    events.append(StreamEvent("token", line))
                    if state.get("_code_rec") and state.get("code_on"):
                        # 逐行过滤噪声
                        for ln in line.splitlines(True):
                            if FENCE_RE.match(ln) or OUTPUT_NOISE_RE.match(ln):
                                continue
                            state["_code_buf"] += ln
                continue

            # 3) EVT code_end
            if t == "code_end":
                for k in ("stdout", "stderr"):
                    if p.get(k):
                        out = p[k]
                        out = out if out.endswith("\n") else out + "\n"
                        events.append(StreamEvent("token", out))
                continue

            if t in ("warn", "error"):
                msg = p.get("msg") or p.get("text") or ""
                prefix = "⚠️" if t == "warn" else "❌"
                events.append(StreamEvent("token", f"\n{prefix} {msg}\n"))
                continue

            if t == "final":
                close_any_fence()  # flush code buffer simultaneously
                final_md = p.get("text_md") or p.get("text") or ""
                events.append(StreamEvent("final", final_md))
                continue

            # view unrecognized EVT as normal text
            events.append(StreamEvent("token", raw_line))
            if state.get("_code_rec") and state.get("code_on"):
                state["_code_buf"] += raw_line
            continue

        # 2) ReAct fallback
        line = raw_line
        # ReAct: Action
        m_act = ACTION_LINE_RE.match(line)
        if m_act:
            tool = m_act.group(1).strip()
            state["current_tool"] = tool

            # close old fence & finish up any collecting Action Input code part
            if state.get("_collect_code") and state.get("_code_buf"):
                cleaned = _clean_action_input_code(state["_code_buf"])
                if cleaned.strip():
                    state.setdefault("_raw_events", []).append(
                        {"type": "code_start", "lang": "python", "source": cleaned})
            state["_collect_code"] = False
            state["_code_buf"] = ""

            close_any_fence()
            events.append(StreamEvent("token", f"\n### 🛠️ Action: `{tool}`\n"))

            if (tool or "").lower() in EXECUTE_TOOL_NAMES:
                # Execution Tools and Wait for Action Input before opening the Python fence.
                state["exec_mode"] = True
            else:
                open_fence("text")
                state["exec_mode"] = False
            state.setdefault("_raw_events", []).append({"type": "tool_start", "name": tool})
            continue

        # ReAct: Action Input
        m_in = ACTION_INPUT_LINE_RE.match(line)
        if m_in:
            tail = m_in.group(1) or ""
            # Only when executing the tool, enter the "Collect Action Input Source Code" mode.
            if (state.get("current_tool", "").lower() in EXECUTE_TOOL_NAMES):
                # Open the Python fence (for displaying in chat)
                if not state.get("code_on"):
                    open_fence("python")
                # start collecting
                state["_collect_code"] = True
                state["_code_buf"] = ""
                # take same line's tail
                if tail:
                    state["_code_buf"] += (tail + ("" if tail.endswith("\n") else "\n"))
                # Render the tail portion in the chat (display it exactly as it is within the fenced area).
                events.append(StreamEvent("token", tail + ("" if tail.endswith("\n") else "\n")))
                continue
            else:
                # Non-executable tool, rendered as plain text.
                events.append(StreamEvent("token", tail + ("" if tail.endswith("\n") else "\n")))
                continue

        def _is_action_input_boundary(ln: str) -> bool:
            return bool(
                EXEC_BANNER_RE.match(ln) or
                OUTPUT_HEADER_RE.match(ln) or
                FENCE_TICKS_RE.match(ln) or
                EVT_PREFIX_RE.match(ln) or
                ACTION_LINE_RE.match(ln) or
                OBS_LINE_RE.match(ln) or
                FINAL_LINE_RE.match(ln) or
                SECTION_BAR_RE.match(ln)
            )

        # Plain text: If data is currently being collected, prioritize checking the boundaries; otherwise, continue writing to _code_buf.
        if state.get("_collect_code"):
            if _is_action_input_boundary(line):
                # Reaching the boundary: First, inject the notebook event, then hand this line back to the channel for subsequent rule processing.
                cleaned = _clean_action_input_code(state["_code_buf"])
                if cleaned.strip():
                    state.setdefault("_raw_events", []).append(
                        {"type": "code_start", "lang": "python", "source": cleaned})
                state["_collect_code"] = False
                state["_code_buf"] = ""
                # close python fence simultaneously
                close_any_fence()
            else:
                # Continue accumulating code & rendering text within the fence.
                state["_code_buf"] += line
                events.append(StreamEvent("token", line))
                continue

        # Observation / Final
        if OBS_LINE_RE.match(line) or FINAL_LINE_RE.match(line):
            if state.get("_collect_code") and state.get("_code_buf"):
                cleaned = _clean_action_input_code(state["_code_buf"])
                if cleaned.strip():
                    state.setdefault("_raw_events", []).append(
                        {"type": "code_start", "lang": "python", "source": cleaned})
            state["_collect_code"] = False
            state["_code_buf"] = ""

            close_any_fence()
            events.append(StreamEvent("token", line))
            if FINAL_LINE_RE.match(line):
                events.append(StreamEvent("final", ""))  # 让上层渲染最终 markdown
            continue

        if GEN_PLOTS_RE.match(line) or AVAIL_FILES_RE.match(line):
            state["list_mode"] = "files"
            events.append(StreamEvent("token", line))
            continue

        if state.get("list_mode"):
            mb = BULLET_FILE_RE.match(line)
            if mb:
                name = mb.group(1).strip()
                for cand in (name, os.path.join(cwd, name)):
                    if os.path.exists(cand):
                        events.append(StreamEvent("artifact", {"path": cand, "kind": None}))
                        break
                events.append(StreamEvent("token", line))
                continue
            if line.strip() == "" or line.lower().lstrip().startswith("final"):
                state["list_mode"] = None

        ms = SAVED_LINE_RE.search(line)
        if ms:
            fname = ms.group(2).strip()
            for cand in (fname, os.path.join(cwd, fname)):
                if os.path.exists(cand):
                    events.append(StreamEvent("artifact", {"path": cand, "kind": None}))
                    break
            events.append(StreamEvent("token", line))
            continue

        # Plain text: Output & If within a Python code block, simultaneously enter into the code buffer.
        events.append(StreamEvent("token", line))
        if state.get("_code_rec") and state.get("code_on"):
            if not (FENCE_RE.match(line) or OUTPUT_NOISE_RE.match(line)):
                state["_code_buf"] += line
    return events


def consume_stream(stdout_q: "queue.Queue[str]",
                   history: List[Dict[str, str]],
                   artifacts: List[str],
                   rs: RunState,
                   evs: List[dict],
                   preview_markdown_for_path,
                   find_paths_or_files):
    """
    Read chunks from stdout_q, convert to StreamEvent, update history/artifacts/events_state.
    Yields: (history, artifacts, chatbot_update, run_state, events_state)
    NOTE: preview_markdown_for_path & find_paths_or_files are injected to avoid circular imports.
    """

    acc = history[-1]["content"] if history else ""
    text_buf: List[str] = []
    last_flush = time.time()
    previewed = set()
    FLUSH_EVERY = 0.08
    state = {"current_tool": None, "code_on": False, "fence_on": False, "exec_mode": False, "verbatim_on": False, "list_mode": None, "_raw_events": []}

    while True:
        try:
            chunk = stdout_q.get(timeout=0.1)
        except queue.Empty:
            chunk = None

        if chunk == "__<<DONE>>__":
            rs.running = False
            break

        if chunk:
            events = iter_events_from_chunk(chunk, os.getcwd(), state)
            for ev in events:

                if ev.type == "mode":
                    vb = bool((ev.payload or {}).get("verbatim"))
                    state["verbatim_on"] = vb

                if ev.type == "token":
                    txt = ev.payload if isinstance(ev.payload, str) else str(ev.payload)
                    txt = strip_ansi(txt)
                    if state.get("code_on") or state.get("fence_on"):
                        pass
                    else:
                        txt = html.escape(txt)
                    text_buf.append(txt)


                elif ev.type == "tool_start":
                    name = ev.payload.get("name", "tool")
                    text_buf.append(f"\n### 🛠️ Action: `{name}`\n")

                elif ev.type == "artifact":
                    path = ev.payload.get("path")
                    if path and os.path.exists(path) and path not in artifacts:
                        artifacts.append(path)
                        text_buf.append(preview_markdown_for_path(path))

                elif ev.type == "needs_input":
                    rs.awaiting = True

                elif ev.type == "final":
                    # close any fence
                    if state.get("code_on"):
                        text_buf.append("\n```\n")
                        state["code_on"] = False
                    if state.get("fence_on"):
                        text_buf.append("\n```\n")
                        state["fence_on"] = False
                    # close fence + close verbatim
                    if state.get("verbatim_on"):
                        text_buf.append("\n```\n")
                        state["verbatim_on"] = False
                    # Render final text
                    final_md = ev.payload if isinstance(ev.payload, str) else (ev.payload or "")
                    text_buf.append("\n\n" + final_md + "\n\n")

            # reinsurance：The path/filename appeared in a regular token.
            for p in find_paths_or_files(chunk, os.getcwd()):
                if p not in artifacts:
                    artifacts.append(p)
                    text_buf.append(preview_markdown_for_path(p))

        # refresh
        now = time.time()
        if text_buf and (now - last_flush >= FLUSH_EVERY or chunk is None):
            acc += "".join(text_buf)
            text_buf.clear()
            history[-1]["content"] = clean_text(acc)
            # Merge the new events in this batch before/after flushing.
            if state.get("_raw_events"):
                evs.extend(state["_raw_events"])
                state["_raw_events"].clear()

            # write back events when yielding
            yield history, artifacts, rs, evs
            last_flush = now

        if chunk and (INPUT_PROMPT in chunk):
            rs.awaiting = True

        if rs.awaiting and chunk is not None:
            if text_buf:
                acc += "".join(text_buf)
                text_buf.clear()
                history[-1]["content"] = clean_text(acc)
            # Merge the new events in this batch before/after flushing.
            if state.get("_raw_events"):
                evs.extend(state["_raw_events"])
                state["_raw_events"].clear()

            yield history, artifacts, rs, evs
            return

    # ending
    if state.get("code_on"):
        acc += "\n```\n"
        state["code_on"] = False
    if state.get("fence_on"):
        acc += "\n```\n"
        state["fence_on"] = False
    if text_buf:
        acc += "".join(text_buf)
    if not acc.strip():
        acc = "_No output captured._"
    history[-1]["content"] = clean_text(acc)

    if state.get("_raw_events"):
        evs.extend(state["_raw_events"])
        state["_raw_events"].clear()

    yield history, artifacts, rs, evs

