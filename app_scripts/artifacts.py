from __future__ import annotations
import re, os, base64, json, pandas as pd
from typing import List, Tuple
from PIL import Image
import html as _h

IMG_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp")
PATH_OR_FILE_RE = re.compile(
    r"(?i)(?:"
    r"([A-Za-z]:[^\s]+?\.(?:png|jpg|jpeg|csv|json))|"  # Windows absolute path
    r"(\.[^\s]+?\.(?:png|jpg|jpeg|csv|json))|"  # Relative paths (starting with .)
    r"([A-Za-z0-9._\-]+?\.(?:png|jpg|jpeg|csv|json))"  # Bare file name
    r")"
)

def preview_markdown_for_path(p: str) -> str:
    """Return a small Markdown snippet to preview a file path."""

    p = os.path.abspath(p)
    name = os.path.basename(p)
    ext = os.path.splitext(name)[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        return f"\n![{name}](file={p})\n"
    elif ext == ".csv" and not name.lower().startswith("chatlog_"):
        try:
            df = pd.read_csv(p).head(5)
            return f"\n**{name}**\n\n" + df.to_markdown(index=False) + "\n"
        except Exception:
            return f"\n[{name}](file={p})\n"
    elif ext == ".json":
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            snippet = json.dumps(data, ensure_ascii=False, indent=2)
            if len(snippet) > 4000:  # 太长就截断
                snippet = snippet[:4000] + "\n…"
            return f"\n**{name}**\n\n```json\n{snippet}\n```\n"
        except Exception:
            return f"\n[{name}](file={p})\n"
    else:
        return f"\n[{name}](file={p})\n"

def build_images_html(img_paths: list[str]) -> str:
    cards = []
    for p in img_paths or []:
        try:
            with open(p, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
            ext = os.path.splitext(p)[1].lower().lstrip(".") or "png"
            mime = f"image/{'jpeg' if ext in ('jpg','jpeg') else ext}"
            src  = f"data:{mime};base64,{b64}"
            name = _h.escape(os.path.basename(p))
            cards.append(
                f"<div class='imgcard'><figure>"
                f"<img src='{src}' alt='{name}' "
                f"onclick=\"document.getElementById('lightbox-img').src='{src}';"
                f"document.getElementById('lightbox').style.display='flex'\">"
                f"<figcaption>{name}</figcaption></figure></div>"
            )
        except Exception:
            continue

    if not cards:
        return "<div style='color:#888;'>No images</div>"

    return (
      "<div class='imggrid'>" + "\n".join(cards) + "</div>"
      "<div id='lightbox' onclick=\"this.style.display='none'\">"
      "<img id='lightbox-img' src='' alt='preview'></div>"
    )


def render_artifacts(artifacts: List[str]) -> Tuple[List[Image.Image], str]:
    """Return (images_for_gallery, html_for_tables) from a list of artifact paths."""
    images, html = [], ""
    for p in artifacts or []:
        try:
            if p.lower().endswith(IMG_EXT):
                images.append(p)
            elif p.lower().endswith(".csv") and not p.lower().startswith("chatlog_"):
                df = pd.read_csv(p).head(5)
                html += f"<h4>{os.path.basename(p)}</h4>" + df.to_html(index=False)
            elif p.lower().endswith(".json"):
                df = pd.read_json(p).head(5)
                html += f"<h4>{os.path.basename(p)}</h4>" + df.to_html(index=False)
        except Exception:
            pass
    return images, html

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
