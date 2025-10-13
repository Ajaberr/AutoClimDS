import requests
import csv
import time
import pandas as pd
from urllib.parse import urlparse
from collections import defaultdict

# === USER SETTINGS ===
INPUT_CSV = r"C:\Users\ayon-\Desktop\datasets_with_urls_check.csv"
URL_COLUMN = "related_url_1"
BATCH_SIZE = 500
OUTPUT_PREFIX = "api_check_results_batch"
TIMEOUT = 8
SLEEP = 0.3

# === Keywords for detecting API-like URLs ===
API_KEYWORDS = [
    # General API terms
    "api", "rest", "rpc", "json", "xml", "odata", "graphql", "soap",
    "swagger", "openapi", "interface", "endpoint", "service", "feed",
    "query", "request", "response", "resource", "dataset", "collection",

    # Geospatial / scientific APIs
    "wms", "wfs", "wcs", "wps", "csw", "geojson", "arcgis", "mapserver",
    "feature", "coverage", "geoserver", "ows", "ogc", "sos", "stac",
    "geoapi", "thredds", "opendap", "erddap", "hydroserver", "timeseries",

    # Data-related / portal keywords
    "data", "download", "catalog", "metadata", "record", "access", "repository",
    "search", "export", "fetch", "inventory", "archive", "getdata", "viewdata",

    # Machine-readable / automation indicators
    "v1", "v2", "v3", "public", "restapi", "jsonapi", "endpoint", "ajax",
    "api-docs", "spec", "schema", "jsonld", "rdf", "sparql", "ttl", "feed",
    "atom", "rss",

    # Environmental / research domains
    "nasa", "noaa", "usgs", "copernicus", "geodata", "earthdata",
    "aadc", "polar", "arcticdata", "nsidc", "esa"
]

# --- Helper functions ---
def is_api_like(url, headers, content_type, text_preview):
    if any(kw in url.lower() for kw in API_KEYWORDS):
        return True
    if "application/json" in content_type.lower() or "application/xml" in content_type.lower():
        return True
    preview = text_preview.strip().lower()[:200]
    if preview.startswith("{") or preview.startswith("["):
        return True
    if preview.startswith("<?xml") or "<response" in preview:
        return True
    return False

def check_url(url):
    """Check if a URL works and is API-like"""
    try:
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        if response.status_code >= 400:
            response = requests.get(url, timeout=TIMEOUT)
    except requests.RequestException:
        return {"url": url, "status": "ERROR", "content_type": "N/A", "api_like": False, "working": False}

    content_type = response.headers.get("Content-Type", "unknown")
    text_preview = response.text[:300] if hasattr(response, "text") else ""
    api_like = is_api_like(url, response.headers, content_type, text_preview)

    # Optional test query param
    if not api_like:
        try:
            test_url = url + "?test=1"
            test_resp = requests.get(test_url, timeout=TIMEOUT)
            if "application/json" in test_resp.headers.get("Content-Type", ""):
                api_like = True
        except:
            pass

    return {"url": url, "status": response.status_code, "content_type": content_type,
            "api_like": api_like, "working": 200 <= response.status_code < 400}

def get_parent_domain(url):
    parsed = urlparse(url)
    if parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return None

def save_batch(batch_results, batch_number):
    output_file = f"{OUTPUT_PREFIX}_{batch_number}.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Parent Domain", "Status", "Content-Type", "API-like", "Assumed Status"])
        for r in batch_results:
            writer.writerow(r)
    print(f"💾 Saved batch {batch_number} -> {output_file}")

# --- Main processing ---
def main():
    df = pd.read_csv(INPUT_CSV)
    if URL_COLUMN not in df.columns:
        raise ValueError(f"Column '{URL_COLUMN}' not found in {INPUT_CSV}")

    urls = df[URL_COLUMN].dropna().unique().tolist()
    print(f"🔍 Loaded {len(urls)} URLs")

    # Group URLs by parent domain
    parent_to_children = defaultdict(list)
    for url in urls:
        parent = get_parent_domain(url)
        if parent:
            parent_to_children[parent].append(url)

    batch_results = []
    batch_number = 1

    for i, (parent, children) in enumerate(parent_to_children.items(), 1):
        print(f"[{i}/{len(parent_to_children)}] Checking dummy child for parent: {parent}")

        # Pick one dummy child to determine API-callable status
        dummy_child = children[0]
        child_result = check_url(dummy_child)

        # Assign the dummy child result to all children
        for url in children:
            batch_results.append([
                url,
                parent,
                child_result["status"],
                child_result["content_type"],
                child_result["api_like"],
                # ✅ Assumed Working is now based on API-likeness
                "Assumed Working" if child_result["working"] and child_result["api_like"] else "Checked & Failed"
            ])

        # Save in batches
        if len(batch_results) >= BATCH_SIZE:
            save_batch(batch_results, batch_number)
            batch_results = []
            batch_number += 1

        time.sleep(SLEEP)

    if batch_results:
        save_batch(batch_results, batch_number)

    print("\n✅ Done! All batches saved.")

if __name__ == "__main__":
    main()
