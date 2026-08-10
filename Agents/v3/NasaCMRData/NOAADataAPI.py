#!/usr/bin/env python3
"""
NOAA Climate Data API Integration for Knowledge Graph
Matches NASA CMR structure for Neptune compatibility
"""

import requests
import json
import time
import os
import pandas as pd
from datetime import datetime, timedelta
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union
import logging
from typing import Dict, List, Optional, Any
import re

# Import NASA CMR functions to process NOAA field values
from NasaDataAPI import (
    classify_location_offline_fast,
    get_location_info_from_coords,
    parse_cmr_spatial,
    extract_polygons,
    classify_location_offline,
    extract_geographic_info_from_boundaries,
    mapbox_rate_limit,
    get_location_from_geometry,
    classify_location_from_bbox,
    extract_resolution_from_additional_attributes,
    extract_resolution_units,
    standardize_temporal_frequency
)

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, try direct env vars

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

##############################
#  CONFIG
##############################
NOAA_NCEI_BASE_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
NOAA_NCEI_DATA_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
NOAA_NCEI_SEARCH_URL = "https://www.ncei.noaa.gov/access/services/search/v1"
NOAA_ONESTOP_SEARCH_URL = "https://data.noaa.gov/onestop/api/search/search"
ERDDAP_BASE_URL = "https://coastwatch.pfeg.noaa.gov/erddap"
COOPS_BASE_URL = "https://api.tidesandcurrents.noaa.gov/api/prod"

# API Headers
HEADERS = {"User-Agent": "NOAA-KG-Extractor/1.0"}

# NOAA API Token (set via environment variable)
NOAA_TOKEN = os.getenv("NOAA_CDO_TOKEN", "")

# Rate limiting
REQUESTS_PER_SECOND = 5
_last_request_times = []

##############################
#  RATE LIMITING
##############################
def rate_limit():
    """Implement rate limiting for NOAA APIs."""
    global _last_request_times
    current_time = time.time()

    # Remove requests older than 1 second
    _last_request_times = [t for t in _last_request_times if current_time - t < 1.0]

    # If we've made too many requests, wait
    if len(_last_request_times) >= REQUESTS_PER_SECOND:
        sleep_time = 1.0 - (current_time - _last_request_times[0])
        if sleep_time > 0:
            time.sleep(sleep_time)

    _last_request_times.append(current_time)

##############################
#  CORE FETCH FUNCTIONS
##############################
def fetch_noaa_ncei_datasets(limit=1000, offset=0):
    """
    Fetch datasets from NOAA NCEI Climate Data Online API.
    Returns datasets in NASA CMR-compatible format.
    """
    # NCEI API requires a token - skip if not available
    if not NOAA_TOKEN:
        logger.warning("NOAA_TOKEN not set - skipping NCEI API (get token from https://www.ncdc.noaa.gov/cdo-web/token)")
        return []

    rate_limit()

    url = f"{NOAA_NCEI_BASE_URL}/datasets"
    headers = HEADERS.copy()
    headers["token"] = NOAA_TOKEN  # Token is required, not optional

    params = {
        "limit": min(limit, 1000),  # NCEI max is 1000
        "offset": offset
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=60)
        response.raise_for_status()
        data = response.json()

        if "results" in data and data["results"]:
            logger.info(f"Fetched {len(data['results'])} NCEI datasets")
            return transform_ncei_to_cmr_format(data["results"])
        else:
            logger.warning("No results found in NCEI response")
            return []

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            logger.error(f"NCEI API 400 error - check token validity and parameters: {e}")
        elif e.response.status_code == 401:
            logger.error(f"NCEI API 401 error - invalid or missing token: {e}")
        else:
            logger.error(f"NCEI API HTTP error: {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching NCEI datasets: {e}")
        return []

def fetch_noaa_erddap_datasets(max_datasets=1000):
    """
    Fetch datasets from NOAA ERDDAP servers.
    Returns datasets in NASA CMR-compatible format.
    """
    datasets = []

    # List of NOAA ERDDAP servers
    erddap_servers = [
        "https://coastwatch.pfeg.noaa.gov/erddap",
        "https://data.pmel.noaa.gov/generic/erddap",
        "https://oceanwatch.pifsc.noaa.gov/thredds/erddap"
    ]

    for server in erddap_servers:
        try:
            rate_limit()

            # Get dataset list
            url = f"{server}/info/index.json"
            response = requests.get(url, headers=HEADERS, timeout=60)
            response.raise_for_status()

            data = response.json()
            if "table" in data and "rows" in data["table"]:
                server_datasets = []
                for row in data["table"]["rows"][:max_datasets]:
                    dataset_id = row[0] if row and len(row) > 0 else None
                    if dataset_id and not dataset_id.startswith("http"):  # Skip malformed IDs
                        # Get detailed metadata for each dataset
                        dataset_meta = fetch_erddap_dataset_metadata(server, dataset_id)
                        if dataset_meta:
                            server_datasets.append(dataset_meta)

                logger.info(f"Fetched {len(server_datasets)} datasets from {server}")
                datasets.extend(server_datasets)

        except Exception as e:
            logger.error(f"Error fetching from ERDDAP server {server}: {e}")
            continue

    return transform_erddap_to_cmr_format(datasets)

def fetch_erddap_dataset_metadata(server_url, dataset_id):
    """Fetch detailed metadata for a specific ERDDAP dataset."""
    try:
        rate_limit()

        url = f"{server_url}/info/{dataset_id}/index.json"
        response = requests.get(url, headers=HEADERS, timeout=60)
        response.raise_for_status()

        data = response.json()
        if "table" in data:
            return {
                "dataset_id": dataset_id,
                "server_url": server_url,
                "metadata": data["table"]
            }
    except Exception as e:
        logger.error(f"Error fetching ERDDAP metadata for {dataset_id}: {e}")
        return None

def fetch_noaa_coops_stations(max_stations=500):
    """
    CO-OPS API requires specific station IDs and doesn't have a discovery endpoint.
    Returns empty list since we can't discover stations without hardcoding.
    """
    logger.info("CO-OPS API requires specific station IDs - no discovery endpoint available")
    logger.info("To get CO-OPS data, you need to specify station IDs directly")
    logger.info("Available at: https://api.tidesandcurrents.noaa.gov/api/prod/")
    return []

def fetch_noaa_onestop_datasets(max_datasets=None):
    """
    Fetch ALL datasets from NCEI Search Service (OneStop backend) using pagination.
    Returns datasets in NASA CMR-compatible format.
    """
    all_datasets = []
    page_size = 100  # Results per page
    offset = 0

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()

    while True:  # Unlimited pagination
        rate_limit()

        # OneStop requires POST with JSON body
        search_body = {
            "page": {
                "max": page_size,
                "offset": offset
            }
        }

        headers["Content-Type"] = "application/json"

        try:
            response = requests.post(url, headers=headers, json=search_body, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"]:
                page_results = data["data"]
                all_datasets.extend(page_results)

                total_count = data.get("meta", {}).get("total", "unknown")
                logger.info(f"OneStop Search page offset {offset}: fetched {len(page_results)} collections, total collected: {len(all_datasets)}, total available: {total_count}")

                # Stop if we got fewer results than requested (last page)
                if len(page_results) < page_size:
                    logger.info("Reached last page of OneStop results")
                    break

                # Continue to next page - no max limit check
                offset += page_size
                time.sleep(0.1)  # Small delay between requests

            else:
                logger.info(f"No more results at offset {offset}")
                break

        except Exception as e:
            logger.error(f"Error fetching OneStop page at offset {offset}: {e}")
            break

    # Return all datasets - no limiting
    logger.info(f"Fetched {len(all_datasets)} total OneStop datasets")
    return transform_onestop_to_cmr_format(all_datasets)

##############################
#  TRANSFORMATION FUNCTIONS
##############################
def transform_ncei_to_cmr_format(ncei_datasets):
    """Transform NCEI dataset format to NASA CMR-compatible format."""
    cmr_datasets = []

    for i, dataset in enumerate(ncei_datasets):
        cmr_dataset = {
            "short_name": dataset.get("id", f"ncei_dataset_{i}"),
            "title": dataset.get("name", "NCEI Dataset"),
            "entry_id": f"ncei_{dataset.get('id', i)}",
            "version_id": "1.0",
            "processing_level_id": dataset.get("processing_level") or None,
            "online_access_flag": True,
            "browse_flag": False,
            "dataset_id": dataset.get("name", f"NCEI Dataset {i}"),
            "data_center": "NOAA_NCEI",
            "archive_center": "NOAA/NCEI",
            "doi": "",
            "doi_authority": "",
            "collection_data_type": "SCIENCE_QUALITY",
            "data_set_language": "eng",
            "native_id": dataset.get("id", ""),
            "granule_count": 0,
            "day_night_flag": "",
            "cloud_cover": "",

            # Temporal extent from NCEI API
            "temporal_extent": {
                "start_date": dataset.get("mindate", ""),
                "end_date": dataset.get("maxdate", "")
            },

            # Science keywords - NCEI doesn't provide these, so empty
            "science_keywords": [],

            # NCEI-specific metadata
            "data_coverage": dataset.get("datacoverage", 0),

            # Organizations
            "organizations": [
                {
                    "name": "NOAA National Centers for Environmental Information",
                    "short_name": "NOAA NCEI",
                    "role": "ARCHIVER"
                }
            ],

            # Platforms - only if available in dataset
            "platforms": dataset.get("platforms") or [],

            # Data formats - only specify known API formats
            "data_formats": dataset.get("data_formats") or ["JSON"],  # API always returns JSON

            # Links
            "links": [
                {
                    "rel": "http://esipfed.org/ns/fedsearch/1.1/data#",
                    "href": f"{NOAA_NCEI_DATA_URL}?dataset={dataset.get('id', '')}",
                    "hreflang": "en-US",
                    "title": "Data Access"
                }
            ],

            # Spatial extent (to be populated if available)
            "spatial_extent": {
                "spatial_coverage_type": "HORIZONTAL",
                "horizontal_spatial_domain": {
                    "geometry": {
                        "coordinate_system": "GEOGRAPHIC",
                        "bounding_rectangles": []
                    }
                }
            },

            # Additional NOAA-specific fields
            "noaa_specific": {
                "data_category": dataset.get("datacoverage", ""),
                "station_count": dataset.get("stationcount", 0),
                "api_endpoint": f"{NOAA_NCEI_BASE_URL}/datasets/{dataset.get('id', '')}"
            }
        }

        cmr_datasets.append(cmr_dataset)

    return cmr_datasets

def transform_erddap_to_cmr_format(erddap_datasets):
    """Transform ERDDAP dataset format to NASA CMR-compatible format."""
    cmr_datasets = []

    for i, dataset in enumerate(erddap_datasets):
        dataset_id = dataset.get("dataset_id", f"erddap_{i}")
        server_url = dataset.get("server_url", "")
        metadata = dataset.get("metadata", {})

        # Extract metadata attributes
        attributes = {}
        if "rows" in metadata:
            for row in metadata["rows"]:
                if len(row) >= 2:
                    key = row[0]
                    value = row[1] if len(row) > 1 else ""
                    attributes[key] = value

        cmr_dataset = {
            "short_name": dataset_id,
            "title": attributes.get("title", f"ERDDAP Dataset {dataset_id}"),
            "entry_id": f"erddap_{dataset_id}",
            "version_id": attributes.get("version", "1.0"),
            "processing_level_id": attributes.get("processing_level") or None,
            "online_access_flag": True,
            "browse_flag": True,
            "dataset_id": attributes.get("title", dataset_id),
            "data_center": "NOAA_ERDDAP",
            "archive_center": attributes.get("institution", "NOAA"),
            "doi": "",
            "doi_authority": "",
            "collection_data_type": "SCIENCE_QUALITY",
            "data_set_language": "eng",
            "native_id": dataset_id,
            "granule_count": 0,
            "day_night_flag": "",
            "cloud_cover": "",

            # Temporal extent
            "temporal_extent": {
                "start_date": attributes.get("time_coverage_start", ""),
                "end_date": attributes.get("time_coverage_end", "")
            },

            # Science keywords - extract from ERDDAP keywords if available
            "science_keywords": parse_erddap_keywords(attributes.get("keywords", "")),

            # Organizations
            "organizations": [
                {
                    "name": attributes.get("institution", "NOAA"),
                    "short_name": "NOAA",
                    "role": "ORIGINATOR"
                }
            ],

            # Platforms
            "platforms": [
                {
                    "short_name": attributes.get("platform", "Ocean Platforms"),
                    "long_name": attributes.get("platform", "Ocean Observation Platforms"),
                    "type": "Ocean Platforms"
                }
            ],

            # Data formats
            "data_formats": ["NetCDF", "CSV", "JSON"],

            # Links
            "links": [
                {
                    "rel": "http://esipfed.org/ns/fedsearch/1.1/data#",
                    "href": f"{server_url}/griddap/{dataset_id}.html",
                    "hreflang": "en-US",
                    "title": "Data Access"
                },
                {
                    "rel": "http://esipfed.org/ns/fedsearch/1.1/browse#",
                    "href": f"{server_url}/griddap/{dataset_id}.graph",
                    "hreflang": "en-US",
                    "title": "Browse Imagery"
                }
            ],

            # Spatial extent
            "spatial_extent": create_spatial_extent_from_erddap(attributes),

            # Additional ERDDAP-specific fields
            "erddap_specific": {
                "server_url": server_url,
                "dataset_type": "griddap",
                "opendap_url": f"{server_url}/griddap/{dataset_id}",
                "variables": extract_erddap_variables(metadata)
            }
        }

        cmr_datasets.append(cmr_dataset)

    return cmr_datasets

def transform_coops_to_cmr_format(coops_data):
    """Transform CO-OPS station data to NASA CMR-compatible format."""
    cmr_datasets = []

    for i, station_data in enumerate(coops_data):
        station_id = station_data.get("station_id", f"coops_{i}")
        product = station_data.get("product", "water_level")
        metadata = station_data.get("metadata", {})

        cmr_dataset = {
            "short_name": f"{station_id}_{product}",
            "title": f"CO-OPS {product.replace('_', ' ').title()} - Station {station_id}",
            "entry_id": f"coops_{station_id}_{product}",
            "version_id": "1.0",
            "processing_level_id": "Level 1",
            "online_access_flag": True,
            "browse_flag": False,
            "dataset_id": f"CO-OPS {product} {station_id}",
            "data_center": "NOAA_COOPS",
            "archive_center": "NOAA/CO-OPS",
            "doi": "",
            "doi_authority": "",
            "collection_data_type": "NEAR_REAL_TIME",
            "data_set_language": "eng",
            "native_id": f"{station_id}_{product}",
            "granule_count": 0,
            "day_night_flag": "",
            "cloud_cover": "",

            # Temporal extent (operational data)
            "temporal_extent": {
                "start_date": "1950-01-01T00:00:00Z",  # Historical start
                "end_date": datetime.now().isoformat() + "Z"  # Current
            },

            # Science keywords - only if we can derive from product type
            "science_keywords": metadata.get("science_keywords") or [],

            # Organizations
            "organizations": [
                {
                    "name": "NOAA Center for Operational Oceanographic Products and Services",
                    "short_name": "NOAA CO-OPS",
                    "role": "ORIGINATOR"
                }
            ],

            # Platforms (stations)
            "platforms": [
                {
                    "short_name": station_id,
                    "long_name": metadata.get("name", f"Station {station_id}"),
                    "type": "Coastal Station"
                }
            ],

            # Data formats
            "data_formats": ["JSON", "CSV", "XML"],

            # Links
            "links": [
                {
                    "rel": "http://esipfed.org/ns/fedsearch/1.1/data#",
                    "href": station_data.get("api_url", ""),
                    "hreflang": "en-US",
                    "title": "Real-time Data Access"
                }
            ],

            # Spatial extent (point location)
            "spatial_extent": create_spatial_extent_from_coops(metadata),

            # Additional CO-OPS specific fields
            "coops_specific": {
                "station_id": station_id,
                "product": product,
                "datum": "MLLW",
                "units": "metric",
                "real_time": True,
                "forecast_available": product in ["water_level", "currents"]
            }
        }

        cmr_datasets.append(cmr_dataset)

    return cmr_datasets

def transform_onestop_to_cmr_format(onestop_datasets):
    """Transform OneStop dataset format to NASA CMR-compatible format."""
    cmr_datasets = []

    for i, dataset in enumerate(onestop_datasets):
        # Extract metadata from OneStop response - now with full metadata
        identifier = dataset.get("id", f"onestop_{i}")
        title = dataset.get("name") or dataset.get("title") or identifier.replace("-", " ").title()
        description = dataset.get("description", "")

        cmr_dataset = {
            "short_name": identifier,
            "title": title,
            "entry_id": f"onestop_{identifier}",
            "version_id": dataset.get("version", "1.0"),
            "processing_level_id": dataset.get("processingLevel") or None,
            "online_access_flag": True,
            "browse_flag": dataset.get("thumbnail") is not None,
            "dataset_id": title,
            "data_center": "NOAA_ONESTOP",
            "archive_center": dataset.get("dataCenter", "NOAA"),
            "doi": dataset.get("doi", ""),
            "doi_authority": "",
            "collection_data_type": dataset.get("dataFormat", "SCIENCE_QUALITY"),
            "data_set_language": "eng",
            "native_id": identifier,
            "granule_count": 0,
            "day_night_flag": "",
            "cloud_cover": "",

            # Temporal extent from OneStop
            "temporal_extent": {
                "start_date": dataset.get("startDate", ""),
                "end_date": dataset.get("endDate", "")
            },

            # Science keywords from OneStop - use parsedKeywords which are already in GCMD format
            "science_keywords": parse_onestop_parsed_keywords(dataset.get("parsedKeywords", [])),

            # Organizations from OneStop
            "organizations": [
                {
                    "name": dataset.get("organization", {}).get("name", "NOAA"),
                    "short_name": "NOAA",
                    "role": "ORIGINATOR"
                }
            ],

            # Platforms from OneStop - use observationTypes
            "platforms": parse_onestop_observation_types(dataset.get("observationTypes", [])),

            # Data formats from OneStop
            "data_formats": [fmt.get("name", "").upper() for fmt in dataset.get("formats", [])],

            # Links from OneStop
            "links": parse_onestop_rich_links(dataset.get("links", {})),

            # Spatial extent from OneStop
            "spatial_extent": create_spatial_extent_from_onestop(dataset.get("spatialCoverage", {})),

            # OneStop-specific fields
            "onestop_specific": {
                "uuid": dataset.get("uuid", ""),
                "hierarchyLevel": dataset.get("hierarchyLevel", ""),
                "thumbnail": dataset.get("thumbnail", ""),
                "services": dataset.get("services", [])
            }
        }

        cmr_datasets.append(cmr_dataset)

    return cmr_datasets

##############################
#  HELPER FUNCTIONS
##############################
def parse_erddap_keywords(keywords_string):
    """Parse ERDDAP keywords string into science keywords structure."""
    if not keywords_string:
        return []

    # ERDDAP keywords are often comma-separated
    keywords = [k.strip() for k in keywords_string.split(",")]

    # Only return if we have meaningful keywords, otherwise empty list
    if len(keywords) > 0 and any(len(k) > 2 for k in keywords):
        # Return as simple keyword list since ERDDAP doesn't use GCMD structure
        return [{"keyword": k} for k in keywords if len(k) > 2]

    return []

def parse_onestop_keywords(keywords_list):
    """Parse OneStop keywords into science keywords structure."""
    if not keywords_list:
        return []

    science_keywords = []
    for keyword in keywords_list:
        if isinstance(keyword, dict):
            keyword_text = keyword.get("keyword", "")
            thesaurus = keyword.get("thesaurus", "")
            # Only add if keyword has actual content
            if keyword_text and keyword_text.strip():
                science_keywords.append({
                    "keyword": keyword_text,
                    "thesaurus": thesaurus
                })
        elif isinstance(keyword, str) and keyword.strip():
            science_keywords.append({"keyword": keyword})

    return science_keywords

def parse_onestop_parsed_keywords(parsed_keywords_list):
    """Parse OneStop parsedKeywords which are already in GCMD format."""
    if not parsed_keywords_list:
        return []

    science_keywords = []
    for keyword_str in parsed_keywords_list:
        # Parse GCMD format: "EARTH SCIENCE > ATMOSPHERE > ATMOSPHERIC TEMPERATURE > SURFACE TEMPERATURE > AIR TEMPERATURE"
        parts = [part.strip() for part in keyword_str.split(">")]

        if len(parts) >= 3:
            keyword_obj = {
                "Category": parts[0],
                "Topic": parts[1],
                "Term": parts[2]
            }
            if len(parts) > 3:
                keyword_obj["VariableLevel1"] = parts[3]
            if len(parts) > 4:
                keyword_obj["VariableLevel2"] = parts[4]
            if len(parts) > 5:
                keyword_obj["VariableLevel3"] = parts[5]

            science_keywords.append(keyword_obj)

    return science_keywords

def parse_onestop_observation_types(observation_types_list):
    """Parse OneStop observationTypes into platforms structure."""
    if not observation_types_list:
        return []

    platforms = []
    for obs_type in observation_types_list:
        if isinstance(obs_type, dict):
            name = obs_type.get("name", "")
            platforms.append({
                "short_name": name.replace(" ", "_"),
                "long_name": name,
                "type": "Observation Platform"
            })

    return platforms

def parse_onestop_formats(links_list):
    """Parse OneStop links to extract data formats."""
    if not links_list:
        return ["JSON"]  # Default API format

    formats = set()
    for link in links_list:
        if isinstance(link, dict):
            url = link.get("linkUrl", "")
            if ".nc" in url or "netcdf" in url.lower():
                formats.add("NetCDF")
            elif ".csv" in url:
                formats.add("CSV")
            elif ".xml" in url:
                formats.add("XML")
            elif ".json" in url:
                formats.add("JSON")

    return list(formats) if formats else ["JSON"]

def parse_onestop_links(links_list):
    """Parse OneStop links into CMR links structure."""
    if not links_list:
        return []

    cmr_links = []
    for link in links_list:
        if isinstance(link, dict):
            cmr_links.append({
                "rel": link.get("linkFunction", "http://esipfed.org/ns/fedsearch/1.1/data#"),
                "href": link.get("linkUrl", ""),
                "title": link.get("linkName", ""),
                "hreflang": "en-US"
            })

    return cmr_links

def parse_onestop_rich_links(links_dict):
    """Parse OneStop rich links structure into CMR links format."""
    if not links_dict:
        return []

    cmr_links = []

    # Parse different link categories
    for category, links_list in links_dict.items():
        for link in links_list:
            if isinstance(link, dict):
                cmr_links.append({
                    "rel": f"http://esipfed.org/ns/fedsearch/1.1/{link.get('type', 'data')}#",
                    "href": link.get("url", ""),
                    "title": link.get("name", ""),
                    "hreflang": "en-US"
                })

    return cmr_links

def create_spatial_extent_from_onestop(location_data):
    """Create spatial extent from OneStop location data."""
    if not location_data:
        return {
            "spatial_coverage_type": "HORIZONTAL",
            "horizontal_spatial_domain": {
                "geometry": {
                    "coordinate_system": "GEOGRAPHIC",
                    "bounding_rectangles": []
                }
            }
        }

    # OneStop uses GeoJSON-style coordinates
    if "coordinates" in location_data and location_data["coordinates"]:
        try:
            coords = location_data["coordinates"][0]  # Get first polygon
            if len(coords) >= 4:
                # Extract bounding box from polygon coordinates
                lons = [coord[0] for coord in coords]
                lats = [coord[1] for coord in coords]

                return {
                    "spatial_coverage_type": "HORIZONTAL",
                    "horizontal_spatial_domain": {
                        "geometry": {
                            "coordinate_system": "GEOGRAPHIC",
                            "bounding_rectangles": [
                                {
                                    "north": max(lats),
                                    "south": min(lats),
                                    "east": max(lons),
                                    "west": min(lons)
                                }
                            ]
                        }
                    }
                }
        except (IndexError, TypeError, ValueError):
            pass

    return {
        "spatial_coverage_type": "HORIZONTAL",
        "horizontal_spatial_domain": {
            "geometry": {
                "coordinate_system": "GEOGRAPHIC",
                "bounding_rectangles": []
            }
        }
    }

def create_spatial_extent_from_erddap(attributes):
    """Create spatial extent from ERDDAP attributes."""
    try:
        lat_min = float(attributes.get("geospatial_lat_min", 0))
        lat_max = float(attributes.get("geospatial_lat_max", 0))
        lon_min = float(attributes.get("geospatial_lon_min", 0))
        lon_max = float(attributes.get("geospatial_lon_max", 0))

        return {
            "spatial_coverage_type": "HORIZONTAL",
            "horizontal_spatial_domain": {
                "geometry": {
                    "coordinate_system": "GEOGRAPHIC",
                    "bounding_rectangles": [
                        {
                            "north": lat_max,
                            "south": lat_min,
                            "east": lon_max,
                            "west": lon_min
                        }
                    ]
                }
            }
        }
    except (ValueError, TypeError):
        return {
            "spatial_coverage_type": "HORIZONTAL",
            "horizontal_spatial_domain": {
                "geometry": {
                    "coordinate_system": "GEOGRAPHIC",
                    "bounding_rectangles": []
                }
            }
        }

def create_spatial_extent_from_coops(metadata):
    """Create spatial extent from CO-OPS station metadata."""
    try:
        lat = float(metadata.get("lat", 0))
        lon = float(metadata.get("lon", 0))

        # Create a small bounding box around the point
        buffer = 0.01  # ~1km buffer

        return {
            "spatial_coverage_type": "HORIZONTAL",
            "horizontal_spatial_domain": {
                "geometry": {
                    "coordinate_system": "GEOGRAPHIC",
                    "bounding_rectangles": [
                        {
                            "north": lat + buffer,
                            "south": lat - buffer,
                            "east": lon + buffer,
                            "west": lon - buffer
                        }
                    ]
                }
            }
        }
    except (ValueError, TypeError):
        return {
            "spatial_coverage_type": "HORIZONTAL",
            "horizontal_spatial_domain": {
                "geometry": {
                    "coordinate_system": "GEOGRAPHIC",
                    "bounding_rectangles": []
                }
            }
        }

def extract_erddap_variables(metadata):
    """Extract variable information from ERDDAP metadata."""
    variables = []

    if "rows" in metadata:
        for row in metadata["rows"]:
            if len(row) >= 2 and "variable" in str(row[0]).lower():
                variables.append({
                    "name": row[0],
                    "description": row[1] if len(row) > 1 else "",
                    "units": row[2] if len(row) > 2 else ""
                })

    return variables

##############################
#  MAIN AGGREGATION FUNCTION
##############################
def fetch_noaa_all_sources(max_per_source=500):
    """
    Fetch metadata from all NOAA sources and return in NASA CMR-compatible format.
    """
    all_datasets = []
    raw_responses = {}

    # Create output directory for raw API responses
    os.makedirs("noaa_json", exist_ok=True)

    logger.info("Starting NOAA data aggregation...")

    # 1. Fetch NCEI datasets
    logger.info("Fetching NCEI datasets...")
    ncei_datasets = fetch_noaa_ncei_datasets(limit=max_per_source)
    all_datasets.extend(ncei_datasets)
    raw_responses["ncei"] = ncei_datasets
    logger.info(f"Added {len(ncei_datasets)} NCEI datasets")

    # 2. Fetch ERDDAP datasets
    logger.info("Fetching ERDDAP datasets...")
    erddap_datasets = fetch_noaa_erddap_datasets(max_datasets=max_per_source)
    all_datasets.extend(erddap_datasets)
    raw_responses["erddap"] = erddap_datasets
    logger.info(f"Added {len(erddap_datasets)} ERDDAP datasets")

    # 3. Fetch CO-OPS station data
    logger.info("Fetching CO-OPS station data...")
    coops_datasets = fetch_noaa_coops_stations(max_stations=50)  # Fewer due to per-product expansion
    all_datasets.extend(coops_datasets)
    raw_responses["coops"] = coops_datasets
    logger.info(f"Added {len(coops_datasets)} CO-OPS datasets")

    # 4. Fetch OneStop datasets
    logger.info("Fetching ALL OneStop datasets...")
    onestop_datasets = fetch_noaa_onestop_datasets()  # No limit - fetch all
    all_datasets.extend(onestop_datasets)
    raw_responses["onestop"] = onestop_datasets
    logger.info(f"Added {len(onestop_datasets)} OneStop datasets")

    # Save all raw API responses
    raw_api_file = "noaa_json/noaa_raw_api_response.json"
    with open(raw_api_file, 'w', encoding='utf-8') as f:
        json.dump(raw_responses, f, indent=2, ensure_ascii=False)
    logger.info(f"All raw API responses saved to {raw_api_file}")

    logger.info(f"Total NOAA datasets collected: {len(all_datasets)}")

    return all_datasets

def transform_noaa_to_classes_from_raw(raw_onestop_datasets):
    """
    Transform raw OneStop datasets directly into the class structure expected by json_to_csvs.py.
    This extracts ALL available metadata from the raw OneStop API response without losing data.
    """
    classes_data = {
        "Dataset": [],
        "DataCategory": [],
        "DataFormat": [],
        "CoordinateSystem": [],
        "Location": [],
        "Station": [],
        "Organization": [],
        "Platform": [],
        "Consortium": [],
        "TemporalExtent": [],
        "Variable": [],
        "CESMVariable": [],  # Empty for NOAA (CESM is NASA-specific)
        "Component": [],    # Empty for NOAA
        "Contact": [],
        "Project": [],
        "RelatedUrl": [],
        "SpatialResolution": [],
        "TemporalResolution": [],
        "Granule": [],
        "Instrument": [],
        "ScienceKeyword": [],
        "ProcessingLevel": [],
        "Relationship": []   # Added to match NASA CMR structure
    }

    # Track unique items to avoid duplicates
    seen_organizations = set()
    seen_platforms = set()
    seen_data_formats = set()
    seen_locations = set()
    seen_science_keywords = set()
    seen_contacts = set()
    seen_data_categories = set()
    seen_variables = set()

    for i, raw_dataset in enumerate(raw_onestop_datasets):
        # Work directly with raw OneStop API response structure
        dataset_id = raw_dataset.get("id", f"dataset_{i}")
        dataset_name = raw_dataset.get("name", raw_dataset.get("title", dataset_id))

        # 1. Dataset - Core information
        dataset_entry = {
            "short_name": dataset_id,
            "title": dataset_name,
            "dataset_id": dataset_name,
            "entry_id": f"onestop_{dataset_id}",
            "version_id": "1.0",
            "processing_level_id": "",
            "online_access_flag": raw_dataset.get("available", True),
            "browse_flag": bool(raw_dataset.get("thumbnail")),
            "science_keywords": [],  # Will be populated below
            "doi": raw_dataset.get("doiLink", "").replace("https://doi.org/", "") if raw_dataset.get("doiLink") else "",
            "doi_authority": "DOI" if raw_dataset.get("doiLink") else "",
            "collection_data_type": "SCIENCE_QUALITY",
            "data_set_language": "eng",
            "archive_center": "NOAA",
            "native_id": raw_dataset.get("fileId", ""),
            "granule_count": 0,
            "day_night_flag": "",
            "cloud_cover": "",
            "data_center": "NOAA_NCEI",
            "description": raw_dataset.get("description", ""),
            "frequency": raw_dataset.get("frequency", ""),
            "featured": raw_dataset.get("featured", False),
            "contact_info": raw_dataset.get("contactInfo", "")
        }
        classes_data["Dataset"].append(dataset_entry)

        # Create data category from dataset summary/title/description as requested
        dataset_summary = raw_dataset.get("summary", "")
        dataset_description = raw_dataset.get("description", "")

        # Use summary first, then description, then title for data category
        data_category_source = dataset_summary or dataset_description or dataset_name

        if data_category_source and data_category_source not in seen_data_categories:
            # Clean and truncate for category name
            category_name = data_category_source.strip()
            if len(category_name) > 100:
                category_name = category_name[:97] + "..."

            classes_data["DataCategory"].append({
                "name": category_name,
                "description": f"Dataset category: {data_category_source}",
                "type": "DATASET_SUMMARY"
            })
            seen_data_categories.add(data_category_source)

        # 2. Variables - Extract ALL dataTypes (this is the comprehensive field)
        data_types = raw_dataset.get("dataTypes", [])
        for var in data_types:
            var_id = var.get("id", "")
            var_name = var.get("name", var_id)
            var_key = f"{dataset_id}_{var_id}"

            if var_key not in seen_variables:
                classes_data["Variable"].append({
                    "name": var_name,
                    "description": var.get("name", ""),  # Full description is in name field
                    "variable_id": var_id,
                    "units": "",  # Not provided in OneStop
                    "standard_name": "",
                    "long_name": var_name,
                    "search_weight": var.get("searchWeight", 1),
                    "date_range": var.get("dateRange", {}),
                    "dataset_id": dataset_id
                })
                seen_variables.add(var_key)


        # 3. Contacts - Extract ALL people with full details
        people = raw_dataset.get("people", [])
        for person in people:
            org_info = person.get("organization", {})
            person_key = f"{person.get('name', '')}_{org_info.get('name', '')}_{person.get('role', '')}"

            if person_key not in seen_contacts:
                classes_data["Contact"].append({
                    "name": person.get("name", ""),
                    "role": person.get("role", ""),
                    "organization": org_info.get("name", ""),
                    "position": person.get("position", ""),
                    "url": person.get("url", ""),
                    "email": "",  # Not provided in OneStop
                    "phone": "",
                    "address": "",
                    "dataset_id": dataset_id
                })
                seen_contacts.add(person_key)

            # Also extract organizations from people
            org_name = org_info.get("name", "")
            if org_name and org_name not in seen_organizations:
                classes_data["Organization"].append({
                    "short_name": org_name.split(">")[-1].strip() if ">" in org_name else org_name[:50],
                    "long_name": org_name,
                    "type": "DATA_PROVIDER",
                    "url": "",
                    "dataset_id": dataset_id
                })
                seen_organizations.add(org_name)

        # 4. Data Formats - Extract ALL formats with details
        formats = raw_dataset.get("formats", [])
        for fmt in formats:
            fmt_name = fmt.get("name", "").upper()
            fmt_id = fmt.get("id", "")

            if fmt_name and fmt_name not in seen_data_formats:
                classes_data["DataFormat"].append({
                    "format": fmt_name,
                    "mime_type": get_mime_type(fmt_name),
                    "description": f"{fmt_name} format",
                    "format_id": fmt_id,
                    "dataset_id": dataset_id
                })
                seen_data_formats.add(fmt_name)

        # 5. Platforms - Extract observation types as platforms
        obs_types = raw_dataset.get("observationTypes", [])
        for obs in obs_types:
            obs_name = obs.get("name", "")
            obs_id = obs.get("id", "")

            if obs_name and obs_name not in seen_platforms:
                classes_data["Platform"].append({
                    "short_name": obs_name.replace(" ", "_"),
                    "long_name": obs_name,
                    "type": "Observation Platform",
                    "platform_id": obs_id,
                    "dataset_id": dataset_id
                })
                seen_platforms.add(obs_name)

        # 6. Science Keywords - Extract parsedKeywords (GCMD format)
        parsed_keywords = raw_dataset.get("parsedKeywords", [])
        for kw_string in parsed_keywords:
            if kw_string not in seen_science_keywords:
                # Parse GCMD format: "EARTH SCIENCE > ATMOSPHERE > TEMPERATURE"
                parts = [part.strip() for part in kw_string.split(">")]

                keyword_obj = {
                    "category": parts[0] if len(parts) > 0 else "",
                    "topic": parts[1] if len(parts) > 1 else "",
                    "term": parts[2] if len(parts) > 2 else "",
                    "variable_level_1": parts[3] if len(parts) > 3 else "",
                    "variable_level_2": parts[4] if len(parts) > 4 else "",
                    "variable_level_3": parts[5] if len(parts) > 5 else "",
                    "full_path": kw_string,
                    "dataset_id": dataset_id
                }
                classes_data["ScienceKeyword"].append(keyword_obj)
                seen_science_keywords.add(kw_string)

                # Also create data categories from top-level categories
                category = keyword_obj["category"]
                if category and category not in seen_data_categories:
                    classes_data["DataCategory"].append({
                        "name": category,
                        "description": f"Climate data category: {category}",
                        "type": "GCMD_CATEGORY"
                    })
                    seen_data_categories.add(category)

        # 7. Spatial Location - Extract from location coordinates
        location = raw_dataset.get("location", {})
        if location.get("coordinates"):
            try:
                coords = location["coordinates"][0]  # First polygon
                if coords and len(coords) >= 4:
                    # Extract bounding box
                    lons = [coord[0] for coord in coords]
                    lats = [coord[1] for coord in coords]

                    bbox = {
                        "west": min(lons),
                        "south": min(lats),
                        "east": max(lons),
                        "north": max(lats)
                    }

                    location_key = f"{bbox['west']}_{bbox['south']}_{bbox['east']}_{bbox['north']}"
                    if location_key not in seen_locations:
                        location_name = generate_location_name(bbox)

                        # Try to get place names using NASA functions during main extraction
                        place_names = []
                        countries = []
                        try:
                            # Format for NASA function: "SouthLat WestLon NorthLat EastLon"
                            bbox_str = f"{bbox['south']} {bbox['west']} {bbox['north']} {bbox['east']}"
                            spatial_geom = parse_cmr_spatial(boxes=[bbox_str])
                            if spatial_geom:
                                location_info = classify_location_offline_fast(spatial_geom)
                                if location_info:
                                    place_names = location_info.get("place_names", [])
                                    countries = location_info.get("countries", [])
                                    scope = location_info.get("scope", "unclassified")

                                    # Add scope as location category to DataCategory
                                    if scope and scope != "unclassified":
                                        scope_category = scope.title()  # Convert to title case
                                        if scope_category not in seen_data_categories:
                                            classes_data["DataCategory"].append({
                                                "name": scope_category,
                                                "description": f"Geographic scope: {scope_category}",
                                                "type": "LOCATION_SCOPE"
                                            })
                                            seen_data_categories.add(scope_category)

                                    if place_names or countries:
                                        logger.debug(f"NASA location enhancement for {dataset_id}: scope={scope}, {len(place_names)} places, {len(countries)} countries")

                        except Exception as e:
                            logger.debug(f"NASA location enhancement failed for {dataset_id}: {e}")
                            pass  # Continue without NASA enhancement if it fails

                        classes_data["Location"].append({
                            "name": location_name,
                            "bounding_box": bbox,
                            "coordinate_system": "GEOGRAPHIC",
                            "dataset_id": dataset_id,
                            "place_names": place_names,
                            "countries": countries,
                            "scope": scope if 'scope' in locals() else "unclassified",
                            "nasa_enhanced": bool(place_names or countries)
                        })
                        seen_locations.add(location_key)

                        # Also create data categories from spatial coverage
                        if bbox["west"] == -180.0 and bbox["east"] == 180.0:
                            spatial_category = "Global Coverage"
                        elif abs(bbox["east"] - bbox["west"]) > 60:
                            spatial_category = "Regional Coverage"
                        else:
                            spatial_category = "Local Coverage"

                        if spatial_category not in seen_data_categories:
                            classes_data["DataCategory"].append({
                                "name": spatial_category,
                                "description": f"Spatial coverage type: {spatial_category}",
                                "type": "SPATIAL_COVERAGE"
                            })
                            seen_data_categories.add(spatial_category)
            except (IndexError, TypeError, ValueError) as e:
                pass  # Skip malformed coordinates

        # 8. Temporal Extent
        start_date = raw_dataset.get("startDate", "")
        end_date = raw_dataset.get("endDate", "")
        if start_date or end_date:
            classes_data["TemporalExtent"].append({
                "start_date": start_date,
                "end_date": end_date,
                "dataset_id": dataset_id
            })

        # 9. Related URLs - Extract ALL links with categorization
        links = raw_dataset.get("links", {})
        if isinstance(links, dict):
            for category, link_list in links.items():
                if isinstance(link_list, list):
                    for link in link_list:
                        if isinstance(link, dict) and link.get("url"):
                            classes_data["RelatedUrl"].append({
                                "url": link.get("url", ""),
                                "description": link.get("name", ""),
                                "type": f"{category}#{link.get('type', '')}",
                                "category": category,
                                "link_type": link.get("type", ""),
                                "dataset_id": dataset_id
                            })

        # 10. Temporal Resolution from frequency
        frequency = raw_dataset.get("frequency", "")
        if frequency:
            classes_data["TemporalResolution"].append({
                "resolution": frequency,
                "description": f"Data collection frequency: {frequency}",
                "dataset_id": dataset_id
            })

        # 11. Spatial Resolution using NASA CMR functions
        # Convert NOAA dataset to NASA CMR format for resolution extraction
        nasa_format_dataset = {
            "summary": raw_dataset.get("description", ""),
            "title": raw_dataset.get("name", raw_dataset.get("title", "")),
            "short_name": raw_dataset.get("id", ""),
            "spatial_resolution": raw_dataset.get("spatialResolution", ""),
            "additional_attributes": []  # NOAA doesn't have this structure
        }

        spatial_resolution, _ = extract_resolution_from_additional_attributes(nasa_format_dataset)

        if spatial_resolution:
            classes_data["SpatialResolution"].append({
                "spatial_id": f"spatial_{dataset_id}",
                "resolution": spatial_resolution,
                "units": extract_resolution_units(spatial_resolution),
                "dataset_id": dataset_id
            })

        # 12. Processing Level from featured status
        if raw_dataset.get("featured", False):
            classes_data["ProcessingLevel"].append({
                "id": "Featured",
                "description": "Featured dataset with high visibility and quality",
                "dataset_id": dataset_id
            })

        # 12. Coordinate System
        if location:
            classes_data["CoordinateSystem"].append({
                "name": "GEOGRAPHIC",
                "description": "Geographic coordinate system (WGS84)"
            })

    return classes_data

def transform_noaa_to_classes(all_datasets):
    """
    Transform NOAA datasets into the class structure expected by json_to_csvs.py.
    Matches the NASA CMR structure exactly with comprehensive node extraction.
    Now properly extracts from actual OneStop API field structure.
    """
    classes_data = {
        "Dataset": [],
        "DataCategory": [],
        "DataFormat": [],
        "CoordinateSystem": [],
        "Location": [],
        "Station": [],
        "Organization": [],
        "Platform": [],
        "Consortium": [],
        "TemporalExtent": [],
        "Variable": [],
        "CESMVariable": [],  # Empty for NOAA (CESM is NASA-specific)
        "Component": [],    # Empty for NOAA
        "Contact": [],
        "Project": [],
        "RelatedUrl": [],
        "SpatialResolution": [],
        "TemporalResolution": [],
        "Granule": [],
        "Instrument": [],
        "ScienceKeyword": [],
        "ProcessingLevel": [],
        "Relationship": []   # Added to match NASA CMR structure
    }

    # Track unique items to avoid duplicates
    seen_organizations = set()
    seen_platforms = set()
    seen_data_formats = set()
    seen_locations = set()
    seen_science_keywords = set()
    seen_contacts = set()
    seen_data_categories = set()
    seen_instruments = set()

    for i, dataset in enumerate(all_datasets):
        # Extract actual OneStop dataset structure - this comes from the raw API
        # The dataset is already in OneStop format from transform_onestop_to_cmr_format

        # Get original OneStop fields if available in onestop_specific
        onestop_data = dataset.get("onestop_specific", {})

        # 1. Dataset
        dataset_entry = {
            "short_name": dataset.get("short_name", ""),
            "title": dataset.get("title", ""),
            "dataset_id": dataset.get("dataset_id", ""),
            "entry_id": dataset.get("entry_id", ""),
            "version_id": dataset.get("version_id", ""),
            "processing_level_id": dataset.get("processing_level_id", ""),
            "online_access_flag": dataset.get("online_access_flag", True),
            "browse_flag": dataset.get("browse_flag", False),
            "science_keywords": dataset.get("science_keywords", []),
            "doi": dataset.get("doi", ""),
            "doi_authority": dataset.get("doi_authority", ""),
            "collection_data_type": dataset.get("collection_data_type", ""),
            "data_set_language": dataset.get("data_set_language", ""),
            "archive_center": dataset.get("archive_center", ""),
            "native_id": dataset.get("native_id", ""),
            "granule_count": dataset.get("granule_count", 0),
            "day_night_flag": dataset.get("day_night_flag", ""),
            "cloud_cover": dataset.get("cloud_cover", ""),
            "data_center": dataset.get("data_center", ""),
            "links": dataset.get("links", []),
            "description": dataset.get("summary", "") or dataset.get("description", ""),
            "frequency": dataset.get("frequency", "")
        }
        classes_data["Dataset"].append(dataset_entry)

        # 2. Organizations - Extract from dataset organization field
        for org in dataset.get("organizations", []):
            org_key = org.get("short_name", "")
            if org_key and org_key not in seen_organizations:
                classes_data["Organization"].append({
                    "short_name": org.get("short_name", ""),
                    "long_name": org.get("name", ""),
                    "type": org.get("role", ""),
                    "url": ""
                })
                seen_organizations.add(org_key)

        # 3. Data Formats - Extract from actual OneStop formats field
        for fmt in dataset.get("data_formats", []):
            if fmt and fmt not in seen_data_formats:
                classes_data["DataFormat"].append({
                    "format": fmt,
                    "mime_type": get_mime_type(fmt),
                    "description": f"{fmt} format"
                })
                seen_data_formats.add(fmt)

        # 4. Observation Types as Platforms - Extract from observationTypes
        for platform in dataset.get("platforms", []):
            platform_key = platform.get("short_name", "")
            if platform_key and platform_key not in seen_platforms:
                classes_data["Platform"].append({
                    "short_name": platform.get("short_name", ""),
                    "long_name": platform.get("long_name", ""),
                    "type": platform.get("type", "")
                })
                seen_platforms.add(platform_key)

        # 5. Science Keywords - Extract from parsedKeywords (GCMD format)
        for keyword in dataset.get("science_keywords", []):
            keyword_str = f"{keyword.get('Category', '')}_{keyword.get('Topic', '')}_{keyword.get('Term', '')}"
            if keyword_str not in seen_science_keywords:
                classes_data["ScienceKeyword"].append({
                    "category": keyword.get("Category", ""),
                    "topic": keyword.get("Topic", ""),
                    "term": keyword.get("Term", ""),
                    "variable_level_1": keyword.get("VariableLevel1", ""),
                    "variable_level_2": keyword.get("VariableLevel2", ""),
                    "variable_level_3": keyword.get("VariableLevel3", "")
                })
                seen_science_keywords.add(keyword_str)

        # 6. Data Categories - Extract from keywords and observation types
        # Use science keywords to derive data categories
        for keyword in dataset.get("science_keywords", []):
            category = keyword.get("Category", "")
            if category and category not in seen_data_categories:
                classes_data["DataCategory"].append({
                    "name": category,
                    "description": f"Climate data category: {category}",
                    "type": "GCMD_Category"
                })
                seen_data_categories.add(category)

        # 7. Temporal Extent - Extract from startDate/endDate
        temporal = dataset.get("temporal_extent", {})
        if temporal.get("start_date") or temporal.get("end_date"):
            classes_data["TemporalExtent"].append({
                "start_date": temporal.get("start_date", ""),
                "end_date": temporal.get("end_date", ""),
                "dataset_id": dataset.get("short_name", "")
            })

        # 8. Spatial Location - Extract from location coordinates
        spatial = dataset.get("spatial_extent", {})
        if spatial:
            horizontal_domain = spatial.get("horizontal_spatial_domain", {})
            geometry = horizontal_domain.get("geometry", {})
            bounding_rectangles = geometry.get("bounding_rectangles", [])

            for bbox in bounding_rectangles:
                if bbox:  # Check if bbox has actual values
                    location_key = f"{bbox.get('west', 0)}_{bbox.get('south', 0)}_{bbox.get('east', 0)}_{bbox.get('north', 0)}"
                    if location_key not in seen_locations and bbox.get('west') != bbox.get('east'):  # Avoid empty bboxes
                        # Create a more descriptive location name based on coordinates
                        location_name = generate_location_name(bbox)
                        classes_data["Location"].append({
                            "name": location_name,
                            "bounding_box": {
                                "west": bbox.get("west", 0),
                                "south": bbox.get("south", 0),
                                "east": bbox.get("east", 0),
                                "north": bbox.get("north", 0)
                            },
                            "coordinate_system": geometry.get("coordinate_system", "GEOGRAPHIC")
                        })
                        seen_locations.add(location_key)

        # 9. Related URLs - Extract from links with proper categorization
        link_data = dataset.get("links", [])
        if isinstance(link_data, list):
            for link in link_data:
                if isinstance(link, dict) and link.get("href"):
                    classes_data["RelatedUrl"].append({
                        "url": link.get("href", ""),
                        "description": link.get("title", ""),
                        "type": link.get("rel", ""),
                        "mime_type": ""
                    })

        # 10. Variables - Extract from dataTypes if available
        data_types = dataset.get("data_types", [])
        for data_type in data_types:
            if isinstance(data_type, dict):
                var_name = data_type.get("name", data_type.get("id", ""))
                if var_name:
                    classes_data["Variable"].append({
                        "name": var_name,
                        "description": data_type.get("description", data_type.get("name", "")),
                        "units": data_type.get("units", ""),
                        "standard_name": data_type.get("standard_name", ""),
                        "long_name": data_type.get("description", data_type.get("name", ""))
                    })

        # 11. Contacts - Extract from people field
        people = dataset.get("people", [])
        for person in people:
            if isinstance(person, dict):
                person_key = f"{person.get('name', '')}_{person.get('organization', {}).get('name', '')}"
                if person_key not in seen_contacts:
                    classes_data["Contact"].append({
                        "name": person.get("name", ""),
                        "role": person.get("role", ""),
                        "organization": person.get("organization", {}).get("name", ""),
                        "email": "",  # Not provided in OneStop
                        "phone": "",  # Not provided in OneStop
                        "address": ""  # Not provided in OneStop
                    })
                    seen_contacts.add(person_key)

        # 12. Processing Level
        if dataset.get("processing_level_id"):
            classes_data["ProcessingLevel"].append({
                "id": dataset.get("processing_level_id", ""),
                "description": get_processing_level_description(dataset.get("processing_level_id", ""))
            })

        # 13. Coordinate System
        coord_system = spatial.get("horizontal_spatial_domain", {}).get("geometry", {}).get("coordinate_system", "")
        if coord_system:
            classes_data["CoordinateSystem"].append({
                "name": coord_system,
                "description": f"Coordinate system: {coord_system}"
            })

    return classes_data

def get_mime_type(format_name):
    """Get MIME type for data format."""
    mime_types = {
        "JSON": "application/json",
        "CSV": "text/csv",
        "NetCDF": "application/netcdf",
        "XML": "application/xml",
        "PDF": "application/pdf"
    }
    return mime_types.get(format_name, "application/octet-stream")

def get_processing_level_description(level_id):
    """Get description for processing level."""
    descriptions = {
        "Level 0": "Raw instrument data",
        "Level 1": "Calibrated and geolocated data",
        "Level 2": "Derived geophysical variables",
        "Level 3": "Variables mapped on uniform space-time grid",
        "Level 4": "Model output or results from analyses"
    }
    return descriptions.get(level_id, "Processed data")

def generate_location_name(bbox):
    """Generate a descriptive location name from bounding box coordinates."""
    if not bbox or not all(key in bbox for key in ["west", "south", "east", "north"]):
        return "Unknown Location"

    # Simple geographic naming based on coordinates
    west, south, east, north = bbox["west"], bbox["south"], bbox["east"], bbox["north"]

    # Determine hemispheres
    ns = "North" if north >= 0 else "South"
    ew = "East" if east >= 0 else "West"

    # Create descriptive name
    if abs(east - west) > 180 or abs(north - south) > 90:
        return "Global Coverage"
    elif abs(east - west) > 60 or abs(north - south) > 45:
        return f"Regional Coverage ({ns}-{ew})"
    else:
        return f"Local Area ({abs(north):.1f}°{ns[0]}, {abs(east):.1f}°{ew[0]})"

def get_mime_type_from_protocol(protocol):
    """Get MIME type from protocol string."""
    protocol_mime_map = {
        "OPeNDAP:OPeNDAP": "application/x-netcdf",
        "OGC:WMS": "image/png",
        "UNIDATA:NCSS": "application/x-netcdf",
        "file": "application/octet-stream",
        "WWW:LINK": "text/html"
    }
    return protocol_mime_map.get(protocol, "application/octet-stream")

def extract_climate_variables_from_text(text):
    """Extract climate variables from text descriptions."""
    if not text:
        return []

    text_lower = text.lower()
    climate_vars = []

    # Common climate variables
    variable_patterns = [
        "sea surface temperature", "sst", "temperature", "temp",
        "salinity", "chlorophyll", "wind speed", "wind direction",
        "current", "velocity", "ssh", "sea surface height",
        "precipitation", "pressure", "humidity", "radiation",
        "ice concentration", "ice thickness", "albedo",
        "ocean color", "turbidity", "dissolved oxygen"
    ]

    for pattern in variable_patterns:
        if pattern in text_lower:
            # Convert to proper case
            var_name = pattern.replace("_", " ").title()
            if var_name not in climate_vars:
                climate_vars.append(var_name)

    return climate_vars[:10]  # Limit to avoid too many variables

def get_climate_variable_units(var_name):
    """Get standard units for climate variables."""
    var_lower = var_name.lower()
    unit_map = {
        "temperature": "degrees_C",
        "sea surface temperature": "degrees_C",
        "sst": "degrees_C",
        "salinity": "psu",
        "wind speed": "m/s",
        "current": "m/s",
        "velocity": "m/s",
        "pressure": "Pa",
        "precipitation": "mm",
        "chlorophyll": "mg/m^3",
        "ssh": "m",
        "sea surface height": "m"
    }

    for key, unit in unit_map.items():
        if key in var_lower:
            return unit

    return ""

def extract_climate_keywords_from_text(text):
    """Extract climate science keywords from text."""
    if not text:
        return []

    text_lower = text.lower()
    keywords = []

    # Climate science keywords
    keyword_patterns = [
        ("ocean", "OCEANS"),
        ("atmosphere", "ATMOSPHERE"),
        ("temperature", "TEMPERATURE"),
        ("wind", "WINDS"),
        ("current", "OCEAN CURRENTS"),
        ("salinity", "SALINITY"),
        ("chlorophyll", "OCEAN CHEMISTRY"),
        ("sea ice", "SEA ICE"),
        ("precipitation", "PRECIPITATION"),
        ("radar", "RADAR"),
        ("satellite", "REMOTE SENSING"),
        ("forecast", "WEATHER FORECASTING"),
        ("model", "NUMERICAL MODELING")
    ]

    for pattern, keyword in keyword_patterns:
        if pattern in text_lower:
            if keyword not in keywords:
                keywords.append(keyword)

    return keywords[:5]  # Limit keywords

def get_climate_topic(keyword):
    """Get climate topic for science keyword."""
    keyword_lower = keyword.lower()

    if any(term in keyword_lower for term in ["ocean", "current", "salinity", "ssh"]):
        return "OCEANS"
    elif any(term in keyword_lower for term in ["atmosphere", "wind", "pressure"]):
        return "ATMOSPHERE"
    elif any(term in keyword_lower for term in ["temperature", "thermal"]):
        return "TEMPERATURE"
    elif any(term in keyword_lower for term in ["ice", "snow"]):
        return "CRYOSPHERE"
    elif any(term in keyword_lower for term in ["radar", "satellite", "remote"]):
        return "REMOTE SENSING"
    else:
        return "EARTH SCIENCE"

##############################
#  MAIN FUNCTION
##############################
def main():
    """Main function to demonstrate comprehensive NOAA data extraction."""
    if not NOAA_TOKEN:
        logger.warning("NOAA_TOKEN not set. Some APIs may have limited access.")

    # Create output directory
    os.makedirs("noaa_json", exist_ok=True)

    # Test comprehensive extraction with raw OneStop data first
    logger.info("Fetching ALL OneStop datasets...")
    raw_onestop = fetch_raw_onestop_data()  # No limit - fetch all

    if raw_onestop:
        # Save raw OneStop API response
        raw_onestop_file = "noaa_json/noaa_raw_onestop.json"
        with open(raw_onestop_file, 'w', encoding='utf-8') as f:
            json.dump(raw_onestop, f, indent=2, ensure_ascii=False)
        logger.info(f"Raw OneStop API response saved to {raw_onestop_file}")

        # Transform OneStop collections using correct format
        comprehensive_data = transform_onestop_collections_to_classes(raw_onestop)

        # Enhance with NASA CMR functions (if needed)
        # comprehensive_data = enhance_noaa_extraction_with_nasa_functions(comprehensive_data, raw_onestop)

        # Save comprehensive results
        comp_file = "noaa_json/noaa_comprehensive_data.json"
        with open(comp_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Comprehensive NOAA data with NASA enhancement saved to {comp_file}")

        # Print comprehensive summary
        print("\n=== COMPREHENSIVE NOAA Extraction Summary ===")
        total_items = 0
        for class_name, items in comprehensive_data.items():
            if items:  # Only show non-empty classes
                count = len(items)
                total_items += count
                print(f"{class_name}: {count} items")

                # Show sample for key classes
                if class_name in ["Variable", "Contact", "ScienceKeyword"] and count > 0:
                    sample = items[0]
                    if class_name == "Variable":
                        print(f"  Sample: {sample.get('name', 'N/A')} (ID: {sample.get('variable_id', 'N/A')})")
                    elif class_name == "Contact":
                        print(f"  Sample: {sample.get('name', 'N/A')} ({sample.get('role', 'N/A')})")
                    elif class_name == "ScienceKeyword":
                        print(f"  Sample: {sample.get('full_path', 'N/A')}")

        print(f"\nTotal extracted items: {total_items}")
        return comprehensive_data

    else:
        logger.error("Failed to fetch raw OneStop data")
        return None

def fetch_raw_onestop_data_by_spatial(max_datasets=None):
    """
    Fetch raw OneStop data using spatial/geographic filtering to bypass 10,000 record pagination limit.
    This strategy divides the world into geographic regions to access more of the 109,791 available collections.
    """
    all_datasets = []

    # Geographic regions covering the entire globe - designed to stay under 10,000 per region
    # Using bounding boxes: [west, south, east, north] format
    spatial_regions = [
        {"name": "North Pacific", "bbox": "120,-60,180,60"},          # North Pacific Ocean
        {"name": "Central Pacific", "bbox": "-180,-60,-120,60"},      # Central Pacific
        {"name": "Eastern Pacific", "bbox": "-120,-60,-60,60"},       # Eastern Pacific
        {"name": "North Atlantic", "bbox": "-60,-30,0,70"},           # North Atlantic
        {"name": "South Atlantic", "bbox": "-60,-60,20,-30"},         # South Atlantic
        {"name": "Indian Ocean", "bbox": "20,-60,120,30"},            # Indian Ocean
        {"name": "Arctic Ocean", "bbox": "-180,60,180,90"},           # Arctic Ocean
        {"name": "Antarctic", "bbox": "-180,-90,180,-60"},            # Antarctic region
        {"name": "North America", "bbox": "-170,30,-50,75"},          # North America
        {"name": "South America", "bbox": "-90,-60,-30,15"},          # South America
        {"name": "Europe", "bbox": "-15,35,40,75"},                   # Europe
        {"name": "Africa", "bbox": "-20,-35,55,40"},                  # Africa
        {"name": "Asia", "bbox": "40,0,180,75"},                      # Asia
        {"name": "Australia_Oceania", "bbox": "110,-50,180,-10"},     # Australia/Oceania
        {"name": "Global_Coverage", "bbox": "-180,-90,180,90"},       # Global datasets
    ]

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json"

    # Track unique collections to avoid duplicates
    seen_ids = set()

    for i, region in enumerate(spatial_regions, 1):
        logger.info(f"Fetching region {i}/{len(spatial_regions)}: {region['name']}")

        region_datasets = fetch_onestop_spatial_region(url, headers, region)

        # Add unique collections from this region
        new_collections = []
        for dataset in region_datasets:
            dataset_id = dataset.get("id")
            if dataset_id and dataset_id not in seen_ids:
                new_collections.append(dataset)
                seen_ids.add(dataset_id)

        all_datasets.extend(new_collections)
        logger.info(f"Region {region['name']}: fetched {len(region_datasets)}, added {len(new_collections)} unique. Total unique: {len(all_datasets)}")

        time.sleep(1)  # Delay between regions to be respectful to API

    logger.info(f"Spatial filtering complete. Total unique collections: {len(all_datasets)}")
    return all_datasets

def fetch_onestop_spatial_region(url, headers, region):
    """Fetch OneStop collections for a specific spatial region."""
    region_datasets = []
    page_size = 100
    offset = 0

    while True:
        rate_limit()

        # Search with spatial filter - OneStop API uses URL parameters for bounding box
        search_body = {
            "page": {
                "max": page_size,
                "offset": offset
            }
        }

        # Add spatial parameters as URL query parameters
        # Format: bbox=west,south,east,north
        spatial_params = {
            "bbox": region["bbox"]
        }

        try:
            # Add spatial parameters to the URL
            response = requests.post(url, headers=headers, json=search_body, params=spatial_params, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"]:
                page_results = data["data"]
                region_datasets.extend(page_results)

                total_count = data.get("meta", {}).get("total", "unknown")
                logger.info(f"  {region['name']} offset {offset}: {len(page_results)} collections, region total: {len(region_datasets)}, available: {total_count}")

                # Check if we're done with this region
                if len(page_results) < page_size:
                    logger.info(f"  Finished region {region['name']}: collected {len(region_datasets)} collections")
                    break

                offset += page_size
                time.sleep(0.1)

            else:
                logger.info(f"  No more results for region {region['name']}")
                break

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                logger.warning(f"  500 error for region {region['name']} at offset {offset}. Collected {len(region_datasets)} so far.")
                break
            else:
                logger.error(f"  HTTP error {e.response.status_code} for region {region['name']}: {e}")
                break
        except Exception as e:
            logger.error(f"  Error fetching region {region['name']}: {e}")
            break

    return region_datasets

def fetch_raw_onestop_data_scroll(max_datasets=None):
    """
    Fetch raw OneStop data using Elasticsearch scroll API to access all 109,791 collections.
    This approach bypasses pagination limits and retrieves the complete dataset efficiently.
    """
    all_datasets = []

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json"

    # Initial request with scroll parameter - use OneStop format
    initial_body = {
        "page": {
            "max": 1000,  # Large batch size for efficiency
            "offset": 0
        }
    }

    logger.info("Testing if OneStop API supports scroll-like functionality...")

    try:
        # Test initial request to see if OneStop returns scroll_id
        rate_limit()
        response = requests.post(url, headers=headers, json=initial_body, timeout=120)
        response.raise_for_status()
        data = response.json()

        # Extract data and scroll_id from initial response
        if "data" in data and data["data"]:
            batch_results = data["data"]
            all_datasets.extend(batch_results)

            total_available = data.get("meta", {}).get("total", "unknown")
            logger.info(f"Initial scroll batch: {len(batch_results)} collections, total available: {total_available}")

            # Check if there's a scroll_id for subsequent requests
            scroll_id = data.get("_scroll_id") or data.get("scrollId")

            if scroll_id:
                # Continue with scroll requests
                scroll_url = f"{NOAA_ONESTOP_SEARCH_URL}/_search/scroll"

                while True:
                    rate_limit()

                    # Subsequent scroll requests
                    scroll_body = {
                        "scroll": "5m",
                        "scroll_id": scroll_id
                    }

                    try:
                        response = requests.post(scroll_url, headers=headers, json=scroll_body, timeout=120)
                        response.raise_for_status()
                        data = response.json()

                        if "data" in data and data["data"]:
                            batch_results = data["data"]
                            all_datasets.extend(batch_results)

                            logger.info(f"Scroll batch: {len(batch_results)} collections, total fetched: {len(all_datasets)}")

                            # Get new scroll_id for next request
                            scroll_id = data.get("_scroll_id") or data.get("scrollId")

                            # If no more results, break
                            if len(batch_results) == 0:
                                logger.info("No more results from scroll API")
                                break

                        else:
                            logger.info("No more data from scroll API")
                            break

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Error in scroll request: {e}")
                        break
            else:
                logger.info("No scroll_id found - API may not support scroll")

        else:
            logger.warning("No data in initial scroll response")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error in initial scroll request: {e}")
        return []

    logger.info(f"Scroll API complete. Total collections fetched: {len(all_datasets)}")
    return all_datasets

def fetch_raw_onestop_data_from_size(max_datasets=None):
    """
    Fetch raw OneStop data using proper from/size pagination to access all collections.
    This approach uses Elasticsearch-style pagination with larger offsets.
    """
    all_datasets = []

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json"

    batch_size = 1000  # Larger batch size
    from_offset = 0
    max_offset = 100000  # Try much higher offsets

    logger.info("Starting from/size pagination to fetch all OneStop collections...")

    while from_offset < max_offset:
        rate_limit()

        # Use OneStop pagination format
        search_body = {
            "page": {
                "max": batch_size,
                "offset": from_offset
            }
        }

        try:
            response = requests.post(url, headers=headers, json=search_body, timeout=120)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"]:
                batch_results = data["data"]
                all_datasets.extend(batch_results)

                total_available = data.get("meta", {}).get("total", "unknown")
                logger.info(f"From/size batch offset {from_offset}: {len(batch_results)} collections, total fetched: {len(all_datasets)}, available: {total_available}")

                # If we got fewer results than requested, we've reached the end
                if len(batch_results) < batch_size:
                    logger.info(f"Reached end of results at offset {from_offset}")
                    break

                from_offset += batch_size
                time.sleep(0.2)  # Longer delay for large requests

            else:
                logger.info(f"No more results at offset {from_offset}")
                break

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                logger.warning(f"500 error at offset {from_offset} - may have hit server limit")
                break
            else:
                logger.error(f"HTTP error {e.response.status_code} at offset {from_offset}: {e}")
                break
        except Exception as e:
            logger.error(f"Error at offset {from_offset}: {e}")
            break

    logger.info(f"From/size pagination complete. Total collections fetched: {len(all_datasets)}")
    return all_datasets

def fetch_raw_onestop_data_large_batches(max_datasets=None):
    """
    Try to fetch more data using larger batch sizes and systematic offset testing.
    """
    all_datasets = []

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json"

    # Try different batch sizes and systematic offsets
    batch_strategies = [
        {"size": 1000, "max_offset": 200000},  # Large batches, high offset
        {"size": 500, "max_offset": 200000},   # Medium batches, high offset
        {"size": 100, "max_offset": 200000},   # Small batches, high offset
    ]

    for strategy in batch_strategies:
        logger.info(f"Trying batch size {strategy['size']} with max offset {strategy['max_offset']}")

        batch_size = strategy["size"]
        max_offset = strategy["max_offset"]
        from_offset = 0

        strategy_datasets = []

        while from_offset < max_offset:
            rate_limit()

            search_body = {
                "page": {
                    "max": batch_size,
                    "offset": from_offset
                }
            }

            try:
                response = requests.post(url, headers=headers, json=search_body, timeout=120)
                response.raise_for_status()
                data = response.json()

                if "data" in data and data["data"]:
                    batch_results = data["data"]
                    strategy_datasets.extend(batch_results)

                    total_available = data.get("meta", {}).get("total", "unknown")
                    logger.info(f"  Batch size {batch_size}, offset {from_offset}: {len(batch_results)} collections, strategy total: {len(strategy_datasets)}, available: {total_available}")

                    # If we got fewer results than requested, we've reached the end
                    if len(batch_results) < batch_size:
                        logger.info(f"  Reached end of results at offset {from_offset} for batch size {batch_size}")
                        break

                    from_offset += batch_size
                    time.sleep(0.1)

                else:
                    logger.info(f"  No more results at offset {from_offset} for batch size {batch_size}")
                    break

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 500 and from_offset >= 10000:
                    logger.info(f"  Hit 500 error at offset {from_offset} - this might be the API limit")
                    break
                else:
                    logger.error(f"  HTTP error {e.response.status_code} at offset {from_offset}: {e}")
                    break
            except Exception as e:
                logger.error(f"  Error at offset {from_offset}: {e}")
                break

        logger.info(f"Strategy batch size {batch_size} complete: {len(strategy_datasets)} collections")

        # If this strategy got more data, use it
        if len(strategy_datasets) > len(all_datasets):
            all_datasets = strategy_datasets
            logger.info(f"Strategy with batch size {batch_size} gave the most data: {len(all_datasets)} collections")

        # If we got significantly more than 10,000, we can stop
        if len(all_datasets) > 15000:
            logger.info(f"Got {len(all_datasets)} collections - stopping here")
            break

    return all_datasets

def fetch_raw_onestop_data_multiple_queries(max_datasets=None):
    """
    Fetch OneStop data using multiple different query strategies to get more unique records.
    Since search_after doesn't work, use different search terms and filters.
    """
    all_datasets = []
    seen_ids = set()

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json"

    # Different query strategies to get different subsets of data
    query_strategies = [
        # 1. Get all data (default)
        {"name": "all_data", "body": {"page": {"max": 1000, "offset": 0}}},

        # 2. Query by different text terms
        {"name": "ocean_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "ocean"}]}},
        {"name": "climate_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "climate"}]}},
        {"name": "atmosphere_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "atmosphere"}]}},
        {"name": "satellite_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "satellite"}]}},
        {"name": "temperature_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "temperature"}]}},
        {"name": "precipitation_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "precipitation"}]}},
        {"name": "model_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "model"}]}},
        {"name": "forecast_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "forecast"}]}},
        {"name": "historical_data", "body": {"page": {"max": 1000, "offset": 0}, "queries": [{"type": "queryText", "value": "historical"}]}},

        # 3. Try different offset strategies with smaller batches
        {"name": "offset_batch_1", "body": {"page": {"max": 500, "offset": 0}}},
        {"name": "offset_batch_2", "body": {"page": {"max": 500, "offset": 500}}},
        {"name": "offset_batch_3", "body": {"page": {"max": 500, "offset": 1000}}},
        {"name": "offset_batch_4", "body": {"page": {"max": 500, "offset": 2000}}},
        {"name": "offset_batch_5", "body": {"page": {"max": 500, "offset": 4000}}},
        {"name": "offset_batch_6", "body": {"page": {"max": 500, "offset": 6000}}},
        {"name": "offset_batch_7", "body": {"page": {"max": 500, "offset": 8000}}},
    ]

    logger.info("Using multiple query strategies to get diverse datasets...")

    for strategy in query_strategies:
        logger.info(f"Trying strategy: {strategy['name']}")

        strategy_datasets = []

        # For each strategy, paginate through all available results up to 10K limit
        offset = strategy["body"]["page"]["offset"]
        max_size = strategy["body"]["page"]["max"]

        while offset < 10000:  # Stay within OneStop limit
            rate_limit()

            # Update the request body with current offset
            request_body = strategy["body"].copy()
            request_body["page"]["offset"] = offset

            try:
                response = requests.post(url, headers=headers, json=request_body, timeout=120)
                response.raise_for_status()
                data = response.json()

                if "data" in data and data["data"]:
                    batch_results = data["data"]
                    strategy_datasets.extend(batch_results)

                    total_available = data.get("meta", {}).get("total", "unknown")
                    logger.info(f"  {strategy['name']} offset {offset}: {len(batch_results)} collections, strategy total: {len(strategy_datasets)}, available: {total_available}")

                    # If we got fewer results than requested, we've reached the end for this strategy
                    if len(batch_results) < max_size:
                        logger.info(f"  Strategy {strategy['name']} complete at offset {offset}")
                        break

                    offset += max_size
                    time.sleep(0.1)

                else:
                    logger.info(f"  No more results for strategy {strategy['name']} at offset {offset}")
                    break

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 500 and offset >= 10000:
                    logger.info(f"  Hit 500 error at offset {offset} for strategy {strategy['name']} - expected limit")
                    break
                else:
                    logger.error(f"  HTTP error {e.response.status_code} for strategy {strategy['name']}: {e}")
                    break
            except Exception as e:
                logger.error(f"  Error for strategy {strategy['name']}: {e}")
                break

        # Add unique collections from this strategy
        new_collections = []
        for dataset in strategy_datasets:
            dataset_id = dataset.get("id")
            if dataset_id and dataset_id not in seen_ids:
                new_collections.append(dataset)
                seen_ids.add(dataset_id)

        all_datasets.extend(new_collections)
        logger.info(f"Strategy {strategy['name']}: fetched {len(strategy_datasets)}, added {len(new_collections)} unique. Total unique: {len(all_datasets)}")

        time.sleep(1)  # Delay between strategies

    logger.info(f"Multiple query strategies complete. Total unique collections: {len(all_datasets)}")
    return all_datasets

def fetch_raw_onestop_data_pit(max_datasets=None):
    """
    Fetch OneStop data using Point-in-Time (PIT) for consistent pagination.
    This ensures consistent results even if the index is updated during pagination.
    """
    all_datasets = []

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()
    headers["Content-Type"] = "application/json"

    batch_size = 1000

    logger.info("Attempting to use Point-in-Time (PIT) for consistent pagination...")

    # Try to create a Point-in-Time
    try:
        pit_url = f"{NOAA_ONESTOP_SEARCH_URL}/_pit"
        pit_response = requests.post(pit_url, headers=headers, json={"keep_alive": "5m"}, timeout=60)

        if pit_response.status_code == 200:
            pit_data = pit_response.json()
            pit_id = pit_data.get("id")

            if pit_id:
                logger.info(f"Created PIT: {pit_id}")

                # Use PIT with search_after
                search_after = None
                page_count = 0
                max_pages = 200

                while page_count < max_pages:
                    rate_limit()

                    search_body = {
                        "size": batch_size,
                        "pit": {
                            "id": pit_id,
                            "keep_alive": "5m"
                        },
                        "sort": [{"_id": "asc"}]
                    }

                    if search_after:
                        search_body["search_after"] = search_after

                    response = requests.post(f"{NOAA_ONESTOP_SEARCH_URL}/_search",
                                           headers=headers, json=search_body, timeout=120)
                    response.raise_for_status()
                    data = response.json()

                    hits = data.get("hits", {}).get("hits", [])
                    if not hits:
                        break

                    # Convert to OneStop format
                    batch_results = []
                    for hit in hits:
                        if "_source" in hit:
                            batch_results.append(hit["_source"])

                    all_datasets.extend(batch_results)
                    logger.info(f"PIT page {page_count + 1}: {len(batch_results)} collections, total: {len(all_datasets)}")

                    if len(hits) < batch_size:
                        break

                    # Get search_after from last hit
                    search_after = hits[-1]["sort"]
                    page_count += 1

                # Close PIT
                try:
                    close_pit_response = requests.delete(f"{NOAA_ONESTOP_SEARCH_URL}/_pit",
                                                       headers=headers, json={"id": pit_id}, timeout=60)
                    logger.info("PIT closed successfully")
                except:
                    logger.warning("Failed to close PIT - it will expire automatically")

            else:
                logger.warning("No PIT ID returned")
        else:
            logger.info(f"PIT not supported (status {pit_response.status_code})")

    except Exception as e:
        logger.info(f"PIT not available: {e}")

    logger.info(f"PIT pagination fetched: {len(all_datasets)} collections")
    return all_datasets

def fetch_raw_onestop_data(max_datasets=None):
    """Fetch raw OneStop data using multiple query strategies to get more unique records."""
    logger.info("Using multiple query strategies to access more of the 109,000+ OneStop collections...")

    # Try multiple different queries to get different subsets of data
    multi_query_data = fetch_raw_onestop_data_multiple_queries(max_datasets)
    if len(multi_query_data) > 10000:
        logger.info(f"Multiple query strategy successful: {len(multi_query_data)} collections")
        return multi_query_data

    # Fall back to spatial filtering if multi-query doesn't get more data
    logger.info("Multiple queries didn't get more data, falling back to spatial filtering...")
    return fetch_raw_onestop_data_by_spatial(max_datasets)

def fetch_raw_onestop_data_legacy(max_datasets=None):
    """Legacy OneStop fetch function (original pagination method)."""
    all_datasets = []
    page_size = 100
    offset = 0

    url = f"{NOAA_ONESTOP_SEARCH_URL}/collection"
    headers = HEADERS.copy()

    # Try different strategies if we hit pagination limits
    strategies = [
        {"name": "default", "sort": None},
        {"name": "by_title", "sort": [{"field": "title", "order": "asc"}]},
        {"name": "by_date", "sort": [{"field": "beginDate", "order": "desc"}]},
    ]

    current_strategy = 0

    while True:  # Unlimited pagination
        rate_limit()

        # OneStop requires POST with JSON body
        search_body = {
            "page": {
                "max": page_size,
                "offset": offset
            }
        }

        # Add sorting if using alternative strategy
        if current_strategy < len(strategies) and strategies[current_strategy]["sort"]:
            search_body["sort"] = strategies[current_strategy]["sort"]

        headers["Content-Type"] = "application/json"

        try:
            response = requests.post(url, headers=headers, json=search_body, timeout=60)
            response.raise_for_status()
            data = response.json()

            if "data" in data and data["data"]:
                page_results = data["data"]
                all_datasets.extend(page_results)

                total_count = data.get("meta", {}).get("total", "unknown")
                logger.info(f"OneStop raw data page offset {offset}: fetched {len(page_results)} collections, total: {len(all_datasets)}, available: {total_count}")

                # Stop if we got fewer results than requested (last page)
                if len(page_results) < page_size:
                    logger.info("Reached last page of OneStop results")
                    break

                # Continue to next page - no max limit check
                offset += page_size
                time.sleep(0.1)

            else:
                logger.info(f"No more results at offset {offset}")
                break

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 500:
                logger.warning(f"OneStop API 500 error at offset {offset} - possible pagination limit. Total collected: {len(all_datasets)}")
                logger.info("Attempting different pagination strategies...")

                # Try different strategies to bypass pagination limits
                if current_strategy < len(strategies) - 1:
                    current_strategy += 1
                    offset = 0  # Reset offset for new strategy
                    page_size = 100  # Reset page size
                    logger.info(f"Switching to strategy '{strategies[current_strategy]['name']}' and restarting from offset 0...")
                    time.sleep(2)
                    continue
                elif page_size > 50:
                    page_size = 50
                    logger.info(f"Reducing page size to {page_size} and continuing...")
                    time.sleep(2)  # Longer delay
                    continue
                else:
                    logger.warning(f"API limit reached at offset {offset} after trying all strategies. Collected {len(all_datasets)} out of {total_count} available collections")
                    break
            else:
                logger.error(f"OneStop API HTTP error {e.response.status_code} at offset {offset}: {e}")
                break
        except Exception as e:
            logger.error(f"Error fetching OneStop raw data at offset {offset}: {e}")
            break

    # Return all datasets - no limiting
    logger.info(f"Fetched {len(all_datasets)} total raw OneStop datasets")
    return all_datasets

def transform_onestop_collections_to_classes(onestop_collections):
    """
    Transform OneStop collection responses to knowledge graph classes.
    Handles the correct OneStop API format: {type: "collection", id: "...", attributes: {...}}
    """
    classes_data = {
        "Dataset": [],
        "DataCategory": [],
        "DataFormat": [],
        "CoordinateSystem": [],
        "Location": [],
        "Station": [],
        "Organization": [],
        "Platform": [],
        "Consortium": [],
        "TemporalExtent": [],
        "Variable": [],
        "CESMVariable": [],  # Empty for NOAA (CESM is NASA-specific)
        "Component": [],    # Empty for NOAA
        "Contact": [],
        "Project": [],
        "RelatedUrl": [],
        "SpatialResolution": [],
        "TemporalResolution": [],
        "Granule": [],
        "Instrument": [],
        "ScienceKeyword": [],
        "ProcessingLevel": [],
        "Relationship": []   # Added to match NASA CMR structure
    }

    # Tracking sets to avoid duplicates
    seen_data_formats = set()
    seen_platforms = set()
    seen_organizations = set()
    seen_locations = set()
    seen_science_keywords = set()
    seen_contacts = set()
    seen_data_categories = set()
    seen_variables = set()

    for i, collection in enumerate(onestop_collections):
        if collection.get("type") != "collection":
            continue  # Skip non-collection items

        # Extract basic info
        collection_id = collection.get("id", f"collection_{i}")
        attributes = collection.get("attributes", {})

        # 1. Dataset
        dataset_entry = {
            "short_name": collection_id,
            "title": attributes.get("title", ""),
            "dataset_id": collection_id,
            "entry_id": f"onestop_{collection_id}",
            "version_id": "1.0",
            "processing_level_id": "",
            "online_access_flag": True,
            "browse_flag": bool(attributes.get("thumbnail")),
            "data_center": "NOAA_ONESTOP",
            "archive_center": "NOAA",
            "doi": "",
            "doi_authority": "",
            "collection_data_type": "SCIENCE_QUALITY",
            "data_set_language": "eng",
            "native_id": collection_id,
            "granule_count": 0,
            "day_night_flag": "",
            "cloud_cover": "",
            "description": attributes.get("description", ""),
            "keywords": attributes.get("keywords", []),
            "begin_date": attributes.get("beginDate", ""),
            "end_date": attributes.get("endDate", "")
        }
        classes_data["Dataset"].append(dataset_entry)

        # Extract key attributes for processing
        title = attributes.get("title", "")
        description = attributes.get("description", "")

        # Create data category from title
        if title and title not in seen_data_categories:
            category_name = title.strip()
            if len(category_name) > 100:
                category_name = category_name[:97] + "..."

            classes_data["DataCategory"].append({
                "name": category_name,
                "description": f"Dataset category: {title}",
                "type": "DATASET_TITLE"
            })
            seen_data_categories.add(title)

        # 2. Temporal Extent
        begin_date = attributes.get("beginDate", "")
        end_date = attributes.get("endDate", "")
        if begin_date or end_date:
            classes_data["TemporalExtent"].append({
                "start_date": begin_date,
                "end_date": end_date,
                "dataset_id": collection_id
            })

        # 3. Spatial Location from spatialBounding
        spatial_bounding = attributes.get("spatialBounding", {})
        if spatial_bounding and spatial_bounding.get("coordinates"):
            try:
                coords = spatial_bounding["coordinates"]
                if spatial_bounding.get("type") == "Polygon" and coords:
                    # Extract bounding box from polygon coordinates
                    polygon_coords = coords[0] if isinstance(coords[0][0], list) else coords
                    lons = [coord[0] for coord in polygon_coords]
                    lats = [coord[1] for coord in polygon_coords]

                    bbox = {
                        "west": min(lons),
                        "south": min(lats),
                        "east": max(lons),
                        "north": max(lats)
                    }

                    location_key = f"{bbox['west']}_{bbox['south']}_{bbox['east']}_{bbox['north']}"
                    if location_key not in seen_locations:
                        location_name = generate_location_name(bbox)

                        # Try to get place names using NASA functions
                        place_names = []
                        countries = []
                        scope = "unclassified"
                        try:
                            bbox_str = f"{bbox['south']} {bbox['west']} {bbox['north']} {bbox['east']}"
                            spatial_geom = parse_cmr_spatial(boxes=[bbox_str])
                            if spatial_geom:
                                location_info = classify_location_offline_fast(spatial_geom)
                                if location_info:
                                    place_names = location_info.get("place_names", [])
                                    countries = location_info.get("countries", [])
                                    scope = location_info.get("scope", "unclassified")
                        except Exception as e:
                            pass

                        classes_data["Location"].append({
                            "name": location_name,
                            "bounding_box": bbox,
                            "coordinate_system": "GEOGRAPHIC",
                            "dataset_id": collection_id,
                            "place_names": place_names,
                            "countries": countries,
                            "scope": scope,
                            "nasa_enhanced": bool(place_names or countries)
                        })
                        seen_locations.add(location_key)

            except (IndexError, TypeError, ValueError, KeyError):
                pass  # Skip malformed spatial data

        # 4. Extract Data Formats from serviceLinks protocols
        service_links = attributes.get("serviceLinks", [])
        for service in service_links:
            if isinstance(service, dict):
                service_title = service.get("title", "")
                service_desc = service.get("description", "")

                # Extract data formats from service links
                service_links_list = service.get("links", [])
                for link in service_links_list:
                    if isinstance(link, dict):
                        protocol = link.get("linkProtocol", "")
                        link_name = link.get("linkName", "")

                        # Map protocols to data formats
                        if protocol and protocol not in seen_data_formats:
                            format_name = protocol.split(":")[-1].upper()  # e.g., "OPeNDAP:OPeNDAP" -> "OPeNDAP"
                            classes_data["DataFormat"].append({
                                "format": format_name,
                                "mime_type": get_mime_type_from_protocol(protocol),
                                "description": f"{format_name} format",
                                "dataset_id": collection_id
                            })
                            seen_data_formats.add(protocol)

                # Extract platforms/instruments from service titles
                if service_title and service_title not in seen_platforms:
                    classes_data["Platform"].append({
                        "short_name": service_title.replace(" ", "_")[:50],
                        "long_name": service_title,
                        "type": "Data Service Platform",
                        "dataset_id": collection_id
                    })
                    seen_platforms.add(service_title)

                # Extract organizations from service descriptions
                if "MARACOOS" in service_desc or "RUTGERS" in service_desc.upper():
                    org_name = "Rutgers University Marine and Coastal Sciences"
                    if org_name not in seen_organizations:
                        classes_data["Organization"].append({
                            "short_name": "RUTGERS_MARINE",
                            "long_name": org_name,
                            "type": "DATA_PROVIDER",
                            "dataset_id": collection_id
                        })
                        seen_organizations.add(org_name)

        # 5. Extract Variables from service titles and descriptions
        for service in service_links:
            if isinstance(service, dict):
                service_title = service.get("title", "")
                service_desc = service.get("description", "")

                # Extract climate variables from descriptions
                variables = extract_climate_variables_from_text(service_desc + " " + service_title)
                for var_name in variables:
                    var_key = f"{collection_id}_{var_name}"
                    if var_key not in seen_variables:
                        classes_data["Variable"].append({
                            "name": var_name,
                            "description": f"Climate variable: {var_name}",
                            "units": get_climate_variable_units(var_name),
                            "standard_name": var_name.lower().replace(" ", "_"),
                            "long_name": var_name,
                            "dataset_id": collection_id
                        })
                        seen_variables.add(var_key)

        # 6. Related URLs from links and serviceLinks
        links = attributes.get("links", [])

        # Process regular links
        for link in links:
            if isinstance(link, dict) and link.get("linkUrl"):
                classes_data["RelatedUrl"].append({
                    "url": link["linkUrl"],
                    "description": link.get("linkDescription", link.get("linkName", "")),
                    "url_content_type": link.get("linkFunction", "information"),
                    "type": link.get("linkFunction", "GET DATA"),
                    "dataset_id": collection_id
                })

        # Process service links
        for service in service_links:
            if isinstance(service, dict):
                service_links_list = service.get("links", [])
                for link in service_links_list:
                    if isinstance(link, dict) and link.get("linkUrl"):
                        classes_data["RelatedUrl"].append({
                            "url": link["linkUrl"],
                            "description": link.get("linkDescription", link.get("linkName", "")),
                            "url_content_type": link.get("linkFunction", "download"),
                            "type": link.get("linkFunction", "GET DATA"),
                            "dataset_id": collection_id
                        })

        # 7. Extract Science Keywords from descriptions
        full_text = title + " " + description
        for service in service_links:
            if isinstance(service, dict):
                full_text += " " + service.get("description", "") + " " + service.get("title", "")

        # Create science keywords from climate terms
        climate_keywords = extract_climate_keywords_from_text(full_text)
        for keyword in climate_keywords:
            if keyword not in seen_science_keywords:
                classes_data["ScienceKeyword"].append({
                    "category": "EARTH SCIENCE",
                    "topic": get_climate_topic(keyword),
                    "term": keyword,
                    "variable_level_1": "",
                    "variable_level_2": "",
                    "variable_level_3": "",
                    "full_path": f"EARTH SCIENCE > {get_climate_topic(keyword)} > {keyword}",
                    "dataset_id": collection_id
                })
                seen_science_keywords.add(keyword)

        # 8. Processing Level (basic)
        classes_data["ProcessingLevel"].append({
            "id": "Standard",
            "description": "Standard OneStop collection",
            "dataset_id": collection_id
        })

        # 9. Coordinate System
        if attributes.get("spatialBounding"):
            classes_data["CoordinateSystem"].append({
                "name": "GEOGRAPHIC",
                "description": "Geographic coordinate system (WGS84)",
                "dataset_id": collection_id
            })

    logger.info(f"Transformed {len(onestop_collections)} OneStop collections to knowledge graph classes")
    return classes_data

def enhance_noaa_extraction_with_nasa_functions(classes_data, raw_datasets):
    """
    Enhance NOAA extraction by applying NASA CMR functions to process NOAA field values.
    This reuses NASA logic without hardcoding, processing actual NOAA data.
    """
    logger.info("Enhancing NOAA extraction with NASA CMR functions...")

    # Process each raw dataset with NASA functions
    for i, raw_dataset in enumerate(raw_datasets):
        dataset_id = raw_dataset.get("id", f"dataset_{i}")

        # 1. Enhanced Location Processing with NASA functions
        location = raw_dataset.get("location", {})
        if location.get("coordinates"):
            try:
                coords = location["coordinates"][0]
                if coords and len(coords) >= 4:
                    lons = [coord[0] for coord in coords]
                    lats = [coord[1] for coord in coords]

                    # NASA parse_cmr_spatial expects format: "SouthLat WestLon NorthLat EastLon"
                    south_lat = min(lats)
                    west_lon = min(lons)
                    north_lat = max(lats)
                    east_lon = max(lons)
                    bbox_str = f"{south_lat} {west_lon} {north_lat} {east_lon}"

                    # Use NASA spatial processing on NOAA coordinates
                    spatial_geom = parse_cmr_spatial(boxes=[bbox_str])
                    if spatial_geom:
                        location_info = classify_location_offline_fast(spatial_geom)
                        # Create geographic categories based on location info
                        geo_categories = []
                        if location_info:
                            if location_info.get("countries"):
                                geo_categories.extend([f"Country: {country}" for country in location_info["countries"]])
                            if location_info.get("continents"):
                                geo_categories.extend([f"Continent: {continent}" for continent in location_info["continents"]])
                            if location_info.get("place_names"):
                                geo_categories.extend([f"Region: {place}" for place in location_info["place_names"]])

                        # Add enhanced categories to DataCategory
                        for category in geo_categories:
                            if category:
                                classes_data["DataCategory"].append({
                                    "name": category,
                                    "description": f"NASA-enhanced geographic category: {category}",
                                    "type": "GEOGRAPHIC_NASA",
                                    "dataset_id": dataset_id
                                })

                        # Add enhanced location info to existing locations
                        for loc in classes_data.get("Location", []):
                            if loc.get("dataset_id") == dataset_id:
                                loc["nasa_place_names"] = location_info.get("place_names", [])
                                loc["nasa_countries"] = location_info.get("countries", [])
                                loc["nasa_enhanced"] = True
            except Exception as e:
                logger.debug(f"NASA location enhancement failed for {dataset_id}: {e}")

        # 2. Enhanced Variables with NASA patterns
        data_types = raw_dataset.get("dataTypes", [])
        enhanced_variables = []
        for var in data_types:
            var_name = var.get("name", "")
            if var_name:
                # Apply NASA variable classification to NOAA variables
                nasa_enhanced = apply_nasa_variable_patterns(var_name)
                enhanced_variables.append({
                    **var,
                    "nasa_units": nasa_enhanced["units"],
                    "nasa_cf_name": nasa_enhanced["cf_name"],
                    "nasa_category": nasa_enhanced["category"],
                    "dataset_id": dataset_id
                })

        # Update existing variables with NASA enhancements
        for var in classes_data.get("Variable", []):
            if var.get("dataset_id") == dataset_id:
                for enhanced in enhanced_variables:
                    if var.get("variable_id") == enhanced.get("id"):
                        var.update({
                            "nasa_units": enhanced["nasa_units"],
                            "nasa_cf_name": enhanced["nasa_cf_name"],
                            "nasa_category": enhanced["nasa_category"]
                        })

        # 3. Enhanced Platforms with NASA classification
        obs_types = raw_dataset.get("observationTypes", [])
        for obs in obs_types:
            obs_name = obs.get("name", "")
            if obs_name:
                nasa_platform = apply_nasa_platform_patterns(obs_name)

                # Add NASA-enhanced platform info
                classes_data["Platform"].append({
                    "short_name": f"{obs_name.replace(' ', '_')}_NASA",
                    "long_name": nasa_platform["long_name"],
                    "type": nasa_platform["type"],
                    "nasa_category": nasa_platform["category"],
                    "nasa_instruments": nasa_platform["instruments"],
                    "original_obs_type": obs_name,
                    "dataset_id": dataset_id
                })

                # Add corresponding instruments
                for instrument in nasa_platform["instruments"]:
                    classes_data["Instrument"].append({
                        "short_name": instrument.replace(" ", "_"),
                        "long_name": instrument,
                        "type": nasa_platform["category"],
                        "platform": obs_name,
                        "dataset_id": dataset_id
                    })

        # 4. Enhanced Temporal Resolution with NASA patterns
        frequency = raw_dataset.get("frequency", "")
        if frequency:
            nasa_temporal = apply_nasa_temporal_patterns(frequency)
            classes_data["TemporalResolution"].append({
                "resolution": nasa_temporal["resolution"],
                "nasa_unit": nasa_temporal["unit"],
                "nasa_interval": nasa_temporal["interval"],
                "original_frequency": frequency,
                "dataset_id": dataset_id
            })

    logger.info("NOAA extraction enhanced with NASA CMR functions")
    return classes_data

def apply_nasa_variable_patterns(noaa_var_name):
    """Apply NASA variable classification patterns to NOAA variable names."""
    var_lower = noaa_var_name.lower()

    # NASA-style patterns
    if "temperature" in var_lower:
        return {"units": "kelvin", "cf_name": "air_temperature", "category": "Atmospheric Temperature"}
    elif "pressure" in var_lower:
        return {"units": "Pa", "cf_name": "air_pressure", "category": "Atmospheric Pressure"}
    elif "precipitation" in var_lower:
        return {"units": "mm", "cf_name": "precipitation_amount", "category": "Precipitation"}
    elif "wind" in var_lower:
        return {"units": "m/s", "cf_name": "wind_speed", "category": "Wind"}
    else:
        return {"units": "", "cf_name": "", "category": "General"}

def apply_nasa_platform_patterns(noaa_obs_name):
    """Apply NASA platform classification patterns to NOAA observation types."""
    obs_lower = noaa_obs_name.lower()

    if "satellite" in obs_lower:
        return {
            "long_name": f"Earth Observation Satellites - {noaa_obs_name}",
            "type": "Satellite Platform",
            "category": "Earth Observation Satellites",
            "instruments": ["Multi-spectral Imager", "Radiometer"]
        }
    elif "radar" in obs_lower:
        return {
            "long_name": f"Weather Surveillance Radar - {noaa_obs_name}",
            "type": "Ground-based Radar",
            "category": "Weather Radar",
            "instruments": ["Doppler Radar"]
        }
    elif "land surface" in obs_lower:
        return {
            "long_name": f"Surface Weather Stations - {noaa_obs_name}",
            "type": "Ground-based Station",
            "category": "Surface Stations",
            "instruments": ["Thermometer", "Barometer", "Rain Gauge"]
        }
    else:
        return {
            "long_name": noaa_obs_name,
            "type": "Observation Platform",
            "category": "General",
            "instruments": []
        }

def apply_nasa_temporal_patterns(noaa_frequency):
    """Apply NASA temporal resolution patterns to NOAA frequency values."""
    freq_lower = noaa_frequency.lower()

    if "daily" in freq_lower:
        return {"resolution": "Daily", "unit": "days", "interval": 1}
    elif "hourly" in freq_lower:
        return {"resolution": "Hourly", "unit": "hours", "interval": 1}
    elif "monthly" in freq_lower:
        return {"resolution": "Monthly", "unit": "months", "interval": 1}
    elif "annual" in freq_lower:
        return {"resolution": "Annual", "unit": "years", "interval": 1}
    else:
        return {"resolution": noaa_frequency, "unit": "unknown", "interval": 0}

def main_with_nasa_enhancement():
    """Main function with NASA CMR enhancement."""
    if not NOAA_TOKEN:
        logger.warning("NOAA_TOKEN not set. Some APIs may have limited access.")

    # Create output directory
    os.makedirs("noaa_json", exist_ok=True)

    # Fetch raw OneStop data using multiple query strategies to get more diverse data
    logger.info("Fetching MORE OneStop datasets using multiple query strategies to access diverse subsets...")
    raw_onestop = fetch_raw_onestop_data()  # Uses multiple queries, then spatial as fallback

    if raw_onestop:
        # Save raw OneStop API response with multi-query filename
        raw_onestop_file = "noaa_json/noaa_raw_onestop_multi_query.json"
        with open(raw_onestop_file, 'w', encoding='utf-8') as f:
            json.dump(raw_onestop, f, indent=2, ensure_ascii=False)
        logger.info(f"Raw OneStop API response (multi-query strategy) saved to {raw_onestop_file}")
        logger.info(f"Successfully fetched {len(raw_onestop)} unique collections using diverse query strategies")

        # Basic transformation first using enhanced function
        classes_data = transform_onestop_collections_to_classes(raw_onestop)

        # Save basic transformation
        basic_file = "noaa_json/noaa_basic_transformation_multi_query.json"
        with open(basic_file, 'w', encoding='utf-8') as f:
            json.dump(classes_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Basic transformation saved to {basic_file}")

        # Enhance with NASA functions
        enhanced_data = enhance_noaa_extraction_with_nasa_functions(classes_data, raw_onestop)

        # Save enhanced results
        output_file = "noaa_json/noaa_nasa_enhanced_multi_query.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)

        logger.info(f"NASA-enhanced NOAA data saved to {output_file}")

        # Print summary
        print("\n=== NASA-Enhanced NOAA Extraction Summary ===")
        total_items = 0
        for class_name, items in enhanced_data.items():
            if items:
                count = len(items)
                total_items += count
                print(f"{class_name}: {count} items")

        print(f"\nTotal items: {total_items}")
        print("Enhancement: NASA CMR functions applied to NOAA field values")

        return enhanced_data
    else:
        logger.error("Failed to fetch raw OneStop data")
        return None

if __name__ == "__main__":
    main_with_nasa_enhancement()