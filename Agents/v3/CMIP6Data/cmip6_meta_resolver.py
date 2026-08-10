# -*- coding: utf-8 -*-
"""
CMIP6 Meta Resolver
-------------------
Use a locally stored CMIP6 metadata JSON to:
  1) Inspect: print a minimal example mapping (instance_id, directory path,
     filename prefix, and ESGF queries) to check the format.
  2) Search: resolve real datasets/files on ESGF with robust fail-over.
  3) Download: download matched files to disk.

Minimal DRS fields:
  mip_era, activity_id, institution_id, source_id, experiment_id,
  variant_label, table_id, variable_id, grid_label, version

CLI:
  - Inspect one record (default: first)
      python cmip6_meta_resolver.py inspect
      python cmip6_meta_resolver.py inspect --pick 20

  - Search ESGF (dataset or file level) with a local-record filter and show N hits
      python cmip6_meta_resolver.py search --type File --limit 50 --filter activity_id=RFMIP source_id=LBLRTM-12-8 variable_id=rld

  - Download a few matched files
      python cmip6_meta_resolver.py download --limit 3 --filter activity_id=DCPP experiment_id=dcppA-hindcast variable_id=sfcWind

"""

from __future__ import annotations
import os
import sys
import json
import time
import argparse
import hashlib
from typing import Dict, Any, Iterable, Tuple, Optional, List

import requests

# ---------- ESGF settings (edit if needed) ----------
ESGF_NODES = [
    "https://esgf-node.llnl.gov",
    "https://esgf-data.dkrz.de",
    "https://esgf-node.ipsl.upmc.fr",
]
ESGF_API = "/esg-search/search"
HTTP_TIMEOUT = 30
RETRIES_PER_NODE = 2
BACKOFF_SEC = 1.5

# ---------- Output ----------
OUTDIR = "cmip6_out"
os.makedirs(OUTDIR, exist_ok=True)

# ---------- DRS core fields ----------
"""
1. mip_era
   → Project name (e.g., "CMIP6")
   Defines the overall model intercomparison project.

2. activity_id
   → Experiment activity or MIP group (e.g., "CMIP", "ScenarioMIP")
   Indicates the specific scientific focus or experiment activity under CMIP6.

3. institution_id
   → Data-producing institution (e.g., "MOHC")
   Refers to the organization or research center that performed the simulations.

4. source_id
   → Model name (e.g., "HadGEM3-GC31-MM")
   Identifies the Earth System Model (ESM) or climate model used to produce the data.

5. experiment_id
   → Experiment type (e.g., "historical", "ssp585")
   Describes the experimental configuration or forcing scenario.

6. variant_label
   → Realization/member label (e.g., "r1i1p1f3")
   Distinguishes between different ensemble members of the same experiment.

7. table_id
   → CMIP output table / frequency type (e.g., "Amon", "day", "Efx")
   Indicates the temporal frequency and variable group.

8. variable_id
   → Variable short name (e.g., "tas", "pr", "psl")
   Refers to the physical quantity measured or simulated in the dataset.

9. grid_label
   → Grid version label (e.g., "gn", "gr", "gr1")
   Describes the grid configuration (native, regridded, etc.).

10. version
    → Dataset version identifier (e.g., "v20191207")
    Indicates the publication or revision version of the dataset.
"""

DRS_FIELDS = [
    "mip_era",        # usually "CMIP6"
    "activity_id",
    "institution_id",
    "source_id",
    "experiment_id",
    "variant_label",  # (= member_id)
    "table_id",
    "variable_id",
    "grid_label",
    "version",
]

# ========== JSON structure sniff ==========

def sniff_structure(path: str, sample_bytes: int = 4096) -> str:
    """Return 'array' | 'object' | 'jsonl' based on the first bytes."""
    with open(path, "rb") as f:
        head = f.read(sample_bytes)
    s = head.lstrip()
    if not s:
        return "jsonl"  # fallback
    c0 = chr(s[0])
    if c0 == "[":
        return "array"
    if c0 == "{":
        return "object"
    return "jsonl"


def iter_records(path: str) -> Iterable[Dict[str, Any]]:
    """
    Yield records as dicts from:
      - array JSON  [ {...}, {...} ]
      - object JSON { "key": {...}, ... }  (adds _top_key)
      - jsonl       {...}\\n{...}\\n
    """
    mode = sniff_structure(path)
    if mode == "array":
        with open(path, "r", encoding="utf-8") as f:
            for rec in json.load(f):
                if isinstance(rec, dict):
                    yield rec
    elif mode == "object":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, rec in data.items():
            if isinstance(rec, dict):
                rec = dict(rec)  # shallow copy
                rec.setdefault("_top_key", k)
                yield rec
    else:  # jsonl
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    if isinstance(rec, dict):
                        yield rec
                except Exception:
                    continue


# ========== DRS helpers ==========

def rec_to_instance_id(rec: Dict[str, Any]) -> str:
    """CMIP6 instance_id (with version) in dotted form."""
    vals = [
        rec.get("mip_era", "CMIP6"),
        rec.get("activity_id", ""),
        rec.get("institution_id", ""),
        rec.get("source_id", ""),
        rec.get("experiment_id", ""),
        rec.get("variant_label", ""),
        rec.get("table_id", ""),
        rec.get("variable_id", ""),
        rec.get("grid_label", ""),
        rec.get("version", ""),
    ]
    return ".".join(v for v in map(str, vals) if v)


def rec_to_directory_path(rec: Dict[str, Any]) -> str:
    """Directory path-like DRS view (no leading slash)."""
    parts = [
        rec.get("mip_era", "CMIP6"),
        rec.get("activity_id", ""),
        rec.get("institution_id", ""),
        rec.get("source_id", ""),
        rec.get("experiment_id", ""),
        rec.get("variant_label", ""),
        rec.get("table_id", ""),
        rec.get("variable_id", ""),
        rec.get("grid_label", ""),
        rec.get("version", ""),
    ]
    return "/".join(p for p in parts if p) + "/"


def rec_to_filename_prefix(rec: Dict[str, Any]) -> str:
    """Common filename prefix (without the date range at the end)."""
    parts = [
        rec.get("variable_id", ""),
        rec.get("table_id", ""),
        rec.get("source_id", ""),
        rec.get("experiment_id", ""),
        rec.get("variant_label", ""),
        rec.get("grid_label", ""),
    ]
    return "_".join(p for p in parts if p) + "_"


def rec_to_esgf_query(rec: Dict[str, Any],
                      target: str = "File",
                      latest: bool = True,
                      minimal: bool = True) -> Dict[str, str]:
    """
    Build an ESGF search query dict (no request performed here).
    target: "Dataset" or "File"
    minimal: only use fields that help uniquely locate the record.
    """
    q = {
        "project": "CMIP6",
        "type": target,
        "distrib": "true",
        "latest": "true" if latest else "false",
    }
    if minimal:
        keys = ["activity_id","institution_id","source_id","experiment_id",
                "variant_label","table_id","variable_id","grid_label","version"]
    else:
        keys = DRS_FIELDS

    for k in keys:
        v = rec.get(k)
        if v not in (None, "", [], {}):
            q[k] = str(v)
    return q


# ========== ESGF client ==========

def _http_get_json(node: str, params: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """GET json with retry + backoff; return parsed JSON or None."""
    url = node + ESGF_API
    for attempt in range(RETRIES_PER_NODE):
        try:
            r = requests.get(url, params=params, timeout=HTTP_TIMEOUT)
            if r.status_code == 200:
                return r.json()
        except requests.RequestException:
            pass
        time.sleep(BACKOFF_SEC * (attempt + 1))
    return None


def esgf_search(params: Dict[str, str]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    """
    Try ESGF nodes in order. Return (node, docs) where docs is a list of hits.
    """
    for node in ESGF_NODES:
        js = _http_get_json(node, params)
        if not js:
            continue
        docs = js.get("response", {}).get("docs", [])
        if docs:
            return node, docs
    return None, []


def pick_first_file_url(doc: Dict[str, Any]) -> Optional[str]:
    """
    From a 'File' doc, choose a direct URL we can download (HTTPServer or THREDDS).
    ESGF schema differs across nodes; we try the common keys.
    """
    # try exact 'url' array of "link|protocol" pairs
    urls = doc.get("url") or []
    if isinstance(urls, list):
        for u in urls:
            # examples: "http://...|application/netcdf|HTTPServer"
            parts = str(u).split("|")
            if len(parts) >= 3 and parts[-1].lower() in ("httpserver", "thredds"):
                return parts[0]
    # sometimes there is a single string
    if isinstance(urls, str) and urls:
        return urls.split("|")[0]
    return None


def download_file(url: str, outdir: str) -> str:
    """
    Stream download a file to 'outdir'. The filename is derived from the URL.
    Returns the local path.
    """
    os.makedirs(outdir, exist_ok=True)
    fname = url.split("/")[-1].split("?")[0]
    # be conservative: short hash prefix to avoid collisions
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]
    local = os.path.join(outdir, f"{h}_{fname}")

    with requests.get(url, stream=True, timeout=HTTP_TIMEOUT) as r:
        r.raise_for_status()
        with open(local, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 256):
                if chunk:
                    f.write(chunk)
    return local


# ========== High-level commands ==========

def cmd_inspect(args: argparse.Namespace) -> None:
    """Print a single example mapping from the JSON file."""
    rec = None
    for i, r in enumerate(iter_records(args.json)):
        if args.pick is None or i == args.pick:
            rec = r
            break
    if not rec:
        print("[ERR] No records found.")
        return

    example = {
        "instance_id": rec_to_instance_id(rec),
        "directory_path": rec_to_directory_path(rec),
        "filename_prefix": rec_to_filename_prefix(rec),
        "esgf_query_minimal_dataset": rec_to_esgf_query(rec, target="Dataset", minimal=True),
        "esgf_query_minimal_file": rec_to_esgf_query(rec, target="File", minimal=True),
    }
    print(json.dumps(example, indent=2, ensure_ascii=False))


def _rec_matches_filters(rec: Dict[str, Any], filters: List[str]) -> bool:
    """
    Return True if rec matches all key=value filters (exact match, string compare).
    Example: ["activity_id=DCPP", "variable_id=sfcWind"]
    """
    for spec in filters:
        if "=" not in spec:
            continue
        k, v = spec.split("=", 1)
        if str(rec.get(k, "")) != v:
            return False
    return True


def cmd_search(args: argparse.Namespace) -> None:
    """
    Iterate local records (optionally filtered) and query ESGF for matches.
    Print a few results.
    """
    count = 0
    hits = 0
    for rec in iter_records(args.json):
        if args.filter and not _rec_matches_filters(rec, args.filter):
            continue

        q = rec_to_esgf_query(rec, target=args.type, minimal=True, latest=not args.include_non_latest)
        node, docs = esgf_search(q)
        count += 1

        if node and docs:
            hits += 1
            print(f"[HIT] node={node} type={args.type}  id={rec_to_instance_id(rec)}")
            # print a compact line for first result
            doc = docs[0]
            title = doc.get("title") or doc.get("id") or "(no-title)"
            print("      ", title)
        else:
            print(f"[MISS] type={args.type} id={rec_to_instance_id(rec)}")

        if args.limit and hits >= args.limit:
            break
    print(f"\n[SUMMARY] scanned={count}, hits={hits}")


def cmd_download(args: argparse.Namespace) -> None:
    """
    Find 'File' hits and download up to N files.
    """
    saved = 0
    for rec in iter_records(args.json):
        if args.filter and not _rec_matches_filters(rec, args.filter):
            continue

        q = rec_to_esgf_query(rec, target="File", minimal=True, latest=not args.include_non_latest)
        node, docs = esgf_search(q)
        if not (node and docs):
            continue

        url = pick_first_file_url(docs[0])
        if not url:
            continue

        try:
            local = download_file(url, args.outdir)
            saved += 1
            print(f"[OK] {url}  ->  {local}")
        except Exception as e:
            print(f"[ERR] download failed: {e}")

        if args.limit and saved >= args.limit:
            break

    print(f"\n[SUMMARY] downloaded={saved}, outdir={args.outdir}")


# ========== CLI ==========

def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Resolve/Download CMIP6 files using local JSON metadata only.")
    p.add_argument("--json", default="./CMIP6Meta/220514_CMIP6_metaData_restartedInd-24949000.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    # inspect
    s = sub.add_parser("inspect", help="Print an example mapping from one record")
    s.add_argument("--pick", type=int, default=None, help="Index of the record to show (default: first)")
    s.set_defaults(func=cmd_inspect)

    # search
    s = sub.add_parser("search", help="Resolve ESGF hits (Dataset/File) for matching records")
    s.add_argument("--type", choices=["Dataset", "File"], default="File")
    s.add_argument("--filter", nargs="*", default=[], help="Key=Value filters applied to local records")
    s.add_argument("--limit", type=int, default=10, help="Stop after N hits found (for display)")
    s.add_argument("--include-non-latest", action="store_true", help="Include non-latest versions in ESGF search")
    s.set_defaults(func=cmd_search)

    # download
    s = sub.add_parser("download", help="Download a few matched files")
    s.add_argument("--filter", nargs="*", default=[], help="Key=Value filters applied to local records")
    s.add_argument("--limit", type=int, default=3, help="Max number of files to download")
    s.add_argument("--outdir", default=os.path.join(OUTDIR, "files"), help="Download directory")
    s.add_argument("--include-non-latest", action="store_true", help="Include non-latest versions in ESGF search")
    s.set_defaults(func=cmd_download)

    return p


def main() -> None:
    cli = build_cli()
    args = cli.parse_args()
    if not os.path.exists(args.json):
        print(f"[ERR] JSON not found: {args.json}")
        sys.exit(2)
    args.func(args)


if __name__ == "__main__":
    main()
