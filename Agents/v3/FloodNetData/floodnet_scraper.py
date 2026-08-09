#!/usr/bin/env python3
"""
FloodNet Data Scraper
=====================

Fetches street flooding event metadata from the NYC FloodNet sensor network
via the NYC Open Data SODA API (dataset aq7i-eu5q) and outputs a JSON file
in the format expected by KGNeptune/json_to_csvs.py.

Source: NYC Department of Environmental Protection
Dataset: https://data.cityofnewyork.us/resource/aq7i-eu5q.json

Output: floodnet_json/floodnet_data.json  (+ upload to S3)
"""

import os
import json
import time
import logging
import requests
import boto3
from typing import Dict, List, Any, Optional
from datetime import datetime

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
SODA_API_URL = "https://data.cityofnewyork.us/resource/aq7i-eu5q.json"
DATASET_PAGE  = "https://data.cityofnewyork.us/d/aq7i-eu5q"
PAGE_SIZE     = 1000
HEADERS       = {"User-Agent": "FloodNet-KG-Extractor/1.0"}

S3_BUCKET     = "autoclimds-simulation-kg"
S3_KEY        = "FloodNetData/floodnet_data.json"
LOCAL_DIR     = "floodnet_json"
LOCAL_FILE    = os.path.join(LOCAL_DIR, "floodnet_data.json")


##############################
#  FETCH
##############################
def fetch_floodnet_events(max_records: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Page through the SODA API and return all flood event records.
    Each record represents one sensor-detected flood event.
    """
    all_records: List[Dict[str, Any]] = []
    offset = 0

    while True:
        params: Dict[str, Any] = {
            "$limit":  PAGE_SIZE,
            "$offset": offset,
            "$order":  "flood_start_time DESC",
        }

        try:
            response = requests.get(SODA_API_URL, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
            batch = response.json()
        except Exception as e:
            logger.error("SODA API request failed at offset %d: %s", offset, e)
            break

        if not batch:
            break

        all_records.extend(batch)
        logger.info("Fetched %d records (total so far: %d)", len(batch), len(all_records))

        if len(batch) < PAGE_SIZE:
            break
        if max_records and len(all_records) >= max_records:
            all_records = all_records[:max_records]
            break

        offset += PAGE_SIZE
        time.sleep(0.2)

    logger.info("Total FloodNet records fetched: %d", len(all_records))
    return all_records


##############################
#  TRANSFORM
##############################
def _build_bbox(record: Dict[str, Any]) -> str:
    """Return a rough NYC bounding box; individual sensor lat/lon not in this dataset."""
    return "40.4774 -74.2591 40.9176 -73.7004"


def _science_keywords() -> List[Dict[str, str]]:
    return [
        {
            "category":        "EARTH SCIENCE",
            "topic":           "TERRESTRIAL HYDROSPHERE",
            "term":            "SURFACE WATER",
            "variable_level_1": "FLOODS",
        },
        {
            "category":        "EARTH SCIENCE",
            "topic":           "ATMOSPHERE",
            "term":            "PRECIPITATION",
            "variable_level_1": "RAIN",
        },
    ]


def transform_to_kg_format(raw_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert raw SODA records to the class structure expected by json_to_csvs.py.
    One Dataset entry is created per flood event record.
    """
    classes_data: Dict[str, Any] = {
        "Dataset":           [],
        "DataCategory":      [],
        "DataFormat":        [],
        "CoordinateSystem":  [],
        "Location":          [],
        "Station":           [],
        "Organization":      [],
        "Platform":          [],
        "Consortium":        [],
        "TemporalExtent":    [],
        "Variable":          [],
        "CESMVariable":      [],
        "Component":         [],
        "Contact":           [],
        "Project":           [],
        "RelatedUrl":        [],
        "SpatialResolution": [],
        "TemporalResolution": [],
        "Granule":           [],
        "Instrument":        [],
        "ScienceKeyword":    [],
        "ProcessingLevel":   [],
        "Relationship":      [],
    }

    seen_organizations: set = set()
    seen_variables: set     = set()
    seen_locations: set     = set()
    seen_keywords: set      = set()

    # --- Organization (one shared entry) ---
    org_name = "NYC_DEP"
    classes_data["Organization"].append({
        "short_name":  org_name,
        "long_name":   "New York City Department of Environmental Protection",
        "url":         "https://www.nyc.gov/dep",
        "data_center": org_name,
    })

    # --- Platform ---
    classes_data["Platform"].append({
        "short_name":  "FLOODNET_SENSOR",
        "long_name":   "FloodNet IoT Ultrasonic Flood Sensor",
        "type":        "In Situ Land-based Platforms",
    })

    # --- Variable entries ---
    variable_defs = [
        ("flood_depth_mm",      "Flood Water Depth",             "mm",   "Surface water depth measured by ultrasonic sensor"),
        ("flood_duration_min",  "Flood Event Duration",          "min",  "Total duration of flood event above baseline"),
        ("time_to_peak_min",    "Time to Peak Flood Depth",      "min",  "Duration from flood start to maximum depth"),
        ("drain_time_min",      "Flood Drain Time",              "min",  "Duration from peak depth to end of flood event"),
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

    # --- ScienceKeyword entries ---
    for kw in _science_keywords():
        kw_key = f"{kw['category']}_{kw['topic']}_{kw['term']}"
        if kw_key not in seen_keywords:
            classes_data["ScienceKeyword"].append(kw)
            seen_keywords.add(kw_key)

    # --- Dataset entries (one per event record) ---
    for i, record in enumerate(raw_records):
        sensor_id   = record.get("sensor_id",   f"sensor_{i}")
        sensor_name = record.get("sensor_name", sensor_id)
        start_dt    = record.get("flood_start_time", "")
        end_dt      = record.get("flood_end_time",   "")
        max_depth   = record.get("max_depth_inches",  "")

        dataset_id  = f"FLOODNET_{sensor_id}_{i}"
        title       = (
            f"FloodNet Flood Event — Sensor {sensor_name}"
            + (f" ({start_dt[:10]})" if start_dt else "")
        )
        description = (
            f"Street flooding event detected by FloodNet sensor {sensor_name}. "
            f"Max depth: {max_depth} mm. "
            f"Duration: {record.get('total_duration_in_minutes', 'N/A')} min. "
            f"Source: NYC DEP FloodNet network."
        )

        dataset_entry: Dict[str, Any] = {
            "short_name":           dataset_id,
            "title":                title,
            "summary":              description,
            "description":          description,
            "dataset_id":           dataset_id,
            "entry_id":             f"floodnet_{dataset_id}",
            "version_id":           "1.0",
            "processing_level_id":  "2",
            "online_access_flag":   True,
            "browse_flag":          False,
            "collection_data_type": "SCIENCE_QUALITY",
            "data_set_language":    "eng",
            "archive_center":       "NYC_OPENDATA",
            "data_center":          "NYC_DEP",
            "native_id":            dataset_id,
            "granule_count":        0,
            "day_night_flag":       "",
            "cloud_cover":          "",
            "frequency":            "event-based",
            "time_start":           start_dt,
            "time_end":             end_dt,
            "boxes":                [_build_bbox(record)],
            "polygons":             [],
            "points":               [],
            "organizations":        [{"short_name": org_name}],
            "platforms":            [{"short_name": "FLOODNET_SENSOR"}],
            "consortiums":          [],
            "science_keywords":     _science_keywords(),
            "links": [
                {
                    "href":        DATASET_PAGE,
                    "rel":         "http://esipfed.org/ns/fedsearch/1.1/metadata#",
                    "hreflang":    "en-US",
                    "description": "FloodNet NYC Open Data dataset page",
                },
                {
                    "href":        SODA_API_URL,
                    "rel":         "http://esipfed.org/ns/fedsearch/1.1/data#",
                    "hreflang":    "en-US",
                    "description": "SODA API endpoint",
                },
            ],
            # Raw sensor fields preserved in extra metadata
            "sensor_id":                     sensor_id,
            "sensor_name":                   sensor_name,
            "max_depth_inches":              max_depth,
            "total_duration_min":            record.get("duration_mins", ""),
            "onset_time_min":                record.get("onset_time_mins", ""),
            "drain_time_min":                record.get("drain_time_mins", ""),
            "duration_above_4in_min":        record.get("duration_above_4_inches_mins", ""),
            "duration_above_12in_min":       record.get("duration_above_12_inches_mins", ""),
            "duration_above_24in_min":       record.get("duration_above_24_inches_mins", ""),
        }
        classes_data["Dataset"].append(dataset_entry)

        # Location entry per sensor (deduplicated)
        if sensor_name not in seen_locations:
            classes_data["Location"].append({
                "name":          sensor_name,
                "type":          "Urban Flood Sensor Site",
                "city":          "New York City",
                "country":       "USA",
                "dataset_id":    dataset_id,
                "bounding_box":  _build_bbox(record),
            })
            seen_locations.add(sensor_name)

    logger.info(
        "Transformed %d events into %d Dataset entries",
        len(raw_records), len(classes_data["Dataset"]),
    )
    return classes_data


##############################
#  UPLOAD
##############################
def upload_to_s3(local_path: str, bucket: str, key: str) -> None:
    """Upload a local file to S3."""
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

    logger.info("Fetching FloodNet flood event records from NYC Open Data...")
    raw_records = fetch_floodnet_events()

    if not raw_records:
        logger.error("No records fetched. Exiting.")
        return

    logger.info("Transforming %d records to KG format...", len(raw_records))
    kg_data = transform_to_kg_format(raw_records)

    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(kg_data, f, indent=2, ensure_ascii=False)
    logger.info("Saved KG-format JSON to %s", LOCAL_FILE)

    logger.info("Uploading to S3...")
    upload_to_s3(LOCAL_FILE, S3_BUCKET, S3_KEY)

    total = len(kg_data["Dataset"])
    logger.info("FloodNet scraper complete. %d dataset entries written.", total)
    print(f"\n=== FloodNet Scraper Summary ===")
    for key, val in kg_data.items():
        if val:
            print(f"  {key}: {len(val)} items")


if __name__ == "__main__":
    main()
