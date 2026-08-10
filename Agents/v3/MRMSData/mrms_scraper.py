#!/usr/bin/env python3
"""
MRMS Data Scraper
=================

Fetches the MRMS (Multi-Radar/Multi-Sensor System) operational product catalog
from the NOAA/NSSL tables page and outputs a JSON file in the format expected
by KGNeptune/json_to_csvs.py.

MRMS is NOAA's high-resolution (~1 km / 2-min) quantitative precipitation
estimation and severe weather product suite covering the contiguous United States.

Sources:
  Product catalog : https://nssl.noaa.gov/projects/mrms/operational/tables.php
  GitHub support  : https://github.com/NOAA-National-Severe-Storms-Laboratory/mrms-support

Output: mrms_json/mrms_data.json  (+ upload to S3)
"""

import os
import re
import json
import time
import logging
import requests
import boto3
from typing import Dict, List, Any, Optional
from html.parser import HTMLParser

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
MRMS_TABLES_URL  = "https://nssl.noaa.gov/projects/mrms/operational/tables.php"
MRMS_PROJECT_URL = "https://nssl.noaa.gov/projects/mrms/"
MRMS_GITHUB_URL  = "https://github.com/NOAA-National-Severe-Storms-Laboratory/mrms-support"
HEADERS = {"User-Agent": "MRMS-KG-Extractor/1.0"}

S3_BUCKET  = "autoclimds-simulation-kg"
S3_KEY     = "MRMSData/mrms_data.json"
LOCAL_DIR  = "mrms_json"
LOCAL_FILE = os.path.join(LOCAL_DIR, "mrms_data.json")

# MRMS continental US bounding box
MRMS_CONUS_BBOX = "20.0 -130.0 55.0 -60.0"


##############################
#  STATIC PRODUCT CATALOG
# Used as fallback if the tables.php page cannot be scraped,
# and to ensure correct category / update interval metadata.
##############################
MRMS_STATIC_PRODUCTS: List[Dict[str, Any]] = [
    # --- Precipitation (QPE) ---
    {
        "product_name":     "MultiSensor_QPE_01H_Pass1",
        "long_name":        "Multi-Sensor QPE 1-Hour Accumulation (Pass 1)",
        "category":         "Precipitation",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "mm",
        "description":      "Hourly quantitative precipitation estimate combining radar, rain gauges, and satellite data.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "MultiSensor_QPE_01H_Pass2",
        "long_name":        "Multi-Sensor QPE 1-Hour Accumulation (Pass 2 — gauge-corrected)",
        "category":         "Precipitation",
        "update_interval_min": 60,
        "levels":           ["L2"],
        "units":            "mm",
        "description":      "Gauge-corrected hourly QPE. Higher latency, higher accuracy than Pass 1.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "MultiSensor_QPE_24H_Pass2",
        "long_name":        "Multi-Sensor QPE 24-Hour Accumulation (Pass 2)",
        "category":         "Precipitation",
        "update_interval_min": 60,
        "levels":           ["L2"],
        "units":            "mm",
        "description":      "Daily gauge-corrected quantitative precipitation estimate.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "RadarOnly_QPE_01H",
        "long_name":        "Radar-Only QPE 1-Hour Accumulation",
        "category":         "Precipitation",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "mm",
        "description":      "Hourly precipitation accumulation derived from radar only (no gauge correction).",
        "format":           "GRIB2",
    },
    # --- Reflectivity ---
    {
        "product_name":     "MergedReflectivityQCComposite",
        "long_name":        "Merged QC Reflectivity Composite",
        "category":         "Reflectivity",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "dBZ",
        "description":      "Quality-controlled merged reflectivity from all WSR-88D radars at lowest elevation.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "MergedReflectivityCompositeH",
        "long_name":        "Merged Reflectivity at Hybrid Scan",
        "category":         "Reflectivity",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "dBZ",
        "description":      "Composite reflectivity using the hybrid scan approach to minimize beam blockage.",
        "format":           "GRIB2",
    },
    # --- Rotation / Severe Weather ---
    {
        "product_name":     "RotationTrack30min",
        "long_name":        "Maximum Rotation Track (30-minute)",
        "category":         "Severe Weather",
        "update_interval_min": 2,
        "levels":           ["L3"],
        "units":            "s-1",
        "description":      "Maximum azimuthal shear over a 30-minute window, used to detect tornado/mesocyclone signatures.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "MergedAzShear_0-2kmAGL",
        "long_name":        "Merged Azimuthal Shear 0-2 km AGL",
        "category":         "Severe Weather",
        "update_interval_min": 2,
        "levels":           ["L3"],
        "units":            "s-1",
        "description":      "Vertical wind shear in the 0-2 km layer above ground, indicating low-level rotation.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "MergedAzShear_3-6kmAGL",
        "long_name":        "Merged Azimuthal Shear 3-6 km AGL",
        "category":         "Severe Weather",
        "update_interval_min": 2,
        "levels":           ["L3"],
        "units":            "s-1",
        "description":      "Vertical wind shear in the 3-6 km layer, associated with mid-level mesocyclones.",
        "format":           "GRIB2",
    },
    # --- Hail ---
    {
        "product_name":     "MergedHCIZ",
        "long_name":        "Hail Classification Index (MESH)",
        "category":         "Hail",
        "update_interval_min": 2,
        "levels":           ["L3"],
        "units":            "mm",
        "description":      "Maximum Expected Size of Hail (MESH) derived from reflectivity profile.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "MESH",
        "long_name":        "Maximum Expected Size of Hail",
        "category":         "Hail",
        "update_interval_min": 2,
        "levels":           ["L3"],
        "units":            "mm",
        "description":      "Estimated maximum hail diameter at the surface.",
        "format":           "GRIB2",
    },
    # --- Lightning ---
    {
        "product_name":     "LightningDensity_NMQ_30min",
        "long_name":        "Lightning Density 30-minute",
        "category":         "Lightning",
        "update_interval_min": 2,
        "levels":           ["L3"],
        "units":            "flashes km-2 min-1",
        "description":      "Cloud-to-ground and in-cloud lightning density over a 30-minute window.",
        "format":           "GRIB2",
    },
    # --- Velocity / Winds ---
    {
        "product_name":     "MergedReflectivityAtLowestAltitude",
        "long_name":        "Merged Reflectivity at Lowest Altitude (MRLA)",
        "category":         "Reflectivity",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "dBZ",
        "description":      "Reflectivity sampled at the lowest unblocked radar altitude.",
        "format":           "GRIB2",
    },
    # --- Precipitation Rate ---
    {
        "product_name":     "PrecipRate",
        "long_name":        "Instantaneous Precipitation Rate",
        "category":         "Precipitation",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "mm hr-1",
        "description":      "Instantaneous surface precipitation rate derived from the MRMS dual-pol algorithm.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "PrecipFlag",
        "long_name":        "Precipitation Flag",
        "category":         "Precipitation",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "categorical",
        "description":      "Surface precipitation type classification (rain, snow, mixed, etc.).",
        "format":           "GRIB2",
    },
    # --- Quality / Coverage ---
    {
        "product_name":     "SeamlessHSR",
        "long_name":        "Seamless Hybrid Scan Reflectivity",
        "category":         "Reflectivity",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "dBZ",
        "description":      "Reflectivity mosaic using a seamless transition between scan elevations.",
        "format":           "GRIB2",
    },
    {
        "product_name":     "RadarQualityIndex",
        "long_name":        "Radar Quality Index",
        "category":         "Quality",
        "update_interval_min": 2,
        "levels":           ["L2"],
        "units":            "dimensionless",
        "description":      "Composite radar data quality index (0-1) indicating coverage and blockage.",
        "format":           "GRIB2",
    },
]


##############################
#  SCRAPE
##############################
class _TableParser(HTMLParser):
    """Minimal HTML parser to extract table rows from tables.php."""

    def __init__(self) -> None:
        super().__init__()
        self._in_table = False
        self._in_row   = False
        self._in_cell  = False
        self._current_row: List[str] = []
        self.rows: List[List[str]]   = []
        self._cell_text = ""

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag == "table":
            self._in_table = True
        elif tag == "tr" and self._in_table:
            self._in_row = True
            self._current_row = []
        elif tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._cell_text = ""

    def handle_endtag(self, tag: str) -> None:
        if tag == "table":
            self._in_table = False
        elif tag == "tr" and self._in_row:
            self._in_row = False
            if self._current_row:
                self.rows.append(self._current_row)
        elif tag in ("td", "th") and self._in_cell:
            self._in_cell = False
            self._current_row.append(self._cell_text.strip())

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_text += data


def scrape_mrms_products() -> List[Dict[str, Any]]:
    """
    Attempt to scrape the MRMS product table from tables.php.
    Falls back to the static catalog on any error.
    """
    try:
        response = requests.get(MRMS_TABLES_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        html = response.text
    except Exception as e:
        logger.warning("Could not fetch MRMS tables page (%s). Using static catalog.", e)
        return MRMS_STATIC_PRODUCTS

    parser = _TableParser()
    parser.feed(html)

    products: List[Dict[str, Any]] = []
    for row in parser.rows:
        if len(row) < 2:
            continue
        product_name = row[0].strip()
        if not product_name or product_name.lower() in ("product", "name", "variable"):
            continue
        product: Dict[str, Any] = {
            "product_name":        product_name,
            "long_name":           row[1] if len(row) > 1 else product_name,
            "category":            row[2] if len(row) > 2 else "MRMS",
            "update_interval_min": _parse_interval(row[3] if len(row) > 3 else "2"),
            "levels":              [row[4]] if len(row) > 4 else [],
            "units":               row[5] if len(row) > 5 else "",
            "description":         " ".join(row[6:]) if len(row) > 6 else "",
            "format":              "GRIB2",
        }
        products.append(product)

    if not products:
        logger.warning("No products parsed from tables.php. Using static catalog.")
        return MRMS_STATIC_PRODUCTS

    logger.info("Scraped %d MRMS products from tables.php", len(products))
    return products


def _parse_interval(value: str) -> int:
    """Extract a numeric update interval in minutes from a string."""
    match = re.search(r"\d+", value)
    return int(match.group()) if match else 2


##############################
#  TRANSFORM
##############################
def _science_keywords() -> List[Dict[str, str]]:
    return [
        {
            "category":         "EARTH SCIENCE",
            "topic":            "ATMOSPHERE",
            "term":             "PRECIPITATION",
            "variable_level_1": "PRECIPITATION RATE",
        },
        {
            "category":         "EARTH SCIENCE",
            "topic":            "ATMOSPHERE",
            "term":             "WEATHER EVENTS",
            "variable_level_1": "SEVERE WEATHER",
        },
        {
            "category":         "EARTH SCIENCE",
            "topic":            "SPECTRAL/ENGINEERING",
            "term":             "RADAR",
            "variable_level_1": "RADAR REFLECTIVITY",
        },
    ]


def _category_to_keywords(category: str) -> List[Dict[str, str]]:
    mapping: Dict[str, List[Dict[str, str]]] = {
        "Precipitation": [
            {
                "category": "EARTH SCIENCE", "topic": "ATMOSPHERE",
                "term": "PRECIPITATION", "variable_level_1": "PRECIPITATION RATE",
            }
        ],
        "Reflectivity": [
            {
                "category": "EARTH SCIENCE", "topic": "SPECTRAL/ENGINEERING",
                "term": "RADAR", "variable_level_1": "RADAR REFLECTIVITY",
            }
        ],
        "Severe Weather": [
            {
                "category": "EARTH SCIENCE", "topic": "ATMOSPHERE",
                "term": "WEATHER EVENTS", "variable_level_1": "SEVERE WEATHER",
            }
        ],
        "Hail": [
            {
                "category": "EARTH SCIENCE", "topic": "ATMOSPHERE",
                "term": "WEATHER EVENTS", "variable_level_1": "HAIL",
            }
        ],
        "Lightning": [
            {
                "category": "EARTH SCIENCE", "topic": "ATMOSPHERE",
                "term": "WEATHER EVENTS", "variable_level_1": "LIGHTNING",
            }
        ],
        "Quality": [
            {
                "category": "EARTH SCIENCE", "topic": "SPECTRAL/ENGINEERING",
                "term": "RADAR", "variable_level_1": "QUALITY INDEX",
            }
        ],
    }
    return mapping.get(category, _science_keywords())


def transform_to_kg_format(products: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Convert the MRMS product list to the KG class structure.
    One Dataset entry per MRMS product.
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

    # --- Organization ---
    classes_data["Organization"].append({
        "short_name":  "NOAA_NSSL",
        "long_name":   "NOAA National Severe Storms Laboratory",
        "url":         "https://nssl.noaa.gov",
        "data_center": "NOAA_NSSL",
    })

    # --- Platform ---
    classes_data["Platform"].append({
        "short_name": "WSR-88D",
        "long_name":  "NEXRAD WSR-88D Doppler Radar Network",
        "type":       "Earth Observation Satellites and Sensors",
    })

    # --- DataFormat ---
    classes_data["DataFormat"].append({
        "format":      "GRIB2",
        "mime_type":   "application/x-grib2",
        "description": "WMO GRIB Edition 2 gridded binary format",
    })

    # --- SpatialResolution ---
    classes_data["SpatialResolution"].append({
        "value":       "0.01",
        "unit":        "deg",
        "description": "~1 km horizontal resolution (0.01-degree grid)",
    })

    # --- CoordinateSystem ---
    classes_data["CoordinateSystem"].append({
        "name":        "MRMS_CONUS_LonLat",
        "description": "Regular longitude/latitude grid covering CONUS at 0.01-degree resolution",
        "epsg":        "4326",
    })

    # --- Collect unique categories for DataCategory and ScienceKeyword ---
    seen_categories: set = set()
    seen_keywords: set   = set()

    for kw in _science_keywords():
        kw_key = f"{kw['category']}_{kw['term']}"
        if kw_key not in seen_keywords:
            classes_data["ScienceKeyword"].append(kw)
            seen_keywords.add(kw_key)

    # --- One Dataset entry per product ---
    for product in products:
        pname    = product["product_name"]
        category = product.get("category", "MRMS")
        interval = product.get("update_interval_min", 2)
        units    = product.get("units", "")
        desc     = product.get("description", "")
        fmt      = product.get("format", "GRIB2")
        levels   = product.get("levels", [])

        full_desc = (
            desc
            or (
                f"MRMS {product.get('long_name', pname)} product. "
                f"Category: {category}. "
                f"Update interval: {interval} minutes. "
                f"Format: {fmt} (GRIB2 compressed). "
                f"Coverage: CONUS at ~1 km / 0.01-degree resolution."
            )
        )

        product_keywords = _category_to_keywords(category)
        for kw in product_keywords:
            kw_key = f"{kw['category']}_{kw['term']}_{kw.get('variable_level_1','')}"
            if kw_key not in seen_keywords:
                classes_data["ScienceKeyword"].append(kw)
                seen_keywords.add(kw_key)

        if category not in seen_categories:
            classes_data["DataCategory"].append({
                "name":        category,
                "description": f"MRMS {category} products",
            })
            seen_categories.add(category)

        filename_pattern = f"MRMS_{pname}_{'_'.join(levels) if levels else 'L2'}_YYYYMMDD-HHmmss.grib2.gz"

        dataset_entry: Dict[str, Any] = {
            "short_name":           pname,
            "title":                f"MRMS {product.get('long_name', pname)}",
            "summary":              full_desc,
            "description":          full_desc,
            "dataset_id":           f"MRMS_{pname}",
            "entry_id":             f"mrms_{pname.lower()}",
            "version_id":           "12.0",
            "processing_level_id":  "2",
            "online_access_flag":   True,
            "browse_flag":          False,
            "collection_data_type": "NEAR_REAL_TIME",
            "data_set_language":    "eng",
            "archive_center":       "NOAA_NSSL",
            "data_center":          "NOAA_NSSL",
            "native_id":            pname,
            "granule_count":        0,
            "day_night_flag":       "BOTH",
            "cloud_cover":          "",
            "frequency":            f"{interval}-minute",
            "time_start":           "2012-01-01T00:00:00Z",
            "time_end":             "",
            "boxes":                [MRMS_CONUS_BBOX],
            "polygons":             [],
            "points":               [],
            "organizations":        [{"short_name": "NOAA_NSSL"}],
            "platforms":            [{"short_name": "WSR-88D"}],
            "consortiums":          [],
            "science_keywords":     product_keywords,
            "links": [
                {
                    "href":        MRMS_TABLES_URL,
                    "rel":         "http://esipfed.org/ns/fedsearch/1.1/metadata#",
                    "hreflang":    "en-US",
                    "description": "MRMS operational product table",
                },
                {
                    "href":        MRMS_PROJECT_URL,
                    "rel":         "http://esipfed.org/ns/fedsearch/1.1/documentation#",
                    "hreflang":    "en-US",
                    "description": "MRMS project page",
                },
                {
                    "href":        MRMS_GITHUB_URL,
                    "rel":         "http://esipfed.org/ns/fedsearch/1.1/documentation#",
                    "hreflang":    "en-US",
                    "description": "MRMS GRIB2 format specifications and support tools",
                },
            ],
            "mrms_category":        category,
            "mrms_update_interval_min": interval,
            "mrms_units":           units,
            "mrms_format":          fmt,
            "mrms_levels":          levels,
            "mrms_filename_pattern": filename_pattern,
            "spatial_resolution_deg": 0.01,
            "spatial_resolution_km":  1.0,
            "coordinate_system":    "Regular lon/lat, CONUS domain",
        }
        classes_data["Dataset"].append(dataset_entry)

    logger.info("Built %d Dataset entries for MRMS products", len(classes_data["Dataset"]))
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

    logger.info("Scraping MRMS product catalog from NSSL tables page...")
    products = scrape_mrms_products()
    logger.info("Total MRMS products: %d", len(products))

    logger.info("Transforming to KG format...")
    kg_data = transform_to_kg_format(products)

    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(kg_data, f, indent=2, ensure_ascii=False)
    logger.info("Saved KG-format JSON to %s", LOCAL_FILE)

    logger.info("Uploading to S3...")
    upload_to_s3(LOCAL_FILE, S3_BUCKET, S3_KEY)

    logger.info("MRMS scraper complete.")
    print("\n=== MRMS Scraper Summary ===")
    for key, val in kg_data.items():
        if val:
            print(f"  {key}: {len(val)} items")


if __name__ == "__main__":
    main()
