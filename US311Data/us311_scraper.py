#!/usr/bin/env python3
"""
US City 311 Data Scraper
========================

Fetches 311 Service Request metadata from multiple US cities via the
Socrata Open Data API and outputs a JSON file in the format expected
by KGNeptune/json_to_csvs.py.

One Dataset entry is created per (city, complaint_type) pair, capturing
the top complaint categories per city. This gives the knowledge graph
structured awareness of what 311 data exists and where to find it.

Sources (Socrata SODA API):
- New York City:    data.cityofnewyork.us  dataset erm2-nwe9
- Chicago:          data.cityofchicago.org dataset v6vf-nfxy
- San Francisco:    data.sfgov.org         dataset vw6y-z8j6
- Austin:           data.austintexas.gov   dataset xwdj-i9he

Output: us311_json/us311_data.json  (+ upload to S3)
"""

import os
import json
import time
import logging
import requests
import boto3
from typing import Dict, List, Any, Optional

try:
    from dotenv import load_dotenv
    _here = os.path.dirname(os.path.abspath(__file__))
    _env_path = os.path.join(_here, "..", "Agents", ".env")
    load_dotenv(_env_path)
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

##############################
#  CONFIG
##############################
CITY_ENDPOINTS = {
    "nyc": {
        "name":         "New York City",
        "domain":       "data.cityofnewyork.us",
        "dataset_id":   "erm2-nwe9",
        "type_field":   "complaint_type",
        "date_field":   "created_date",
        "bbox":         "40.4774 -74.2591 40.9176 -73.7004",
        "doc_url":      "https://data.cityofnewyork.us/d/erm2-nwe9",
    },
    "chicago": {
        "name":         "Chicago",
        "domain":       "data.cityofchicago.org",
        "dataset_id":   "v6vf-nfxy",
        "type_field":   "sr_type",
        "date_field":   "created_date",
        "bbox":         "41.6445 -87.9401 42.0230 -87.5237",
        "doc_url":      "https://data.cityofchicago.org/d/v6vf-nfxy",
    },
    "san_francisco": {
        "name":         "San Francisco",
        "domain":       "data.sfgov.org",
        "dataset_id":   "vw6y-z8j6",
        "type_field":   "service_name",
        "date_field":   "requested_datetime",
        "bbox":         "37.6398 -122.5157 37.9298 -122.3566",
        "doc_url":      "https://data.sfgov.org/d/vw6y-z8j6",
    },
    "austin": {
        "name":         "Austin",
        "domain":       "data.austintexas.gov",
        "dataset_id":   "xwdj-i9he",
        "type_field":   "sr_type_desc",
        "date_field":   "sr_created_date",
        "bbox":         "30.0986 -97.9383 30.5170 -97.5685",
        "doc_url":      "https://data.austintexas.gov/d/xwdj-i9he",
    },
}

TOP_N_CATEGORIES = 30   # complaint types per city to index in KG
S3_BUCKET        = "autoclimds-simulation-kg"
S3_KEY           = "US311Data/us311_data.json"
LOCAL_DIR        = "us311_json"
LOCAL_FILE       = os.path.join(LOCAL_DIR, "us311_data.json")
HEADERS          = {"User-Agent": "US311-KG-Extractor/1.0"}


##############################
#  FETCH
##############################
def fetch_top_categories(city_key: str, meta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetch the top complaint categories for a city.
    Strategy: try a 90-day GROUP BY first (fast); fall back to sampling
    500 recent records and extracting unique types if the aggregate times out.
    Returns a list of {type_field: name, 'total_count': n} dicts.
    """
    domain     = meta["domain"]
    dataset_id = meta["dataset_id"]
    type_field = meta["type_field"]
    date_field = meta["date_field"]
    url        = f"https://{domain}/resource/{dataset_id}.json"

    # --- Strategy 1: GROUP BY on last 90 days (fast for most cities) ---
    params_agg = {
        "$select": f"{type_field}, count(*) as total_count",
        "$where":  f"{date_field} >= '2025-01-01T00:00:00'",
        "$group":  type_field,
        "$order":  "total_count DESC",
        "$limit":  TOP_N_CATEGORIES,
    }
    try:
        resp = requests.get(url, headers=HEADERS, params=params_agg, timeout=25)
        resp.raise_for_status()
        rows = resp.json()
        if rows:
            logger.info("  %s: fetched %d categories (aggregate)", meta["name"], len(rows))
            return rows
    except Exception:
        pass  # fall through to sampling

    # --- Strategy 2: Sample 500 recent records, extract unique types ---
    logger.info("  %s: aggregate timed out, using sample...", meta["name"])
    params_sample = {
        "$select": type_field,
        "$order":  f"{date_field} DESC",
        "$limit":  500,
    }
    try:
        resp = requests.get(url, headers=HEADERS, params=params_sample, timeout=20)
        resp.raise_for_status()
        records = resp.json()
        counts: Dict[str, int] = {}
        for r in records:
            t = r.get(type_field, "")
            if t:
                counts[t] = counts.get(t, 0) + 1
        rows = [
            {type_field: k, "total_count": v}
            for k, v in sorted(counts.items(), key=lambda x: -x[1])
        ][:TOP_N_CATEGORIES]
        logger.info("  %s: sampled %d unique categories from %d records", meta["name"], len(rows), len(records))
        return rows
    except Exception as e:
        logger.error("  %s: both strategies failed: %s", meta["name"], e)
        return []


def fetch_date_range(city_key: str, meta: Dict[str, Any]) -> Dict[str, str]:
    """Return the earliest and latest dates in the dataset."""
    domain     = meta["domain"]
    dataset_id = meta["dataset_id"]
    date_field = meta["date_field"]
    url        = f"https://{domain}/resource/{dataset_id}.json"

    dates = {}
    for order, label in [("ASC", "time_start"), ("DESC", "time_end")]:
        try:
            resp = requests.get(url, headers=HEADERS, params={
                "$select": date_field,
                "$order":  f"{date_field} {order}",
                "$limit":  1,
            }, timeout=20)
            resp.raise_for_status()
            rows = resp.json()
            if rows:
                dates[label] = rows[0].get(date_field, "")
        except Exception:
            dates[label] = ""
        time.sleep(0.2)

    return dates


##############################
#  TRANSFORM
##############################
def _science_keywords() -> List[Dict[str, str]]:
    return [
        {
            "category":         "EARTH SCIENCE SERVICES",
            "topic":            "ENVIRONMENTAL ADVISORIES",
            "term":             "URBAN SERVICES",
            "variable_level_1": "311 SERVICE REQUESTS",
        },
        {
            "category":         "EARTH SCIENCE",
            "topic":            "HUMAN DIMENSIONS",
            "term":             "INFRASTRUCTURE",
            "variable_level_1": "URBAN SERVICES",
        },
    ]


def transform_to_kg_format(
    city_categories: Dict[str, List[Dict[str, Any]]],
    city_dates: Dict[str, Dict[str, str]],
) -> Dict[str, Any]:
    """
    Build the KG JSON structure.
    One Dataset node per (city, complaint_type) pair.
    """
    classes_data: Dict[str, Any] = {
        "Dataset":            [],
        "DataCategory":       [],
        "DataFormat":         [],
        "CoordinateSystem":   [],
        "Location":           [],
        "Station":            [],
        "Organization":       [],
        "Platform":           [],
        "Consortium":         [],
        "TemporalExtent":     [],
        "Variable":           [],
        "CESMVariable":       [],
        "Component":          [],
        "Contact":            [],
        "Project":            [],
        "RelatedUrl":         [],
        "SpatialResolution":  [],
        "TemporalResolution": [],
        "Granule":            [],
        "Instrument":         [],
        "ScienceKeyword":     [],
        "ProcessingLevel":    [],
        "Relationship":       [],
    }

    seen_orgs      = set()
    seen_variables = set()
    seen_locations = set()

    # Shared science keywords
    for kw in _science_keywords():
        classes_data["ScienceKeyword"].append(kw)

    # Shared variable definitions
    variable_defs = [
        ("complaint_type",       "Complaint / Service Request Type",  "",      "Category of the 311 service request"),
        ("status",               "Request Status",                    "",      "Current status of the 311 request (Open, Closed, etc.)"),
        ("created_date",         "Request Creation Date",             "UTC",   "Timestamp when the 311 request was submitted"),
        ("closed_date",          "Request Closed Date",               "UTC",   "Timestamp when the 311 request was resolved"),
        ("resolution_days",      "Days to Resolution",                "days",  "Number of days from creation to closure"),
    ]
    for vname, vlong, vunit, vdesc in variable_defs:
        if vname not in seen_variables:
            classes_data["Variable"].append({
                "name":          vname,
                "long_name":     vlong,
                "units":         vunit,
                "description":   vdesc,
                "standard_name": vname,
            })
            seen_variables.add(vname)

    # One Dataset entry per (city, complaint_type)
    for city_key, meta in CITY_ENDPOINTS.items():
        city_name  = meta["name"]
        domain     = meta["domain"]
        dataset_id = meta["dataset_id"]
        bbox       = meta["bbox"]
        doc_url    = meta["doc_url"]
        api_url    = f"https://{domain}/resource/{dataset_id}.json"
        type_field = meta["type_field"]

        dates      = city_dates.get(city_key, {})
        time_start = dates.get("time_start", "")
        time_end   = dates.get("time_end",   "")

        # Organization node (one per city)
        org_key = f"CITY_311_{city_key.upper()}"
        if org_key not in seen_orgs:
            classes_data["Organization"].append({
                "short_name":  org_key,
                "long_name":   f"{city_name} Open Data – 311 Service Requests",
                "url":         f"https://{domain}",
                "data_center": org_key,
            })
            seen_orgs.add(org_key)

        # Platform node (one per city)
        classes_data["Platform"].append({
            "short_name": f"SOCRATA_{city_key.upper()}",
            "long_name":  f"Socrata Open Data Platform – {city_name}",
            "type":       "Digital Collection Platform",
        })

        # Location node (one per city)
        if city_name not in seen_locations:
            classes_data["Location"].append({
                "name":         city_name,
                "type":         "Urban Municipality",
                "city":         city_name,
                "country":      "USA",
                "bounding_box": bbox,
            })
            seen_locations.add(city_name)

        categories = city_categories.get(city_key, [])
        if not categories:
            # Fallback: one Dataset entry for the whole city dataset
            categories = [{"_fallback": True, type_field: "All Requests", "total_count": "N/A"}]

        for row in categories:
            complaint_type = row.get(type_field, "Unknown")
            record_count   = row.get("total_count", 0)

            safe_type  = complaint_type.replace(" ", "_").replace("/", "-").replace("&", "and")[:50]
            dataset_id_node = f"US311_{city_key.upper()}_{safe_type}"

            title = f"311 Service Requests – {city_name} – {complaint_type}"
            description = (
                f"311 non-emergency service request records for '{complaint_type}' "
                f"in {city_name}, sourced from the Socrata Open Data portal. "
                f"Total records: {record_count}. "
                f"Data accessible via Socrata SODA API at {api_url}."
            )

            dataset_entry: Dict[str, Any] = {
                "short_name":           dataset_id_node,
                "title":                title,
                "summary":              description,
                "description":          description,
                "dataset_id":           dataset_id_node,
                "entry_id":             f"us311_{dataset_id_node}",
                "version_id":           "1.0",
                "processing_level_id":  "2",
                "online_access_flag":   True,
                "browse_flag":          False,
                "collection_data_type": "SCIENCE_QUALITY",
                "data_set_language":    "eng",
                "archive_center":       "SOCRATA_OPENDATA",
                "data_center":          org_key,
                "native_id":            dataset_id_node,
                "granule_count":        int(record_count) if str(record_count).isdigit() else 0,
                "day_night_flag":       "",
                "cloud_cover":          "",
                "frequency":            "daily",
                "time_start":           time_start,
                "time_end":             time_end,
                "boxes":                [bbox],
                "polygons":             [],
                "points":               [],
                "organizations":        [{"short_name": org_key}],
                "platforms":            [{"short_name": f"SOCRATA_{city_key.upper()}"}],
                "consortiums":          [],
                "science_keywords":     _science_keywords(),
                "links": [
                    {
                        "href":        doc_url,
                        "rel":         "http://esipfed.org/ns/fedsearch/1.1/metadata#",
                        "hreflang":    "en-US",
                        "description": f"{city_name} 311 Open Data dataset page",
                    },
                    {
                        "href":        api_url,
                        "rel":         "http://esipfed.org/ns/fedsearch/1.1/data#",
                        "hreflang":    "en-US",
                        "description": "Socrata SODA API endpoint",
                    },
                ],
                # 311-specific fields
                "city":            city_name,
                "city_key":        city_key,
                "complaint_type":  complaint_type,
                "type_field":      type_field,
                "socrata_domain":  domain,
                "socrata_dataset": meta["dataset_id"],
                "record_count":    record_count,
            }
            classes_data["Dataset"].append(dataset_entry)

    logger.info("Transformed %d Dataset entries total", len(classes_data["Dataset"]))
    return classes_data


##############################
#  UPLOAD
##############################
def upload_to_s3(local_path: str, bucket: str, key: str) -> None:
    try:
        s3 = boto3.client("s3")
        s3.upload_file(local_path, bucket, key)
        logger.info("Uploaded %s to s3://%s/%s", local_path, bucket, key)
    except Exception as e:
        logger.error("S3 upload failed: %s", e)
        raise


##############################
#  MAIN
##############################
def main() -> None:
    os.makedirs(LOCAL_DIR, exist_ok=True)

    city_categories: Dict[str, List[Dict[str, Any]]] = {}
    city_dates:      Dict[str, Dict[str, str]]        = {}

    for city_key, meta in CITY_ENDPOINTS.items():
        logger.info("Fetching categories for %s...", meta["name"])
        city_categories[city_key] = fetch_top_categories(city_key, meta)
        logger.info("Fetching date range for %s...", meta["name"])
        city_dates[city_key]      = fetch_date_range(city_key, meta)
        time.sleep(0.5)

    kg_data = transform_to_kg_format(city_categories, city_dates)

    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(kg_data, f, indent=2, ensure_ascii=False)
    logger.info("Saved KG-format JSON to %s", LOCAL_FILE)

    logger.info("Uploading to S3...")
    upload_to_s3(LOCAL_FILE, S3_BUCKET, S3_KEY)

    total = len(kg_data["Dataset"])
    logger.info("311 scraper complete. %d dataset entries written.", total)
    print(f"\n=== US 311 Scraper Summary ===")
    for key, val in kg_data.items():
        if val:
            print(f"  {key}: {len(val)} items")


if __name__ == "__main__":
    main()
