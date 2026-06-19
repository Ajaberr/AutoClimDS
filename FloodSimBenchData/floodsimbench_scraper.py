#!/usr/bin/env python3
"""
FloodSimBench Data Scraper
==========================

Fetches dataset metadata for the FloodSimBench benchmark from the Hugging Face Hub API
and outputs a JSON file in the format expected by KGNeptune/json_to_csvs.py.

FloodSimBench contains 461 GB of flood inundation simulation data across 10 US cities,
including Digital Elevation Models (DEMs), water depth time series (72 frames x 5-min),
and 5-class flood severity maps for 4 rainfall return periods (10/25/50/100-year).

Source: https://huggingface.co/datasets/chrimerss/FloodSimBench

Output: floodsimbench_json/floodsimbench_data.json  (+ upload to S3)
"""

import os
import json
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
HF_API_DATASET  = "https://huggingface.co/api/datasets/chrimerss/FloodSimBench"
HF_DATASET_PAGE = "https://huggingface.co/datasets/chrimerss/FloodSimBench"
HEADERS         = {"User-Agent": "FloodSimBench-KG-Extractor/1.0"}

S3_BUCKET = "autoclimds-simulation-kg"
S3_KEY    = "FloodSimBenchData/floodsimbench_data.json"
LOCAL_DIR = "floodsimbench_json"
LOCAL_FILE = os.path.join(LOCAL_DIR, "floodsimbench_data.json")

# The 10 cities included in FloodSimBench (from dataset documentation)
FLOODSIMBENCH_CITIES = [
    {"city_id": "C01", "name": "Houston",      "state": "TX", "lat": 29.76,  "lon": -95.37},
    {"city_id": "C02", "name": "Miami",        "state": "FL", "lat": 25.77,  "lon": -80.19},
    {"city_id": "C03", "name": "New Orleans",  "state": "LA", "lat": 29.95,  "lon": -90.07},
    {"city_id": "C04", "name": "Jacksonville", "state": "FL", "lat": 30.33,  "lon": -81.66},
    {"city_id": "C05", "name": "Memphis",      "state": "TN", "lat": 35.15,  "lon": -90.05},
    {"city_id": "C06", "name": "Louisville",   "state": "KY", "lat": 38.25,  "lon": -85.76},
    {"city_id": "C07", "name": "Baton Rouge",  "state": "LA", "lat": 30.45,  "lon": -91.15},
    {"city_id": "C08", "name": "Nashville",    "state": "TN", "lat": 36.17,  "lon": -86.78},
    {"city_id": "C09", "name": "Birmingham",   "state": "AL", "lat": 33.52,  "lon": -86.80},
    {"city_id": "C10", "name": "Charlotte",    "state": "NC", "lat": 35.23,  "lon": -80.84},
]

RAINFALL_RETURN_PERIODS = [10, 25, 50, 100]  # years


##############################
#  FETCH
##############################
def fetch_hf_metadata() -> Optional[Dict[str, Any]]:
    """Fetch dataset card metadata from Hugging Face Hub API."""
    try:
        response = requests.get(HF_API_DATASET, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning("Hugging Face API request failed: %s. Using static metadata.", e)
        return None


##############################
#  TRANSFORM
##############################
def _science_keywords() -> List[Dict[str, str]]:
    return [
        {
            "category":         "EARTH SCIENCE",
            "topic":            "TERRESTRIAL HYDROSPHERE",
            "term":             "SURFACE WATER",
            "variable_level_1": "FLOODS",
            "variable_level_2": "FLOOD INUNDATION",
        },
        {
            "category":         "EARTH SCIENCE",
            "topic":            "ATMOSPHERE",
            "term":             "PRECIPITATION",
            "variable_level_1": "RAIN",
            "variable_level_2": "RAINFALL RETURN PERIOD",
        },
        {
            "category":         "EARTH SCIENCE SERVICES",
            "topic":            "MODELS",
            "term":             "FLOOD SIMULATION",
            "variable_level_1": "HYDRODYNAMIC MODELING",
        },
    ]


def _build_city_bbox(city: Dict[str, Any]) -> str:
    """Return a ~0.5-degree bounding box around a city centroid."""
    lat, lon = city["lat"], city["lon"]
    return f"{lat - 0.25:.4f} {lon - 0.25:.4f} {lat + 0.25:.4f} {lon + 0.25:.4f}"


def transform_to_kg_format(hf_meta: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build the KG-format JSON for FloodSimBench.
    Creates:
      - One top-level Dataset entry for the full benchmark collection.
      - One Dataset entry per city x rainfall return period combination (40 entries).
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

    # Pull description from HF metadata if available
    hf_description = ""
    if hf_meta:
        hf_description = (
            hf_meta.get("cardData", {}).get("description", "")
            or hf_meta.get("description", "")
        )

    collection_description = (
        hf_description
        or (
            "FloodSimBench is a large-scale urban flood simulation benchmark dataset "
            "covering 10 US cities prone to flooding. It provides paired inputs and outputs "
            "for training and evaluating deep learning flood prediction models. "
            "Data includes 1-m resolution Digital Elevation Models (DEMs), "
            "72-frame water depth time series at 5-minute intervals over 6 hours, "
            "and 5-class flood severity maps for four rainfall return periods "
            "(10, 25, 50, and 100-year events). Total size: ~461 GB."
        )
    )

    # --- Organization ---
    classes_data["Organization"].append({
        "short_name": "HUGGINGFACE_CHRIMERSS",
        "long_name":  "chrimerss — Hugging Face dataset contributor",
        "url":        "https://huggingface.co/chrimerss",
        "data_center": "HUGGINGFACE",
    })

    # --- DataFormat ---
    classes_data["DataFormat"].append({
        "format":    "GeoTIFF",
        "mime_type": "image/tiff",
        "description": "Geospatially referenced raster format for DEM and water depth grids",
    })

    # --- SpatialResolution ---
    classes_data["SpatialResolution"].append({
        "value":       "1",
        "unit":        "m",
        "description": "1-meter horizontal grid resolution",
    })

    # --- TemporalResolution ---
    classes_data["TemporalResolution"].append({
        "value":       "5",
        "unit":        "min",
        "description": "5-minute temporal resolution (72 frames over 6 hours)",
    })

    # --- Variables ---
    variable_defs = [
        ("dem",              "Digital Elevation Model",       "m",   "Terrain elevation above datum"),
        ("water_depth",      "Flood Water Depth",             "m",   "Simulated water depth at each grid cell"),
        ("rainfall_intensity","Rainfall Intensity",           "mm",  "Design storm total rainfall depth"),
        ("flood_severity",   "Flood Severity Class",          "class","5-class flood severity classification (0-4)"),
    ]
    for vname, vlong, vunit, vdesc in variable_defs:
        classes_data["Variable"].append({
            "name":          vname,
            "long_name":     vlong,
            "units":         vunit,
            "description":   vdesc,
            "standard_name": vname,
        })

    # --- ScienceKeyword entries ---
    for kw in _science_keywords():
        classes_data["ScienceKeyword"].append(kw)

    # --- Top-level collection Dataset entry ---
    collection_entry: Dict[str, Any] = {
        "short_name":           "FloodSimBench",
        "title":                "FloodSimBench: Urban Flood Simulation Benchmark Dataset",
        "summary":              collection_description,
        "description":          collection_description,
        "dataset_id":           "FLOODSIMBENCH_COLLECTION",
        "entry_id":             "floodsimbench_collection",
        "version_id":           "1.0",
        "processing_level_id":  "4",
        "online_access_flag":   True,
        "browse_flag":          False,
        "collection_data_type": "SCIENCE_QUALITY",
        "data_set_language":    "eng",
        "archive_center":       "HUGGINGFACE",
        "data_center":          "HUGGINGFACE_CHRIMERSS",
        "native_id":            "chrimerss/FloodSimBench",
        "granule_count":        len(FLOODSIMBENCH_CITIES) * len(RAINFALL_RETURN_PERIODS),
        "day_night_flag":       "",
        "cloud_cover":          "",
        "frequency":            "static",
        "time_start":           "",
        "time_end":             "",
        "boxes":                ["25.0 -98.0 39.0 -80.0"],
        "polygons":             [],
        "points":               [],
        "organizations":        [{"short_name": "HUGGINGFACE_CHRIMERSS"}],
        "platforms":            [{"short_name": "FLOOD_SIMULATION_MODEL"}],
        "consortiums":          [],
        "science_keywords":     _science_keywords(),
        "links": [
            {
                "href":        HF_DATASET_PAGE,
                "rel":         "http://esipfed.org/ns/fedsearch/1.1/metadata#",
                "hreflang":    "en-US",
                "description": "FloodSimBench Hugging Face dataset page",
            },
            {
                "href":        "https://huggingface.co/datasets/chrimerss/FloodSimBench/resolve/main/README.md",
                "rel":         "http://esipfed.org/ns/fedsearch/1.1/documentation#",
                "hreflang":    "en-US",
                "description": "Dataset documentation (README)",
            },
        ],
        "total_size_gb":        461,
        "num_cities":           len(FLOODSIMBENCH_CITIES),
        "rainfall_return_periods_years": RAINFALL_RETURN_PERIODS,
        "temporal_frames":      72,
        "temporal_interval_min": 5,
        "spatial_resolution_m": 1,
        "flood_severity_classes": 5,
    }
    classes_data["Dataset"].append(collection_entry)

    # --- Per-city x per-return-period Dataset entries ---
    for city in FLOODSIMBENCH_CITIES:
        # Location entry
        classes_data["Location"].append({
            "name":         city["name"],
            "type":         "City",
            "state":        city["state"],
            "country":      "USA",
            "bounding_box": _build_city_bbox(city),
        })

        for rp in RAINFALL_RETURN_PERIODS:
            entry_id   = f"FLOODSIMBENCH_{city['city_id']}_{rp}yr"
            entry_title = (
                f"FloodSimBench — {city['name']}, {city['state']} "
                f"({rp}-year Return Period)"
            )
            entry_desc = (
                f"Flood inundation simulation data for {city['name']}, {city['state']} "
                f"under a {rp}-year design storm. "
                f"Includes 1-m DEM, 72 water depth frames at 5-min intervals, "
                f"and 5-class flood severity map. "
                f"City ID: {city['city_id']}. "
                f"Filename pattern: {city['city_id']}_{rp}mm_WaterDepth_{{T}}.tif"
            )

            sub_entry: Dict[str, Any] = {
                "short_name":           entry_id,
                "title":                entry_title,
                "summary":              entry_desc,
                "description":          entry_desc,
                "dataset_id":           entry_id,
                "entry_id":             f"floodsimbench_{entry_id.lower()}",
                "version_id":           "1.0",
                "processing_level_id":  "4",
                "online_access_flag":   True,
                "browse_flag":          False,
                "collection_data_type": "SCIENCE_QUALITY",
                "data_set_language":    "eng",
                "archive_center":       "HUGGINGFACE",
                "data_center":          "HUGGINGFACE_CHRIMERSS",
                "native_id":            f"chrimerss/FloodSimBench/{city['city_id']}_{rp}mm",
                "granule_count":        72,
                "day_night_flag":       "",
                "cloud_cover":          "",
                "frequency":            "static",
                "time_start":           "",
                "time_end":             "",
                "boxes":                [_build_city_bbox(city)],
                "polygons":             [],
                "points":               [f"{city['lat']} {city['lon']}"],
                "organizations":        [{"short_name": "HUGGINGFACE_CHRIMERSS"}],
                "platforms":            [{"short_name": "FLOOD_SIMULATION_MODEL"}],
                "consortiums":          [],
                "science_keywords":     _science_keywords(),
                "links": [
                    {
                        "href":        HF_DATASET_PAGE,
                        "rel":         "http://esipfed.org/ns/fedsearch/1.1/data#",
                        "hreflang":    "en-US",
                        "description": "Hugging Face dataset repository",
                    }
                ],
                "city":                  city["name"],
                "state":                 city["state"],
                "city_id":               city["city_id"],
                "rainfall_return_period_years": rp,
                "file_pattern":          f"{city['city_id']}_{rp}mm_WaterDepth_{{T}}.tif",
                "spatial_resolution_m":  1,
                "temporal_frames":       72,
                "temporal_interval_min": 5,
            }
            classes_data["Dataset"].append(sub_entry)

    logger.info("Built %d Dataset entries for FloodSimBench", len(classes_data["Dataset"]))
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

    logger.info("Fetching FloodSimBench metadata from Hugging Face Hub API...")
    hf_meta = fetch_hf_metadata()

    logger.info("Transforming to KG format...")
    kg_data = transform_to_kg_format(hf_meta)

    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(kg_data, f, indent=2, ensure_ascii=False)
    logger.info("Saved KG-format JSON to %s", LOCAL_FILE)

    logger.info("Uploading to S3...")
    upload_to_s3(LOCAL_FILE, S3_BUCKET, S3_KEY)

    logger.info("FloodSimBench scraper complete.")
    print("\n=== FloodSimBench Scraper Summary ===")
    for key, val in kg_data.items():
        if val:
            print(f"  {key}: {len(val)} items")


if __name__ == "__main__":
    main()
