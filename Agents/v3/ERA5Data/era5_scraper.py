import os, re, time, json, pathlib
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

# ----------------- Basic configuration -----------------
# Base portal for Copernicus Climate Data Store (CDS)
BASE = "https://cds.climate.copernicus.eu"

# Candidate list pages to maximize recall when searching ERA5-like datasets.
# The site has multiple query params historically; we probe several to be robust.
DATASETS_LIST_URL_CANDIDATES = [
    "/datasets?text={q}",
    "/datasets?search={q}",
    "/datasets?keywords={q}",
    "/datasets?type=dataset&q={q}"
]

# Polite headers; language fallback includes EN + ZH for mixed pages.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (ERA5MetaScraper; +https://example.org)",
    "Accept-Language": "en;q=0.9,zh;q=0.8"
}

# Output directory for normalized JSONs (one per dataset)
OUTDIR = pathlib.Path("ERA5Meta")
NORM_DIR = OUTDIR / "normalized"
NORM_DIR.mkdir(parents=True, exist_ok=True)

# HTTP settings
TIMEOUT = 30
S = requests.Session()
S.headers.update(HEADERS)

# ----------------- Helpers -----------------
def fetch(url, params=None):
    """
    GET a web page with small exponential backoff.
    Returns HTML text on HTTP 200, otherwise "".
    """
    for i in range(5):
        try:
            r = S.get(url, params=params, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.text
            # backoff even on non-200 to be gentle
            time.sleep(1 + i)
        except requests.RequestException:
            # network hiccup -> retry
            time.sleep(1 + i)
    return ""

def fetch_json(url):
    """
    GET a JSON resource with retries.
    Returns parsed dict on success, otherwise {}.
    """
    for i in range(5):
        try:
            r = S.get(url, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
        except Exception:
            time.sleep(1 + i)
    return {}

# ----------------- Step 1: discover dataset slugs -----------------
def extract_dataset_slugs(query="era5", max_pages=30):
    """
    Crawl CDS dataset listing pages to collect dataset slugs.
    - Tries several listing URL patterns.
    - Paginates until a page yields no new hits.
    Returns a sorted list of unique slugs.
    """
    slugs = set()
    for tpl in DATASETS_LIST_URL_CANDIDATES:
        for page in range(1, max_pages + 1):
            list_url = urljoin(BASE, tpl.format(q=query))
            params = {"page": page}
            html = fetch(list_url, params=params)
            if not html:
                break
            soup = BeautifulSoup(html, "lxml")
            found = 0
            # CDS dataset links look like /datasets/<slug>
            for a in soup.select('a[href^="/datasets/"]'):
                href = a.get("href", "")
                path = urlparse(href).path
                parts = path.strip("/").split("/")
                if len(parts) >= 2 and parts[0] == "datasets":
                    slug = parts[1]
                    # filter out anchors/query noise
                    if slug and ("?" not in slug) and ("#" not in slug):
                        if slug not in slugs:
                            slugs.add(slug)
                            found += 1
            # stop paging when this pattern yields no new slugs
            if found == 0:
                break
    return sorted(slugs)

# ----------------- Step 2: merge collection + layout + form -----------------
def inject_form_into_layout(layout_json, form_json):
    """
    Place the raw 'form' JSON (download UI schema) inside the 'Download' section
    of the 'layout' JSON (page structure), so a single document mirrors the website tabs:
      - Overview
      - Download (we inject here)
      - Documentation
    If Download section is missing, create it.
    """
    body = layout_json.get("body", {})
    main = body.get("main", {})
    sections = main.get("sections", [])
    target = None
    for sec in sections:
        sid = (sec.get("id") or "").lower().strip()
        title = (sec.get("title") or "").lower().strip()
        if sid == "download" or title == "download":
            target = sec
            break
    # Create a Download section if it doesn't exist
    if target is None:
        target = {"title": "Download", "id": "download", "blocks": []}
        sections.append(target)
        if "sections" not in main:
            layout_json.setdefault("body", {}).setdefault("main", {})["sections"] = sections
    # Overwrite blocks with the full form JSON as a single block
    target["blocks"] = [form_json]
    return layout_json

def assemble_dataset(slug):
    """
    For a given dataset slug:
      1) GET its STAC-like 'collection' JSON from the CDS catalogue API.
      2) Follow 'layout' and 'form' links inside 'links'.
      3) Inject the 'form' JSON into the 'Download' section of the 'layout'.
      4) Return a single OrderedDict that:
         - preserves all original collection fields, and
         - adds 'related datasets' (flattened) and
         - adds 'webpages' (the merged layout+form structure).
    """
    print(f"→ Processing {slug} ...")
    coll_url = f"{BASE}/api/catalogue/v1/collections/{slug}"
    coll = fetch_json(coll_url)
    if not coll or not isinstance(coll, dict):
        print(f"  ⚠️ collection fetch failed for {slug}")
        return None

    # Resolve hyperlinks embedded in collection.links
    links = coll.get("links", [])
    layout_url = next((lk["href"] for lk in links if lk.get("rel") == "layout"), None)
    form_url = next((lk["href"] for lk in links if lk.get("rel") == "form"), None)
    related_ls = [lk for lk in links if lk.get("rel") == "related"]

    # Pull layout + form; if layout missing, we don't attempt injection
    layout = fetch_json(layout_url) if layout_url else {}
    form = fetch_json(form_url) if form_url else {}
    layout_with_form = inject_form_into_layout(layout, form) if layout else layout

    # Build normalized output document:
    # - Start with the original collection dict (all fields preserved, order kept)
    # - Add "related datasets" as a top-level convenience key
    # - Add "webpages" containing the merged layout-with-form
    out = OrderedDict()
    for k, v in coll.items():
        out[k] = v
    if related_ls:
        out["related datasets"] = related_ls
    out["webpages"] = layout_with_form
    return out

# ----------------- Orchestrator -----------------
def main():
    """
    1) Discover all ERA5-like dataset slugs via list pages.
    2) For each slug:
         - Assemble a normalized JSON (collection + layout + form).
         - Save to ERA5Meta/normalized/dataset_<slug>.json
    """
    slugs = extract_dataset_slugs("era5")
    print(f"Found {len(slugs)} ERA5-like datasets:")
    for s in slugs:
        print("  -", s)

    for slug in slugs:
        try:
            out = assemble_dataset(slug)
            if out:
                fn = NORM_DIR / f"dataset_{slug}.json"
                with open(fn, "w", encoding="utf-8") as f:
                    json.dump(out, f, ensure_ascii=False, indent=2)
                print(f"Saved -> {fn.name}")
        except Exception as e:
            # Keep the loop resilient: log and continue
            print(f"Error on {slug}: {e}")

if __name__ == "__main__":
    main()
