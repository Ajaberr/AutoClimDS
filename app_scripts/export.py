from __future__ import annotations
import re, os, csv, json, datetime, textwrap, time
import nbformat as nbf
import pandas as pd
from typing import List, Dict, Any, Optional

from collections import defaultdict

FENCE_RE = re.compile(r'^\s*```')
OUTPUT_NOISE_RE = re.compile(
    r'^\s*(📝|🔍|📊|✅|❌|⚠️|Output:|Full traceback:|Traceback|Error|Exception|Observation:|Final Answer:)\b',
    re.IGNORECASE
)

def summarize_tools(evs: List[dict]) -> pd.DataFrame:
    stat = defaultdict(lambda: {"count":0,"ok":0,"fail":0,"dur":[], "last_error":""})
    last_tool = None
    for e in evs or []:
        t = e.get("type")
        if t == "tool_start":
            name = e.get("name") or e.get("tool") or "tool"
            stat[name]["count"] += 1
            last_tool = name
        elif t == "tool_end":
            name = e.get("name") or last_tool or e.get("tool") or "tool"
            ok = bool(e.get("ok", True))
            stat[name]["ok"]   += int(ok)
            stat[name]["fail"] += int(not ok)
            if "duration_ms" in e:
                try:
                    stat[name]["dur"].append(float(e["duration_ms"]))
                except Exception:
                    pass
            if not ok and e.get("error"):
                stat[name]["last_error"] = str(e["error"])[:200]

    rows = []
    for name, s in stat.items():
        avg = (sum(s["dur"])/len(s["dur"])) if s["dur"] else None
        rows.append([name, s["count"], s["ok"], s["fail"], (round(avg,1) if avg else None), s["last_error"]])
    rows.sort(key=lambda r: (-r[2], r[3], r[0]))  # ok desc, fail asc, name
    return pd.DataFrame(rows, columns=["tool","count","ok","fail","avg_ms","last_error"])

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

def make_notebook_from_events(evs: List[dict], out_path: Optional[str] = None) -> str:
    """
    Build a reproducible Jupyter notebook from event stream.
    - Adds kernelspec metadata
    - Records run context + tool recap
    - Captures code from code_start and fenced ```python blocks
    - Embeds artifacts (img/csv/json) with minimal runnable code
    """

    # Notebook skeleton
    nb = nbf.v4.new_notebook()
    nb.metadata.update({
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    })
    md   = nbf.v4.new_markdown_cell
    code = nbf.v4.new_code_cell

    # Run context
    run_id = None
    for e in evs or []:
        if e.get("type") == "run_start":
            run_id = e.get("run_id"); break
    ts_iso = datetime.datetime.now().isoformat(timespec="seconds")
    title  = f"AutoClimDS Research Notebook ({run_id or ts_iso})"
    nb.cells.append(md(f"# {title}\nThis notebook was generated from an AutoClimDS agent run."))

    # Recap tools
    tool_starts = [e for e in (evs or []) if e.get("type") == "tool_start"]
    recap_lines = []
    for i, e in enumerate(tool_starts, 1):
        name  = e.get("name") or e.get("tool") or "tool"
        ipt   = e.get("input") or e.get("args")
        ipt_s = json.dumps(ipt, ensure_ascii=False)[:300] + ("…" if ipt and len(json.dumps(ipt, ensure_ascii=False)) > 300 else "")
        recap_lines.append(f"{i}. **{name}** — input preview: `{ipt_s}`")
    nb.cells.append(md("## Run Context\n"
                       f"- **Run ID:** `{run_id or 'N/A'}`\n"
                       f"- **Generated At:** `{ts_iso}`\n"
                       f"- **Tool Calls:** {len(tool_starts)}\n\n" +
                       ("**Sequence:**\n" + "\n".join(recap_lines) if recap_lines else "_No tool_start events captured._")))

    # Environment setup
    nb.cells.append(code(textwrap.dedent("""\
        # Environment setup (idempotent)
        try:
            import xarray, netCDF4, pandas, matplotlib
        except Exception:
            %pip -q install xarray netCDF4 pandas matplotlib cartopy s3fs zarr
        import pandas as pd
    """)))

    # Code cells: explicit code_start
    for e in evs or []:
        if e.get("type") == "code_start":
            src = e.get("source") or ""
            src = clean_code_for_notebook(src)
            if src.strip():
                nb.cells.append(nbf.v4.new_code_cell(src))

    # Fallback: fenced ```python blocks from text/stdout
    text_blob = "\n".join((e.get("text") or e.get("msg") or "")
                          for e in (evs or []) if e.get("type") in ("stdout", "token"))
    for m in re.finditer(r"```python\s+([\s\S]*?)```", text_blob, re.IGNORECASE):
        src = m.group(1).strip()
        if src:
            nb.cells.append(code(src + "\n"))

    # Artifacts embedding
    # Prefer relative paths inside current working dir if possible
    arts: List[str] = []
    for e in (evs or []):
        if e.get("type") == "artifact" and e.get("path"):
            p = e["path"]
            try:
                if os.path.exists(p):
                    # make relative if file is under CWD
                    cwd = os.path.abspath(os.getcwd())
                    ap  = os.path.abspath(p)
                    if ap.startswith(cwd + os.sep):
                        p = os.path.relpath(ap, cwd)
            except Exception:
                pass
            if p not in arts:
                arts.append(p)

    if arts:
        nb.cells.append(md("## Artifacts Preview"))
        for p in arts[:16]:
            ext = os.path.splitext(p)[1].lower()
            if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                nb.cells.append(md(f"**{os.path.basename(p)}**\n\n![]({p})"))
            elif ext == ".csv":
                nb.cells.append(code(
                    f"# {os.path.basename(p)}\nimport pandas as pd\n_df = pd.read_csv(r'''{p}''')\n_df.head()"))
            elif ext == ".json":
                nb.cells.append(code(
                    f"# {os.path.basename(p)}\nimport json, pprint\npprint.pp(json.load(open(r'''{p}''','r',encoding='utf-8')))"))

    # Conclusion
    final = None
    for e in reversed(evs or []):
        if e.get("type") == "final":
            final = e.get("text_md") or e.get("text")
            break
    nb.cells.append(md("## Conclusion\n" + (final or "_No explicit final answer captured._")))

    # Save
    if not out_path:
        out_path = os.path.abspath(f"research_run_{int(time.time()*1000)}.ipynb")
    with open(out_path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    return out_path


def build_notebook_and_return_path(evs: list) -> str:
    """
    Build a minimal reproducible notebook from events and return absolute file path.
    THIS MUST return a path string that exists on disk.
    """
    # `make_notebook_from_events` write the file and return the path.
    out_path = make_notebook_from_events(evs, out_path=None)
    print(out_path)
    # Defense: Ensure it is a genuine string.
    if not isinstance(out_path, str):
        raise RuntimeError(f"Notebook builder returned non-str: {type(out_path)}")
    if not os.path.exists(out_path):
        raise FileNotFoundError(f"Notebook file not found: {out_path}")
    return out_path

def build_notebook_path(evs: list) -> str:
    out_path = os.path.abspath(f"research_{int(time.time()*1000)}.ipynb")
    try:
        make_notebook_from_events(evs, out_path=out_path)
    except Exception as e:
        import nbformat as nbf
        nb = nbf.v4.new_notebook()
        nb.cells.append(nbf.v4.new_markdown_cell(f"Notebook build error:\n\n{e!r}"))
        with open(out_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)
    return out_path


def save_chat_csv(history):
    """Dump chat history to CSV and return absolute path."""
    fname = f"chatlog_{datetime.datetime.now():%Y%m%d_%H%M%S}.csv"
    out_path = os.path.abspath(os.path.join(os.getcwd(), fname))
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["role", "content"])
        for m in history:
            w.writerow([m.get("role", ""), (m.get("content", "") or "").replace("\r", "")])
    return out_path

def refresh_chat_csv(history):
    """Gradio-friendly wrapper returning file path for DownloadButton."""
    path = save_chat_csv(history)
    return path