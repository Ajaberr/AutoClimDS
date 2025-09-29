#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NASA CMR Data Acquisition Agent

An intelligent agent for discovering, querying, and acquiring NASA CMR climate datasets
from S3 buckets using the knowledge graph. This agent works similarly to the CESM LENS
agent but focuses on NASA's Common Metadata Repository (CMR) data.

Features:
- Query NASA CMR datasets from Neptune knowledge graph
- Discover S3 bucket locations from dataset metadata
- Efficient data loading and processing
- Format auto-detection (NetCDF, HDF5, CSV, etc.)
- Temporal and spatial subsetting
- Data validation and quality checks
"""

import json
import uuid
import os
import sys
import re
import traceback
import warnings
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from http.cookiejar import CookieJar

# Data analysis and processing
import numpy as np
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns

# Climate and geospatial data handling
try:
    import xarray as xr
    import netCDF4
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    print(" xarray not available. NetCDF support limited.")

try:
    import h5py
    HDF5_AVAILABLE = True
except ImportError:
    HDF5_AVAILABLE = False
    print(" h5py not available. HDF5 support limited.")

# AWS and S3 access
import boto3
import s3fs
from botocore.exceptions import ClientError, NoCredentialsError

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.callbacks import CallbackManagerForToolRun

# AWS imports for Neptune connection
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

from dotenv import load_dotenv

# Load .env if present (harmless in prod CI as well)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning, module="xarray")
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

# --- Configuration Constants ---
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
NEPTUNE_REGION = os.getenv("NEPTUNE_REGION", "us-east-2")
GRAPH_ID = os.getenv("GRAPH_ID", "g-xxxx")

# Earthdata Login Configuration
EARTHDATA_USERNAME = os.getenv("EARTHDATA_USERNAME")
EARTHDATA_PASSWORD = os.getenv("EARTHDATA_PASSWORD")
EARTHDATA_LOGIN_URL = "https://urs.earthdata.nasa.gov"  # not secret

# NOAA Climate Data Online (CDO) API Configuration
NOAA_CDO_API_BASE = "https://www.ncei.noaa.gov/cdo-web/api/v2"
NOAA_CDO_TOKEN = os.getenv("NOAA_CDO_TOKEN")
NOAA_CDO_EMAIL = os.getenv("NOAA_CDO_EMAIL", "")
NOAA_CDO_DOMAINS = [
    'www.ncdc.noaa.gov',
    'www.ncei.noaa.gov',
    'data.nodc.noaa.gov',
    'www.noaa.gov',
    'ncei.noaa.gov'
]

# Known Earthdata domains that require authentication (comprehensive list based on 2024 research)
EARTHDATA_DOMAINS = [
    # Core Earthdata Login
    'urs.earthdata.nasa.gov',

    # NSIDC DAAC
    'n5eil01u.ecs.nsidc.org',
    'daacdata.apps.nsidc.org',

    # LAADS DAAC
    'ladsweb.modaps.eosdis.nasa.gov',

    # LP DAAC
    'e4ftl01.cr.usgs.gov',
    'lpdaac.usgs.gov',

    # GES DISC
    'disc.gsfc.nasa.gov',
    'daac.gsfc.nasa.gov',

    # Ocean Biology DAAC
    'oceandata.sci.gsfc.nasa.gov',
    'oceancolor.gsfc.nasa.gov',

    # Physical Oceanography DAAC
    'podaac.jpl.nasa.gov',
    'podaac-www.jpl.nasa.gov',

    # ORNL DAAC
    'data.ornldaac.earthdata.nasa.gov',
    'webmap.ornl.gov',
    'modis.ornl.gov',
    'thredds.daac.ornl.gov',

    # GHRC DAAC
    'ghrcdaac.nasa.gov',
    'ghrc.nsstc.nasa.gov',

    # SEDAC
    'sedac.ciesin.columbia.edu',

    # CDDIS
    'cddis.nasa.gov',

    # ASDC (Atmospheric Science Data Center)
    'asdc.larc.nasa.gov',

    # ASF DAAC
    'vertex.daac.asf.alaska.edu',
    'datapool.asf.alaska.edu'
]

# Earthdata domain patterns for dynamic detection
EARTHDATA_PATTERNS = [
    r'.*\.earthdata\.nasa\.gov$',
    r'.*\.eosdis\.nasa\.gov$',
    r'.*\.gsfc\.nasa\.gov$',
    r'.*\.jpl\.nasa\.gov$',
    r'.*\.nasa\.gov$',
    r'.*\.nsidc\.org$',
    r'.*\.usgs\.gov$',
    r'.*\.ciesin\.columbia\.edu$',
    r'.*\.alaska\.edu$'
]

# AWS Open Data Registry - NASA datasets (Primary Source)
AWS_OPEN_DATA_NASA_BUCKETS = {
    "nasa-nex": {
        "description": "NASA Earth Exchange (NEX) downscaled climate projections",
        "data_types": ["climate", "temperature", "precipitation", "CMIP5"],
        "formats": ["NetCDF", "Zarr"]
    },
    "nasa-power": {
        "description": "NASA POWER solar radiation and meteorological datasets",
        "data_types": ["solar", "radiation", "meteorology", "power"],
        "formats": ["CSV", "JSON", "NetCDF"]
    },
    "nasa-osdr": {
        "description": "NASA Space Biology Open Science Data Repository",
        "data_types": ["biology", "spaceflight", "experiments"],
        "formats": ["CSV", "JSON", "HDF5"]
    },
    "nasa-lambda": {
        "description": "NASA Legacy Archive for Microwave Background Data",
        "data_types": ["cosmic", "microwave", "background", "astrophysics"],
        "formats": ["FITS", "HDF5"]
    },
    "nasa-sdo-ml": {
        "description": "Solar Dynamics Observatory Machine Learning Dataset",
        "data_types": ["solar", "dynamics", "machine learning", "heliophysics"],
        "formats": ["HDF5", "NetCDF"]
    },
    "nasa-terra-fusion": {
        "description": "Terra Fusion datasets",
        "data_types": ["terra", "satellite", "fusion"],
        "formats": ["HDF5", "NetCDF"]
    },
    "modis-pds": {
        "description": "MODIS satellite data",
        "data_types": ["modis", "satellite", "earth observation"],
        "formats": ["HDF4", "NetCDF"]
    },
    "landsat-pds": {
        "description": "Landsat satellite imagery",
        "data_types": ["landsat", "satellite", "imagery"],
        "formats": ["GeoTIFF", "MTL"]
    },
    "sentinel-pds": {
        "description": "Sentinel satellite data",
        "data_types": ["sentinel", "satellite", "earth observation"],
        "formats": ["NetCDF", "GeoTIFF"]
    },
    "noaa-goes16": {
        "description": "GOES-16 weather satellite data",
        "data_types": ["goes", "weather", "satellite"],
        "formats": ["NetCDF"]
    },
    "noaa-goes17": {
        "description": "GOES-17 weather satellite data",
        "data_types": ["goes", "weather", "satellite"],
        "formats": ["NetCDF"]
    }
}

# NASA CMR S3 Bucket patterns (Fallback Source)
NASA_CMR_S3_PATTERNS = [
    "s3://nasa-",
    "s3://gesdisc-",
    "s3://ornldaac-",
    "s3://lpdaac-",
    "s3://nsidc-",
    "s3://podaac-"
]

# Common data formats in NASA CMR
SUPPORTED_FORMATS = {
    '.nc': 'NetCDF',
    '.nc4': 'NetCDF4',
    '.hdf': 'HDF4',
    '.hdf5': 'HDF5',
    '.h5': 'HDF5',
    '.csv': 'CSV',
    '.txt': 'Text',
    '.json': 'JSON',
    '.zarr': 'Zarr'
}

# --- AWS Bedrock LLM (same as other agents) ---
class BedrockClaudeLLM(LLM):
    """LangChain wrapper for AWS Bedrock using the Claude Sonnet model"""
    bedrock: Any = None
    model_id: str = BEDROCK_MODEL_ID

    def __init__(self):
        super().__init__()
        try:
            self.bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
            print(" Bedrock Claude LLM initialized successfully")
        except Exception as e:
            print(f" Bedrock client failed to initialize: {e}. LLM calls will use a fallback.")
            self.bedrock = None

    @property
    def _llm_type(self) -> str:
        return "bedrock_claude_sonnet"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> str:
        if not self.bedrock:
            return f"DUMMY LLM RESPONSE: Bedrock is not configured. The prompt was: {prompt}"

        stop_sequences = stop or ["\nObservation:"]

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": stop_sequences
            })
            response = self.bedrock.invoke_model(modelId=self.model_id, body=body)
            response_body = json.loads(response["body"].read())
            return response_body["content"][0]["text"].strip()
        except Exception as e:
            raise e

# --- CMR Knowledge Graph Connector ---
class CMRKnowledgeGraphConnector:
    """Enhanced connector for NASA CMR dataset discovery via Neptune knowledge graph"""

    def __init__(self):
        self.region = NEPTUNE_REGION
        self.graph_id = GRAPH_ID
        try:
            self.neptune = boto3.client("neptune-graph", region_name=self.region)
            print(f" CMR Knowledge Graph connector initialized for graph: {self.graph_id}")
        except Exception as e:
            print(f" Neptune client failed: {e}")
            self.neptune = None

    def execute_query(self, query: str) -> Dict:
        """Execute Cypher query against Neptune"""
        if not self.neptune:
            print(f"--- MOCK NEPTUNE QUERY ---\n{query}\n-------------------------")
            return {"results": []}

        try:
            endpoint = f"https://{self.graph_id}.{self.region}.neptune-graph.amazonaws.com"
            url = f"{endpoint}/openCypher"

            session = boto3.Session()
            credentials = session.get_credentials()

            request = AWSRequest(
                method='POST',
                url=url,
                data=json.dumps({"query": query}),
                headers={'Content-Type': 'application/json'}
            )

            SigV4Auth(credentials, 'neptune-graph', self.region).add_auth(request)

            response = requests.post(
                url,
                data=request.body,
                headers=dict(request.headers),
                verify=True
            )

            return response.json()

        except Exception as e:
            print(f" Neptune query failed: {e}")
            return {"results": []}

    def search_datasets_by_keywords(self, keywords: str, limit: int = 10) -> List[Dict]:
        """Search for NASA CMR datasets using science keywords"""
        try:
            # Build search query for datasets
            search_terms = keywords.lower().replace(" ", "").replace(",", " OR ")

            query = f"""
            MATCH (d:Dataset)
            WHERE toLower(d.title) CONTAINS '{keywords.lower()}'
               OR toLower(d.short_name) CONTAINS '{keywords.lower()}'
               OR toLower(d.science_keywords) CONTAINS '{keywords.lower()}'
            RETURN d.`~id` as dataset_id,
                   d.title as title,
                   d.short_name as short_name,
                   d.data_center as data_center,
                   d.science_keywords as science_keywords,
                   d.links as links,
                   d.doi as doi
            ORDER BY d.title
            LIMIT {limit}
            """

            result = self.execute_query(query)
            return result.get("results", [])

        except Exception as e:
            print(f" Dataset search failed: {e}")
            return []

    def get_dataset_metadata(self, dataset_id: str) -> Dict:
        """Get complete metadata for a specific dataset including links - checks local DB first"""
        try:
            # PRIORITY 1: Check local SQLite database for stored links first
            try:
                import sqlite3
                db_path = "climate_knowledge_graph.db"

                with sqlite3.connect(db_path) as conn:
                    cursor = conn.execute("""
                        SELECT dataset_properties, links
                        FROM stored_datasets
                        WHERE dataset_id = ?
                    """, (dataset_id.strip(),))

                    local_result = cursor.fetchone()

                    if local_result and local_result[1]:  # If we have stored links
                        print(f" Using stored links from local database for {dataset_id}")

                        # Parse stored dataset properties
                        try:
                            import json
                            stored_metadata = json.loads(local_result[0]) if local_result[0] else {}
                        except json.JSONDecodeError:
                            stored_metadata = {}

                        # Parse stored links
                        try:
                            stored_links = json.loads(local_result[1])
                            if stored_links:
                                # Convert stored links to pipe-separated format for compatibility
                                href_urls = []
                                for link in stored_links:
                                    if isinstance(link, dict) and link.get('url'):
                                        href_urls.append(link['url'])
                                    elif isinstance(link, str):
                                        href_urls.append(link)

                                if href_urls:
                                    stored_metadata["links"] = "|".join(href_urls)
                                    print(f" Loaded {len(href_urls)} stored links from database")
                                    return stored_metadata
                        except json.JSONDecodeError:
                            print(f" Could not parse stored links for {dataset_id}")

            except Exception as db_error:
                print(f" Local database check failed: {db_error}")

            # PRIORITY 2: If no stored links found, query Neptune graph as fallback
            print(f" No stored links found, querying Neptune graph for {dataset_id}")

            # Get dataset properties
            dataset_query = f"""
            MATCH (d:Dataset)
            WHERE d.`~id` = '{dataset_id}' OR d.id = '{dataset_id}'
            RETURN d as dataset_properties
            """

            result = self.execute_query(dataset_query)
            if not result.get("results"):
                return {}

            metadata = result["results"][0].get("dataset_properties", {})

            # Get associated links if they exist
            try:
                links_query = f"""
                MATCH (d:Dataset)-[:hasLink]-(link)
                WHERE d.`~id` = '{dataset_id}' OR d.id = '{dataset_id}'
                RETURN properties(link) as link_properties
                ORDER BY link.type, link.url
                """

                links_result = self.execute_query(links_query)
                if links_result.get("results"):
                    # Process links from Neptune hasLink relationship
                    href_urls = []
                    for link_result in links_result["results"]:
                        link_props = link_result.get("link_properties", {})
                        url = link_props.get('url', '')
                        if url:
                            href_urls.append(url)

                    if href_urls:
                        metadata["links"] = "|".join(href_urls)
                        print(f" Found {len(href_urls)} links from Neptune graph")

            except Exception as link_error:
                # If link queries fail, continue with basic metadata
                print(f" Could not retrieve links from Neptune for {dataset_id}: {link_error}")

            return metadata

        except Exception as e:
            print(f" Dataset metadata retrieval failed: {e}")
            return {}

    def get_dataset_relationships(self, dataset_id: str) -> Dict:
        """Get all relationships and connected entities for a dataset"""
        try:
            query = f"""
            MATCH (d:Dataset)-[r]-(connected)
            WHERE d.`~id` = '{dataset_id}'
            RETURN type(r) as relationship_type,
                   labels(connected) as connected_labels,
                   connected.`~id` as connected_id,
                   properties(connected) as connected_properties
            ORDER BY relationship_type
            """

            result = self.execute_query(query)
            relationships = {}

            for rel in result.get("results", []):
                rel_type = rel.get("relationship_type", "unknown")
                if rel_type not in relationships:
                    relationships[rel_type] = []

                relationships[rel_type].append({
                    "id": rel.get("connected_id"),
                    "labels": rel.get("connected_labels", []),
                    "properties": rel.get("connected_properties", {})
                })

            return relationships

        except Exception as e:
            print(f" Dataset relationships retrieval failed: {e}")
            return {}

# --- AWS Open Data Registry Connector ---
class AWSOpenDataConnector:
    """Connector for NASA datasets in AWS Open Data Registry (Primary Source)"""

    def __init__(self):
        self.s3_fs = None
        self._init_s3_client()

    def _init_s3_client(self):
        """Initialize S3 client for anonymous access to public data"""
        try:
            # AWS Open Data is publicly accessible - no credentials needed
            self.s3_fs = s3fs.S3FileSystem(anon=True)
            print(" AWS Open Data S3 client initialized (anonymous access)")
        except Exception as e:
            print(f" AWS Open Data S3 client initialization failed: {e}")
            self.s3_fs = None

    def search_open_data_buckets(self, keywords: str) -> List[Dict]:
        """Search AWS Open Data NASA buckets by keywords"""
        keywords_lower = keywords.lower()
        matching_buckets = []

        for bucket_name, bucket_info in AWS_OPEN_DATA_NASA_BUCKETS.items():
            # Check if keywords match data types or description
            data_types = bucket_info.get("data_types", [])
            description = bucket_info.get("description", "").lower()

            match_score = 0
            matched_terms = []

            # Check description
            for keyword in keywords_lower.split():
                if keyword in description:
                    match_score += 2
                    matched_terms.append(f"description:{keyword}")

            # Check data types
            for data_type in data_types:
                for keyword in keywords_lower.split():
                    if keyword in data_type.lower():
                        match_score += 3
                        matched_terms.append(f"type:{data_type}")

            if match_score > 0:
                matching_buckets.append({
                    "bucket_name": bucket_name,
                    "s3_path": f"s3://{bucket_name}",
                    "description": bucket_info.get("description", ""),
                    "data_types": data_types,
                    "formats": bucket_info.get("formats", []),
                    "match_score": match_score,
                    "matched_terms": matched_terms,
                    "source": "AWS_Open_Data"
                })

        # Sort by match score
        matching_buckets.sort(key=lambda x: x["match_score"], reverse=True)
        return matching_buckets

    def check_bucket_accessibility(self, bucket_name: str) -> Dict:
        """Check if an AWS Open Data bucket is accessible"""
        if not self.s3_fs:
            return {"accessible": False, "error": "S3 client not available"}

        try:
            bucket_path = f"s3://{bucket_name}"
            exists = self.s3_fs.exists(bucket_path)

            if exists:
                # Try to list some contents
                try:
                    contents = self.s3_fs.ls(bucket_path, max_items=5)
                    return {
                        "accessible": True,
                        "exists": True,
                        "sample_contents": contents[:3],
                        "total_items_sampled": len(contents)
                    }
                except Exception as list_error:
                    return {
                        "accessible": True,
                        "exists": True,
                        "list_error": str(list_error)
                    }
            else:
                return {"accessible": False, "exists": False}

        except Exception as e:
            return {"accessible": False, "error": str(e)}

    def explore_bucket_structure(self, bucket_name: str, max_depth: int = 2) -> Dict:
        """Explore the structure of an AWS Open Data bucket"""
        if not self.s3_fs:
            return {"error": "S3 client not available"}

        try:
            bucket_path = f"s3://{bucket_name}"

            structure = {
                "bucket": bucket_name,
                "bucket_path": bucket_path,
                "structure": {}
            }

            # Get top-level contents
            try:
                top_level = self.s3_fs.ls(bucket_path)
                structure["top_level_count"] = len(top_level)

                # Categorize contents
                directories = []
                files = []

                for item in top_level[:20]:  # Limit to first 20 items
                    if item.endswith('/') or '.' not in Path(item).name:
                        directories.append(item)
                    else:
                        files.append(item)

                structure["structure"]["directories"] = directories[:10]
                structure["structure"]["sample_files"] = files[:10]
                structure["structure"]["total_directories"] = len(directories)
                structure["structure"]["total_files"] = len(files)

                # Explore a few directories
                if directories and max_depth > 1:
                    structure["structure"]["directory_samples"] = {}
                    for directory in directories[:3]:  # Explore first 3 directories
                        try:
                            dir_contents = self.s3_fs.ls(directory)
                            structure["structure"]["directory_samples"][directory] = {
                                "item_count": len(dir_contents),
                                "sample_items": [Path(item).name for item in dir_contents[:5]]
                            }
                        except Exception:
                            structure["structure"]["directory_samples"][directory] = {"error": "access_denied"}

                return structure

            except Exception as e:
                return {"error": f"Failed to explore bucket structure: {str(e)}"}

        except Exception as e:
            return {"error": f"Bucket exploration failed: {str(e)}"}

# --- S3 Data Connector ---
class EarthdataAuth:
    """Authentication handler for NASA Earthdata Login with streaming support"""

    def __init__(self, username: str = EARTHDATA_USERNAME, password: str = EARTHDATA_PASSWORD):
        self.username = username
        self.password = password
        self.session = None

        # Authentication caching
        self._auth_cache = {}  # hostname -> timestamp of successful auth
        self._cache_ttl = 3600  # 1 hour cache
        self._successful_urls = set()  # URLs that have been successfully accessed

        self._setup_session()

    def _setup_session(self):
        """Setup requests session with Earthdata authentication"""
        from requests import Session

        class SessionWithHeaderRedirection(Session):
            AUTH_HOST = 'urs.earthdata.nasa.gov'

            def __init__(self, username, password):
                super().__init__()
                self.auth = (username, password)

            def rebuild_auth(self, prepared_request, response):
                headers = prepared_request.headers
                url = prepared_request.url

                if 'Authorization' in headers:
                    original_parsed = urlparse(response.request.url)
                    redirect_parsed = urlparse(url)

                    if (original_parsed.hostname != redirect_parsed.hostname) and \
                            redirect_parsed.hostname != self.AUTH_HOST and \
                            original_parsed.hostname != self.AUTH_HOST:
                        del headers['Authorization']

                return

        self.session = SessionWithHeaderRedirection(self.username, self.password)

    def is_earthdata_url(self, url: str) -> bool:
        """Check if URL requires Earthdata authentication using exact domain matching"""
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname

            if not hostname:
                return False

            # Use only exact matches - more reliable and faster
            return hostname in EARTHDATA_DOMAINS

        except:
            return False

    def _is_auth_cached(self, hostname: str) -> bool:
        """Check if authentication is cached and still valid"""
        import time
        if hostname in self._auth_cache:
            cache_time = self._auth_cache[hostname]
            return (time.time() - cache_time) < self._cache_ttl
        return False

    def _cache_successful_auth(self, hostname: str):
        """Cache successful authentication for a hostname"""
        import time
        self._auth_cache[hostname] = time.time()
        logger.info(f"Cached successful authentication for {hostname}")

    def _is_url_successful(self, url: str) -> bool:
        """Check if URL has been successfully accessed before"""
        return url in self._successful_urls

    def _cache_successful_url(self, url: str):
        """Cache successful URL access"""
        self._successful_urls.add(url)
        logger.info(f"Cached successful access for {url}")

    def open_url_stream(self, url: str):
        """Open URL as a streaming response (no download) with caching"""
        if not self.is_earthdata_url(url):
            return None

        # Check if URL was previously successful
        if self._is_url_successful(url):
            logger.info(f"Using cached successful URL: {url}")

        try:
            response = self.session.get(url, stream=True)

            # Check for specific HTTP errors before raising
            if response.status_code == 401:
                logger.error(f"Earthdata authentication failed for {url}. Check credentials.")
                return None
            elif response.status_code == 403:
                logger.error(f"Earthdata access forbidden for {url}. You may need permission or valid credentials.")
                return None
            elif response.status_code == 404:
                logger.error(f"Earthdata resource not found: {url}")
                return None
            elif response.status_code != 200:
                logger.error(f"Earthdata API returned status {response.status_code} for {url}")
                return None

            response.raise_for_status()

            # Cache successful access
            parsed_url = urlparse(url)
            self._cache_successful_auth(parsed_url.hostname)
            self._cache_successful_url(url)

            return response
        except Exception as e:
            logger.error(f"Failed to open stream for {url}: {e}")
            return None

    def read_url_content(self, url: str, max_bytes: int = None):
        """Read URL content into memory (without downloading to disk)"""
        if not self.is_earthdata_url(url):
            return None

        try:
            response = self.session.get(url, stream=True)
            response.raise_for_status()

            if max_bytes:
                content = response.raw.read(max_bytes)
            else:
                content = response.content

            return content
        except Exception as e:
            logger.error(f"Failed to read content from {url}: {e}")
            return None

    def get_authenticated_session(self):
        """Get the authenticated requests session"""
        return self.session


class NOAACDOApiConnector:
    """Connector for accessing NOAA Climate Data Online (CDO) API"""

    def __init__(self, token: str = None):
        self.base_url = NOAA_CDO_API_BASE
        self.token = token or os.getenv('NOAA_CDO_TOKEN', NOAA_CDO_TOKEN)
        self.session = requests.Session()
        self.session.headers.update({'token': self.token} if self.token else {})
        self._token_validated = False

    def is_noaa_url(self, url: str) -> bool:
        """Check if URL is a NOAA domain"""
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            return hostname and any(domain in hostname for domain in NOAA_CDO_DOMAINS)
        except:
            return False

    def validate_token(self) -> bool:
        """Validate NOAA CDO API token by making a simple API call"""
        if not self.token:
            return False

        if self._token_validated:
            return True

        try:
            # Make a simple API call to validate token
            url = f"{self.base_url}/datasets"
            response = self.session.get(url, params={'limit': 1})

            if response.status_code == 200:
                self._token_validated = True
                return True
            elif response.status_code == 401:
                print(f"⚠️ NOAA API token is invalid. Get a new token at: https://www.ncdc.noaa.gov/cdo-web/token")
                return False
            else:
                print(f"⚠️ NOAA API validation failed with status {response.status_code}")
                return False

        except Exception as e:
            print(f"⚠️ NOAA API token validation error: {e}")
            return False

    def get_dataset_info(self, dataset_id: str) -> Dict:
        """Get dataset information from NOAA CDO API"""
        if not self.token:
            return {"error": "NOAA CDO API token required. Get one at: https://www.ncdc.noaa.gov/cdo-web/token"}

        # Validate token before making API call
        if not self.validate_token():
            return {"error": "NOAA CDO API token validation failed. Check your token at: https://www.ncdc.noaa.gov/cdo-web/token"}

        try:
            # Try different dataset ID formats
            possible_ids = [dataset_id, dataset_id.replace('gov.noaa.ncdc:', '')]

            for did in possible_ids:
                url = f"{self.base_url}/datasets/{did}"
                response = self.session.get(url)

                if response.status_code == 200:
                    return response.json()

            # If specific dataset not found, search datasets
            url = f"{self.base_url}/datasets"
            params = {'limit': 1000}  # Get more datasets to search
            response = self.session.get(url, params=params)

            if response.status_code == 200:
                datasets = response.json().get('results', [])
                # Search for matching dataset
                for ds in datasets:
                    if any(term in ds.get('id', '').lower() for term in dataset_id.lower().split('_')):
                        return ds

            return {"error": f"Dataset {dataset_id} not found in NOAA CDO API"}

        except Exception as e:
            return {"error": f"NOAA CDO API error: {str(e)}"}

    def get_data_urls(self, dataset_id: str, location_id: str = None, start_date: str = None, end_date: str = None) -> List[str]:
        """Get data access URLs from NOAA CDO API"""
        if not self.token:
            return []

        try:
            # Get dataset info first
            dataset_info = self.get_dataset_info(dataset_id)
            if "error" in dataset_info:
                return []

            # Construct data query
            url = f"{self.base_url}/data"
            params = {
                'datasetid': dataset_info.get('id', dataset_id),
                'limit': 1000
            }

            if location_id:
                params['locationid'] = location_id
            if start_date:
                params['startdate'] = start_date
            if end_date:
                params['enddate'] = end_date

            response = self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                # Extract data access URLs if available
                results = data.get('results', [])
                urls = []

                # Look for data access endpoints
                for result in results[:10]:  # Limit to first 10 results
                    # NOAA CDO API typically provides structured data, not direct file URLs
                    # But we can construct access URLs
                    if 'station' in result and 'date' in result:
                        # Construct data access URL
                        access_url = f"{self.base_url}/data?datasetid={params['datasetid']}&stationid={result.get('station')}&startdate={result.get('date')}&enddate={result.get('date')}"
                        urls.append(access_url)

                return urls

            return []

        except Exception as e:
            logger.error(f"Error getting NOAA CDO data URLs: {e}")
            return []

    def download_data(self, dataset_id: str, **params) -> Dict:
        """Download data from NOAA CDO API"""
        if not self.token:
            return {"error": "NOAA CDO API token required. Get one at: https://www.ncdc.noaa.gov/cdo-web/token"}

        try:
            url = f"{self.base_url}/data"
            query_params = {
                'datasetid': dataset_id,
                'limit': 1000,
                **params
            }

            response = self.session.get(url, params=query_params)

            # Check for specific HTTP errors
            if response.status_code == 401:
                return {"error": "NOAA API authentication failed. Check your token at: https://www.ncdc.noaa.gov/cdo-web/token"}
            elif response.status_code == 403:
                return {"error": "NOAA API access forbidden. Your token may be invalid or expired."}
            elif response.status_code == 429:
                return {"error": "NOAA API rate limit exceeded. Please wait and try again."}
            elif response.status_code != 200:
                return {"error": f"NOAA API returned status {response.status_code}: {response.text[:200]}"}

            response.raise_for_status()

            data = response.json()
            return {
                'data': data.get('results', []),
                'metadata': data.get('metadata', {}),
                'count': len(data.get('results', [])),
                'api_url': response.url
            }

        except Exception as e:
            return {"error": f"NOAA CDO download error: {str(e)}"}

    def search_locations(self, location_name: str, location_type: str = "CITY") -> List[Dict]:
        """Search for location codes by name"""
        if not self.token:
            return []

        try:
            url = f"{self.base_url}/locations"
            params = {
                'locationcategoryid': location_type,
                'limit': 1000,
                'sortfield': 'name'
            }

            response = self.session.get(url, params=params)
            if response.status_code != 200:
                return []

            data = response.json()
            locations = data.get('results', [])

            # Filter by location name (case-insensitive)
            location_name_lower = location_name.lower()
            matching_locations = []

            for loc in locations:
                name = loc.get('name', '').lower()
                if location_name_lower in name or name in location_name_lower:
                    matching_locations.append({
                        'id': loc.get('id'),
                        'name': loc.get('name'),
                        'mindate': loc.get('mindate'),
                        'maxdate': loc.get('maxdate'),
                        'datacoverage': loc.get('datacoverage')
                    })

            return matching_locations[:10]  # Return top 10 matches

        except Exception as e:
            logger.error(f"Error searching NOAA locations: {e}")
            return []

    def auto_resolve_location_code(self, location_input: str) -> str:
        """Dynamically resolve location names to NOAA location codes using live API lookup"""
        if not location_input:
            return None
            
        # If already a location code (contains colon), return as-is
        if ':' in location_input and any(prefix in location_input.upper() for prefix in ['CITY:', 'ST:', 'FIPS:', 'ZIP:']):
            return location_input
        
        # Otherwise, search for the location dynamically via NOAA API
        try:
            # Try different location types in priority order
            location_types = ['CITY', 'ST', 'ZIP', 'FIPS']
            
            for loc_type in location_types:
                locations = self.search_locations(location_input, loc_type)
                if locations:
                    best_match = locations[0]  # Return best match
                    logger.info(f"Auto-resolved '{location_input}' to {best_match['id']} ({best_match['name']})")
                    return best_match['id']
            
            logger.warning(f"No location code found for '{location_input}'")
            return None
            
        except Exception as e:
            logger.error(f"Auto-resolution failed for '{location_input}': {e}")
            return None


class S3DataConnector:
    """Connector for accessing NASA data from S3 buckets and Earthdata sources"""

    def __init__(self):
        self.s3_client = None
        self.s3_fs = None
        self.earthdata_auth = EarthdataAuth()
        self.noaa_api = NOAACDOApiConnector()
        self._init_s3_clients()

    def _init_s3_clients(self):
        """Initialize S3 clients for both authenticated and anonymous access"""
        try:
            # Try authenticated access first
            self.s3_client = boto3.client('s3')
            self.s3_fs = s3fs.S3FileSystem()
            print(" S3 clients initialized with credentials")
        except (NoCredentialsError, ClientError):
            try:
                # Fall back to anonymous access
                self.s3_client = boto3.client('s3',
                    aws_access_key_id='',
                    aws_secret_access_key='',
                    aws_session_token='')
                self.s3_fs = s3fs.S3FileSystem(anon=True)
                print(" S3 clients initialized with anonymous access")
            except Exception as e:
                print(f" S3 client initialization failed: {e}")
                self.s3_client = None
                self.s3_fs = None

    def extract_data_urls_from_links(self, links_str: str) -> List[str]:
        """Extract S3 paths and Earthdata URLs from dataset links string"""
        if not links_str:
            return []

        data_urls = []

        try:
            # Parse links if it's JSON format
            if links_str.startswith('[') or links_str.startswith('{'):
                links_data = json.loads(links_str)
                if isinstance(links_data, list):
                    for link in links_data:
                        if isinstance(link, dict):
                            href = link.get('href', '')
                            # Check for S3 URLs
                            if href.startswith('s3://'):
                                data_urls.append(href)
                            # Check for Earthdata URLs
                            elif self.earthdata_auth.is_earthdata_url(href):
                                data_urls.append(href)
                            # Check for NOAA URLs
                            elif self.noaa_api.is_noaa_url(href):
                                data_urls.append(href)
                elif isinstance(links_data, dict):
                    href = links_data.get('href', '')
                    if href.startswith('s3://') or self.earthdata_auth.is_earthdata_url(href) or self.noaa_api.is_noaa_url(href):
                        data_urls.append(href)
            else:
                # Check if it's pipe-separated URLs (new format from json_to_csvs.py)
                if '|' in links_str and ('http' in links_str or 's3://' in links_str):
                    pipe_urls = links_str.split('|')
                    for url in pipe_urls:
                        url = url.strip()
                        if url.startswith('s3://') or self.earthdata_auth.is_earthdata_url(url) or self.noaa_api.is_noaa_url(url):
                            data_urls.append(url)
                else:
                    # Look for S3 URLs in plain text
                    s3_pattern = r's3://[a-zA-Z0-9\-./]+'
                    s3_matches = re.findall(s3_pattern, links_str)
                    data_urls.extend(s3_matches)

                    # Look for Earthdata URLs (https URLs with known domains)
                    earthdata_pattern = r'https://[a-zA-Z0-9\-./]+(?:' + '|'.join(EARTHDATA_DOMAINS) + r')[a-zA-Z0-9\-./]*'
                    earthdata_matches = re.findall(earthdata_pattern, links_str)
                    data_urls.extend(earthdata_matches)

                    # Look for NOAA URLs
                    noaa_pattern = r'https://[a-zA-Z0-9\-./]*(?:' + '|'.join(NOAA_CDO_DOMAINS) + r')[a-zA-Z0-9\-./]*'
                    noaa_matches = re.findall(noaa_pattern, links_str)
                    data_urls.extend(noaa_matches)

        except (json.JSONDecodeError, TypeError):
            # Fallback: search for both S3 and Earthdata patterns
            s3_pattern = r's3://[a-zA-Z0-9\-./]+'
            s3_matches = re.findall(s3_pattern, str(links_str))
            data_urls.extend(s3_matches)

            earthdata_pattern = r'https://[a-zA-Z0-9\-./]+(?:' + '|'.join(EARTHDATA_DOMAINS) + r')[a-zA-Z0-9\-./]*'
            earthdata_matches = re.findall(earthdata_pattern, str(links_str))
            data_urls.extend(earthdata_matches)

            # Look for NOAA URLs in fallback
            noaa_pattern = r'https://[a-zA-Z0-9\-./]*(?:' + '|'.join(NOAA_CDO_DOMAINS) + r')[a-zA-Z0-9\-./]*'
            noaa_matches = re.findall(noaa_pattern, str(links_str))
            data_urls.extend(noaa_matches)

        return list(set(data_urls))  # Remove duplicates

    def extract_s3_paths_from_links(self, links_str: str) -> List[str]:
        """Legacy method - now calls extract_data_urls_from_links for backward compatibility"""
        return self.extract_data_urls_from_links(links_str)

    def categorize_data_urls(self, links_str: str) -> Dict[str, List[str]]:
        """Categorize URLs into S3, Earthdata, and NOAA URLs"""
        data_urls = self.extract_data_urls_from_links(links_str)

        categorized = {
            "s3_urls": [],
            "earthdata_urls": [],
            "noaa_urls": [],
            "other_urls": []
        }

        for url in data_urls:
            if url.startswith('s3://'):
                categorized["s3_urls"].append(url)
            elif self.earthdata_auth.is_earthdata_url(url):
                categorized["earthdata_urls"].append(url)
            elif self.noaa_api.is_noaa_url(url):
                categorized["noaa_urls"].append(url)
            else:
                categorized["other_urls"].append(url)

        return categorized

    def check_s3_path_exists(self, s3_path: str) -> bool:
        """Check if an S3 path exists"""
        if not self.s3_fs:
            return False

        try:
            return self.s3_fs.exists(s3_path)
        except Exception as e:
            print(f" Error checking S3 path {s3_path}: {e}")
            return False

    def list_s3_contents(self, s3_path: str, pattern: str = None) -> List[str]:
        """List contents of an S3 path, optionally filtering by pattern"""
        if not self.s3_fs:
            return []

        try:
            if not self.s3_fs.exists(s3_path):
                return []

            contents = self.s3_fs.ls(s3_path)

            if pattern:
                import fnmatch
                contents = [item for item in contents if fnmatch.fnmatch(item, pattern)]

            return contents

        except Exception as e:
            print(f" Error listing S3 contents at {s3_path}: {e}")
            return []

    def find_actual_data_files(self, s3_path: str, max_files: int = 10) -> List[str]:
        """Find actual data files by exploring directory structure with enhanced NASA pattern detection"""
        data_files = []

        try:
            print(f" Searching for data files in: {s3_path}")

            # Enhanced NASA file pattern detection function
            def is_nasa_data_file(file_path: str) -> bool:
                """Check if a file path matches NASA data file patterns"""
                path_obj = Path(file_path)
                filename = path_obj.name.upper()

                # Standard extensions
                if path_obj.suffix.lower() in ['.nc', '.nc4', '.hdf', '.hdf5', '.h5', '.zarr']:
                    return True

                # NASA satellite naming patterns (often without extensions)
                nasa_patterns = [
                    # MODIS products
                    lambda f: f.startswith(('MOD', 'MYD', 'MCD')),
                    # GOES ABI products
                    lambda f: f.startswith('OR_ABI') or 'ABI-L2' in f,
                    # Sea Surface Temperature products
                    lambda f: 'SST' in f and ('L2' in f or 'L3' in f),
                    # General Level 2/3 products
                    lambda f: ('L2' in f or 'L3' in f) and any(sat in f for sat in ['GOES', 'MODIS', 'VIIRS']),
                    # Collection numbers (MODIS)
                    lambda f: f.endswith(('.006', '.061', '.005')),
                    # Date-time patterns in filename (common in NASA files)
                    lambda f: any(pattern in f for pattern in ['s2019', 's2020', 's2021', 's2022', 's2023', 's2024']),
                    # Product type indicators
                    lambda f: any(indicator in f for indicator in ['SSTF', 'TEMP', 'OCEAN', 'ATM']),
                ]

                return any(pattern(filename) for pattern in nasa_patterns)

            # Check if the path itself is a data file
            if is_nasa_data_file(s3_path):
                print(f" Direct file detected: {Path(s3_path).name}")
                if self.s3_fs.exists(s3_path):
                    print(f" File exists: {s3_path}")
                    return [s3_path]
                else:
                    print(f" Specific file path does not exist: {s3_path}")
                    return []

            # Check if it's actually a directory and explore it
            if not self.s3_fs.exists(s3_path):
                print(f" Path does not exist: {s3_path}")
                return []

            # Get directory contents
            print(f"📂 Exploring directory contents...")
            contents = self.list_s3_contents(s3_path)
            print(f" Found {len(contents)} items in directory")

            for item in contents:
                # Check if it's a data file
                if is_nasa_data_file(item):
                    print(f" Data file found: {Path(item).name}")
                    data_files.append(item)
                    if len(data_files) >= max_files:
                        break

                # If it's a directory, explore one level deeper
                elif not Path(item).suffix:
                    try:
                        print(f" Exploring subdirectory: {Path(item).name}")
                        sub_contents = self.s3_fs.ls(item)

                        for sub_item in sub_contents[:10]:  # Increased from 5 to 10
                            if is_nasa_data_file(sub_item):
                                print(f" Data file found in subdirectory: {Path(sub_item).name}")
                                data_files.append(sub_item)
                                if len(data_files) >= max_files:
                                    break

                        if len(data_files) >= max_files:
                            break

                    except Exception as sub_error:
                        print(f" Could not explore subdirectory {Path(item).name}: {str(sub_error)[:50]}")
                        continue

        except Exception as e:
            print(f" Error finding data files in {s3_path}: {e}")

        print(f" Total data files found: {len(data_files)}")
        if data_files:
            print(f" First file: {Path(data_files[0]).name}")

        return data_files

    def detect_data_format(self, file_path: str) -> str:
        """Detect data format from file extension"""
        path_obj = Path(file_path)
        ext = path_obj.suffix.lower()
        return SUPPORTED_FORMATS.get(ext, 'Unknown')

    def load_data_from_url_or_s3(self, path_or_url: str, format_hint: str = None,
                                sample_only: bool = True, max_size_mb: int = 100) -> Optional[Any]:
        """Load data from Earthdata URL or S3 path with authentication support"""
        # Check if it's an Earthdata URL first
        if self.earthdata_auth.is_earthdata_url(path_or_url):
            print(f" Detected Earthdata URL, using authenticated access: {path_or_url}")
            return self._load_from_earthdata(path_or_url, format_hint, sample_only, max_size_mb)

        # Fall back to S3 loading
        print(f" Loading from S3: {path_or_url}")
        return self.load_data_from_s3(path_or_url, format_hint, sample_only, max_size_mb)

    def _load_from_earthdata(self, url: str, format_hint: str = None,
                            sample_only: bool = True, max_size_mb: int = 100) -> Optional[Any]:
        """Load data from Earthdata URL using streaming (no download)"""
        try:
            # Get streaming response
            response = self.earthdata_auth.open_url_stream(url)
            if response is None:
                print(f" Failed to open Earthdata stream: {url}")
                return None

            # Check content length if available
            content_length = response.headers.get('content-length')
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                print(f" File size: {size_mb:.2f} MB")

                if size_mb > max_size_mb and sample_only:
                    print(f" File too large ({size_mb:.2f} MB > {max_size_mb} MB). Skipping for safety.")
                    return {"error": "file_too_large", "size_mb": size_mb}

            # For any file format, provide the authenticated stream response
            # This allows the calling code to handle the format as needed
            print(f" Returning authenticated stream for: {url}")
            return {
                "stream_response": response,
                "url": url,
                "content_length": content_length,
                "source": "earthdata"
            }

        except Exception as e:
            print(f" Error loading from Earthdata: {e}")
            return None

    def load_data_from_s3(self, s3_path: str, format_hint: str = None,
                         sample_only: bool = True, max_size_mb: int = 100) -> Optional[Any]:
        """Load data from S3 with format auto-detection and size limits"""
        if not self.s3_fs:
            print(" S3 filesystem not available")
            return None

        try:
            # Check if path exists
            if not self.s3_fs.exists(s3_path):
                print(f" S3 path does not exist: {s3_path}")
                return None

            # Get file info
            info = self.s3_fs.info(s3_path)
            size_mb = info.get('size', 0) / (1024 * 1024)

            print(f" File size: {size_mb:.2f} MB")

            # Check size limit
            if size_mb > max_size_mb and sample_only:
                print(f" File too large ({size_mb:.2f} MB > {max_size_mb} MB). Skipping for safety.")
                return {"error": "file_too_large", "size_mb": size_mb}

            # Detect format
            data_format = format_hint or self.detect_data_format(s3_path)
            print(f" Detected format: {data_format}")

            # Load based on format
            if data_format == 'NetCDF' and XARRAY_AVAILABLE:
                return self._load_netcdf_from_s3(s3_path)
            elif data_format in ['HDF4', 'HDF5'] and HDF5_AVAILABLE:
                return self._load_hdf_from_s3(s3_path)
            elif data_format == 'CSV':
                return self._load_csv_from_s3(s3_path)
            elif data_format == 'JSON':
                return self._load_json_from_s3(s3_path)
            else:
                print(f" Unsupported format: {data_format}")
                return {"error": "unsupported_format", "format": data_format}

        except Exception as e:
            print(f" Error loading data from {s3_path}: {e}")
            return {"error": str(e)}

    def _load_netcdf_from_s3(self, s3_path: str) -> Optional[xr.Dataset]:
        """Load NetCDF file from S3 with enhanced error handling"""
        try:
            print(f" Attempting NetCDF load from: {Path(s3_path).name}")

            # Try different loading methods
            loading_methods = [
                # Method 1: Direct s3fs mapper
                lambda: xr.open_dataset(self.s3_fs.get_mapper(s3_path), chunks=None),
                # Method 2: s3fs open with different backends
                lambda: xr.open_dataset(self.s3_fs.open(s3_path), engine='h5netcdf'),
                # Method 3: Try with netcdf4 engine explicitly
                lambda: xr.open_dataset(self.s3_fs.open(s3_path), engine='netcdf4'),
                # Method 4: Try fsspec integration
                lambda: xr.open_dataset(f"s3://{s3_path.replace('s3://', '')}",
                                      storage_options={'anon': True})
            ]

            for i, method in enumerate(loading_methods):
                try:
                    print(f" Trying loading method {i+1}...")
                    ds = method()
                    print(f" Loaded NetCDF dataset with dimensions: {dict(ds.dims)}")
                    if ds.data_vars:
                        print(f" Variables: {list(ds.data_vars)[:5]}")
                    return ds
                except Exception as method_error:
                    print(f" Method {i+1} failed: {str(method_error)[:100]}")
                    continue

            # If all methods fail, provide detailed guidance
            print(f" All NetCDF loading methods failed")
            return None

        except Exception as e:
            print(f" NetCDF loading failed: {e}")

            # Provide helpful error diagnosis
            error_msg = str(e).lower()
            if "no match" in error_msg and "backends" in error_msg:
                print(f" DEPENDENCY ISSUE DETECTED:")
                print(f"   Missing NetCDF reading dependencies. Install with:")
                print(f"   pip install netcdf4 h5netcdf")
                print(f"   conda install netcdf4 h5netcdf")
            elif "permission" in error_msg or "access" in error_msg:
                print(f"🔒 ACCESS ISSUE: File may require authentication")
            elif "corrupt" in error_msg or "invalid" in error_msg:
                print(f"📁 FILE ISSUE: File may be corrupted or not a valid NetCDF")

            return None

    def _load_csv_from_s3(self, s3_path: str) -> Optional[pl.DataFrame]:
        """Load CSV file from S3"""
        try:
            with self.s3_fs.open(s3_path, 'r') as f:
                df = pl.read_csv(f)
            print(f" Loaded CSV with shape: {df.shape}")
            return df
        except Exception as e:
            print(f" CSV loading failed: {e}")
            return None

    def _load_json_from_s3(self, s3_path: str) -> Optional[Dict]:
        """Load JSON file from S3"""
        try:
            with self.s3_fs.open(s3_path, 'r') as f:
                data = json.load(f)
            print(f" Loaded JSON data")
            return data
        except Exception as e:
            print(f" JSON loading failed: {e}")
            return None

    def _load_hdf_from_s3(self, s3_path: str) -> Optional[Dict]:
        """Load HDF file from S3 (basic structure inspection)"""
        try:
            # For HDF files, we'll return basic structure info since
            # full loading can be complex and memory-intensive
            with self.s3_fs.open(s3_path, 'rb') as f:
                with h5py.File(f, 'r') as hdf:
                    structure = self._inspect_hdf_structure(hdf)
            print(f" Inspected HDF structure")
            return {"hdf_structure": structure}
        except Exception as e:
            print(f" HDF loading failed: {e}")
            return None

    def _inspect_hdf_structure(self, hdf_obj, max_depth: int = 3, current_depth: int = 0) -> Dict:
        """Recursively inspect HDF structure"""
        if current_depth >= max_depth:
            return {"...": "max_depth_reached"}

        structure = {}
        for key in hdf_obj.keys():
            item = hdf_obj[key]
            if hasattr(item, 'shape'):  # Dataset
                structure[key] = {
                    "type": "dataset",
                    "shape": item.shape,
                    "dtype": str(item.dtype)
                }
            elif hasattr(item, 'keys'):  # Group
                structure[key] = {
                    "type": "group",
                    "contents": self._inspect_hdf_structure(item, max_depth, current_depth + 1)
                }
        return structure

# Initialize services
kg_connector = CMRKnowledgeGraphConnector()
open_data_connector = AWSOpenDataConnector()
s3_connector = S3DataConnector()
llm = BedrockClaudeLLM()

# --- LangChain Tools ---

class QueryNOAADatasetTool(BaseTool):
    """Query NOAA Climate Data Online (CDO) API for dataset information"""
    name: str = "query_noaa_dataset"
    description: str = "Get detailed information about a NOAA dataset using the Climate Data Online API. Requires NOAA CDO API token."

    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Remove 'dataset_' prefix if present
            clean_id = dataset_id.replace('dataset_', '')

            # Try to extract NOAA dataset code from stored links first
            metadata = kg_connector.get_dataset_metadata(dataset_id)
            extracted_codes = []
            if metadata and 'links' in metadata:
                links = metadata.get('links', '')
                # Extract codes like C00127 from URLs like gov.noaa.ncdc:C00127
                import re
                codes = re.findall(r'gov\.noaa\.ncdc:([A-Z0-9]+)', str(links))
                extracted_codes = codes

            # Get dataset info from NOAA CDO API
            dataset_info = s3_connector.noaa_api.get_dataset_info(clean_id)

            if "error" in dataset_info and extracted_codes:
                # Try the extracted codes from the URLs
                for code in extracted_codes:
                    dataset_info = s3_connector.noaa_api.get_dataset_info(code)
                    if "error" not in dataset_info:
                        break

                if "error" in dataset_info:
                    return f" {dataset_info['error']}\n\n Note: You need a NOAA CDO API token. Get one at: https://www.ncdc.noaa.gov/cdo-web/token"

            output = f" NOAA DATASET INFO: {dataset_id}\n"
            output += "=" * 60 + "\n\n"

            if isinstance(dataset_info, dict) and "error" not in dataset_info:
                output += f" Dataset ID: {dataset_info.get('id', 'N/A')}\n"
                output += f" Name: {dataset_info.get('name', 'N/A')}\n"
                output += f" Description: {dataset_info.get('datacoverage', 'N/A')}\n"
                output += f" Date Range: {dataset_info.get('mindate', 'N/A')} to {dataset_info.get('maxdate', 'N/A')}\n"
                output += f" Data Coverage: {dataset_info.get('datacoverage', 'N/A')}\n\n"

                output += f" Use 'download_noaa_data' to get actual climate data from this dataset"
            else:
                output += f" Dataset information not available via NOAA CDO API"

            return output

        except Exception as e:
            return f" Error querying NOAA dataset: {str(e)}"


class SearchNOAALocationsTool(BaseTool):
    """Search for NOAA location codes by name"""
    name: str = "search_noaa_locations"
    description: str = "Search for NOAA CDO API location codes by location name (e.g., 'New York', 'Chicago'). Returns location IDs needed for data queries."

    def _run(self, location_name: str, location_type: str = "CITY", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            locations = s3_connector.noaa_api.search_locations(location_name, location_type)

            if not locations:
                return f" No locations found for '{location_name}'\n\n Try different search terms or location types: CITY, ST (state), ZIP, FIPS"

            output = f" NOAA LOCATION SEARCH: '{location_name}'\n"
            output += "=" * 50 + "\n\n"

            output += f" Found {len(locations)} matching locations:\n\n"

            for i, loc in enumerate(locations, 1):
                output += f"{i}.  {loc['name']}\n"
                output += f"    Location ID: {loc['id']}\n"
                output += f"    Data Range: {loc['mindate']} to {loc['maxdate']}\n"
                output += f"    Data Coverage: {loc['datacoverage']}\n\n"

            output += f" Use these location IDs with 'download_noaa_data':\n"
            output += f"   Example: download_noaa_data GHCND locationid={locations[0]['id']} startdate=2023-01-01 enddate=2023-12-31"

            return output

        except Exception as e:
            return f" Error searching locations: {str(e)}"


class DownloadNOAADataTool(BaseTool):
    """Download climate data from NOAA Climate Data Online API"""
    name: str = "download_noaa_data"
    description: str = "Download actual climate data from NOAA CDO API. Accepts location names (e.g. 'New York City') or location codes - will auto-resolve names to codes. Format: 'GHCND locationid=New York City startdate=2020-01-01 enddate=2023-12-31 datatypeid=PRCP' OR separate parameters."

    def _run(self, query_input: str, location_id: str = None, start_date: str = None, end_date: str = None, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Parse input - handle both concatenated string and separate parameters
            dataset_id = None
            params = {}

            # Check if input is a concatenated parameter string
            if ' ' in query_input and ('=' in query_input or 'locationid' in query_input.lower()):
                # Parse concatenated format: "GHCND locationid=CITY:US360005 startdate=2020-01-01"
                parts = query_input.split()
                dataset_id = parts[0]

                # Parse parameters - handle both = and space-separated formats
                i = 1
                while i < len(parts):
                    part = parts[i]
                    if '=' in part:
                        # Handle format: key=value
                        key, value = part.split('=', 1)
                        params[key.lower()] = value
                        i += 1
                    elif i + 1 < len(parts) and not '=' in parts[i + 1]:
                        # Handle format: key value (space-separated)
                        key = part.lower()
                        value = parts[i + 1]
                        params[key] = value
                        i += 2  # Skip both key and value
                    else:
                        i += 1

                # Extract common parameters
                location_id = params.get('locationid') or location_id
                start_date = params.get('startdate') or start_date
                end_date = params.get('enddate') or end_date
                data_type = params.get('datatypeid')

            else:
                # Use as dataset_id if no spaces/equals found
                dataset_id = query_input

            # Clean dataset ID
            if dataset_id:
                clean_id = dataset_id.replace('dataset_', '').replace('gov.noaa.ncdc:', '')
            else:
                return "❌ No dataset ID provided. Format: 'GHCND locationid=New York City startdate=2020-01-01 enddate=2023-12-31'"

            # Set default date range if not provided (recent dates, not future)
            if not start_date or not end_date:
                from datetime import datetime, timedelta
                end_dt = datetime.now() - timedelta(days=1)  # Yesterday
                start_dt = end_dt - timedelta(days=30)       # 30 days ago
                start_date = start_dt.strftime('%Y-%m-%d')
                end_date = end_dt.strftime('%Y-%m-%d')

            output = f"🌡️ DOWNLOADING NOAA CLIMATE DATA\n"
            output += "=" * 50 + "\n\n"
            output += f"📊 Dataset: {clean_id}\n"
            output += f"📅 Date Range: {start_date} to {end_date}\n"
            output += f"📍 Location: {location_id or 'All locations'}\n"
            if data_type:
                output += f"🌡️ Data Type: {data_type}\n"
            output += "\n"

            # Auto-resolve location code if needed
            if location_id:
                resolved_location = s3_connector.noaa_api.auto_resolve_location_code(location_id)
                if resolved_location:
                    location_id = resolved_location
                    output += f"🔍 Auto-resolved location to: {location_id}\n\n"
                else:
                    output += f"❌ Could not resolve location: {location_id}\n"
                    output += f"💡 Try using 'search_noaa_locations' to find valid location names\n"
                    return output

            # Build API parameters
            api_params = {}
            if location_id:
                api_params['locationid'] = location_id
            if start_date:
                api_params['startdate'] = start_date
            if end_date:
                api_params['enddate'] = end_date
            if data_type:
                api_params['datatypeid'] = data_type

            result = s3_connector.noaa_api.download_data(clean_id, **api_params)

            if "error" in result:
                output += f" {result['error']}\n\n"
                output += f" Common issues:\n"
                output += f"   • Invalid dataset ID (try 'query_noaa_dataset' first)\n"
                output += f"   • Missing API token (get one at https://www.ncdc.noaa.gov/cdo-web/token)\n"
                output += f"   • Date range too broad (try smaller date ranges)\n"
                output += f"   • Location not available for this dataset\n"
                return output

            # Process successful result
            data_points = result.get('data', [])
            metadata = result.get('metadata', {})

            # Store data for later saving
            s3_connector.noaa_api.last_downloaded_data = data_points

            output += f" SUCCESS: Downloaded {result.get('count', 0)} data points\n\n"

            if data_points:
                output += f" DATA SAMPLE (first 5 records):\n"
                for i, point in enumerate(data_points[:5], 1):
                    output += f"  {i}. Date: {point.get('date', 'N/A')}\n"
                    output += f"     Station: {point.get('station', 'N/A')}\n"
                    output += f"     Data Type: {point.get('datatype', 'N/A')}\n"
                    output += f"     Value: {point.get('value', 'N/A')}\n"
                    output += f"     Attributes: {point.get('attributes', 'N/A')}\n\n"

                if len(data_points) > 5:
                    output += f"... and {len(data_points) - 5} more records\n\n"

            output += f" API Request: {result.get('api_url', 'N/A')}\n"
            output += f" Data ready for analysis and visualization"

            return output

        except Exception as e:
            return f" Error downloading NOAA data: {str(e)}"


class SearchAWSOpenDataTool(BaseTool):
    """Search AWS Open Data Registry for NASA datasets (Primary Source)"""
    name: str = "search_aws_open_data"
    description: str = "Search AWS Open Data Registry for NASA datasets using keywords. This is the preferred method for finding cloud-optimized NASA data."

    def _run(self, search_keywords: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Search AWS Open Data buckets
            matching_buckets = open_data_connector.search_open_data_buckets(search_keywords)

            if not matching_buckets:
                return f" No matching NASA datasets found in AWS Open Data Registry for '{search_keywords}'.\n Consider using 'search_cmr_datasets' to search the full NASA CMR catalog."

            output = f" Found {len(matching_buckets)} NASA datasets in AWS Open Data Registry for '{search_keywords}':\n\n"

            for i, bucket in enumerate(matching_buckets):
                bucket_name = bucket["bucket_name"]
                description = bucket["description"]
                data_types = bucket["data_types"]
                formats = bucket["formats"]
                match_score = bucket["match_score"]
                matched_terms = bucket["matched_terms"]

                output += f"{i+1}. 📦 {bucket_name}\n"
                output += f"    Description: {description}\n"
                output += f"    Data Types: {', '.join(data_types)}\n"
                output += f"    Formats: {', '.join(formats)}\n"
                output += f"    Match Score: {match_score} (matched: {', '.join(matched_terms[:3])})\n"
                output += f"   📂 S3 Path: s3://{bucket_name}\n\n"

            output += f" ADVANTAGE: AWS Open Data provides:\n"
            output += f"   • Direct S3 access (no authentication needed)\n"
            output += f"   • Cloud-optimized formats for better performance\n"
            output += f"   • No data egress costs\n"
            output += f"   • Analytics-ready data (minimal preprocessing)\n\n"

            output += f" Use 'explore_aws_open_data_bucket' to examine bucket contents\n"
            output += f" Use 'load_s3_data' to access specific data files"

            return output

        except Exception as e:
            return f" Error searching AWS Open Data Registry: {str(e)}"

class ExploreAWSOpenDataBucketTool(BaseTool):
    """Explore the structure and contents of an AWS Open Data bucket"""
    name: str = "explore_aws_open_data_bucket"
    description: str = "Explore the structure, accessibility, and contents of a specific AWS Open Data NASA bucket."

    def _run(self, bucket_name: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Check accessibility first
            access_info = open_data_connector.check_bucket_accessibility(bucket_name)

            output = f" AWS OPEN DATA BUCKET EXPLORATION: {bucket_name}\n"
            output += "=" * 60 + "\n\n"

            if not access_info.get("accessible", False):
                error_msg = access_info.get("error", "Unknown error")
                output += f" Bucket not accessible: {error_msg}\n"
                output += f" Available buckets: {', '.join(AWS_OPEN_DATA_NASA_BUCKETS.keys())}"
                return output

            output += f" Bucket is accessible\n"
            if "sample_contents" in access_info:
                sample_contents = access_info["sample_contents"]
                output += f" Sample contents ({len(sample_contents)} items shown):\n"
                for item in sample_contents:
                    output += f"   • {Path(item).name}\n"
                output += "\n"

            # Get detailed structure
            structure_info = open_data_connector.explore_bucket_structure(bucket_name)

            if "error" in structure_info:
                output += f" Structure exploration error: {structure_info['error']}\n"
                return output

            structure = structure_info.get("structure", {})
            top_level_count = structure_info.get("top_level_count", 0)

            output += f"📁 BUCKET STRUCTURE:\n"
            output += f"    Total top-level items: {top_level_count}\n"
            output += f"   📂 Directories: {structure.get('total_directories', 0)}\n"
            output += f"    Files: {structure.get('total_files', 0)}\n\n"

            # Show sample directories
            directories = structure.get("directories", [])
            if directories:
                output += f"📂 Sample Directories:\n"
                for directory in directories[:5]:
                    dir_name = Path(directory).name
                    output += f"   • {dir_name}/\n"
                if len(directories) > 5:
                    output += f"   ... and {len(directories) - 5} more directories\n"
                output += "\n"

            # Show sample files
            sample_files = structure.get("sample_files", [])
            if sample_files:
                output += f" Sample Files:\n"
                for file_path in sample_files[:5]:
                    file_name = Path(file_path).name
                    file_format = s3_connector.detect_data_format(file_path)
                    output += f"   • {file_name} ({file_format})\n"
                if len(sample_files) > 5:
                    output += f"   ... and {len(sample_files) - 5} more files\n"
                output += "\n"

            # Show directory samples
            dir_samples = structure.get("directory_samples", {})
            if dir_samples:
                output += f" Directory Content Samples:\n"
                for dir_path, dir_info in list(dir_samples.items())[:3]:
                    dir_name = Path(dir_path).name
                    if "error" in dir_info:
                        output += f"   📂 {dir_name}/: {dir_info['error']}\n"
                    else:
                        item_count = dir_info.get("item_count", 0)
                        sample_items = dir_info.get("sample_items", [])
                        output += f"   📂 {dir_name}/: {item_count} items\n"
                        for item in sample_items[:3]:
                            output += f"      • {item}\n"
                output += "\n"

            output += f" Use 'load_s3_data' with specific file paths to access data\n"
            output += f" Example: load_s3_data s3://{bucket_name}/path/to/file.nc"

            return output

        except Exception as e:
            return f" Error exploring AWS Open Data bucket: {str(e)}"

class ListAllStoredDatasetsTool(BaseTool):
    """List ALL datasets from the knowledge graph database for comprehensive analysis"""
    name: str = "list_all_stored_datasets"
    description: str = "List ALL datasets stored in the knowledge graph database regardless of keywords. Use this to get a complete inventory of available datasets for comprehensive S3 enhancement."

    def _run(self, limit: str = "50", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import sqlite3
            db_path = "climate_knowledge_graph.db"

            # Get ALL datasets from the database
            limit_num = int(limit) if limit.isdigit() else 50

            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT dataset_id, title, short_name, dataset_properties, links, created_at
                    FROM stored_datasets
                    ORDER BY
                        CASE WHEN links IS NULL OR links = '[]' THEN 0 ELSE 1 END,  -- Prioritize datasets without links
                        created_at DESC
                    LIMIT ?
                """, (limit_num,))

                results = cursor.fetchall()

                if not results:
                    return f" No datasets found in the database.\n Run the Knowledge Graph agent first to populate the database with datasets."

                output = f" ALL STORED DATASETS ({len(results)} total, showing up to {limit_num}):\n\n"

                datasets_without_links = 0
                datasets_with_links = 0

                # Group datasets by data center for better organization
                by_data_center = {}

                for result in results:
                    dataset_id, title, short_name, props_json, links_json, created_at = result

                    # Parse properties to get data center and other info
                    data_center = "Unknown"
                    science_keywords = ""
                    try:
                        if props_json:
                            props = json.loads(props_json)
                            data_center = props.get('data_center', 'Unknown')
                            science_keywords = props.get('science_keywords', '')[:100]
                    except:
                        pass

                    # Status indicator - check if links exist and are not empty
                    has_links = False
                    if links_json:
                        try:
                            links_data = json.loads(links_json)
                            has_links = links_data and len(links_data) > 0
                        except:
                            pass

                    if has_links:
                        status = " Links Available"
                        datasets_with_links += 1
                    else:
                        status = " Needs Data Links"
                        datasets_without_links += 1

                    if data_center not in by_data_center:
                        by_data_center[data_center] = []

                    by_data_center[data_center].append({
                        'dataset_id': dataset_id,
                        'title': title,
                        'short_name': short_name,
                        'status': status,
                        'links': links_json,
                        'science_keywords': science_keywords,
                        'created_at': created_at
                    })

                # Display by data center
                for data_center, datasets in by_data_center.items():
                    output += f"🏢 **{data_center}** ({len(datasets)} datasets):\n"

                    for i, dataset in enumerate(datasets, 1):
                        title_display = dataset['title'][:60] + "..." if len(dataset['title']) > 60 else dataset['title']

                        output += f"   {i}. {title_display}\n"
                        output += f"       Short Name: {dataset['short_name']}\n"
                        output += f"       ID: {dataset['dataset_id']}\n"
                        output += f"       Status: {dataset['status']}\n"

                        if dataset['links']:
                            try:
                                links_data = json.loads(dataset['links'])
                                if links_data and len(links_data) > 0:
                                    output += f"       Data Links: {len(links_data)} available\n"
                                    # Show first link as sample
                                    first_link = links_data[0]
                                    if isinstance(first_link, dict) and first_link.get('url'):
                                        sample_url = first_link['url'][:50] + "..." if len(first_link['url']) > 50 else first_link['url']
                                        output += f"       Sample: {sample_url}\n"
                            except:
                                output += f"       Links: Available (parsing error)\n"

                        if dataset['science_keywords']:
                            output += f"       Keywords: {dataset['science_keywords']}...\n"

                        output += "\n"

                    output += "\n"

                # Summary
                output += f" COMPREHENSIVE SUMMARY:\n"
                output += f"   • Total datasets in database: {len(results)}\n"
                output += f"   • Datasets needing data links: {datasets_without_links} \n"
                output += f"   • Datasets with data access: {datasets_with_links} \n"
                output += f"   • Data centers represented: {len(by_data_center)}\n\n"

                output += f" COMPREHENSIVE ENHANCEMENT STRATEGY:\n"
                if datasets_without_links > 0:
                    output += f"   • Use 'process_all_datasets_for_data_access' to systematically find data links for ALL datasets\n"
                    output += f"   • Use 'find_data_access_for_dataset [dataset_id]' for individual dataset enhancement\n"
                    output += f"   • Use 'add_data_url_to_dataset' to configure data access after finding links\n"

                if datasets_with_links > 0:
                    output += f"   • Use 'load_data' to access data from datasets with configured links\n"

                output += f"\n ALL DATASETS AVAILABLE FOR RESEARCH - NO KEYWORD FILTERING APPLIED!"

                return output

        except Exception as e:
            return f" Error listing all stored datasets: {str(e)}"

class ProcessAllDatasetsForDataAccessTool(BaseTool):
    """Systematically process ALL datasets in the database to find and configure data access (Earthdata URLs and S3 paths)"""
    name: str = "process_all_datasets_for_data_access"
    description: str = "Process ALL datasets in the database systematically to find data access paths (Earthdata URLs and S3 paths). This inspects every dataset individually, checks link compatibility, and can replace existing paths with better ones or add access paths to datasets that lack them."

    def _run(self, batch_size: str = "10", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import sqlite3
            db_path = "climate_knowledge_graph.db"
            batch_size_num = int(batch_size) if batch_size.isdigit() else 10

            # Get ALL datasets that need links configuration
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT dataset_id, title, short_name, dataset_properties
                    FROM stored_datasets
                    WHERE links IS NULL OR links = '[]'
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (batch_size_num,))

                results = cursor.fetchall()

                if not results:
                    return f" All datasets already have data links configured!\n Use 'list_all_stored_datasets' to see the current status."

                output = f" PROCESSING ALL DATASETS FOR DATA ACCESS ENHANCEMENT\n"
                output += "=" * 60 + "\n\n"
                output += f" Processing {len(results)} datasets that need data access links...\n\n"

                successful_enhancements = 0
                failed_enhancements = 0

                for i, (dataset_id, title, short_name, props_json) in enumerate(results, 1):
                    output += f" DATASET {i}/{len(results)}: {title[:50]}...\n"
                    output += f"    ID: {dataset_id}\n"
                    output += f"    Short Name: {short_name}\n"

                    # Smart extraction of dataset-specific search terms
                    search_terms = []
                    data_center = "Unknown"

                    try:
                        if props_json:
                            props = json.loads(props_json)
                            data_center = props.get('data_center', 'Unknown')

                            # Simple search terms - let LLM decide relevance
                            search_terms = [short_name.lower(), title.lower()]

                    except Exception:
                        # Fallback to basic search terms
                        search_terms = [short_name.lower(), 'climate']

                    output += f"   🏢 Data Center: {data_center}\n"
                    output += f"    Search Terms: {', '.join(search_terms[:3])}\n"

                    # PRIORITY 1: Try to find data from Knowledge Graph CMR links (Earthdata first, then S3)
                    found_links = []

                    try:
                        metadata = kg_connector.get_dataset_metadata(dataset_id)
                        if metadata:
                            links = metadata.get('links', '')
                            if links:
                                # Categorize URLs into Earthdata and S3
                                categorized_urls = s3_connector.categorize_data_urls(links)

                                # Store all Earthdata URLs (highest priority)
                                for earthdata_url in categorized_urls["earthdata_urls"]:
                                    found_links.append({
                                        "url": earthdata_url,
                                        "type": "Earthdata",
                                        "source": "CMR_Earthdata",
                                        "description": "From CMR dataset Earthdata links",
                                        "access_method": "authenticated"
                                    })

                                # Add S3 URLs as backup
                                for s3_url in categorized_urls["s3_urls"]:
                                    if s3_connector.check_s3_path_exists(s3_url):
                                        found_links.append({
                                            "url": s3_url,
                                            "type": "S3",
                                            "source": "CMR_S3",
                                            "description": "From CMR dataset S3 links",
                                            "access_method": "anonymous"
                                        })
                    except Exception:
                        pass

                    # PRIORITY 2: Only if no dataset-specific links found, try AWS Open Data Registry as fallback
                    if not found_links and search_terms:
                        for term in search_terms[:2]:  # Try first 2 terms
                            matching_buckets = open_data_connector.search_open_data_buckets(term)

                            if matching_buckets:
                                for bucket in matching_buckets[:1]:  # Take best match
                                    bucket_name = bucket["bucket_name"]
                                    s3_path = f"s3://{bucket_name}"

                                    # Check accessibility
                                    access_info = open_data_connector.check_bucket_accessibility(bucket_name)
                                    if access_info.get("accessible", False):
                                        found_links.append({
                                            "url": s3_path,
                                            "type": "S3",
                                            "source": "AWS_Open_Data_Fallback",
                                            "description": bucket["description"],
                                            "access_method": "anonymous",
                                            "match_term": term
                                        })
                                        break

                    # Configure data access if found
                    if found_links:
                        # Store all found links
                        try:
                            # Update database with all found links
                            current_time = datetime.now().isoformat()
                            conn.execute("""
                                UPDATE stored_datasets
                                SET links = ?, updated_at = ?
                                WHERE dataset_id = ?
                            """, (json.dumps(found_links), current_time, dataset_id))

                            earthdata_count = sum(1 for link in found_links if link.get("type") == "Earthdata")
                            s3_count = sum(1 for link in found_links if link.get("type") == "S3")

                            output += f"    SUCCESS: Configured data access\n"
                            output += f"       Earthdata URLs: {earthdata_count}\n"
                            output += f"       S3 URLs: {s3_count}\n"
                            output += f"       Primary Source: {found_links[0].get('source', 'Unknown')}\n"
                            successful_enhancements += 1

                        except Exception as config_error:
                            output += f"    Found links but failed to configure: {str(config_error)[:50]}\n"
                            failed_enhancements += 1
                    else:
                        output += f"    No data access links found\n"
                        failed_enhancements += 1

                    output += "\n"

                # Final summary
                output += f" BATCH PROCESSING COMPLETE:\n"
                output += f"    Successfully enhanced: {successful_enhancements} datasets\n"
                output += f"    Could not enhance: {failed_enhancements} datasets\n"
                output += f"    Success rate: {(successful_enhancements/(successful_enhancements+failed_enhancements)*100):.1f}%\n\n"

                if successful_enhancements > 0:
                    output += f" NEXT STEPS:\n"
                    output += f"   • Use 'list_all_stored_datasets' to see updated status\n"
                    output += f"   • Use 'load_s3_data' to test access to configured datasets\n"
                    output += f"   • Run 'process_all_datasets_for_s3' again to process more datasets\n"

            return output

        except Exception as e:
            return f" Error processing all datasets for S3: {str(e)}"



class FindDataAccessForDatasetTool(BaseTool):
    """Find data access locations (Earthdata URLs and S3 paths) for an existing stored dataset"""
    name: str = "find_data_access_for_dataset"
    description: str = "Find data access locations (Earthdata URLs and S3 paths) for a dataset that's already stored in the database but lacks data access. Searches CMR metadata first, then AWS Open Data as fallback."

    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import sqlite3
            db_path = "climate_knowledge_graph.db"

            # Get the stored dataset info
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT dataset_id, title, short_name, dataset_properties, links
                    FROM stored_datasets WHERE dataset_id = ?
                """, (dataset_id.strip(),))

                result = cursor.fetchone()

                if not result:
                    return f" Dataset not found: {dataset_id}\n Use 'search_stored_datasets' to find available datasets first."

                dataset_id, title, short_name, props_json, existing_links_json = result

                # Check if dataset already has data access links
                existing_links = []
                if existing_links_json:
                    try:
                        existing_links = json.loads(existing_links_json)
                    except json.JSONDecodeError:
                        existing_links = []

                if existing_links:
                    return f" Dataset already has data access configured: {len(existing_links)} links available\n Use 'load_data' to access the data directly."

                output = f" FINDING S3 DATA FOR EXISTING DATASET\n"
                output += "=" * 50 + "\n\n"
                output += f" Dataset: {title}\n"
                output += f"🔖 Short Name: {short_name}\n"
                output += f" ID: {dataset_id}\n\n"

                # Parse dataset properties to extract useful search terms
                search_terms = []
                data_center = "Unknown"
                science_keywords = ""

                try:
                    if props_json:
                        props = json.loads(props_json)
                        data_center = props.get('data_center', 'Unknown')
                        science_keywords = props.get('science_keywords', '')

                        # Let LLM analyze what search terms are relevant
                        search_terms = [short_name.lower(), title.lower()]

                except Exception as parse_error:
                    output += f" Could not parse dataset properties: {str(parse_error)[:50]}\n"

                output += f"🏢 Data Center: {data_center}\n"
                output += f" Search Terms: {', '.join(search_terms[:5])}\n\n"

                # Method 1: Check Knowledge Graph for CMR links (PRIORITY)
                output += f"🥇 METHOD 1: Knowledge Graph CMR Links (Dataset Metadata)\n"
                found_s3_paths = []

                try:
                    # Query the knowledge graph for this dataset's metadata
                    metadata = kg_connector.get_dataset_metadata(dataset_id)

                    if metadata:
                        links = metadata.get('links', '')
                        if links:
                            # Extract and prioritize data URLs (Earthdata first, then NOAA, then S3)
                            categorized_urls = s3_connector.categorize_data_urls(links)
                            all_data_urls = categorized_urls["earthdata_urls"] + categorized_urls["noaa_urls"] + categorized_urls["s3_urls"]

                            if all_data_urls:
                                earthdata_count = len(categorized_urls["earthdata_urls"])
                                noaa_count = len(categorized_urls["noaa_urls"])
                                s3_count = len(categorized_urls["s3_urls"])

                                url_summary = []
                                if earthdata_count > 0:
                                    url_summary.append(f"{earthdata_count} Earthdata")
                                if noaa_count > 0:
                                    url_summary.append(f"{noaa_count} NOAA")
                                if s3_count > 0:
                                    url_summary.append(f"{s3_count} S3")

                                output += f"    Found {' + '.join(url_summary)} URLs in CMR metadata:\n"

                                for data_url in all_data_urls[:3]:  # Show first 3 (Earthdata/NOAA first)
                                    if s3_connector.earthdata_auth.is_earthdata_url(data_url):
                                        url_type = " Earthdata"
                                        status_desc = " Requires Auth"
                                    elif s3_connector.noaa_api.is_noaa_url(data_url):
                                        url_type = "🌡️ NOAA"
                                        status_desc = " API Access"
                                    else:
                                        url_type = " S3"
                                        status_desc = " Accessible" if s3_connector.check_s3_path_exists(data_url) else " Not accessible"

                                    output += f"       {url_type} {data_url[:60]}... - {status_desc}\n"

                                    # Add to found paths list (Earthdata and NOAA URLs are prioritized)
                                    if s3_connector.earthdata_auth.is_earthdata_url(data_url) or s3_connector.noaa_api.is_noaa_url(data_url) or (data_url.startswith('s3://') and s3_connector.check_s3_path_exists(data_url)):
                                        found_s3_paths.append({
                                            "path": data_url,
                                            "source": "CMR_Metadata",
                                            "description": "From CMR dataset links",
                                            "match_term": "metadata"
                                        })
                            else:
                                output += f"   ⚪ No S3 paths found in CMR links\n"
                        else:
                            output += f"   ⚪ No links found in CMR metadata\n"
                    else:
                        output += f"    Could not retrieve CMR metadata\n"

                except Exception as cmr_error:
                    output += f"    CMR search failed: {str(cmr_error)[:50]}\n"

                output += "\n"

                # Method 2: AWS Open Data Registry (FALLBACK ONLY)
                if not found_s3_paths and search_terms:
                    output += f"🥈 METHOD 2: AWS Open Data Registry (Fallback Only)\n"

                    try:
                        # Only try AWS Open Data if no dataset-specific links were found
                        matching_buckets = open_data_connector.search_buckets(search_terms[:3])  # Use first 3 search terms

                        if matching_buckets:
                            output += f"    Found {len(matching_buckets)} potential matches in AWS Open Data:\n"

                            # Add matches as potential S3 paths
                            for bucket_info in matching_buckets[:2]:  # Limit to top 2 matches
                                bucket_name = bucket_info["bucket_name"]
                                s3_path = f"s3://{bucket_name}/"

                                # Check if bucket is accessible
                                if open_data_connector.check_bucket_accessible(bucket_name):
                                    output += f"        S3 {s3_path} -  Accessible (Generic Match)\n"
                                    found_s3_paths.append({
                                        "path": s3_path,
                                        "source": "AWS_Open_Data_Fallback",
                                        "description": f"AWS Open Data fallback match for {bucket_info.get('description', 'dataset')}",
                                        "match_term": "fallback_search"
                                    })
                                else:
                                    output += f"        S3 {s3_path} -  Not accessible\n"
                        else:
                            output += f"   ⚪ No matches found in AWS Open Data Registry\n"

                    except Exception as aws_error:
                        output += f"    AWS Open Data search failed: {str(aws_error)[:50]}\n"

                    output += "\n"
                elif found_s3_paths:
                    output += f" Skipping AWS Open Data Registry - Dataset metadata links found\n\n"

                # Summary and recommendations
                output += f" SEARCH RESULTS SUMMARY:\n"
                output += f"   • Found {len(found_s3_paths)} accessible S3 locations\n"

                if found_s3_paths:
                    output += f"\n RECOMMENDED S3 PATHS:\n"

                    for i, s3_info in enumerate(found_s3_paths[:3], 1):
                        path = s3_info["path"]
                        source = s3_info["source"]
                        description = s3_info["description"]

                        output += f"{i}. {path}\n"
                        output += f"    Source: {source}\n"
                        output += f"    Description: {description[:60]}...\n"
                        output += f"    Command: add_s3_path_to_dataset {dataset_id}|{path}|{{\"source\":\"{source}\"}}\n\n"

                    # Auto-configure the best option
                    best_path = found_s3_paths[0]["path"]
                    best_source = found_s3_paths[0]["source"]

                    output += f" AUTO-CONFIGURATION AVAILABLE:\n"
                    output += f"   Best match: {best_path}\n"
                    output += f"   Use: add_s3_path_to_dataset {dataset_id}|{best_path}|{{\"source\":\"{best_source}\",\"auto_found\":true}}\n"

                else:
                    output += f"\n NO S3 PATHS FOUND\n"
                    output += f" Possible reasons:\n"
                    output += f"   • Dataset not available in AWS Open Data Registry\n"
                    output += f"   • S3 paths require authentication\n"
                    output += f"   • Data may be in different format or location\n"
                    output += f"   • Try manual search with 'search_aws_open_data' using different keywords\n"

                return output

        except Exception as e:
            return f" Error finding S3 data for dataset: {str(e)}"

class InspectDatasetMetadataTool(BaseTool):
    """Get detailed metadata and data access information for a specific dataset"""
    name: str = "inspect_dataset_metadata"
    description: str = "Get complete metadata, data access links, and S3 locations for a specific NASA CMR dataset using its ID."

    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Get dataset metadata
            metadata = kg_connector.get_dataset_metadata(dataset_id)
            if not metadata:
                return f" Dataset not found: {dataset_id}"

            # Get relationships
            relationships = kg_connector.get_dataset_relationships(dataset_id)

            # Extract key information
            title = metadata.get('title', 'No title')
            short_name = metadata.get('short_name', 'unknown')
            data_center = metadata.get('data_center', 'unknown')
            doi = metadata.get('doi', 'Not available')
            links = metadata.get('links', '')
            science_keywords = metadata.get('science_keywords', '')

            # Extract S3 paths
            s3_paths = s3_connector.extract_s3_paths_from_links(links)

            output = f" DATASET METADATA: {dataset_id}\n"
            output += "=" * 60 + "\n\n"

            output += f" Title: {title}\n"
            output += f"🔖 Short Name: {short_name}\n"
            output += f"🏢 Data Center: {data_center}\n"
            output += f" DOI: {doi}\n\n"

            # Science keywords
            if science_keywords:
                output += f" Science Keywords:\n{science_keywords[:200]}...\n\n"

            # S3 data locations
            if s3_paths:
                output += f" DATA ACCESS LOCATIONS ({len(s3_paths)} found):\n"
                for i, s3_path in enumerate(s3_paths[:5]):  # Show first 5
                    exists = s3_connector.check_s3_path_exists(s3_path)
                    status = " Available" if exists else " Not accessible"
                    output += f"  {i+1}. {s3_path} - {status}\n"

                if len(s3_paths) > 5:
                    output += f"  ... and {len(s3_paths) - 5} more locations\n"
                output += "\n"
            else:
                output += " No S3 data locations found in metadata\n\n"

            # Related entities
            if relationships:
                output += f" RELATED ENTITIES:\n"
                for rel_type, entities in relationships.items():
                    output += f"  • {rel_type}: {len(entities)} items\n"
                output += "\n"

            output += f" Use 'query_s3_data_locations' to explore available data files"

            return output

        except Exception as e:
            return f" Error inspecting dataset metadata: {str(e)}"

class QueryDataLocationsTool(BaseTool):
    """Explore data locations (S3 and Earthdata) and list available files"""
    name: str = "query_data_locations"
    description: str = "Explore data access locations for a dataset (S3 buckets and Earthdata URLs) and list available data files with their formats and sizes."

    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Get dataset metadata to extract data access paths
            metadata = kg_connector.get_dataset_metadata(dataset_id)
            if not metadata:
                return f" Dataset not found: {dataset_id}"

            links = metadata.get('links', '')
            data_paths = s3_connector.extract_s3_paths_from_links(links)  # Legacy name but gets all URLs

            if not data_paths:
                return f" No data access paths found for dataset {dataset_id}"

            output = f" DATA ACCESS EXPLORATION: {dataset_id}\n"
            output += "=" * 50 + "\n\n"

            total_files = 0

            for i, data_path in enumerate(data_paths[:3]):  # Explore first 3 paths
                output += f"📁 Location {i+1}: {data_path}\n"

                if not s3_connector.check_s3_path_exists(data_path):
                    output += "    Path not accessible\n\n"
                    continue

                # List contents
                contents = s3_connector.list_s3_contents(data_path)

                if not contents:
                    output += "   📭 No files found\n\n"
                    continue

                data_files = []
                for item in contents[:10]:  # Show first 10 files
                    format_type = s3_connector.detect_data_format(item)
                    data_files.append({"path": item, "format": format_type})

                output += f"    Found {len(contents)} items (showing first {len(data_files)}):\n"

                for j, file_info in enumerate(data_files):
                    file_path = file_info["path"]
                    file_format = file_info["format"]
                    filename = Path(file_path).name
                    output += f"   {j+1}. {filename} ({file_format})\n"

                if len(contents) > 10:
                    output += f"   ... and {len(contents) - 10} more files\n"

                total_files += len(contents)
                output += "\n"

            if len(data_paths) > 3:
                output += f"... and {len(data_paths) - 3} more data locations to explore\n\n"

            output += f" SUMMARY: {total_files} total files found across {len(data_paths)} data locations\n"
            output += f" Use 'load_s3_data' to load specific files for analysis"

            return output

        except Exception as e:
            return f" Error querying S3 data locations: {str(e)}"

class LoadS3DataTool(BaseTool):
    """Load and preview data from S3 locations or Earthdata URLs"""
    name: str = "load_data"
    description: str = "Load and preview data from S3 paths or Earthdata URLs. Automatically detects Earthdata URLs and uses authentication. Supports all data formats with full file access (no size limits)."

    def _run(self, path_or_url: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            print(f" Loading data from: {path_or_url}")

            # Check if this is a search URL (not an actual data file URL)
            if "search.earthdata.nasa.gov/search" in path_or_url or "/search?" in path_or_url:
                return f" ❌ This is a search URL, not a direct data file URL.\n" + \
                       f" Searching for data files in: {path_or_url}\n" + \
                       f" Path does not exist: {path_or_url}\n" + \
                       f" No data files found at {path_or_url}. Try a specific file path or explore the bucket structure first.\n\n" + \
                       f" 💡 To access actual data:\n" + \
                       f"   • Use 'find_data_access_for_dataset [dataset_id]' to find direct data URLs\n" + \
                       f"   • Use 'query_data_locations [dataset_id]' to explore available files\n" + \
                       f"   • Use 'search_aws_open_data' to find S3 data sources"

            # Check if it's an Earthdata URL
            if s3_connector.earthdata_auth.is_earthdata_url(path_or_url):
                print(" Using Earthdata authentication")
                # Load directly from Earthdata URL
                data = s3_connector.load_data_from_url_or_s3(path_or_url, sample_only=False)
            else:
                # S3 path - first try to find actual data files if this is a directory
                data_files = s3_connector.find_actual_data_files(path_or_url, max_files=5)

                if not data_files:
                    return f" No data files found at {path_or_url}. Try a specific file path or explore the bucket structure first."

                # Use the first data file found
                actual_file = data_files[0]
                print(f" Found data file: {Path(actual_file).name}")
                path_or_url = actual_file

                # Load data without size limits
                data = s3_connector.load_data_from_url_or_s3(path_or_url, sample_only=False)

            if data is None:
                return f" Failed to load data from {path_or_url}"

            if isinstance(data, dict):
                if "error" in data:
                    return f" Error loading data: {data['error']}"
                elif "stream_response" in data:
                    # Handle Earthdata stream response
                    return self._handle_earthdata_stream(data)


            output = f" DATA PREVIEW: {path_or_url}\n"
            output += "=" * 60 + "\n\n"

            # Show file discovery info
            if len(data_files) > 1:
                output += f" Found {len(data_files)} data files, loading first one: {Path(actual_file).name}\n"
                output += f" Other files available: {[Path(f).name for f in data_files[1:3]]}\n\n"

            # Handle different data types
            if hasattr(data, 'dims'):  # xarray Dataset
                output += f" Type: NetCDF Dataset\n"
                output += f"📐 Dimensions: {dict(data.dims)}\n"
                output += f" Variables: {list(data.data_vars)}\n"
                output += f" Coordinates: {list(data.coords)}\n"

                # Show sample of first variable
                if data.data_vars:
                    first_var = list(data.data_vars)[0]
                    var_data = data[first_var]
                    output += f"\n Sample variable '{first_var}':\n"
                    output += f"   Shape: {var_data.shape}\n"
                    output += f"   Data type: {var_data.dtype}\n"
                    if hasattr(var_data, 'attrs'):
                        output += f"   Attributes: {len(var_data.attrs)} items\n"

            elif hasattr(data, 'shape'):  # Polars DataFrame
                output += f" Type: Tabular Data (CSV)\n"
                output += f"📐 Shape: {data.shape}\n"
                output += f" Columns: {data.columns}\n"

                # Show data types
                output += f"\n Column Types:\n"
                for col in data.columns[:10]:  # First 10 columns
                    output += f"   {col}: {data[col].dtype}\n"

                # Show sample data
                output += f"\n Sample Data (first 3 rows):\n"
                sample = data.head(3)
                output += str(sample) + "\n"

            elif isinstance(data, dict):
                if "hdf_structure" in data:
                    output += f" Type: HDF5/HDF4 File Structure\n"
                    structure = data["hdf_structure"]
                    output += f" Root Groups/Datasets: {len(structure)}\n"

                    output += f"\n HDF Structure:\n"
                    for key, info in list(structure.items())[:10]:
                        if isinstance(info, dict):
                            item_type = info.get("type", "unknown")
                            if item_type == "dataset":
                                shape = info.get("shape", "unknown")
                                dtype = info.get("dtype", "unknown")
                                output += f"    {key}: Dataset {shape} ({dtype})\n"
                            elif item_type == "group":
                                contents = info.get("contents", {})
                                output += f"   📁 {key}: Group with {len(contents)} items\n"
                else:
                    output += f" Type: JSON Data\n"
                    output += f" Keys: {list(data.keys())[:10]}\n"
                    output += f" Total entries: {len(data)}\n"

            output += f"\n Data successfully loaded and available for full analysis"
            output += f"\n Complete file access enabled - no size restrictions applied."

            return output

        except Exception as e:
            return f" Error loading S3 data: {str(e)}"

    def _handle_earthdata_stream(self, data: Dict) -> str:
        """Handle Earthdata stream response"""
        try:
            stream_response = data["stream_response"]
            url = data["url"]
            content_length = data.get("content_length")

            output = f" EARTHDATA STREAM ACCESS: {url}\n"
            output += "=" * 60 + "\n\n"

            output += f" Source: NASA Earthdata (Authenticated)\n"
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                output += f" File size: {size_mb:.2f} MB\n"

            output += f"📡 Stream status: {stream_response.status_code}\n"
            output += f" Content type: {stream_response.headers.get('content-type', 'unknown')}\n"

            # Show available headers for debugging
            output += f"\n Available headers:\n"
            for header, value in list(stream_response.headers.items())[:10]:
                output += f"   {header}: {value}\n"

            output += f"\n Earthdata stream successfully opened and authenticated"
            output += f"\n The stream is ready for processing. Use appropriate tools based on the content type."
            output += f"\n Direct URL access available for further processing"

            return output

        except Exception as e:
            return f" Error handling Earthdata stream: {str(e)}"

class LoadSeaSurfaceTemperatureDataTool(BaseTool):
    """Specifically load sea surface temperature data from known sources"""
    name: str = "load_sea_surface_temperature_data"
    description: str = "Load actual sea surface temperature data from known NASA/NOAA sources in AWS Open Data. This tool directly accesses SST data files."

    def _find_data_files_recursive(self, base_path: str, max_depth: int = 3, current_depth: int = 0) -> List[str]:
        """Recursively find actual data files in S3 directories"""
        data_files = []

        if current_depth >= max_depth:
            return data_files

        try:
            contents = open_data_connector.s3_fs.ls(base_path)

            for item in contents[:20]:  # Limit to avoid too many API calls
                path_obj = Path(item)

                # Check if it's a data file (NASA files often have no extensions!)
                filename = path_obj.name.upper()
                if (path_obj.suffix.lower() in ['.nc', '.nc4', '.hdf', '.hdf5', '.h5'] or
                    # NASA naming patterns without extensions
                    filename.startswith(('MOD', 'MYD', 'MCD')) or  # MODIS products
                    'ABI-L2' in filename or  # GOES ABI Level 2
                    'SST' in filename or     # Sea Surface Temperature
                    'L2' in filename or      # Level 2 products
                    filename.endswith('.006') or  # MODIS collection 6
                    filename.endswith('.061')):   # MODIS collection 6.1
                    data_files.append(item)
                # If it's a directory and we haven't reached max depth, recurse
                elif not path_obj.suffix and current_depth < max_depth - 1:
                    sub_files = self._find_data_files_recursive(item, max_depth, current_depth + 1)
                    data_files.extend(sub_files)

                # Stop if we found enough files
                if len(data_files) >= 5:
                    break

        except Exception:
            pass  # Ignore errors in directory exploration

        return data_files

    def _run(self, data_source: str = "auto", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Known SST data locations in AWS Open Data
            sst_sources = {
                "goes16": {
                    "bucket": "noaa-goes16",
                    "description": "GOES-16 ABI L2 Sea Surface Temperature",
                    "sample_path": "noaa-goes16/ABI-L2-SSTF",
                    "format": "NetCDF"
                },
                "goes17": {
                    "bucket": "noaa-goes17",
                    "description": "GOES-17 ABI L2 Sea Surface Temperature",
                    "sample_path": "noaa-goes17/ABI-L2-SSTF",
                    "format": "NetCDF"
                },
                "modis": {
                    "bucket": "modis-pds",
                    "description": "MODIS Sea Surface Temperature (if available)",
                    "sample_path": "modis-pds",
                    "format": "HDF4/NetCDF"
                }
            }

            output = f" LOADING SEA SURFACE TEMPERATURE DATA\n"
            output += "=" * 50 + "\n\n"

            successful_loads = 0

            # Try each known SST source
            for source_name, source_info in sst_sources.items():
                bucket = source_info["bucket"]
                description = source_info["description"]

                output += f"📡 Trying {source_name.upper()}: {description}\n"

                # Check if bucket is accessible
                access_info = open_data_connector.check_bucket_accessibility(bucket)

                if not access_info.get("accessible", False):
                    output += f"    Bucket {bucket} not accessible\n\n"
                    continue

                output += f"    Bucket {bucket} is accessible\n"

                # Try to find SST-specific files
                try:
                    # List contents looking for SST files
                    bucket_path = f"s3://{bucket}"
                    contents = open_data_connector.s3_fs.ls(bucket_path)

                    # Look for SST-related directories or files
                    sst_candidates = []
                    for item in contents[:20]:  # Check first 20 items
                        item_name = item.lower()
                        if any(sst_term in item_name for sst_term in ['sst', 'temperature', 'temp', 'l2']):
                            sst_candidates.append(item)

                    if sst_candidates:
                        output += f"    Found {len(sst_candidates)} potential SST locations:\n"
                        for candidate in sst_candidates[:3]:
                            output += f"      • {Path(candidate).name}\n"

                        # Try to load from the first candidate
                        first_candidate = sst_candidates[0]

                        # If it's a directory, look inside for actual files
                        if not Path(first_candidate).suffix:
                            try:
                                # Recursively explore to find actual data files
                                output += f"    Exploring directory: {Path(first_candidate).name}\n"
                                data_files = self._find_data_files_recursive(first_candidate, max_depth=3)

                                if data_files:
                                    output += f"    Found {len(data_files)} data files\n"
                                    sample_file = data_files[0]
                                    output += f"    Attempting to load: {Path(sample_file).name}\n"

                                    # Try to load the data
                                    data = s3_connector.load_data_from_s3(sample_file)

                                    if data and not (isinstance(data, dict) and "error" in data):
                                        output += f"    Successfully loaded SST data!\n"
                                        output += f"    File: {sample_file}\n"

                                        # Describe the data
                                        if hasattr(data, 'data_vars'):
                                            vars_list = list(data.data_vars)
                                            output += f"    Variables: {vars_list[:5]}\n"
                                            if hasattr(data, 'dims'):
                                                output += f"   📐 Dimensions: {dict(data.dims)}\n"

                                        successful_loads += 1
                                    else:
                                        if isinstance(data, dict) and "error" in data:
                                            output += f"    Load error: {data['error']}\n"
                                        else:
                                            output += f"    Failed to load data\n"
                                else:
                                    output += f"    No data files found in directory structure\n"

                            except Exception as sub_error:
                                output += f"    Error exploring subdirectory: {str(sub_error)[:50]}\n"
                        else:
                            # Direct file - try to load it
                            output += f"    Attempting to load: {Path(first_candidate).name}\n"
                            data = s3_connector.load_data_from_s3(first_candidate)

                            if data and not (isinstance(data, dict) and "error" in data):
                                output += f"    Successfully loaded data!\n"
                                successful_loads += 1
                    else:
                        output += f"    No obvious SST files found in top-level directory\n"

                except Exception as e:
                    output += f"    Error accessing bucket contents: {str(e)[:50]}\n"

                output += "\n"

            # Summary
            output += f" SUMMARY:\n"
            output += f"    Successfully loaded data from {successful_loads} sources\n"
            output += f"    Checked {len(sst_sources)} potential SST data sources\n\n"

            if successful_loads > 0:
                output += f" SUCCESS: Found and loaded sea surface temperature data!\n"
                output += f" Use this data for your ocean temperature analysis.\n"
            else:
                output += f" No SST data successfully loaded. Possible reasons:\n"
                output += f"   • Different file organization than expected\n"
                output += f"   • Files require different access methods\n"
                output += f"   • Network connectivity issues\n"
                output += f" Try exploring specific buckets manually with 'explore_aws_open_data_bucket'\n"

            return output

        except Exception as e:
            return f" Error loading sea surface temperature data: {str(e)}"

class DebugS3StructureTool(BaseTool):
    """Debug tool to explore S3 bucket structure in detail"""
    name: str = "debug_s3_structure"
    description: str = "Debug tool to explore deep S3 directory structures and find actual data files. Use this to troubleshoot data access issues."

    def _run(self, s3_path: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            output = f" DEBUGGING S3 STRUCTURE: {s3_path}\n"
            output += "=" * 60 + "\n\n"

            if not s3_connector.s3_fs:
                return " S3 filesystem not available"

            # Check if path exists
            exists = s3_connector.s3_fs.exists(s3_path)
            output += f" Path exists: {exists}\n\n"

            if not exists:
                return output + " Path does not exist"

            # List contents recursively with detailed info
            def explore_recursive(path, depth=0, max_depth=5):
                if depth > max_depth:
                    return "  " * depth + "... (max depth reached)\n"

                result = ""
                try:
                    contents = s3_connector.s3_fs.ls(path)
                    result += "  " * depth + f"📁 {Path(path).name}/ ({len(contents)} items)\n"

                    # Show first few items
                    for item in contents[:5]:
                        item_name = Path(item).name

                        # Check if it's a file
                        if Path(item).suffix:
                            size_info = ""
                            try:
                                info = s3_connector.s3_fs.info(item)
                                size_mb = info.get('size', 0) / (1024*1024)
                                size_info = f" ({size_mb:.1f}MB)"
                            except:
                                pass
                            result += "  " * (depth+1) + f" {item_name}{size_info}\n"
                        else:
                            # It's a directory - recurse if not too deep
                            if depth < 3:  # Limit recursion
                                result += explore_recursive(item, depth+1, max_depth)
                            else:
                                result += "  " * (depth+1) + f"📁 {item_name}/ (not explored)\n"

                    if len(contents) > 5:
                        result += "  " * (depth+1) + f"... and {len(contents)-5} more items\n"

                except Exception as e:
                    result += "  " * depth + f" Error: {str(e)[:50]}\n"

                return result

            output += explore_recursive(s3_path)

            # Try to find any .nc files specifically
            output += "\n SEARCHING FOR DATA FILES:\n"
            try:
                # Use AWS SDK directly for more control
                import boto3
                from botocore import UNSIGNED
                from botocore.config import Config

                s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
                bucket = s3_path.replace('s3://', '').split('/')[0]
                prefix = '/'.join(s3_path.replace('s3://', '').split('/')[1:])

                response = s3_client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix,
                    MaxKeys=10
                )

                files_found = []
                for obj in response.get('Contents', []):
                    key = obj['Key']
                    filename = Path(key).name.upper()
                    if (key.endswith(('.nc', '.nc4', '.hdf', '.h5')) or
                        filename.startswith(('MOD', 'MYD', 'MCD')) or
                        'ABI-L2' in filename or 'SST' in filename or
                        filename.endswith(('.006', '.061'))):
                        size_mb = obj['Size'] / (1024*1024)
                        files_found.append(f"{key} ({size_mb:.1f}MB)")

                if files_found:
                    output += f" Found {len(files_found)} data files:\n"
                    for file_info in files_found[:5]:
                        output += f"  • {file_info}\n"
                else:
                    output += " No .nc/.hdf files found in this location\n"

            except Exception as e:
                output += f" Advanced search failed: {str(e)}\n"

            return output

        except Exception as e:
            return f" Debug failed: {str(e)}"

class ExploreSubdirectoriesTool(BaseTool):
    """Smart tool to explore S3 subdirectories using NASA data patterns for selective navigation"""
    name: str = "explore_subdirectories"
    description: str = "Intelligently explore S3 subdirectories using NASA data patterns. Supports pattern-based filtering (date_range, data_type, recent) to avoid exhaustive exploration. Use pattern='auto' for smart detection."

    def _run(self, s3_path: str, max_depth: int = 2, pattern: str = "auto", date_range: str = "recent", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            output = f" SUBDIRECTORY EXPLORATION: {s3_path}\n"
            output += "=" * 70 + "\n\n"

            if not s3_connector.s3_fs:
                return " S3 filesystem not available"

            # Validate path exists
            if not s3_connector.s3_fs.exists(s3_path):
                return f" Path does not exist: {s3_path}"

            def detect_pattern_repetition(directories: List[str]) -> Dict[str, any]:
                """Detect if directories follow a repetitive pattern"""
                if len(directories) < 3:
                    return {"is_repetitive": False}

                # Check for numeric patterns (dates, hours, etc.)
                numeric_dirs = [d for d in directories if Path(d).name.isdigit()]
                if len(numeric_dirs) >= len(directories) * 0.8:  # 80% are numeric
                    return {
                        "is_repetitive": True,
                        "pattern_type": "numeric_sequence",
                        "sample_size": min(3, len(numeric_dirs))
                    }

                # Check for similar naming patterns
                dir_names = [Path(d).name for d in directories]
                if len(set(len(name) for name in dir_names)) == 1:  # Same length names
                    return {
                        "is_repetitive": True,
                        "pattern_type": "uniform_naming",
                        "sample_size": min(3, len(directories))
                    }

                return {"is_repetitive": False}

            def explore_recursive(path: str, current_depth: int = 0, max_items_per_level: int = 15) -> str:
                """Smart exploration that detects and handles repetitive patterns"""
                result = ""
                indent = "  " * current_depth

                if current_depth >= max_depth:
                    return f"{indent}📁 {Path(path).name}/ (max depth reached)\n"

                try:
                    contents = s3_connector.s3_fs.ls(path)
                    dir_name = Path(path).name or "root"
                    result += f"{indent}📁 {dir_name}/ ({len(contents)} items)\n"

                    # Separate files and directories
                    files = []
                    directories = []
                    data_files = []

                    for item in contents:
                        item_path = Path(item)
                        filename = item_path.name.upper()

                        # Categorize items
                        if item_path.suffix:  # Has extension - likely a file
                            files.append(item)
                            # Check if it's a NASA data file
                            if (item_path.suffix.lower() in ['.nc', '.nc4', '.hdf', '.hdf5', '.h5', '.zarr'] or
                                filename.startswith(('MOD', 'MYD', 'MCD', 'OR_ABI')) or
                                'SST' in filename or 'L2' in filename or 'L3' in filename or
                                filename.endswith(('.006', '.061', '.005'))):
                                data_files.append(item)
                        else:  # No extension - likely a directory
                            directories.append(item)

                    # Show data files first (most important)
                    if data_files:
                        result += f"{indent}   DATA FILES ({len(data_files)} found):\n"
                        for i, data_file in enumerate(data_files[:max_items_per_level]):
                            file_name = Path(data_file).name
                            try:
                                info = s3_connector.s3_fs.info(data_file)
                                size_mb = info.get('size', 0) / (1024*1024)
                                size_str = f" ({size_mb:.1f}MB)" if size_mb > 0 else ""
                            except:
                                size_str = ""

                            format_type = s3_connector.detect_data_format(data_file)
                            result += f"{indent}     {file_name}{size_str} [{format_type}]\n"

                        if len(data_files) > max_items_per_level:
                            result += f"{indent}    ... and {len(data_files) - max_items_per_level} more data files\n"
                        result += "\n"

                    # Show other files
                    other_files = [f for f in files if f not in data_files]
                    if other_files:
                        result += f"{indent}   OTHER FILES ({len(other_files)}):\n"
                        for i, file_item in enumerate(other_files[:5]):  # Show first 5
                            file_name = Path(file_item).name
                            try:
                                info = s3_connector.s3_fs.info(file_item)
                                size_mb = info.get('size', 0) / (1024*1024)
                                size_str = f" ({size_mb:.1f}MB)" if size_mb > 0 else ""
                            except:
                                size_str = ""
                            result += f"{indent}     {file_name}{size_str}\n"

                        if len(other_files) > 5:
                            result += f"{indent}    ... and {len(other_files) - 5} more files\n"
                        result += "\n"

                    # Smart directory exploration with pattern detection
                    if directories and current_depth < max_depth - 1:
                        # Detect repetitive patterns
                        pattern_info = detect_pattern_repetition(directories)

                        if pattern_info["is_repetitive"]:
                            # Handle repetitive patterns smartly
                            sample_size = pattern_info["sample_size"]
                            pattern_type = pattern_info["pattern_type"]

                            result += f"{indent}  📂 PATTERN DETECTED: {pattern_type} ({len(directories)} similar dirs)\n"

                            if pattern_type == "numeric_sequence":
                                # For date/time patterns, sample first, middle, and last
                                sorted_dirs = sorted(directories, key=lambda x: int(Path(x).name) if Path(x).name.isdigit() else 0)
                                if len(sorted_dirs) >= 3:
                                    sample_dirs = [sorted_dirs[0], sorted_dirs[len(sorted_dirs)//2], sorted_dirs[-1]]
                                else:
                                    sample_dirs = sorted_dirs[:sample_size]

                                result += f"{indent}     Sampling: {Path(sample_dirs[0]).name} ... {Path(sample_dirs[-1]).name}\n"
                            else:
                                # For other patterns, just sample first few
                                sample_dirs = directories[:sample_size]
                                result += f"{indent}     Sampling first {sample_size} directories\n"

                            # Explore only sampled directories
                            for directory in sample_dirs:
                                dir_name = Path(directory).name
                                result += f"{indent}    📂 {dir_name}/\n"

                                try:
                                    sub_result = explore_recursive(directory, current_depth + 1, max_items_per_level)
                                    result += sub_result
                                except Exception as sub_error:
                                    result += f"{indent}       Error: {str(sub_error)[:30]}\n"

                            # Show pattern summary
                            skipped = len(directories) - len(sample_dirs)
                            if skipped > 0:
                                result += f"{indent}     Pattern continues for {skipped} more directories\n"

                        else:
                            # No repetitive pattern - explore normally but limit
                            explore_limit = min(5, len(directories))  # Reduced from 8 to 5
                            result += f"{indent}  📂 SUBDIRECTORIES ({len(directories)}):\n"

                            for directory in directories[:explore_limit]:
                                dir_name = Path(directory).name
                                result += f"{indent}    📂 {dir_name}/\n"

                                try:
                                    sub_result = explore_recursive(directory, current_depth + 1, max_items_per_level)
                                    result += sub_result
                                except Exception as sub_error:
                                    result += f"{indent}       Error: {str(sub_error)[:30]}\n"

                            if len(directories) > explore_limit:
                                result += f"{indent}    📁 ... and {len(directories) - explore_limit} more directories\n"

                    elif directories:
                        result += f"{indent}  📂 SUBDIRECTORIES ({len(directories)}) - at max depth:\n"
                        for directory in directories[:10]:
                            dir_name = Path(directory).name
                            result += f"{indent}    📂 {dir_name}/ (use 'explore_subdirectories {directory}' to explore)\n"
                        if len(directories) > 10:
                            result += f"{indent}    ... and {len(directories) - 10} more directories\n"

                    result += "\n"

                except Exception as e:
                    result += f"{indent} Error exploring {Path(path).name}: {str(e)[:100]}\n"

                return result

            # Start recursive exploration
            exploration_result = explore_recursive(s3_path, 0)
            output += exploration_result

            # Add smart navigation tips
            output += f"🧭 SMART NAVIGATION:\n"
            output += f"   • Pattern detection prevents repetitive loops\n"
            output += f"   • Numeric sequences (dates/hours) are intelligently sampled\n"
            output += f"   • Use specific paths for detailed exploration: 's3://bucket/path/2024/001/12'\n"
            output += f"   • Current settings: depth={max_depth}, pattern={pattern}, date_range={date_range}\n\n"

            output += f" Optimized usage:\n"
            output += f"   explore_subdirectories s3://noaa-goes16/ABI-L2-SSTF max_depth=2 pattern=auto\n"
            output += f"   explore_subdirectories s3://bucket/specific/2024/339 max_depth=3\n"
            output += f"   load_s3_data [discovered_file_path]"

            return output

        except Exception as e:
            return f" Error exploring subdirectories: {str(e)}"

class ExecutePythonCodeTool(BaseTool):
    """Execute Python code to analyze saved climate data files, create graphs, and perform data analysis"""
    name: str = "execute_python_code"
    description: str = "Execute Python code to analyze saved climate data files. Can read CSV, NetCDF, HDF5 files, create matplotlib/seaborn plots, perform pandas analysis, and save results. Use after saving data locally."

    def _run(self, python_code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import sys
            import os
            import traceback
            from io import StringIO
            import matplotlib
            matplotlib.use('Agg')  # Use non-GUI backend
            import matplotlib.pyplot as plt
            
            output = f"🐍 EXECUTING PYTHON CODE\n"
            output += "=" * 40 + "\n\n"
            
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            # Create a safe execution environment with common libraries
            exec_globals = {
                '__builtins__': __builtins__,
                'pd': None,
                'np': None, 
                'plt': plt,
                'sns': None,
                'xr': None,
                'os': os,
                'Path': None
            }
            
            # Import common libraries safely
            try:
                import pandas as pd
                exec_globals['pd'] = pd
            except ImportError:
                pass
                
            try:
                import numpy as np
                exec_globals['np'] = np
            except ImportError:
                pass
                
            try:
                import seaborn as sns
                exec_globals['sns'] = sns
            except ImportError:
                pass
                
            try:
                import xarray as xr
                exec_globals['xr'] = xr
            except ImportError:
                pass
                
            try:
                from pathlib import Path
                exec_globals['Path'] = Path
            except ImportError:
                pass
            
            # Execute the code
            exec(python_code, exec_globals)
            
            # Restore stdout and get captured output
            sys.stdout = old_stdout
            code_output = captured_output.getvalue()
            
            # Show code that was executed
            output += f"📝 Code executed:\n"
            output += f"```python\n{python_code}\n```\n\n"
            
            # Show output from code execution
            if code_output.strip():
                output += f"📊 Output:\n"
                output += f"```\n{code_output}\n```\n\n"
            else:
                output += f"✅ Code executed successfully (no output)\n\n"
                
            # Check for saved files (plots, etc.)
            current_files = os.listdir('.')
            plot_files = [f for f in current_files if f.endswith(('.png', '.jpg', '.svg', '.pdf'))]
            data_files = [f for f in current_files if f.endswith(('.csv', '.nc', '.h5', '.hdf5', '.json'))]
            
            if plot_files:
                output += f"📈 Generated plots:\n"
                for plot_file in plot_files:
                    output += f"   • {plot_file}\n"
                output += "\n"
                
            if data_files:
                output += f"💾 Available data files:\n"
                for data_file in data_files:
                    output += f"   • {data_file}\n"
                output += "\n"
            
            output += f"✅ Python code execution completed successfully!\n"
            output += f"💡 Files are saved in the current directory for analysis.\n"
            
            return output
            
        except Exception as e:
            # Restore stdout
            sys.stdout = old_stdout
            
            error_output = f"❌ Python execution error:\n"
            error_output += f"```\n{str(e)}\n```\n\n"
            error_output += f"🔍 Full traceback:\n"
            error_output += f"```\n{traceback.format_exc()}\n```\n"
            
            return error_output

class DownloadAndSaveDataTool(BaseTool):
    """Download data directly from API/URL and save to local file in one step"""
    name: str = "download_and_save_data"
    description: str = "Download data directly from NOAA API, S3, or Earthdata URL and save to local file immediately. Accepts location names or codes (auto-resolves). Format: 'source_type:NOAA dataset:GHCND location:New York City startdate:2023-01-01 enddate:2023-12-31 datatype:PRCP filename:rainfall.csv' OR 'source_type:S3 url:[s3_path] filename:data.nc' OR 'source_type:Earthdata url:[earthdata_url] filename:data.nc'"

    def _run(self, download_params: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import json
            import pandas as pd
            import requests
            from datetime import datetime
            import os
            
            output = f"⬇️ DOWNLOAD AND SAVE DATA\n"
            output += "=" * 40 + "\n\n"
            
            # Parse parameters
            params = {}
            for param in download_params.split():
                if ':' in param:
                    key, value = param.split(':', 1)
                    params[key] = value
            
            source_type = params.get('source_type', 'NOAA').upper()
            filename = params.get('filename', 'climate_data.csv')
            
            output += f"📡 Source: {source_type}\n"
            output += f"💾 Target file: {filename}\n\n"
            
            if source_type == 'NOAA':
                # Download NOAA data directly to file
                dataset = params.get('dataset', 'GHCND')
                location = params.get('location', '')
                if not location:
                    output += f"❌ No location provided.\n"
                    return output
                
                # Auto-resolve location code
                resolved_location = s3_connector.noaa_api.auto_resolve_location_code(location)
                if resolved_location:
                    location = resolved_location
                    output += f"🔍 Auto-resolved location to: {location}\n"
                else:
                    output += f"❌ Could not resolve location: {location}\n"
                    output += f"💡 Try using 'search_noaa_locations' to find valid location names\n"
                    return output
                startdate = params.get('startdate', '2023-01-01')
                enddate = params.get('enddate', '2023-12-31')
                datatype = params.get('datatype', 'PRCP')
                
                output += f"🌡️ NOAA Parameters:\n"
                output += f"   Dataset: {dataset}\n"
                output += f"   Location: {location}\n"
                output += f"   Date range: {startdate} to {enddate}\n"
                output += f"   Data type: {datatype}\n\n"
                
                # Make NOAA API request
                url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
                headers = {"token": NOAA_CDO_TOKEN} if NOAA_CDO_TOKEN else {}
                
                api_params = {
                    'datasetid': dataset,
                    'locationid': location,
                    'startdate': startdate,
                    'enddate': enddate,
                    'datatypeid': datatype,
                    'limit': 1000
                }
                
                response = requests.get(url, headers=headers, params=api_params)
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('results', [])
                    
                    if records:
                        # Save directly to CSV
                        df = pd.DataFrame(records)
                        df.to_csv(filename, index=False)
                        
                        output += f"✅ Successfully downloaded and saved {len(records)} records\n"
                        output += f"📁 File saved: {filename}\n"
                        output += f"📊 Columns: {', '.join(df.columns)}\n"
                        output += f"📏 Shape: {df.shape}\n\n"
                        
                        # Show sample
                        output += f"📋 Sample data:\n"
                        output += str(df.head(3)) + "\n\n"
                        
                    else:
                        output += f"❌ No data returned from NOAA API\n"
                        output += f"📋 API Response: {data}\n"
                        
                else:
                    output += f"❌ NOAA API request failed: {response.status_code}\n"
                    output += f"📋 Response: {response.text[:200]}\n"
                    
            elif source_type == 'S3':
                url = params.get('url', '')
                if url:
                    # Use S3 connector to download and save
                    try:
                        data = s3_connector.load_data_from_url_or_s3(url, sample_only=False)
                        if data and not isinstance(data, dict) or 'error' not in data:
                            # Save based on file extension
                            if filename.endswith('.csv'):
                                if hasattr(data, 'to_csv'):
                                    data.to_csv(filename, index=False)
                                else:
                                    pd.DataFrame(data).to_csv(filename, index=False)
                            elif filename.endswith('.nc'):
                                if hasattr(data, 'to_netcdf'):
                                    data.to_netcdf(filename)
                            
                            output += f"✅ Downloaded and saved S3 data to {filename}\n"
                        else:
                            output += f"❌ Failed to download S3 data: {data.get('error', 'Unknown error')}\n"
                    except Exception as e:
                        output += f"❌ S3 download error: {str(e)}\n"
                else:
                    output += f"❌ No S3 URL provided\n"
                    
            elif source_type == 'EARTHDATA':
                url = params.get('url', '')
                if url:
                    # Use Earthdata connector to download and save
                    try:
                        data = s3_connector.load_data_from_url_or_s3(url, sample_only=False)
                        
                        # Handle stream response from Earthdata
                        if isinstance(data, dict) and "stream_response" in data:
                            # It's a stream - download the actual file
                            stream_response = data["stream_response"]
                            with open(filename, 'wb') as f:
                                for chunk in stream_response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            output += f"✅ Downloaded Earthdata stream to {filename}\n"
                            
                        elif data and not (isinstance(data, dict) and 'error' in data):
                            # Regular data - save based on file extension
                            if filename.endswith('.csv'):
                                if hasattr(data, 'to_csv'):
                                    data.to_csv(filename, index=False)
                                else:
                                    pd.DataFrame(data).to_csv(filename, index=False)
                            elif filename.endswith('.nc'):
                                if hasattr(data, 'to_netcdf'):
                                    data.to_netcdf(filename)
                            elif filename.endswith('.json'):
                                import json
                                with open(filename, 'w') as f:
                                    json.dump(data, f, indent=2)
                            
                            output += f"✅ Downloaded and saved Earthdata to {filename}\n"
                        else:
                            output += f"❌ Failed to download Earthdata: {data.get('error', 'Unknown error') if isinstance(data, dict) else 'No data returned'}\n"
                    except Exception as e:
                        output += f"❌ Earthdata download error: {str(e)}\n"
                else:
                    output += f"❌ No Earthdata URL provided\n"
            
            else:
                output += f"❌ Unsupported source type: {source_type}\n"
                output += f"💡 Supported: NOAA, S3, Earthdata\n"
            
            # Check if file was actually created
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                output += f"🎯 File verification: {filename} ({file_size} bytes)\n"
                output += f"✅ Data successfully downloaded and saved!\n"
            else:
                output += f"❌ File was not created: {filename}\n"
                
            return output
            
        except Exception as e:
            return f"❌ Download and save error: {str(e)}"

class SaveDownloadedDataTool(BaseTool):
    """Save downloaded data to local files for persistence and analysis"""
    name: str = "save_downloaded_data"
    description: str = "Save downloaded climate data to local files in appropriate formats (NetCDF, HDF5, CSV, JSON, zarr, etc.). Automatically detects best format based on data type. Use after downloading any climate data to persist locally."

    def _run(self, data_description: str, filename: str = "climate_data", format_type: str = "csv", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import json
            import pandas as pd
            from datetime import datetime
            
            output = f"💾 SAVING DOWNLOADED DATA\n"
            output += "=" * 40 + "\n\n"
            
            # Check if we have NOAA data in memory (from download_noaa_data tool)
            if hasattr(s3_connector.noaa_api, 'last_downloaded_data') and s3_connector.noaa_api.last_downloaded_data:
                data = s3_connector.noaa_api.last_downloaded_data
                
                output += f"📊 Data Found: {len(data)} records\n"
                output += f"📁 Saving as: {filename}.{format_type}\n\n"
                
                if format_type.lower() == "csv":
                    # Convert to DataFrame and save as CSV
                    df = pd.DataFrame(data)
                    csv_filename = f"{filename}.csv"
                    df.to_csv(csv_filename, index=False)
                    output += f"✅ Saved to: {csv_filename}\n"
                    output += f"📋 Columns: {', '.join(df.columns)}\n"
                    output += f"📏 Shape: {df.shape}\n"
                    
                elif format_type.lower() == "json":
                    # Save as JSON
                    json_filename = f"{filename}.json"
                    with open(json_filename, 'w') as f:
                        json.dump(data, f, indent=2)
                    output += f"✅ Saved to: {json_filename}\n"
                    output += f"📊 Records: {len(data)}\n"
                    
                elif format_type.lower() == "netcdf":
                    # Save as NetCDF (if xarray data)
                    try:
                        import xarray as xr
                        if hasattr(data, 'to_netcdf'):  # xarray dataset
                            nc_filename = f"{filename}.nc"
                            data.to_netcdf(nc_filename)
                            output += f"✅ Saved to: {nc_filename}\n"
                        else:
                            # Convert to xarray if possible
                            df = pd.DataFrame(data)
                            ds = df.to_xarray()
                            nc_filename = f"{filename}.nc"
                            ds.to_netcdf(nc_filename)
                            output += f"✅ Saved to: {nc_filename}\n"
                    except Exception as e:
                        output += f"❌ NetCDF save failed: {str(e)}\n"
                        output += f"💡 Falling back to CSV format\n"
                        df = pd.DataFrame(data)
                        csv_filename = f"{filename}.csv"
                        df.to_csv(csv_filename, index=False)
                        output += f"✅ Saved to: {csv_filename}\n"
                        
                else:
                    output += f"❌ Unsupported format: {format_type}\n"
                    output += f"💡 Supported formats: csv, json, netcdf\n"
                    return output
                    
                # Show sample of saved data
                if isinstance(data, list) and len(data) > 0:
                    sample = data[0]
                    output += f"\n📋 Sample Record:\n"
                    if isinstance(sample, dict):
                        for key, value in list(sample.items())[:5]:
                            output += f"   {key}: {value}\n"
                    
                output += f"\n🎯 Data saved successfully! File is ready for analysis.\n"
                output += f"💡 You can now open {filename}.{format_type} in Excel, Python, or other tools.\n"
                
            else:
                output += f"❌ No downloaded data found in memory.\n"
                output += f"💡 Use 'download_noaa_data' first to download data, then save it.\n"
                
            return output
            
        except Exception as e:
            return f"❌ Error saving data: {str(e)}"

class ValidateDataQualityTool(BaseTool):
    """Validate data quality and perform basic quality checks"""
    name: str = "validate_data_quality"
    description: str = "Perform data quality validation on loaded datasets including completeness, format consistency, and basic statistical checks."

    def _run(self, dataset_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            output = f" DATA QUALITY VALIDATION\n"
            output += "=" * 40 + "\n\n"

            output += f" Dataset: {dataset_description}\n\n"

            # General validation guidelines for NASA CMR data
            output += f" VALIDATION CHECKLIST:\n"
            output += f"   • Metadata completeness\n"
            output += f"   • S3 data accessibility\n"
            output += f"   • Format consistency\n"
            output += f"   • Temporal coverage\n"
            output += f"   • Spatial coverage\n"
            output += f"   • Data integrity\n\n"

            output += f" RECOMMENDED CHECKS:\n"
            output += f"   1. Verify dataset metadata fields\n"
            output += f"   2. Check S3 data availability\n"
            output += f"   3. Validate file formats and structures\n"
            output += f"   4. Assess data completeness\n"
            output += f"   5. Check for missing values\n"
            output += f"   6. Verify coordinate systems\n"
            output += f"   7. Validate temporal consistency\n\n"

            output += f" Use other tools to load specific datasets and perform detailed validation"

            return output

        except Exception as e:
            return f" Error in data quality validation: {str(e)}"

class ValidateAllDataLinksCompatibilityTool(BaseTool):
    """Check all stored dataset links for compatibility and accessibility"""
    name: str = "validate_all_data_links_compatibility"
    description: str = "Systematically check ALL stored dataset links to determine which ones are accessible and compatible with current authentication. Reports S3, Earthdata, and NOAA API link status."

    def _run(self, max_datasets: str = "50", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import sqlite3
            import json

            max_check = int(max_datasets) if max_datasets.isdigit() else 50
            db_path = "climate_knowledge_graph.db"

            output = f"🔍 **DATA LINKS COMPATIBILITY CHECK**\n"
            output += "=" * 60 + "\n\n"

            # Get all datasets with links
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT dataset_id, title, short_name, links
                    FROM stored_datasets
                    WHERE links IS NOT NULL AND links != '' AND links != '[]'
                    LIMIT ?
                """, (max_check,))
                datasets = cursor.fetchall()

            if not datasets:
                return f"📭 No datasets with data links found in database"

            total_datasets = len(datasets)
            s3_accessible = 0
            earthdata_accessible = 0
            noaa_accessible = 0
            search_urls = 0
            broken_links = 0

            output += f"📊 **Checking {total_datasets} datasets with data links...**\n\n"

            for i, (dataset_id, title, short_name, links_json) in enumerate(datasets):
                output += f"**{i+1}/{total_datasets}** - {short_name or title[:50]}\n"

                try:
                    links = json.loads(links_json) if links_json else []
                    if not links:
                        output += f"   ⚪ No links to check\n\n"
                        continue

                    dataset_s3_ok = 0
                    dataset_earthdata_ok = 0
                    dataset_noaa_ok = 0
                    dataset_search_urls = 0
                    dataset_broken = 0

                    for link in links[:3]:  # Check first 3 links only
                        url = link.get('url', '') if isinstance(link, dict) else str(link)
                        if not url:
                            continue

                        # Check URL type and compatibility
                        if "search.earthdata.nasa.gov" in url or "/search?" in url:
                            output += f"   🔍 Search URL (not direct data): {url[:60]}...\n"
                            dataset_search_urls += 1
                            search_urls += 1
                        elif url.startswith('s3://'):
                            # Check S3 accessibility
                            accessible = s3_connector.check_s3_path_exists(url)
                            status = "✅ Accessible" if accessible else "❌ Not accessible"
                            output += f"   🪣 S3: {status} - {url[:60]}...\n"
                            if accessible:
                                dataset_s3_ok += 1
                                s3_accessible += 1
                            else:
                                dataset_broken += 1
                                broken_links += 1
                        elif s3_connector.earthdata_auth.is_earthdata_url(url):
                            # Check Earthdata accessibility
                            try:
                                stream = s3_connector.earthdata_auth.open_url_stream(url)
                                accessible = stream is not None
                                if stream:
                                    stream.close()
                                status = "✅ Accessible" if accessible else "❌ Auth failed"
                                output += f"   🌍 Earthdata: {status} - {url[:60]}...\n"
                                if accessible:
                                    dataset_earthdata_ok += 1
                                    earthdata_accessible += 1
                                else:
                                    dataset_broken += 1
                                    broken_links += 1
                            except Exception as e:
                                output += f"   🌍 Earthdata: ❌ Error - {url[:60]}...\n"
                                dataset_broken += 1
                                broken_links += 1
                        elif s3_connector.noaa_api.is_noaa_url(url):
                            # Check NOAA API accessibility
                            token_valid = s3_connector.noaa_api.validate_token()
                            status = "✅ Token valid" if token_valid else "❌ Token invalid"
                            output += f"   🌡️ NOAA: {status} - {url[:60]}...\n"
                            if token_valid:
                                dataset_noaa_ok += 1
                                noaa_accessible += 1
                            else:
                                dataset_broken += 1
                                broken_links += 1
                        else:
                            output += f"   ❓ Unknown type: {url[:60]}...\n"
                            dataset_broken += 1
                            broken_links += 1

                    # Dataset summary
                    working_links = dataset_s3_ok + dataset_earthdata_ok + dataset_noaa_ok
                    if working_links > 0:
                        output += f"   ✅ {working_links} working links found\n"
                    elif dataset_search_urls > 0:
                        output += f"   🔍 Only search URLs (need conversion to direct data links)\n"
                    else:
                        output += f"   ❌ No working data links\n"

                    output += "\n"

                except json.JSONDecodeError:
                    output += f"   ❌ Invalid links format\n\n"
                    broken_links += 1
                except Exception as e:
                    output += f"   ❌ Error checking links: {str(e)[:50]}\n\n"
                    broken_links += 1

            # Summary statistics
            output += f"📋 **COMPATIBILITY SUMMARY**\n"
            output += f"   🪣 S3 accessible links: {s3_accessible}\n"
            output += f"   🌍 Earthdata accessible links: {earthdata_accessible}\n"
            output += f"   🌡️ NOAA API accessible links: {noaa_accessible}\n"
            output += f"   🔍 Search URLs (need conversion): {search_urls}\n"
            output += f"   ❌ Broken/inaccessible links: {broken_links}\n\n"

            total_working = s3_accessible + earthdata_accessible + noaa_accessible
            if total_working > 0:
                output += f"✅ **{total_working} total working data links found**\n"
            else:
                output += f"⚠️ **No working data links found - check credentials and tokens**\n"

            output += f"\n💡 **Next Steps:**\n"
            if search_urls > 0:
                output += f"   • Use 'find_data_access_for_dataset' to convert search URLs to direct data links\n"
            if broken_links > 0:
                output += f"   • Use 'process_all_datasets_for_data_access' to find alternative data access\n"
            if earthdata_accessible == 0 and any('earthdata' in str(d[3]) for d in datasets):
                output += f"   • Check Earthdata credentials (currently using: {s3_connector.earthdata_auth.username})\n"
            if noaa_accessible == 0 and any('noaa' in str(d[3]).lower() for d in datasets):
                output += f"   • Check NOAA CDO API token at: https://www.ncdc.noaa.gov/cdo-web/token\n"

            return output

        except Exception as e:
            return f"❌ Error validating data links: {str(e)}"

class QueryExistingDatasetTool(BaseTool):
    """Query existing dataset by ID from knowledge graph database"""
    name: str = "query_existing_dataset"
    description: str = "Query an existing dataset by its ID from the knowledge graph database. Returns dataset information and current data access links status."

    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import sqlite3
            db_path = "climate_knowledge_graph.db"

            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("""
                    SELECT dataset_id, title, short_name, dataset_properties, dataset_labels,
                           links, created_at, updated_at
                    FROM stored_datasets WHERE dataset_id = ?
                """, (dataset_id.strip(),))

                result = cursor.fetchone()

                if not result:
                    return f" Dataset not found: {dataset_id}\n Use knowledge graph search tools to find available datasets first."

                columns = ['dataset_id', 'title', 'short_name', 'dataset_properties', 'dataset_labels',
                          'links', 'created_at', 'updated_at']

                dataset = dict(zip(columns, result))

                output = f" EXISTING DATASET QUERY RESULT\n"
                output += "=" * 45 + "\n\n"

                output += f" Dataset Information:\n"
                output += f"   • ID: {dataset['dataset_id']}\n"
                output += f"   • Title: {dataset['title']}\n"
                output += f"   • Short Name: {dataset['short_name']}\n\n"

                # Data Access Links Status
                if dataset['links']:
                    try:
                        links_data = json.loads(dataset['links'])
                        if links_data and len(links_data) > 0:
                            output += f" DATA ACCESS LINKS CONFIGURED ({len(links_data)} total):\n"

                            earthdata_count = sum(1 for link in links_data if link.get("type") == "Earthdata")
                            s3_count = sum(1 for link in links_data if link.get("type") == "S3")

                            output += f"   •  Earthdata URLs: {earthdata_count}\n"
                            output += f"   •  S3 URLs: {s3_count}\n"

                            # Show details of first few links
                            for i, link in enumerate(links_data[:3]):
                                link_type_icon = "" if link.get("type") == "Earthdata" else ""
                                url = link.get("url", "Unknown URL")
                                source = link.get("source", "Unknown")
                                accessible = "" if link.get("accessible") else ""

                                output += f"   {i+1}. {link_type_icon} {url[:60]}{'...' if len(url) > 60 else ''}\n"
                                output += f"       Source: {source} | Status: {accessible}\n"

                            if len(links_data) > 3:
                                output += f"   ... and {len(links_data) - 3} more links\n"
                        else:
                            output += f" DATA ACCESS: Links field exists but empty\n"
                    except json.JSONDecodeError:
                        output += f" DATA ACCESS: Links data format error\n"

                    output += f"   • Status: Ready for data loading\n"
                    output += f"   • Use 'load_data' with any link URL to access data\n"
                else:
                    output += f" DATA ACCESS NOT CONFIGURED:\n"
                    output += f"   • No data access links found for this dataset\n"
                    output += f"   • Use 'find_data_access_for_dataset' to find data access links\n"
                    output += f"   • Use 'add_data_url_to_dataset' to configure data access\n"

                output += f"\n Timestamps:\n"
                output += f"   • Created: {dataset['created_at']}\n"
                output += f"   • Updated: {dataset['updated_at']}\n"

                # Dataset properties summary
                if dataset['dataset_properties']:
                    try:
                        props = json.loads(dataset['dataset_properties'])
                        output += f"\n Dataset Properties: {len(props)} fields available\n"
                    except:
                        output += f"\n Dataset Properties: Available\n"

                output += f"\n Next steps:\n"
                if dataset['links']:
                    try:
                        links_data = json.loads(dataset['links'])
                        if links_data and len(links_data) > 0:
                            first_url = links_data[0].get("url", "")
                            if first_url:
                                output += f"   • Load data: load_data {first_url}\n"
                                output += f"   • Query data locations: query_data_locations {dataset['dataset_id']}\n"
                    except:
                        pass
                if not dataset['links'] or not json.loads(dataset.get('links', '[]')):
                    output += f"   • Find data links: find_data_access_for_dataset {dataset['dataset_id']}\n"
                    output += f"   • Configure access: add_data_url_to_dataset\n"

                return output

        except Exception as e:
            return f" Error querying existing dataset: {str(e)}"

class AddDataUrlToDatasetTool(BaseTool):
    """Add data URLs (S3 or Earthdata) and metadata to an existing dataset in the knowledge graph database"""
    name: str = "add_data_url_to_dataset"
    description: str = "Add or replace data access URLs (S3 or Earthdata) and metadata for an existing dataset. Input format: 'dataset_id|data_url|metadata_json'. Supports both s3:// URLs and Earthdata URLs. This will replace existing data URLs with better ones when needed."

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Parse input
            parts = tool_input.split('|', 2)
            if len(parts) < 2:
                return " Error: Input format should be 'dataset_id|data_url|metadata_json'\\nExample: 'dataset123|https://data.ornldaac.earthdata.nasa.gov/protected/bundle/file.zip|{\"format\":\"ZIP\",\"size_mb\":150}'"

            dataset_id = parts[0].strip()
            data_url = parts[1].strip()
            data_metadata_str = parts[2].strip() if len(parts) > 2 else "{}"

            # Validate URL format (S3 or Earthdata)
            is_s3 = data_url.startswith('s3://')
            is_earthdata = s3_connector.earthdata_auth.is_earthdata_url(data_url)

            if not (is_s3 or is_earthdata):
                return f" Error: URL must be either S3 (s3://) or Earthdata URL. Got: {data_url}"

            url_type = "s3" if is_s3 else "earthdata"

            # Validate and enhance metadata
            try:
                data_metadata = json.loads(data_metadata_str) if data_metadata_str else {}
            except json.JSONDecodeError:
                return f" Error: Invalid JSON in metadata: {data_metadata_str}"

            # Enhance metadata with URL type and accessibility check
            data_metadata['url_type'] = url_type
            data_metadata['last_checked'] = datetime.now().isoformat()

            # Check accessibility
            if is_s3:
                accessible = s3_connector.check_s3_path_exists(data_url)
            else:
                # For Earthdata, try to open stream (non-blocking check)
                try:
                    stream = s3_connector.earthdata_auth.open_url_stream(data_url)
                    accessible = stream is not None
                    if stream:
                        stream.close()
                except:
                    accessible = False

            data_metadata['accessible'] = accessible

            import sqlite3
            db_path = "climate_knowledge_graph.db"

            with sqlite3.connect(db_path) as conn:
                # Check if dataset exists and get current links
                cursor = conn.execute("SELECT dataset_id, title, short_name, links FROM stored_datasets WHERE dataset_id = ?", (dataset_id,))
                result = cursor.fetchone()

                if not result:
                    return f" Error: Dataset {dataset_id} not found in knowledge graph database\\n Use 'query_existing_dataset' to verify the dataset ID"

                existing_links_json = result[3]
                existing_links = []
                if existing_links_json:
                    try:
                        existing_links = json.loads(existing_links_json)
                    except json.JSONDecodeError:
                        existing_links = []

                # Create new link object
                new_link = {
                    "url": data_url,
                    "type": "S3" if is_s3 else "Earthdata",
                    "source": "Manual_Entry",
                    "description": data_metadata.get("description", f"Manually added {url_type} URL"),
                    "access_method": "anonymous" if is_s3 else "authenticated",
                    "accessible": accessible,
                    "metadata": data_metadata,
                    "added_at": datetime.now().isoformat()
                }

                # Add or replace the link (replace any existing links with same URL)
                updated_links = [link for link in existing_links if link.get("url") != data_url]
                updated_links.append(new_link)

                # Update database with new links array
                current_time = datetime.now().isoformat()
                conn.execute("""
                    UPDATE stored_datasets
                    SET links = ?, updated_at = ?
                    WHERE dataset_id = ?
                """, (json.dumps(updated_links), current_time, dataset_id))

                conn.commit()

                was_replacing = any(link.get("url") == data_url for link in existing_links)
                operation = "updated" if was_replacing else "added"
                access_status = " accessible" if accessible else " not accessible"

                output = f"{'' if was_replacing else ''} Successfully {operation} {url_type.upper()} data link for dataset: {dataset_id}\\n"
                output += f" URL: {data_url}\\n"
                output += f" Status: {access_status}\\n"
                output += f" Type: {url_type.upper()}\\n"
                output += f" Total Links: {len(updated_links)}\\n"

                if was_replacing:
                    output += f" Link updated (URL already existed)\\n"

                output += f"\\n NEXT STEPS:\\n"
                output += f"   • Load data: load_data {data_url}\\n"
                output += f"   • Query updated dataset: query_existing_dataset {dataset_id}\\n"

                if not accessible:
                    output += f"\\n Note: Data URL accessibility could not be verified.\\n"
                    if is_earthdata:
                        output += f"   This may require valid Earthdata Login credentials.\\n"
                    else:
                        output += f"   This may be due to permissions or path format.\\n"

                return output

        except Exception as e:
            return f" Error adding data URL to dataset: {str(e)}"

class AddS3PathToDatasetTool(BaseTool):
    """Legacy tool - Add S3 path and metadata to an existing dataset in the knowledge graph database"""
    name: str = "add_s3_path_to_dataset"
    description: str = "Legacy tool: Add or replace S3 path and metadata for an existing dataset. Use add_data_url_to_dataset for both S3 and Earthdata URLs. Input format: 'dataset_id|s3_path|metadata_json'."

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Parse input
            parts = tool_input.split('|', 2)
            if len(parts) < 2:
                return " Error: Input format should be 'dataset_id|s3_path|metadata_json'\nExample: 'dataset123|s3://nasa-goes16/ABI-L2-SSTF|{\"format\":\"NetCDF\",\"size_gb\":1.2}'"

            dataset_id = parts[0].strip()
            s3_path = parts[1].strip()
            s3_metadata_str = parts[2].strip() if len(parts) > 2 else "{}"

            # Validate S3 path format
            if not s3_path.startswith('s3://'):
                return f" Error: S3 path must start with 's3://'. Got: {s3_path}"

            # Validate and enhance metadata
            try:
                s3_metadata = json.loads(s3_metadata_str) if s3_metadata_str else {}
            except json.JSONDecodeError:
                return f" Error: Invalid JSON in metadata: {s3_metadata_str}"

            # Auto-detect additional metadata from S3 path
            auto_metadata = self._extract_s3_metadata(s3_path)
            s3_metadata.update(auto_metadata)

            # Verify S3 path accessibility if possible
            s3_accessible = s3_connector.check_s3_path_exists(s3_path)
            s3_metadata['accessible'] = s3_accessible
            s3_metadata['last_checked'] = datetime.now().isoformat()

            import sqlite3
            db_path = "climate_knowledge_graph.db"

            with sqlite3.connect(db_path) as conn:
                # Check if dataset exists and get current links
                cursor = conn.execute("SELECT dataset_id, title, short_name, links FROM stored_datasets WHERE dataset_id = ?", (dataset_id,))
                result = cursor.fetchone()

                if not result:
                    return f" Error: Dataset {dataset_id} not found in knowledge graph database\n Use 'query_existing_dataset' to verify the dataset ID"

                existing_links_json = result[3]
                existing_links = []
                if existing_links_json:
                    try:
                        existing_links = json.loads(existing_links_json)
                    except json.JSONDecodeError:
                        existing_links = []

                # Create new S3 link object (for backward compatibility)
                new_link = {
                    "url": s3_path,
                    "type": "S3",
                    "source": "Legacy_S3_Tool",
                    "description": "Added via legacy S3 tool",
                    "access_method": "anonymous",
                    "metadata": s3_metadata,
                    "added_at": datetime.now().isoformat()
                }

                # Add or replace the link
                updated_links = [link for link in existing_links if link.get("url") != s3_path]
                updated_links.append(new_link)

                # Update database with new links
                current_time = datetime.now().isoformat()
                conn.execute("""
                    UPDATE stored_datasets
                    SET links = ?, updated_at = ?
                    WHERE dataset_id = ?
                """, (json.dumps(updated_links), current_time, dataset_id))

                was_replacing = any(link.get("url") == s3_path for link in existing_links)

                if was_replacing:
                    output = f" S3 LINK UPDATED FOR DATASET\n"
                    output += "=" * 38 + "\n\n"
                    output += f" Dataset: {result[1]} ({result[2]})\n"
                    output += f" ID: {dataset_id}\n"
                    output += f" Updated S3 Link: {s3_path}\n"
                    output += f" Total Links: {len(updated_links)}\n"
                    output += f" Accessibility: {'Verified' if s3_accessible else 'Not verified'}\n\n"
                else:
                    output = f" S3 LINK ADDED TO DATASET\n"
                    output += "=" * 35 + "\n\n"
                    output += f" Dataset: {result[1]} ({result[2]})\n"
                    output += f" ID: {dataset_id}\n"
                    output += f" New S3 Link: {s3_path}\n"
                    output += f" Total Links: {len(updated_links)}\n\n"

                # Show metadata
                if s3_metadata:
                    output += f" S3 Metadata ({len(s3_metadata)} fields):\n"
                    for key, value in s3_metadata.items():
                        output += f"   • {key}: {value}\n"

                output += f"\n🕐 Updated: {current_time}\n"
                output += f" Database: {db_path}\n\n"

                output += f" Next Steps:\n"
                output += f"   • Load data: load_s3_data {s3_path}\n"
                output += f"   • Explore structure: explore_subdirectories {s3_path}\n"
                output += f"   • Query updated dataset: query_existing_dataset {dataset_id}\n"

                if not s3_accessible:
                    output += f"\n Note: S3 path accessibility could not be verified.\n"
                    output += f"   This may be due to permissions or path format.\n"

                return output

        except Exception as e:
            return f" Error adding S3 path to dataset: {str(e)}"

    def _extract_s3_metadata(self, s3_path: str) -> dict:
        """Extract metadata from S3 path structure"""
        metadata = {}

        try:
            # Extract bucket name
            bucket = s3_path.replace('s3://', '').split('/')[0]
            metadata['bucket'] = bucket

            # Detect data type from bucket name
            if 'goes' in bucket.lower():
                metadata['data_source'] = 'GOES Satellite'
                metadata['provider'] = 'NOAA'
            elif 'modis' in bucket.lower():
                metadata['data_source'] = 'MODIS Satellite'
                metadata['provider'] = 'NASA'
            elif 'nasa' in bucket.lower():
                metadata['provider'] = 'NASA'
            elif 'noaa' in bucket.lower():
                metadata['provider'] = 'NOAA'

            # Detect product type from path
            path_upper = s3_path.upper()
            if 'SST' in path_upper:
                metadata['variable'] = 'Sea Surface Temperature'
            if 'L2' in path_upper:
                metadata['processing_level'] = 'Level 2'
            if 'L3' in path_upper:
                metadata['processing_level'] = 'Level 3'

            # Detect format from common NASA patterns
            if any(ext in s3_path.lower() for ext in ['.nc', '.nc4']):
                metadata['format'] = 'NetCDF'
            elif any(ext in s3_path.lower() for ext in ['.hdf', '.hdf5', '.h5']):
                metadata['format'] = 'HDF5'

        except Exception:
            pass  # Ignore extraction errors, return partial metadata

        return metadata

# --- Create NASA CMR Data Acquisition Agent ---

def create_nasa_cmr_agent():
    """Create the NASA CMR Data Acquisition LangChain agent"""

    class AskDataProcessingFollowUpTool(BaseTool):
        """Ask follow-up questions about what to do with the acquired climate data"""
        name: str = "ask_data_processing_followup"
        description: str = "Ask the user follow-up questions about how they want to process, analyze, visualize, or store the climate data after acquisition."

        def _run(self, question_context: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            """Ask context-specific follow-up questions about data processing and analysis"""

            follow_up_templates = {
                "visualization": {
                    "title": "📊 Data Visualization & Plotting",
                    "questions": [
                        "What type of plots or visualizations do you need? (time series, maps, histograms, scatter plots, etc.)",
                        "Do you want to create publication-ready figures or exploratory plots?",
                        "Should I generate interactive plots or static images?",
                        "Do you need multiple variables plotted together or separately?"
                    ]
                },
                "analysis": {
                    "title": "🔬 Data Analysis & Processing",
                    "questions": [
                        "What statistical analysis do you want to perform? (trends, correlations, anomalies, extremes)",
                        "Do you need time series analysis, spatial analysis, or both?",
                        "Should I calculate climatologies, anomalies, or seasonal patterns?",
                        "Do you want to compare multiple datasets or time periods?"
                    ]
                },
                "storage": {
                    "title": "💾 Data Storage & Export",
                    "questions": [
                        "How would you like to store the processed data? (CSV, NetCDF, database, memory)",
                        "Do you need the data exported for use in other tools or software?",
                        "Should I save intermediate processing results or only final outputs?",
                        "Do you want metadata preserved in the output files?"
                    ]
                },
                "quality_control": {
                    "title": "✅ Data Quality & Validation",
                    "questions": [
                        "Do you need data quality checks and validation performed?",
                        "Should I identify and handle missing data or outliers?",
                        "Do you want data coverage statistics and completeness reports?",
                        "Should I compare data ranges with expected climatological values?"
                    ]
                },
                "processing_workflow": {
                    "title": "⚙️ Processing Workflow & Methods",
                    "questions": [
                        "Do you need spatial or temporal aggregation/averaging?",
                        "Should I apply any filtering, smoothing, or interpolation?",
                        "Do you want unit conversions or standardization performed?",
                        "Should I subset the data by geographic regions or time periods?"
                    ]
                },
                "comparison": {
                    "title": "🔄 Data Comparison & Integration",
                    "questions": [
                        "Do you want to compare this data with other datasets or model outputs?",
                        "Should I align data temporally and spatially for comparison?",
                        "Do you need bias correction or calibration performed?",
                        "Should I calculate difference maps or correlation statistics?"
                    ]
                },
                "output_format": {
                    "title": "📁 Output Format & Delivery",
                    "questions": [
                        "What output formats do you prefer? (plots as PNG/PDF, data as CSV/NetCDF)",
                        "Do you want a summary report with key findings?",
                        "Should I create a processing log or metadata documentation?",
                        "Do you need the outputs organized in specific folder structures?"
                    ]
                },
                "next_steps": {
                    "title": "🎯 Next Steps & Integration",
                    "questions": [
                        "Will this data be used for further analysis or modeling?",
                        "Do you need the processed data passed to other climate research agents?",
                        "Should I prepare the data for specific software tools (Python, R, MATLAB)?",
                        "Do you want recommendations for additional complementary datasets?"
                    ]
                },
                "general": {
                    "title": "❓ General Data Processing Guidance",
                    "questions": [
                        "What is your main goal with this climate data?",
                        "Do you have any specific processing requirements or constraints?",
                        "What level of analysis detail do you need (quick overview vs detailed analysis)?",
                        "Are there any specific standards or protocols you need to follow?"
                    ]
                }
            }

            # Parse context to determine question type
            context_lower = question_context.lower()

            if any(word in context_lower for word in ['plot', 'graph', 'visualiz', 'chart', 'map', 'figure']):
                question_type = "visualization"
            elif any(word in context_lower for word in ['analysis', 'statistics', 'trend', 'correlation', 'calculate']):
                question_type = "analysis"
            elif any(word in context_lower for word in ['save', 'store', 'export', 'database', 'file']):
                question_type = "storage"
            elif any(word in context_lower for word in ['quality', 'validation', 'check', 'missing', 'outlier']):
                question_type = "quality_control"
            elif any(word in context_lower for word in ['process', 'workflow', 'method', 'filter', 'aggregate']):
                question_type = "processing_workflow"
            elif any(word in context_lower for word in ['compare', 'comparison', 'integrate', 'align', 'bias']):
                question_type = "comparison"
            elif any(word in context_lower for word in ['output', 'format', 'delivery', 'report', 'document']):
                question_type = "output_format"
            elif any(word in context_lower for word in ['next', 'steps', 'integrate', 'further', 'recommend']):
                question_type = "next_steps"
            else:
                question_type = "general"

            template = follow_up_templates[question_type]

            output = f"🤔 **{template['title']}**\n\n"
            output += f"Now that we have the climate data, let me understand how you'd like to process and use it:\n\n"

            for i, question in enumerate(template['questions'], 1):
                output += f"{i}. {question}\n"

            output += f"\n💡 **Context:** {question_context}\n\n"
            output += f"📋 **Available Next Steps:**\n"
            output += f"• Use the **Climate Research Orchestrator** for complex analysis and visualization\n"
            output += f"• Use **code execution tools** for custom data processing\n"
            output += f"• **Store data** in databases or export to files\n"
            output += f"• **Integrate** with other climate research agents\n\n"
            # Actually pause execution and wait for user input
            print(output)
            print("🔴 **WAITING FOR USER INPUT** 🔴")
            print("Please let me know your preferences, and I'll help you process and analyze the climate data effectively!")

            user_response = input("\n>>> Your response: ")

            return f"User provided the following clarification: {user_response}\n\nNow I can proceed with processing and analyzing the climate data based on this information."

    # Define all available tools (prioritized order - Database First!)
    tools = [
        AskDataProcessingFollowUpTool(),      # Follow-up questions for data processing
        ValidateAllDataLinksCompatibilityTool(), # NEW: Check all data links for compatibility
        QueryNOAADatasetTool(),               # NOAA: Query NOAA CDO API for dataset info
        SearchNOAALocationsTool(),            # NOAA: Search for location codes
        DownloadNOAADataTool(),               # NOAA: Download climate data from NOAA CDO API
        ListAllStoredDatasetsTool(),          # PRIMARY: List ALL datasets in database (no keyword filtering)
        ProcessAllDatasetsForDataAccessTool(), # COMPREHENSIVE: Process ALL datasets systematically for data access
        QueryExistingDatasetTool(),           # Database: Query specific existing datasets
        FindDataAccessForDatasetTool(),       # Database: Find data access paths for individual datasets
        AddDataUrlToDatasetTool(),            # Database: Add both S3 and Earthdata URLs to datasets
        AddS3PathToDatasetTool(),             # Legacy: Add S3 paths to datasets (backward compatibility)
        SearchAWSOpenDataTool(),              # Secondary: AWS Open Data Registry
        ExploreAWSOpenDataBucketTool(),       # Secondary: AWS Open Data exploration
        ExploreSubdirectoriesTool(),          # Navigation: Flexible subdirectory exploration
        LoadSeaSurfaceTemperatureDataTool(),  # Direct: SST data loading
        DebugS3StructureTool(),               # Debug: Deep structure exploration
        InspectDatasetMetadataTool(),         # Fallback: CMR metadata
        QueryDataLocationsTool(),             # Fallback: CMR data locations (S3 and Earthdata)
        LoadS3DataTool(),                     # Universal: Data loading (S3 and Earthdata)
        DownloadAndSaveDataTool(),            # Universal: Direct download-to-file from APIs
        ExecutePythonCodeTool(),              # Universal: Execute Python code for analysis and visualization
        ValidateDataQualityTool()             # Universal: Data validation
    ]

    # Create the NASA CMR data acquisition prompt
    template = """You are a Climate Data Acquisition Assistant specialized in enhancing existing climate datasets with data access (Earthdata URLs, NOAA API access, and S3 paths) and analyzing the data.

    DATABASE-FIRST STRATEGY:
    🥇 PRIMARY: Stored Datasets Database - Work with datasets already discovered by the Knowledge Graph Agent
    🥈 SECONDARY: AWS Open Data Registry - Find S3 access for stored datasets as fallback
    🥉 FALLBACK: Full NASA CMR Catalog - Only when stored datasets need additional metadata

    DATA SOURCE PRIORITY:
    EARTHDATA: NASA's official authenticated data access (highest priority)
    🌡️ NOAA CDO API: NOAA Climate Data Online API for NOAA datasets (high priority)
    S3: Anonymous AWS Open Data access (fallback)

    CORE MISSION: Add data access (Earthdata URLs, NOAA API access, and S3 paths) to existing datasets, don't discover new ones!

    CAPABILITIES:
    - Search existing stored datasets from the knowledge graph database
    - Query NOAA Climate Data Online API for NOAA datasets (requires API token)
    - Download climate data directly from NOAA CDO API
    - Find data access locations (Earthdata URLs, NOAA API, and S3 paths) for stored datasets that lack access
    - Add data URLs and metadata to existing dataset records (prioritizing Earthdata URLs)
    - Load and preview actual data files from both S3 and Earthdata locations
    - Perform data quality validation and consistency checks

    SIMPLE DATABASE-FIRST WORKFLOW:
    0. ASK FOR CLARIFICATION: Use 'ask_data_processing_followup' WHENEVER you need more details about data processing, visualization, analysis goals, or output requirements - at ANY point in the workflow!
    1. LIST ALL: Use 'list_all_stored_datasets' to see ALL datasets in database (NO keyword filtering)
    2. VALIDATE LINKS: Use 'validate_all_data_links_compatibility' to check which existing links work with current authentication
    3. PROCESS ALL: Use 'process_all_datasets_for_data_access' to systematically find access for ALL datasets (replaces existing paths with better ones)
    4. INDIVIDUAL: Use 'find_data_access_for_dataset' + 'add_data_url_to_dataset' for specific datasets (can replace existing paths)
    5. DIRECT DOWNLOAD: Use 'download_and_save_data' with existing dataset URLs to download and save data files directly
    6. CODE EXECUTION: Use 'execute_python_code' to read saved files, create dataframes, generate plots, and perform analysis from local file paths
    7. VALIDATION: Assess data quality and format consistency

    REMEMBER: Don't assume what the user wants to do with the data - ask for clarification using 'ask_data_processing_followup' whenever you need more specific information!

    PRIORITY: Trust your intelligence to match relevant data access to dataset descriptions! Replace existing paths when you find better ones. Prioritize Earthdata URLs over S3 paths.

    ADVANTAGES OF AWS OPEN DATA:
    • Direct S3 access (no authentication needed)
    • Cloud-optimized formats for better performance
    • No data egress costs
    • Analytics-ready data (minimal preprocessing)

    You have access to these tools:
    {tools}

    EXAMPLE WORKFLOWS:

    WORKFLOW A - Comprehensive Database Enhancement:
    User: "Enhance all datasets in database with data access"
    1. list_all_stored_datasets: "50" (LIST ALL DATASETS - NO KEYWORD FILTERING)
    2. process_all_datasets_for_data_access: "20" (LET LLM FIND RELEVANT ACCESS FOR ALL DATASETS)
    3. load_data: [sample_data_path] (TEST ACCESS TO ENHANCED DATASETS)
    4. validate_data_quality: [dataset description] (VALIDATE DATA QUALITY)

    WORKFLOW B - Individual Dataset Enhancement:
    User: "Load data for dataset ID abc123"
    1. query_existing_dataset: "abc123" (CHECK DATABASE FIRST)
    2. If data access exists but seems irrelevant: find_data_access_for_dataset: "abc123" (FIND BETTER ACCESS)
    3. add_data_url_to_dataset: "abc123|[better_path]|{{metadata}}" (REPLACE WITH BETTER ACCESS)
    4. If no data access: find_data_access_for_dataset: "abc123" (LET LLM FIND RELEVANT ACCESS)
    5. add_data_url_to_dataset: "abc123|[found_path]|{{metadata}}" (ADD NEW ACCESS)
    6. load_data: [data_path_or_url] (LOAD DATA)

    WORKFLOW C - Research-Specific Data Access:
    User: "I need ocean temperature datasets"
    1. list_all_stored_datasets: "100" (SHOW ALL DATASETS - LLM WILL IDENTIFY OCEAN DATASETS)
    2. For ocean datasets: find_data_access_for_dataset: [dataset_id] (LLM FINDS RELEVANT ACCESS)
    3. load_data: [ocean_data_paths] (LOAD ACTUAL OCEAN TEMPERATURE DATA)
    4. validate_data_quality: [research context] (ASSESS DATA FOR RESEARCH)

    Use the following format:
    Question: the input question you must answer
    Thought: you should always think about what the user wants to accomplish
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}"""

    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad"],
        template=template,
        partial_variables={
            "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
            "tool_names": ", ".join([tool.name for tool in tools])
        }
    )

    # Create the ReAct agent
    agent = create_react_agent(llm, tools, prompt)

    # Create memory
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=5,  # Keep last 5 exchanges
        return_messages=True
    )

    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=75,  # Increased for data loading workflow
        max_execution_time=1200 #20 minutes timeout
    )

    return agent_executor

# Orchestrator integration functions
def get_nasa_cmr_tools():
        """Get NASA CMR tools for orchestrator integration"""
        return [
            ListAllStoredDatasetsTool(),          # PRIMARY: List ALL datasets in database (no keyword filtering)
            ProcessAllDatasetsForDataAccessTool(), # COMPREHENSIVE: Process ALL datasets systematically for data access
            QueryExistingDatasetTool(),           # Database: Query specific existing datasets
            FindDataAccessForDatasetTool(),       # Database: Find data access paths for individual datasets
            AddDataUrlToDatasetTool(),            # Database: Add both S3 and Earthdata URLs to datasets
            AddS3PathToDatasetTool(),             # Legacy: Add S3 paths to datasets (backward compatibility)
            SearchAWSOpenDataTool(),              # Secondary: AWS Open Data Registry
            ExploreAWSOpenDataBucketTool(),       # Secondary: AWS Open Data exploration
            ExploreSubdirectoriesTool(),          # Navigation: Flexible subdirectory exploration
            LoadSeaSurfaceTemperatureDataTool(),  # Direct: SST data loading
            DebugS3StructureTool(),               # Debug: Deep structure exploration
            InspectDatasetMetadataTool(),         # Fallback: CMR metadata
            QueryDataLocationsTool(),             # Fallback: CMR data locations (S3 and Earthdata)
            LoadS3DataTool(),                     # Universal: Data loading (S3 and Earthdata)
            DownloadAndSaveDataTool(),            # Universal: Direct download-to-file from APIs
            ExecutePythonCodeTool(),              # Universal: Execute Python code for analysis and visualization
            ValidateDataQualityTool()             # Universal: Data validation
        ]

def get_nasa_cmr_agent():
    """Get NASA CMR agent for orchestrator coordination"""
    return create_nasa_cmr_agent()

    # Test and example usage
if __name__ == "__main__":
    print(" NASA CMR Data Acquisition Agent")
    print("=" * 80)
    print("\n Using AWS Bedrock Claude Sonnet for reasoning")
    print(" Using AWS Neptune for CMR dataset discovery")
    print(" Using AWS S3 for data access")
    print(" Using LangChain for agent framework")

    print("\n" + "="*80)
    print(" TESTING NASA CMR Data Acquisition Agent")
    print("="*80)

    try:
        # Create the agent
        print("\n Initializing NASA CMR agent...")
        agent = create_nasa_cmr_agent()
        print(" Agent initialized successfully!")

        # Test with NYC rainfall and flooding analysis
        prompt_nasa_cmr = "What is the relationship between NYC rainfall and flooding using the existing data?"
        print(f"\n Research Query: {prompt_nasa_cmr}")

        print("\n Running agent...")
        response = agent.invoke({"input": prompt_nasa_cmr})

        print(f"\n Agent Response:")
        print("-" * 50)
        print(response.get('output', 'No output'))

    except Exception as e:
        print(f"\n TEST FAILED: {str(e)}")
        print(" Error details:")
        traceback.print_exc()

        print(f"\n This might be expected if:")
        print("   - AWS Bedrock credentials are not configured")
        print("   - Neptune Analytics is not accessible")
        print("   - S3 access is not available")
        print("   - Required Python packages are not installed")


                    