#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simulation Data Acquisition Agent

An intelligent agent for downloading and processing ERA5 and CMIP6 simulation datasets
stored by the simulation_kg_agent. This agent handles the actual data download and
processing workflow.

Features:
- Query stored simulation datasets from SQLite database
- Download ERA5 data using cdsapi library (asynchronous CDS API)
- Download CMIP6 data via ESGF HTTP (with authentication support)
- Process and analyze downloaded NetCDF files
- Provide data quality validation and visualization
"""

import json
import os
import sys
import sqlite3
import pathlib
import time
import traceback
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from pathlib import Path
import logging

# Data analysis libraries
try:
    import xarray as xr
    import numpy as np
    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False
    print("[WARN] xarray not available. NetCDF support limited.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("[WARN] pandas not available. Data analysis limited.")

# LangChain imports
try:
    from langchain.agents import AgentExecutor, create_react_agent
    from langchain.tools import BaseTool
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.prompts import PromptTemplate
    from langchain.llms.base import LLM
    from langchain.callbacks.manager import CallbackManagerForLLMRun
    from langchain_core.callbacks import CallbackManagerForToolRun
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("⚠️ LangChain not available. Agent functionality disabled.")

# AWS Bedrock
try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# ERA5 CDS API
try:
    import cdsapi
    CDSAPI_AVAILABLE = True
except ImportError:
    CDSAPI_AVAILABLE = False
    print("[WARN] cdsapi not available. ERA5 downloads disabled.")

# Configure logging (must be early for use in imports)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CMIP6 ESGF
import requests
from urllib.parse import urlparse

# Import CMIP6 helper functions
try:
    cmip6_module_path = Path(__file__).parent.parent / "CMIP6Data" / "cmip6_meta_resolver.py"
    if cmip6_module_path.exists():
        sys.path.insert(0, str(cmip6_module_path.parent))
        from cmip6_meta_resolver import esgf_search, pick_first_file_url, rec_to_esgf_query
        CMIP6_HELPERS_AVAILABLE = True
    else:
        CMIP6_HELPERS_AVAILABLE = False
except ImportError as e:
    CMIP6_HELPERS_AVAILABLE = False
    logger.warning(f"CMIP6 helper functions not available: {e}")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- Configuration Constants ---
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
DB_PATH = pathlib.Path(os.getenv("SIMULATION_DB_PATH", "climate_knowledge_graph.db"))

# ESGF Configuration
ESGF_NODES = [
    "https://esgf-node.llnl.gov",
    "https://esgf-data.dkrz.de",
    "https://esgf-node.ipsl.upmc.fr",
]
ESGF_API_PATH = "/esg-search/search"
ESGF_TIMEOUT = 30

# --- AWS Bedrock LLM ---
class BedrockClaudeLLM(LLM):
    """LangChain wrapper for AWS Bedrock using Claude Sonnet"""
    bedrock: Any = None
    model_id: str = BEDROCK_MODEL_ID

    def __init__(self):
        super().__init__()
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available; Bedrock calls disabled")
            self.bedrock = None
            return
        try:
            self.bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
            logger.info("Bedrock Claude LLM initialized successfully")
        except Exception as e:
            logger.warning(f"Bedrock client init failed: {e}")
            self.bedrock = None

    @property
    def _llm_type(self) -> str:
        return "bedrock_claude_sonnet"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if not self.bedrock:
            return f"[BEDROCK DISABLED] Prompt echo:\n{prompt}"
        stop_sequences = stop or ["\nObservation:"]
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": stop_sequences,
            }
        )
        try:
            response = self.bedrock.invoke_model(modelId=self.model_id, body=body)
            payload = json.loads(response["body"].read())
            return payload["content"][0]["text"].strip()
        except Exception as e:
            raise e


# --- Database Connector ---
class SimulationDatabaseConnector:
    """Connector for reading stored simulation datasets from SQLite database"""

    def __init__(self, db_path: pathlib.Path = DB_PATH):
        self.db_path = db_path

    def list_stored_datasets(
        self, family: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List stored simulation datasets from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                if family:
                    cursor = conn.execute(
                        """
                        SELECT * FROM simulation_datasets
                        WHERE family = ?
                        ORDER BY updated_at DESC
                        LIMIT ?
                        """,
                        (family, limit),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT * FROM simulation_datasets
                        ORDER BY updated_at DESC
                        LIMIT ?
                        """,
                        (limit,),
                    )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to list datasets: {e}")
            return []

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific dataset by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM simulation_datasets WHERE dataset_id = ?",
                    (dataset_id,),
                )
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Failed to get dataset {dataset_id}: {e}")
            return None

    def get_dataset_relationships(self, dataset_id: str) -> List[Dict[str, Any]]:
        """Get relationships for a dataset"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM simulation_dataset_relationships
                    WHERE dataset_id = ?
                    """,
                    (dataset_id,),
                )
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get relationships for {dataset_id}: {e}")
            return []


# --- ERA5 Download Handler ---
class ERA5DownloadHandler:
    """Handle ERA5 data downloads using cdsapi"""

    def __init__(self):
        self.client = None
        if CDSAPI_AVAILABLE:
            try:
                cds_url = os.environ.get("CDSAPI_URL", "")
                cds_key = os.environ.get("CDSAPI_KEY", "")
                if cds_url and cds_key:
                    self.client = cdsapi.Client(url=cds_url, key=cds_key, quiet=True)
                    logger.info("CDS API client initialized from environment variables")
                else:
                    self.client = cdsapi.Client(quiet=True)
                    logger.info("CDS API client initialized from .cdsapirc")
            except Exception as e:
                logger.warning(f"CDS API client init failed: {e}")

    def is_configured(self) -> bool:
        """Check if CDS API is properly configured"""
        return self.client is not None

    def reconfigure(self, url: Optional[str] = None, key: Optional[str] = None):
        """Reconfigure CDS API client with new credentials"""
        if not CDSAPI_AVAILABLE:
            return False, "cdsapi not available"
        try:
            if url and key:
                self.client = cdsapi.Client(url=url, key=key, quiet=True)
                logger.info("CDS API client reconfigured from user input")
                return True, "Successfully reconfigured CDS API."
            # Reload from env or file
            env_url = os.environ.get("CDSAPI_URL", "")
            env_key = os.environ.get("CDSAPI_KEY", "")
            if env_url and env_key:
                self.client = cdsapi.Client(url=env_url, key=env_key, quiet=True)
                logger.info("CDS API client reconfigured from environment")
                return True, "Reconfigured from environment variables."
            self.client = cdsapi.Client(quiet=True)
            logger.info("CDS API client reconfigured from .cdsapirc")
            return True, "Reconfigured from .cdsapirc."
        except Exception as e:
            logger.error(f"Reconfiguration failed: {e}")
            return False, f"Reconfiguration failed: {str(e)}"

    def build_download_request(
        self, dataset_info: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build CDS API request payload from dataset info
        
        CRITICAL: CDS API requires all parameters to be lists, not single values.
        This method ensures proper format conversion.
        """
        # Parse search_handles to get retrieve_payload_schema
        search_handles = json.loads(dataset_info.get("search_handles", "{}"))
        schema = search_handles.get("retrieve_payload_schema", {})
        
        # Build default payload from schema
        payload = {}
        for key, val in schema.items():
            if isinstance(val, dict):
                default_val = val.get("default")
                # CDS API requires lists for most parameters
                if default_val is not None:
                    payload[key] = default_val
            else:
                payload[key] = val

        # Override with user parameters
        if parameters:
            payload.update(parameters)

        # CRITICAL: Convert single values to lists for CDS API compatibility
        # CDS API requires: {"year": ["2020"], "month": ["01"]} NOT {"year": "2020"}
        list_params = ["year", "month", "day", "time", "variable", "product_type", "pressure_level"]
        for key in list_params:
            if key in payload:
                val = payload[key]
                # Convert single string/int to list
                if val is not None and not isinstance(val, list):
                    payload[key] = [str(val)]
                # Ensure all list items are strings
                elif isinstance(val, list):
                    payload[key] = [str(item) for item in val]

        # Handle area parameter (spatial subsetting: [north, west, south, east])
        # ERA5 CDS API requires area as a list of 4 floats: [north, west, south, east]
        if "area" in payload:
            area = payload["area"]
            if isinstance(area, list) and len(area) == 4:
                # Ensure all values are floats (CDS API accepts floats)
                try:
                    payload["area"] = [float(x) for x in area]
                except (ValueError, TypeError):
                    logger.warning(f"Invalid area parameter format: {area}. Expected [north, west, south, east]")
                    payload.pop("area", None)
            else:
                logger.warning(f"Invalid area parameter format: {area}. Expected [north, west, south, east]")
                payload.pop("area", None)

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        return payload

    def _get_chunk_suffix(self, params: Dict[str, Any]) -> str:
        """Generate suffix for chunk filename based on year/month"""
        years = params.get("year", [])
        months = params.get("month", [])
        if len(years) == 1:
            y = years[0]
            if len(months) == 1:
                return f"_{y}{months[0]}"
            return f"_{y}"
        return ""

    def download_era5_data(
        self,
        dataset_id: str,
        output_file: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Download ERA5 data using cdsapi (with auto-chunking)"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "CDS API not configured. Please set up .cdsapirc file.",
            }

        try:
            # Get dataset info from database
            db_connector = SimulationDatabaseConnector()
            dataset_info = db_connector.get_dataset(dataset_id)
            if not dataset_info:
                return {"success": False, "error": f"Dataset {dataset_id} not found"}

            if dataset_info["family"] != "ERA5":
                return {"success": False, "error": "Dataset is not ERA5"}

            # Build request payload
            search_handles = json.loads(dataset_info.get("search_handles", "{}"))
            slug = search_handles.get("slug")
            if not slug:
                return {"success": False, "error": "Dataset missing CDS slug"}

            base_payload = self.build_download_request(dataset_info, parameters)

            # Validate base payload
            if not base_payload.get("variable"):
                return {"success": False, "error": "Missing required parameter: variable"}

            # --- AUTO-CHUNKING LOGIC ---
            # Check if request spans multiple years
            years = base_payload.get("year", [])
            if not isinstance(years, list):
                years = [years]

            # Rule: Split if > 1 year
            should_chunk = len(years) > 1

            if should_chunk:
                logger.info(f"Auto-chunking logic triggered for {len(years)} years")
                downloaded_files = []
                total_size = 0

                for year in sorted(years):
                    chunk_payload = base_payload.copy()
                    chunk_payload["year"] = [year]

                    # Generate chunk filename: inject year before extension
                    p = Path(output_file)
                    chunk_filename = p.parent / f"{p.stem}_{year}{p.suffix}"
                    chunk_file_str = str(chunk_filename)

                    logger.info(f"Downloading chunk: {year} -> {chunk_file_str}")

                    try:
                        self.client.retrieve(slug, chunk_payload, chunk_file_str)

                        if Path(chunk_file_str).exists():
                            sz = Path(chunk_file_str).stat().st_size
                            total_size += sz
                            downloaded_files.append(chunk_file_str)
                        else:
                            logger.error(f"Chunk download failed (file missing): {chunk_file_str}")
                    except Exception as e:
                        logger.error(f"Chunk download error for {year}: {e}")
                        return {"success": False, "error": f"Failed to download chunk {year}: {str(e)}"}

                return {
                    "success": True,
                    "output_file": downloaded_files,
                    "file_size_bytes": total_size,
                    "dataset_id": dataset_id,
                    "payload": base_payload,
                    "chunked": True,
                }

            # --- STANDARD SINGLE DOWNLOAD ---
            logger.info(f"Downloading ERA5 data (single request): {dataset_id} -> {output_file}")
            logger.info(f"CDS Slug: {slug}")

            # Validate payload format (all list params should be lists)
            list_params = ["year", "month", "day", "time", "variable"]
            for key in list_params:
                if key in base_payload and not isinstance(base_payload[key], list):
                    return {
                        "success": False,
                        "error": f"Parameter '{key}' must be a list, got {type(base_payload[key])}: {base_payload[key]}"
                    }

            self.client.retrieve(slug, base_payload, output_file)

            if Path(output_file).exists():
                file_size = Path(output_file).stat().st_size
                return {
                    "success": True,
                    "output_file": output_file,
                    "file_size_bytes": file_size,
                    "dataset_id": dataset_id,
                    "payload": base_payload,
                }
            else:
                return {
                    "success": False,
                    "error": "Download completed but file not found",
                }

        except Exception as e:
            logger.error(f"ERA5 download failed: {e}")
            return {"success": False, "error": str(e)}


# --- CMIP6 Download Handler ---
class CMIP6DownloadHandler:
    """Handle CMIP6 data downloads via ESGF HTTP"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "SimulationDataAcquisitionAgent/1.0"})

    def fetch_download_links(
        self, dataset_info: Dict[str, Any], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Fetch download links for CMIP6 dataset from ESGF"""
        try:
            # Parse DRS fields from search_handles or dataset_id
            search_handles = json.loads(dataset_info.get("search_handles", "{}"))
            drs = search_handles.get("drs", {})
            
            if not drs:
                # Try to parse from dataset_id (CMIP6::CMIP6.CFMIP.AS-RCEC.TaiESM1.amip-4xCO2.r1i1p1f1.3hr.tas.gn)
                dataset_id = dataset_info["dataset_id"]
                if dataset_id.startswith("CMIP6::"):
                    parts = dataset_id.replace("CMIP6::", "").split(".")
                    if len(parts) >= 8:
                        drs = {
                            "activity_id": parts[1],
                            "institution_id": parts[2],
                            "source_id": parts[3],
                            "experiment_id": parts[4],
                            "variant_label": parts[5],
                            "table_id": parts[6],
                            "variable_id": parts[7],
                            "grid_label": parts[8] if len(parts) > 8 else "gn",
                        }

            if not drs:
                return []

            # Build ESGF query parameters
            query_params = {
                "project": "CMIP6",
                "type": "File",
                "limit": limit,
                "format": "application/solr+json",
            }
            for key, value in drs.items():
                query_params[key] = value

            # Use esgf_search if available, otherwise fallback to manual search
            if CMIP6_HELPERS_AVAILABLE:
                try:
                    node, docs = esgf_search(query_params)
                    if docs:
                        links = []
                        for doc in docs[:limit]:
                            url = pick_first_file_url(doc)
                            if url:
                                links.append({
                                    "url": url,
                                    "filename": doc.get("title", url.split("/")[-1]),
                                    "size": doc.get("size", 0),
                                    "checksum": doc.get("checksum", ""),
                                })
                        return links
                except Exception as e:
                    logger.warning(f"esgf_search failed, using fallback: {e}")

            # Fallback: manual ESGF query
            for node_url in ESGF_NODES:
                try:
                    esgf_url = f"{node_url}{ESGF_API_PATH}"
                    response = self.session.get(
                        esgf_url, params=query_params, timeout=ESGF_TIMEOUT
                    )
                    response.raise_for_status()
                    data = response.json()

                    # Extract download URLs
                    links = []
                    for doc in data.get("response", {}).get("docs", [])[:limit]:
                        url = doc.get("url", [""])[0] if doc.get("url") else None
                        if url:
                            # Handle pipe-separated format: "url|mime|protocol"
                            if isinstance(url, str) and "|" in url:
                                url = url.split("|")[0]
                            links.append(
                                {
                                    "url": url,
                                    "filename": doc.get("title", url.split("/")[-1]),
                                    "size": doc.get("size", 0),
                                    "checksum": doc.get("checksum", ""),
                                }
                            )
                    return links

                except Exception as e:
                    logger.warning(f"ESGF node {node_url} failed: {e}")
                    continue

            return []

        except Exception as e:
            logger.error(f"Failed to fetch CMIP6 download links: {e}")
            return []

    def download_cmip6_file(
        self, url: str, output_file: str, verify_checksum: bool = False
    ) -> Dict[str, Any]:
        """Download a single CMIP6 file via HTTP"""
        try:
            output_path = Path(output_file)
            
            # Check if file already exists
            if output_path.exists():
                existing_size = output_path.stat().st_size
                logger.info(f"File already exists: {output_file} ({existing_size / (1024*1024):.2f} MB)")
                return {
                    "success": True,
                    "output_file": str(output_path),
                    "file_size_bytes": existing_size,
                    "url": url,
                    "skipped": True,
                    "message": "File already exists, skipped download"
                }
            
            logger.info(f"Downloading CMIP6 file: {url} -> {output_file}")

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Download file
            response = self.session.get(url, stream=True, timeout=ESGF_TIMEOUT)
            response.raise_for_status()

            file_size = 0
            with open(output_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        file_size += len(chunk)

            if Path(output_file).exists():
                return {
                    "success": True,
                    "output_file": output_file,
                    "file_size_bytes": file_size,
                    "url": url,
                    "skipped": False
                }
            else:
                return {"success": False, "error": "Download completed but file not found"}

        except Exception as e:
            logger.error(f"CMIP6 download failed: {e}")
            return {"success": False, "error": str(e)}


# Initialize handlers
db_connector = SimulationDatabaseConnector()
era5_handler = ERA5DownloadHandler()
cmip6_handler = CMIP6DownloadHandler()
llm = BedrockClaudeLLM() if LANGCHAIN_AVAILABLE else None

# --- LangChain Tools ---

class ListStoredSimulationDatasetsTool(BaseTool):
    """List all stored simulation datasets from the database"""
    name: str = "list_stored_simulation_datasets"
    description: str = (
        "List all simulation datasets stored in the database. "
        "Input JSON: {'family': 'ERA5'|'CMIP6'|None, 'limit': 50}. "
        "Returns dataset IDs, titles, families, and metadata."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input else {}
            family = params.get("family")
            limit = params.get("limit", 50)
            
            datasets = db_connector.list_stored_datasets(family=family, limit=limit)
            
            if not datasets:
                return f"No stored simulation datasets found (family={family}, limit={limit})"
            
            output = f"📊 STORED SIMULATION DATASETS ({len(datasets)} total):\n"
            output += "=" * 60 + "\n\n"
            
            for i, ds in enumerate(datasets, 1):
                output += f"{i}. {ds['title']}\n"
                output += f"   ID: {ds['dataset_id']}\n"
                output += f"   Family: {ds['family']}\n"
                output += f"   Variables: {ds.get('variables', '[]')[:50]}...\n"
                output += f"   Temporal: {ds.get('temporal_coverage', 'N/A')}\n"
                output += f"   Updated: {ds.get('updated_at', 'N/A')}\n\n"
            
            return output
        except Exception as e:
            return f"⚠️ Error listing datasets: {str(e)}\n\n💡 SUGGESTION: Use 'execute_python_code' to query the database directly or check database connection."


class QueryStoredSimulationDatasetTool(BaseTool):
    """Query a specific stored simulation dataset by ID"""
    name: str = "query_stored_simulation_dataset"
    description: str = (
        "Get complete information about a stored simulation dataset by its ID. "
        "Returns dataset metadata, API endpoints, download links, and relationships."
    )

    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            dataset = db_connector.get_dataset(dataset_id)
            if not dataset:
                return f"Dataset not found: {dataset_id}"
            
            output = f"📋 DATASET INFORMATION: {dataset_id}\n"
            output += "=" * 60 + "\n\n"
            
            output += f"Title: {dataset['title']}\n"
            output += f"Family: {dataset['family']}\n"
            output += f"Description: {dataset.get('description', 'N/A')[:200]}...\n\n"
            
            # Parse JSON fields
            try:
                variables = json.loads(dataset.get('variables', '[]'))
                keywords = json.loads(dataset.get('keywords', '[]'))
                download_links = json.loads(dataset.get('download_links', '[]'))
                search_handles = json.loads(dataset.get('search_handles', '{}'))
            except:
                variables = []
                keywords = []
                download_links = []
                search_handles = {}
            
            output += f"Variables: {', '.join(variables[:10])}\n"
            output += f"Keywords: {', '.join(keywords[:10])}\n"
            output += f"Spatial Coverage: {dataset.get('spatial_coverage', 'N/A')}\n"
            output += f"Temporal Coverage: {dataset.get('temporal_coverage', 'N/A')}\n\n"
            
            # API endpoint (for ERA5)
            if dataset['family'] == 'ERA5' and dataset.get('api_endpoint'):
                output += f"🌐 ERA5 API Endpoint: {dataset['api_endpoint']}\n"
                output += f"   Slug: {search_handles.get('slug', 'N/A')}\n"
                output += f"   Note: Use 'download_era5_data' to download actual data\n\n"
            
            # Download links (for CMIP6)
            if download_links:
                output += f"🔗 Download Links ({len(download_links)}):\n"
                for i, link in enumerate(download_links[:5], 1):
                    if isinstance(link, dict):
                        url = link.get('url', 'N/A')
                        output += f"   {i}. {url[:60]}...\n"
                if len(download_links) > 5:
                    output += f"   ... and {len(download_links) - 5} more\n"
                output += "\n"
            
            # Relationships
            relationships = db_connector.get_dataset_relationships(dataset_id)
            if relationships:
                output += f"🔗 Relationships ({len(relationships)}):\n"
                rel_types = {}
                for rel in relationships:
                    rel_type = rel.get('relation_type', 'unknown')
                    rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
                for rel_type, count in list(rel_types.items())[:10]:
                    output += f"   • {rel_type}: {count}\n"
                output += "\n"
            
            return output
        except Exception as e:
            return f"Error querying dataset: {str(e)}"


class AnalyzeDatasetBeforeDownloadTool(BaseTool):
    """Analyze dataset metadata to estimate download size, variables, and requirements before downloading"""
    name: str = "analyze_dataset_before_download"
    description: str = (
        "Analyze a stored simulation dataset to estimate download size, available variables, "
        "temporal/spatial coverage, and download requirements BEFORE downloading. "
        "Input: dataset_id. Returns detailed analysis including estimated file size, "
        "variable information, time range, spatial extent, and download recommendations."
    )

    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            dataset = db_connector.get_dataset(dataset_id)
            if not dataset:
                return f"Dataset not found: {dataset_id}"
            
            output = f"[ANALYSIS] Dataset: {dataset_id}\n"
            output += "=" * 60 + "\n\n"
            
            # Basic info
            output += f"Title: {dataset['title']}\n"
            output += f"Family: {dataset['family']}\n"
            output += f"Description: {dataset.get('description', 'N/A')[:200]}...\n\n"
            
            # Parse JSON fields
            try:
                variables = json.loads(dataset.get('variables', '[]'))
                keywords = json.loads(dataset.get('keywords', '[]'))
                download_links = json.loads(dataset.get('download_links', '[]'))
                search_handles = json.loads(dataset.get('search_handles', '{}'))
            except:
                variables = []
                keywords = []
                download_links = []
                search_handles = {}
            
            # Variables analysis
            output += f"VARIABLES ({len(variables)}):\n"
            for var in variables[:10]:
                output += f"  • {var}\n"
            if len(variables) > 10:
                output += f"  ... and {len(variables) - 10} more\n"
            output += "\n"
            
            # Temporal coverage
            temporal = dataset.get('temporal_coverage', '')
            output += f"TEMPORAL COVERAGE: {temporal}\n"
            
            # Spatial coverage
            spatial = dataset.get('spatial_coverage', '')
            output += f"SPATIAL COVERAGE: {spatial}\n\n"
            
            # Download size estimation
            if dataset['family'] == 'ERA5':
                output += "DOWNLOAD SIZE ESTIMATION (ERA5):\n"
                # Estimate based on parameters
                schema = search_handles.get('retrieve_payload_schema', {})
                if schema:
                    # Rough estimation: ~1-5 MB per variable per month for single-level data
                    var_count = len(variables) if variables else 1
                    time_range = temporal
                    if 'year' in str(search_handles):
                        # Single year: ~12-60 MB per variable (global)
                        estimated_mb_global = var_count * 30  # Conservative estimate
                        estimated_mb_regional = var_count * 5  # City-scale with area parameter
                    else:
                        estimated_mb_global = var_count * 100  # Multi-year estimate
                        estimated_mb_regional = var_count * 15  # Multi-year regional
                    
                    output += f"  Estimated size (GLOBAL, no spatial filter): {estimated_mb_global:.0f} - {estimated_mb_global * 2:.0f} MB\n"
                    output += f"  Estimated size (REGIONAL, with 'area' parameter): {estimated_mb_regional:.0f} - {estimated_mb_regional * 2:.0f} MB\n"
                    output += f"  💡 TIP: Use 'area' parameter [north, west, south, east] to reduce download size significantly!\n"
                    output += f"  (Based on {var_count} variable(s), temporal coverage: {temporal})\n"
                output += f"  Format: NetCDF\n"
                output += f"  Download method: CDS API (asynchronous)\n"
                output += f"  Output location: era5_data/\n\n"
                
            elif dataset['family'] == 'CMIP6':
                output += "DOWNLOAD SIZE ESTIMATION (CMIP6):\n"
                if download_links:
                    total_size = sum(link.get('size', 0) for link in download_links if isinstance(link, dict))
                    if total_size > 0:
                        total_size_mb = total_size / (1024 * 1024)
                        output += f"  Available files: {len(download_links)}\n"
                        output += f"  Total size: {total_size_mb:.2f} MB ({total_size_mb/1024:.2f} GB)\n"
                    else:
                        output += f"  Available files: {len(download_links)}\n"
                        output += f"  Size: Unknown (typically 100-500 MB per file)\n"
                else:
                    output += f"  Files: Will be fetched from ESGF\n"
                    output += f"  Typical size: 100-500 MB per file\n"
                output += f"  Format: NetCDF\n"
                output += f"  Download method: ESGF HTTP (direct)\n"
                output += f"  Output location: cmip6_data/\n\n"
            
            # Download requirements
            output += "DOWNLOAD REQUIREMENTS:\n"
            if dataset['family'] == 'ERA5':
                output += "  • CDS API credentials (.cdsapirc file)\n"
                output += "  • Parameters: variable, year, month, area (optional)\n"
                output += "  • Download time: 5-30 minutes (asynchronous)\n"
            else:
                output += "  • ESGF access (may require OpenID authentication)\n"
                output += "  • DRS fields: activity_id, experiment_id, variable_id, etc.\n"
                output += "  • Download time: Depends on file size and network speed\n"
            
            output += "\nRECOMMENDATIONS:\n"
            if dataset['family'] == 'ERA5':
                output += "  • Use 'download_era5_data' with specific parameters\n"
                output += "  • Consider downloading monthly data first to test\n"
                output += "  • Use 'area' parameter to limit spatial extent\n"
            else:
                output += "  • Use 'download_cmip6_data' with limit parameter\n"
                output += "  • Start with limit=1 to test download\n"
                output += "  • Check file sizes before downloading multiple files\n"
            
            return output
        except Exception as e:
            return f"Error analyzing dataset: {str(e)}"


class DownloadERA5DataTool(BaseTool):
    """Download ERA5 data using cdsapi"""
    name: str = "download_era5_data"
    description: str = (
        "Download ERA5 data for a stored dataset using CDS API. "
        "Input JSON: {'dataset_id': 'ERA5::...', 'output_file': 'data.nc', 'parameters': {...}}. "
        "Parameters can override defaults (e.g., {'variable': '2m_temperature', 'year': '2020', 'month': '01', 'area': [40, -75, 35, -70]}). "
        "SPATIAL SUBSETTING: Use 'area' parameter [north, west, south, east] to limit geographic extent. "
        "This significantly reduces download size (from GBs to MBs for city-scale regions). "
        "If user mentions a location (city/country), use execute_python_code to query coordinates first, then include 'area' in parameters. "
        "Requires .cdsapirc configuration file."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input else {}
            dataset_id = params.get("dataset_id", "")
            # Default to era5_data directory
            default_filename = f"era5_{dataset_id.replace('::', '_').replace(':', '_')}.nc"
            output_file = params.get("output_file", str(Path("era5_data") / default_filename))
            parameters = params.get("parameters", {})
            
            # Ensure output_file is in era5_data directory
            output_path = Path(output_file)
            if output_path.parent.name != "era5_data":
                output_path = Path("era5_data") / output_path.name
                output_file = str(output_path)
            
            if not dataset_id:
                return "Error: dataset_id is required"
            
            # Create directory if needed
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            
            result = era5_handler.download_era5_data(
                dataset_id, output_file, parameters
            )
            
            if result.get("success"):
                file_size_mb = result["file_size_bytes"] / (1024 * 1024)
                output = f"✅ ERA5 DOWNLOAD SUCCESSFUL\n"
                output += "=" * 50 + "\n\n"
                output += f"Dataset: {dataset_id}\n"
                output += f"Output File: {output_file}\n"
                output += f"File Size: {file_size_mb:.2f} MB\n"
                output += f"Payload: {json.dumps(result.get('payload', {}), indent=2)}\n\n"
                output += f"💡 Use 'load_netcdf_data' to analyze the downloaded file"
                return output
            else:
                return f"❌ ERA5 Download Failed: {result.get('error', 'Unknown error')}"
        except Exception as e:
            return f"⚠️ Error downloading ERA5 data: {str(e)}\n\n💡 SUGGESTION: Try using 'execute_python_code' to:\n1. Check CDS API configuration\n2. Verify parameters format\n3. Try alternative download methods\n4. Install/update cdsapi: pip install cdsapi"


class DownloadCMIP6DataTool(BaseTool):
    """Download CMIP6 data files via ESGF HTTP"""
    name: str = "download_cmip6_data"
    description: str = (
        "Download CMIP6 data files for a stored dataset via ESGF HTTP. "
        "Input JSON: {'dataset_id': 'CMIP6::...', 'output_dir': './cmip6_data', 'limit': 100}. "
        "Downloads actual NetCDF files from ESGF nodes."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input else {}
            dataset_id = params.get("dataset_id", "")
            # Default to cmip6_data directory
            output_dir = params.get("output_dir", "cmip6_data")
            limit = params.get("limit", 3)
            
            if not dataset_id:
                return "Error: dataset_id is required"
            
            # Ensure output_dir is cmip6_data
            output_path = Path(output_dir)
            if output_path.name != "cmip6_data":
                output_dir = "cmip6_data"
            
            # Get dataset info
            dataset = db_connector.get_dataset(dataset_id)
            if not dataset:
                return f"Dataset not found: {dataset_id}"
            
            if dataset["family"] != "CMIP6":
                return f"Dataset is not CMIP6: {dataset['family']}"
            
            # Fetch download links
            links = cmip6_handler.fetch_download_links(dataset, limit=limit)
            if not links:
                return f"No download links found for {dataset_id}. Check ESGF availability."
            
            # Download files
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            results = []
            
            for i, link_info in enumerate(links[:limit], 1):
                url = link_info["url"]
                filename = link_info.get("filename", f"file_{i}.nc")
                output_file = Path(output_dir) / filename
                
                result = cmip6_handler.download_cmip6_file(url, str(output_file))
                results.append(result)
            
            # Summary
            successful = sum(1 for r in results if r.get("success"))
            total_size_mb = sum(
                r.get("file_size_bytes", 0) for r in results if r.get("success")
            ) / (1024 * 1024)
            
            output = f"📥 CMIP6 DOWNLOAD SUMMARY\n"
            output += "=" * 50 + "\n\n"
            output += f"Dataset: {dataset_id}\n"
            output += f"Files Downloaded: {successful}/{len(results)}\n"
            output += f"Total Size: {total_size_mb:.2f} MB\n"
            output += f"Output Directory: {output_dir}\n\n"
            
            for i, result in enumerate(results, 1):
                if result.get("success"):
                    if result.get("skipped"):
                        output += f"⏭️  File {i}: {Path(result['output_file']).name} (already exists, skipped)\n"
                    else:
                        output += f"✅ File {i}: {Path(result['output_file']).name}\n"
                else:
                    output += f"❌ File {i}: {result.get('error', 'Unknown error')}\n"
            
            if successful > 0:
                output += f"\n💡 Use 'load_netcdf_data' to analyze downloaded files"
            
            return output
        except Exception as e:
            return f"⚠️ Error downloading CMIP6 data: {str(e)}\n\n💡 SUGGESTION: Try using 'execute_python_code' to:\n1. Check ESGF authentication\n2. Try alternative download URLs\n3. Verify dataset availability\n4. Implement custom download logic"


class LoadNetCDFDataTool(BaseTool):
    """Load and preview NetCDF and GRIB data files (supports both ERA5 GRIB and CMIP6 NetCDF)"""
    name: str = "load_netcdf_data"
    description: str = (
        "Load and preview climate data files downloaded from ERA5 or CMIP6. "
        "Automatically detects file format (NetCDF or GRIB). "
        "Input: file path. Returns dataset dimensions, variables, coordinates, and sample data. "
        "For ERA5 GRIB files, uses cfgrib engine. For CMIP6 NetCDF files, uses netcdf4 engine."
    )

    def _load_grib_file(self, file_path: str):
        """
        Load GRIB file with multiple fallback strategies.
        Handles GRIB1/GRIB2 compatibility issues.
        """
        import warnings
        warnings.filterwarnings('ignore')
        
        # Strategy 1: Try cfgrib (requires eccodes, supports GRIB2)
        try:
            import cfgrib
            # Try with default settings first
            try:
                ds = xr.open_dataset(file_path, engine='cfgrib')
                return ds, "cfgrib"
            except Exception as e1:
                # Try with backend_kwargs for GRIB2
                try:
                    ds = xr.open_dataset(file_path, engine='cfgrib', backend_kwargs={'errors': 'ignore'})
                    return ds, "cfgrib (with error handling)"
                except Exception as e2:
                    # If cfgrib fails, try NetCDF engine (some ERA5 files are actually NetCDF)
                    try:
                        ds = xr.open_dataset(file_path, engine='netcdf4')
                        return ds, "netcdf4 (fallback)"
                    except Exception as e3:
                        # Last resort: try scipy
                        try:
                            ds = xr.open_dataset(file_path, engine='scipy')
                            return ds, "scipy (fallback)"
                        except Exception as e4:
                            raise Exception(
                                f"All loading methods failed:\n"
                                f"  cfgrib (default): {str(e1)}\n"
                                f"  cfgrib (with error handling): {str(e2)}\n"
                                f"  netcdf4: {str(e3)}\n"
                                f"  scipy: {str(e4)}\n"
                                f"Note: If this is a GRIB2 file, ensure eccodes is installed: pip install eccodes"
                            )
        except ImportError:
            # cfgrib not installed, try NetCDF engines
            try:
                ds = xr.open_dataset(file_path, engine='netcdf4')
                return ds, "netcdf4 (cfgrib not available)"
            except Exception as e:
                try:
                    ds = xr.open_dataset(file_path, engine='scipy')
                    return ds, "scipy (cfgrib not available)"
                except Exception as e2:
                    raise ImportError(
                        f"cfgrib not installed and NetCDF engines failed.\n"
                        f"Install cfgrib: pip install cfgrib eccodes\n"
                        f"NetCDF error: {str(e)}\n"
                        f"Scipy error: {str(e2)}"
                    )

    def _run(self, file_path: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4"
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return f"File not found: {file_path}"
            
            # Detect file format
            file_format = self._detect_file_format(file_path_obj)
            
            output = f"[DATA FILE PREVIEW]: {file_path_obj.name}\n"
            output += "=" * 60 + "\n\n"
            output += f"File Format: {file_format}\n"
            output += f"File Size: {file_path_obj.stat().st_size / (1024*1024):.2f} MB\n\n"
            
            # Try loading with appropriate engine
            ds = None
            if file_format == "GRIB":
                # Try loading GRIB file with fallback strategies
                try:
                    ds, method_used = self._load_grib_file(file_path)
                    output += f"✓ Successfully loaded as GRIB file (method: {method_used})\n\n"
                except ImportError as e:
                    return f"Error: {str(e)}"
                except Exception as e:
                    # If GRIB loading fails, try NetCDF as fallback
                    try:
                        ds = xr.open_dataset(file_path, engine='netcdf4')
                        output += "✓ Loaded as NetCDF file (GRIB loading failed, using NetCDF fallback)\n\n"
                    except Exception as e2:
                        return f"⚠️ Error loading GRIB file: {str(e)}\nNetCDF fallback also failed: {str(e2)}\n\n💡 SUGGESTION: Use 'execute_python_code' to try alternative loading methods or install missing dependencies."
            else:
                # Try netcdf4 for NetCDF files (CMIP6)
                try:
                    # Use chunks for CMIP6 files to reduce memory usage
                    ds = xr.open_dataset(file_path, engine='netcdf4', chunks={'time': 100})
                    output += "✓ Successfully loaded as NetCDF file (CMIP6 format)\n\n"
                except Exception as e:
                    # Fallback to scipy
                    try:
                        ds = xr.open_dataset(file_path, engine='scipy', chunks={'time': 100})
                        output += "✓ Successfully loaded with scipy engine\n\n"
                    except Exception as e2:
                        return f"⚠️ Error loading NetCDF file: {str(e)}\nFallback error: {str(e2)}\n\n💡 SUGGESTION: Use 'execute_python_code' to check file format or try alternative engines."
            
            if ds is None:
                return "⚠️ Error: Failed to load dataset\n\n💡 SUGGESTION: Use 'execute_python_code' to diagnose the issue or try alternative loading methods."
            
            try:
                # Use .sizes instead of .dims to avoid FutureWarning
                output += f"Dimensions: {dict(ds.sizes)}\n"
                output += f"Coordinates: {list(ds.coords)}\n"
                output += f"Data Variables: {list(ds.data_vars)}\n\n"
                
                # Show variable details
                if ds.data_vars:
                    output += "VARIABLE DETAILS:\n"
                    for var_name in list(ds.data_vars)[:5]:
                        var = ds[var_name]
                        output += f"  • {var_name}:\n"
                        output += f"    Shape: {var.shape}\n"
                        output += f"    Dtype: {var.dtype}\n"
                        if hasattr(var, "attrs"):
                            attrs = dict(var.attrs)
                            if "long_name" in attrs:
                                output += f"    Long Name: {attrs['long_name']}\n"
                            if "units" in attrs:
                                output += f"    Units: {attrs['units']}\n"
                            if "standard_name" in attrs:
                                output += f"    Standard Name: {attrs['standard_name']}\n"
                        # Show data range (use compute() for chunked data)
                        try:
                            if hasattr(var, 'chunks') and var.chunks:
                                var_min = float(var.min().compute())
                                var_max = float(var.max().compute())
                                var_mean = float(var.mean().compute())
                            else:
                                var_min = float(var.min())
                                var_max = float(var.max())
                                var_mean = float(var.mean())
                            output += f"    Range: {var_min:.3f} to {var_max:.3f} (mean: {var_mean:.3f})\n"
                        except:
                            pass
                        output += "\n"
                
                # Show coordinate details
                if ds.coords:
                    output += "COORDINATE DETAILS:\n"
                    for coord_name in list(ds.coords)[:5]:
                        coord = ds[coord_name]
                        output += f"  • {coord_name}:\n"
                        output += f"    Shape: {coord.shape}\n"
                        try:
                            if hasattr(coord, 'chunks') and coord.chunks:
                                coord_min = float(coord.min().compute())
                                coord_max = float(coord.max().compute())
                            else:
                                coord_min = float(coord.min())
                                coord_max = float(coord.max())
                            output += f"    Range: {coord_min:.3f} to {coord_max:.3f}\n"
                            if coord_name == 'time' and hasattr(coord, 'values'):
                                try:
                                    import pandas as pd
                                    time_values = coord.values if not (hasattr(coord, 'chunks') and coord.chunks) else coord.compute().values
                                    time_start = pd.to_datetime(time_values[0])
                                    time_end = pd.to_datetime(time_values[-1])
                                    output += f"    Time Range: {time_start} to {time_end}\n"
                                except:
                                    pass
                        except:
                            pass
                        output += "\n"
                
                # Show global attributes
                if hasattr(ds, "attrs") and ds.attrs:
                    output += "GLOBAL ATTRIBUTES:\n"
                    for key, value in list(ds.attrs.items())[:10]:
                        output += f"  • {key}: {str(value)[:100]}\n"
                
                output += f"\n✅ Data loaded successfully. Ready for analysis.\n"
                output += f"💡 Use 'process_era5_data' or 'process_cmip6_data' for specialized processing.\n"
                output += f"💡 Use 'execute_python_code' for custom analysis."
                
                return output
            finally:
                # Explicitly close dataset to free memory
                ds.close()
        except Exception as e:
            import traceback
            return f"⚠️ Error loading data file: {str(e)}\n{traceback.format_exc()}\n\n💡 SUGGESTION: Use 'execute_python_code' to diagnose and fix the issue."
    
    def _detect_file_format(self, file_path: Path) -> str:
        """Detect file format by reading file header"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                # GRIB files start with "GRIB"
                if header.startswith(b'GRIB'):
                    return "GRIB"
                # NetCDF files have specific magic numbers
                elif header.startswith(b'\x89HDF') or header.startswith(b'CDF'):
                    return "NetCDF"
                else:
                    # Default to NetCDF if extension is .nc
                    if file_path.suffix.lower() == '.nc':
                        return "NetCDF"
                    return "Unknown"
        except:
            # Fallback to extension
            if file_path.suffix.lower() == '.nc':
                return "NetCDF"
            return "Unknown"


class ExecutePythonCodeTool(BaseTool):
    """Execute Python code for data analysis and visualization"""
    name: str = "execute_python_code"
    description: str = (
        "Execute Python code to analyze downloaded climate data files. "
        "Can read NetCDF files, create plots, perform statistical analysis, and save results. "
        "Input: Python code as string."
    )

    def _run(self, python_code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import sys
            import warnings
            from io import StringIO
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            
            # Suppress common warnings
            warnings.filterwarnings('ignore', category=FutureWarning)
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
            warnings.filterwarnings('ignore', message='.*FigureCanvasAgg.*')
            
            # Capture stdout and stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = captured_output = StringIO()
            sys.stderr = captured_stderr = StringIO()
            
            # Prepend code to suppress warnings and use .sizes instead of .dims
            setup_code = """
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')
warnings.filterwarnings('ignore', message='.*FigureCanvasAgg.*')

# Use .sizes instead of .dims to avoid FutureWarning
# If user code uses .dims, it will still work but may show warnings
"""
            
            # Create execution environment with common libraries
            exec_globals = {
                '__builtins__': __builtins__,
                'xr': xr if XARRAY_AVAILABLE else None,
                'np': np if XARRAY_AVAILABLE else None,
                'pd': pd if PANDAS_AVAILABLE else None,
                'plt': plt,
                'Path': Path,
                'os': os,
                'warnings': warnings,
            }
            
            # Import seaborn if available
            try:
                import seaborn as sns
                exec_globals['sns'] = sns
            except ImportError:
                exec_globals['sns'] = None
            
            # Import cfgrib for GRIB files if available
            try:
                import cfgrib
                exec_globals['cfgrib'] = cfgrib
            except ImportError:
                exec_globals['cfgrib'] = None
            
            # Execute setup code first
            exec(setup_code, exec_globals)
            
            # Execute user code
            exec(python_code, exec_globals)
            
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            code_output = captured_output.getvalue()
            error_output = captured_stderr.getvalue()
            
            output = f"[PYTHON CODE EXECUTION]\n"
            output += "=" * 40 + "\n\n"
            output += f"Code executed successfully.\n"
            if code_output.strip():
                output += f"Output:\n{code_output}\n"
            if error_output.strip():
                # Filter out common warnings
                filtered_errors = [line for line in error_output.split('\n') 
                                 if 'FutureWarning' not in line and 
                                    'FigureCanvasAgg' not in line and
                                    'UserWarning' not in line]
                if filtered_errors:
                    output += f"Warnings/Errors:\n{chr(10).join(filtered_errors)}\n"
            
            # Check for generated files
            plot_files = list(Path('.').glob('*.png')) + list(Path('.').glob('*.pdf'))
            data_files = list(Path('.').glob('*.csv')) + list(Path('.').glob('*.json')) + list(Path('.').glob('*.nc'))
            if plot_files:
                output += f"\nGenerated plots: {[str(f) for f in plot_files]}\n"
            if data_files:
                output += f"Generated data files: {[str(f) for f in data_files]}\n"
            
            return output
        except Exception as e:
            import traceback
            # Restore stdout/stderr in case of error
            try:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            except:
                pass
            return f"[ERROR] Python execution error:\n{traceback.format_exc()}"


class ProcessERA5DataTool(BaseTool):
    """Process ERA5 GRIB data files with specialized ERA5 handling"""
    name: str = "process_era5_data"
    description: str = (
        "Process ERA5 GRIB data files with specialized handling. "
        "Automatically loads GRIB files, extracts variables, calculates statistics, "
        "and creates visualizations. Input: file path. "
        "Returns processed data summary and saves analysis results."
    )

    def _load_grib_file(self, file_path: str):
        """Load GRIB file with multiple fallback strategies"""
        import warnings
        warnings.filterwarnings('ignore')
        
        try:
            import cfgrib
            try:
                ds = xr.open_dataset(file_path, engine='cfgrib')
                return ds, "cfgrib"
            except Exception as e1:
                try:
                    ds = xr.open_dataset(file_path, engine='cfgrib', backend_kwargs={'errors': 'ignore'})
                    return ds, "cfgrib (with error handling)"
                except Exception as e2:
                    try:
                        ds = xr.open_dataset(file_path, engine='netcdf4')
                        return ds, "netcdf4 (fallback)"
                    except Exception as e3:
                        raise Exception(
                            f"GRIB loading failed:\n"
                            f"  cfgrib: {str(e1)}\n"
                            f"  cfgrib (with error handling): {str(e2)}\n"
                            f"  netcdf4: {str(e3)}\n"
                            f"Install eccodes: pip install eccodes"
                        )
        except ImportError:
            try:
                ds = xr.open_dataset(file_path, engine='netcdf4')
                return ds, "netcdf4 (cfgrib not available)"
            except Exception as e:
                raise ImportError(f"cfgrib not installed. Install: pip install cfgrib eccodes\nNetCDF error: {str(e)}")

    def _run(self, file_path: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4 cfgrib"
        
        try:
            import warnings
            warnings.filterwarnings('ignore')
            
            # Load GRIB file with fallback strategies
            try:
                ds, method_used = self._load_grib_file(file_path)
                logger.info(f"Loaded ERA5 file using: {method_used}")
            except Exception as e:
                error_msg = str(e)
                return (
                    f"⚠️ Error loading ERA5 GRIB file: {error_msg}\n\n"
                    f"💡 SUGGESTION: You can try using 'execute_python_code' to:\n"
                    f"  1. Install missing dependencies (e.g., pip install eccodes)\n"
                    f"  2. Try alternative loading methods (netcdf4, scipy engines)\n"
                    f"  3. Convert GRIB to NetCDF format if needed\n"
                    f"  4. Check file format and try different approaches\n\n"
                    f"Example: Use 'execute_python_code' with Python code to attempt loading the file with different methods."
                )
            
            try:
                output = f"[ERA5 DATA PROCESSING]: {Path(file_path).name}\n"
                output += "=" * 60 + "\n\n"
                
                # Extract variables
                variables = list(ds.data_vars)
                output += f"Variables found: {variables}\n\n"
                
                # Process each variable
                results = {}
                for var_name in variables[:3]:  # Process first 3 variables
                    var = ds[var_name]
                    results[var_name] = {
                        'mean': float(var.mean()),
                        'min': float(var.min()),
                        'max': float(var.max()),
                        'std': float(var.std()),
                        'shape': var.shape,
                        'units': var.attrs.get('units', 'N/A')
                    }
                    output += f"{var_name} Statistics:\n"
                    output += f"  Mean: {results[var_name]['mean']:.3f} {results[var_name]['units']}\n"
                    output += f"  Min: {results[var_name]['min']:.3f}\n"
                    output += f"  Max: {results[var_name]['max']:.3f}\n"
                    output += f"  Std: {results[var_name]['std']:.3f}\n\n"
                
                output += "✅ ERA5 data processed successfully.\n"
                output += "💡 Use 'execute_python_code' for custom analysis and visualization.\n"
                
                return output
            finally:
                # Explicitly close dataset to free memory
                ds.close()
        except Exception as e:
            import traceback
            return f"⚠️ Error processing ERA5 data: {str(e)}\n{traceback.format_exc()}\n\n💡 SUGGESTION: Use 'execute_python_code' to try alternative processing methods."


class ProcessCMIP6DataTool(BaseTool):
    """Process CMIP6 NetCDF data files with specialized CMIP6 handling"""
    name: str = "process_cmip6_data"
    description: str = (
        "Process CMIP6 NetCDF data files with specialized handling. "
        "Automatically loads NetCDF files, extracts variables, calculates statistics, "
        "handles DRS metadata, and creates visualizations. Input: file path. "
        "Returns processed data summary and saves analysis results."
    )

    def _run(self, file_path: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4"
        
        try:
            import warnings
            warnings.filterwarnings('ignore')
            
            # Load NetCDF file with chunks to reduce memory usage
            ds = xr.open_dataset(file_path, engine='netcdf4', chunks={'time': 100})
            
            try:
                output = f"[CMIP6 DATA PROCESSING]: {Path(file_path).name}\n"
                output += "=" * 60 + "\n\n"
                
                # Extract DRS information from filename
                filename = Path(file_path).name
                output += f"File: {filename}\n"
                output += f"Dimensions: {dict(ds.sizes)}\n\n"
                
                # Process variables
                variables = list(ds.data_vars)
                output += f"Variables found: {variables}\n\n"
                
                # Process each variable
                results = {}
                for var_name in variables[:3]:  # Process first 3 variables
                    var = ds[var_name]
                    # Use compute() for chunked data
                    if hasattr(var, 'chunks') and var.chunks:
                        var_mean = float(var.mean().compute())
                        var_min = float(var.min().compute())
                        var_max = float(var.max().compute())
                        var_std = float(var.std().compute())
                    else:
                        var_mean = float(var.mean())
                        var_min = float(var.min())
                        var_max = float(var.max())
                        var_std = float(var.std())
                    
                    results[var_name] = {
                        'mean': var_mean,
                        'min': var_min,
                        'max': var_max,
                        'std': var_std,
                        'shape': var.shape,
                        'units': var.attrs.get('units', 'N/A'),
                        'long_name': var.attrs.get('long_name', var_name)
                    }
                    output += f"{var_name} ({results[var_name]['long_name']}):\n"
                    output += f"  Mean: {results[var_name]['mean']:.3f} {results[var_name]['units']}\n"
                    output += f"  Min: {results[var_name]['min']:.3f}\n"
                    output += f"  Max: {results[var_name]['max']:.3f}\n"
                    output += f"  Std: {results[var_name]['std']:.3f}\n\n"
                
                # Time information
                if 'time' in ds.coords:
                    time_coord = ds.coords['time']
                    try:
                        import pandas as pd
                        time_values = time_coord.values if not (hasattr(time_coord, 'chunks') and time_coord.chunks) else time_coord.compute().values
                        time_start = pd.to_datetime(time_values[0])
                        time_end = pd.to_datetime(time_values[-1])
                        output += f"Time Range: {time_start} to {time_end}\n"
                        output += f"Time Steps: {len(time_coord)}\n\n"
                    except:
                        pass
                
                output += "✅ CMIP6 data processed successfully.\n"
                output += "💡 Use 'execute_python_code' for custom analysis and visualization.\n"
                
                return output
            finally:
                # Explicitly close dataset to free memory
                ds.close()
        except Exception as e:
            import traceback
            return f"⚠️ Error processing CMIP6 data: {str(e)}\n{traceback.format_exc()}\n\n💡 SUGGESTION: Use 'execute_python_code' to try alternative processing methods."


class ValidateDataQualityTool(BaseTool):
    """Validate data quality and perform quality checks on downloaded files"""
    name: str = "validate_data_quality"
    description: str = (
        "Validate data quality of downloaded climate data files. "
        "Checks for missing values, data ranges, temporal/spatial consistency, "
        "and format compliance. Input: file path. Returns quality assessment report."
    )

    def _run(self, file_path: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4"
        
        try:
            import warnings
            warnings.filterwarnings('ignore')
            
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return f"File not found: {file_path}"
            
            # Detect and load file
            file_format = self._detect_file_format(file_path_obj)
            if file_format == "GRIB":
                # Use LoadNetCDFDataTool's _load_grib_file method
                loader = LoadNetCDFDataTool()
                try:
                    ds, method_used = loader._load_grib_file(file_path)
                except Exception as e:
                    error_msg = str(e)
                    return (
                        f"⚠️ Error loading GRIB file: {error_msg}\n\n"
                        f"💡 SUGGESTION: Try using 'execute_python_code' to:\n"
                        f"  1. Install missing dependencies (pip install eccodes)\n"
                        f"  2. Try alternative loading methods\n"
                        f"  3. Check and convert file format if needed\n"
                    )
            else:
                # Use chunks for CMIP6 files to reduce memory usage
                ds = xr.open_dataset(file_path, engine='netcdf4', chunks={'time': 100})
            
            try:
                output = f"[DATA QUALITY VALIDATION]: {file_path_obj.name}\n"
                output += "=" * 60 + "\n\n"
                output += f"File Format: {file_format}\n"
                output += f"File Size: {file_path_obj.stat().st_size / (1024*1024):.2f} MB\n\n"
                
                # Quality checks
                checks = []
                
                # Check 1: Missing values
                for var_name in list(ds.data_vars)[:3]:
                    var = ds[var_name]
                    # Use compute() for chunked data
                    if hasattr(var, 'chunks') and var.chunks:
                        missing_count = int((var.isnull().sum().compute()).values)
                        total_count = int(var.size)
                    else:
                        missing_count = int((var.isnull().sum()).values)
                        total_count = int(var.size)
                    missing_pct = (missing_count / total_count) * 100 if total_count > 0 else 0
                    checks.append({
                        'check': f'Missing values in {var_name}',
                        'status': 'PASS' if missing_pct < 1 else 'WARNING',
                        'details': f'{missing_count}/{total_count} ({missing_pct:.2f}%)'
                    })
                
                # Check 2: Data ranges
                for var_name in list(ds.data_vars)[:3]:
                    var = ds[var_name]
                    # Use compute() for chunked data
                    if hasattr(var, 'chunks') and var.chunks:
                        var_min = float(var.min().compute())
                        var_max = float(var.max().compute())
                        var_mean = float(var.mean().compute())
                    else:
                        var_min = float(var.min())
                        var_max = float(var.max())
                        var_mean = float(var.mean())
                    # Check for reasonable ranges (temperature: -100 to 100 C, etc.)
                    if 'temp' in var_name.lower() or 'tas' in var_name.lower():
                        if var_min < -100 or var_max > 100:
                            status = 'WARNING'
                        else:
                            status = 'PASS'
                    else:
                        status = 'PASS'
                    checks.append({
                        'check': f'Data range for {var_name}',
                        'status': status,
                        'details': f'Range: {var_min:.3f} to {var_max:.3f}, Mean: {var_mean:.3f}'
                    })
                
                # Check 3: Coordinate consistency
                if 'time' in ds.coords:
                    time_coord = ds.coords['time']
                    if len(time_coord) > 1:
                        time_values = time_coord.values if not (hasattr(time_coord, 'chunks') and time_coord.chunks) else time_coord.compute().values
                        time_diff = time_values[1] - time_values[0]
                        checks.append({
                            'check': 'Time coordinate consistency',
                            'status': 'PASS',
                            'details': f'Time step: {time_diff}'
                        })
                
                # Check 4: Spatial coordinates
                if 'lat' in ds.coords and 'lon' in ds.coords:
                    lat = ds.coords['lat']
                    lon = ds.coords['lon']
                    # Use compute() for chunked data
                    if hasattr(lat, 'chunks') and lat.chunks:
                        lat_min = float(lat.min().compute())
                        lat_max = float(lat.max().compute())
                        lon_min = float(lon.min().compute())
                        lon_max = float(lon.max().compute())
                    else:
                        lat_min = float(lat.min())
                        lat_max = float(lat.max())
                        lon_min = float(lon.min())
                        lon_max = float(lon.max())
                    checks.append({
                        'check': 'Spatial coordinates',
                        'status': 'PASS',
                        'details': f'Lat: {lat_min:.2f} to {lat_max:.2f}, Lon: {lon_min:.2f} to {lon_max:.2f}'
                    })
                
                # Report results
                output += "QUALITY CHECKS:\n"
                for check in checks:
                    status_icon = "✓" if check['status'] == 'PASS' else "⚠"
                    output += f"{status_icon} {check['check']}: {check['status']}\n"
                    output += f"    {check['details']}\n\n"
                
                passed = sum(1 for c in checks if c['status'] == 'PASS')
                total = len(checks)
                output += f"SUMMARY: {passed}/{total} checks passed\n"
                
                if passed == total:
                    output += "✅ Data quality validation PASSED\n"
                else:
                    output += "⚠️ Some quality checks raised warnings. Review details above.\n"
                
                return output
            finally:
                # Explicitly close dataset to free memory
                ds.close()
        except Exception as e:
            import traceback
            return f"Error validating data quality: {str(e)}\n{traceback.format_exc()}"
    
    def _detect_file_format(self, file_path: Path) -> str:
        """Detect file format by reading file header"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header.startswith(b'GRIB'):
                    return "GRIB"
                elif header.startswith(b'\x89HDF') or header.startswith(b'CDF'):
                    return "NetCDF"
                else:
                    if file_path.suffix.lower() == '.nc':
                        return "NetCDF"
                    return "Unknown"
        except:
            if file_path.suffix.lower() == '.nc':
                return "NetCDF"
            return "Unknown"


class CompareERA5CMIP6Tool(BaseTool):
    """Compare ERA5 and CMIP6 datasets side-by-side with alignment and statistical analysis"""
    name: str = "compare_era5_cmip6"
    description: str = (
        "Compare ERA5 reanalysis data with CMIP6 model output data. "
        "Automatically aligns data temporally and spatially, calculates differences, "
        "bias statistics, and correlation. Input JSON: {'era5_file': 'path', 'cmip6_file': 'path', "
        "'variable': 'temperature', 'output_dir': 'analysis_results'}. "
        "Returns comparison statistics and saves comparison plots."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4 cfgrib"
        
        try:
            import warnings
            warnings.filterwarnings('ignore')
            import json
            
            params = json.loads(tool_input) if tool_input else {}
            era5_file = params.get("era5_file", "")
            cmip6_file = params.get("cmip6_file", "")
            variable = params.get("variable", None)  # Optional: specific variable to compare
            output_dir = params.get("output_dir", "analysis_results")
            
            if not era5_file or not cmip6_file:
                return "Error: Both era5_file and cmip6_file are required"
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Load ERA5 GRIB file
            loader = LoadNetCDFDataTool()
            try:
                era5_ds, method_used = loader._load_grib_file(era5_file)
                logger.info(f"Loaded ERA5 file using: {method_used}")
            except Exception as e:
                return f"⚠️ Error loading ERA5 file: {str(e)}\n\n💡 SUGGESTION: Use 'execute_python_code' to try alternative loading methods or install missing dependencies."
            
            # Load CMIP6 NetCDF file with chunks to reduce memory usage
            try:
                cmip6_ds = xr.open_dataset(cmip6_file, engine='netcdf4', chunks={'time': 100})
            except Exception as e:
                return f"⚠️ Error loading CMIP6 file: {str(e)}\n\n💡 SUGGESTION: Use 'execute_python_code' to try alternative loading methods or check file format."
            
            try:
                output = f"[ERA5 vs CMIP6 COMPARISON]\n"
                output += "=" * 60 + "\n\n"
                output += f"ERA5 File: {Path(era5_file).name}\n"
                output += f"CMIP6 File: {Path(cmip6_file).name}\n\n"
                
                # Find common variables
                era5_vars = list(era5_ds.data_vars)
                cmip6_vars = list(cmip6_ds.data_vars)
                
                # Variable name mapping (common climate variable names)
                var_mapping = {
                    't2m': 'tas', '2m_temperature': 'tas', 'temperature': 'tas',
                    'tp': 'pr', 'total_precipitation': 'pr', 'precipitation': 'pr'
                }
                
                comparison_results = []
                
                # Compare variables
                for era5_var in era5_vars[:3]:  # Compare first 3 variables
                    # Find corresponding CMIP6 variable
                    cmip6_var = None
                    if variable:
                        # Use specified variable
                        if variable in cmip6_vars:
                            cmip6_var = variable
                    else:
                        # Auto-match variables
                        era5_var_lower = era5_var.lower()
                        if era5_var_lower in var_mapping:
                            target_var = var_mapping[era5_var_lower]
                            if target_var in cmip6_vars:
                                cmip6_var = target_var
                        elif era5_var in cmip6_vars:
                            cmip6_var = era5_var
                    
                    if not cmip6_var:
                        continue
                    
                    era5_data = era5_ds[era5_var]
                    cmip6_data = cmip6_ds[cmip6_var]
                    
                    # Align spatial grids if needed
                    try:
                        # Try to align coordinates
                        if 'lat' in era5_data.coords and 'lat' in cmip6_data.coords:
                            # Interpolate to common grid (use ERA5 grid as reference)
                            cmip6_aligned = cmip6_data.interp(
                                lat=era5_data.lat,
                                lon=era5_data.lon,
                                method='nearest'
                            )
                        else:
                            cmip6_aligned = cmip6_data
                        
                        # Align time if both have time dimension
                        if 'time' in era5_data.coords and 'time' in cmip6_aligned.coords:
                            # Find overlapping time period
                            import pandas as pd
                            era5_times = pd.to_datetime(era5_data.time.values)
                            cmip6_times = pd.to_datetime(cmip6_aligned.time.values)
                            common_start = max(era5_times.min(), cmip6_times.min())
                            common_end = min(era5_times.max(), cmip6_times.max())
                            
                            era5_subset = era5_data.sel(time=slice(common_start, common_end))
                            cmip6_subset = cmip6_aligned.sel(time=slice(common_start, common_end))
                        else:
                            era5_subset = era5_data
                            cmip6_subset = cmip6_aligned
                        
                        # Calculate statistics
                        diff = era5_subset - cmip6_subset
                        bias = float(diff.mean())
                        rmse = float(np.sqrt((diff**2).mean()))
                        correlation = float(xr.corr(era5_subset, cmip6_subset))
                        
                        comparison_results.append({
                            'era5_var': era5_var,
                            'cmip6_var': cmip6_var,
                            'bias': bias,
                            'rmse': rmse,
                            'correlation': correlation,
                            'era5_mean': float(era5_subset.mean()),
                            'cmip6_mean': float(cmip6_subset.mean())
                        })
                        
                        output += f"Variable Comparison: {era5_var} (ERA5) vs {cmip6_var} (CMIP6)\n"
                        output += f"  ERA5 Mean: {comparison_results[-1]['era5_mean']:.3f}\n"
                        output += f"  CMIP6 Mean: {comparison_results[-1]['cmip6_mean']:.3f}\n"
                        output += f"  Bias (ERA5 - CMIP6): {bias:.3f}\n"
                        output += f"  RMSE: {rmse:.3f}\n"
                        output += f"  Correlation: {correlation:.3f}\n\n"
                        
                    except Exception as e:
                        output += f"  Warning: Could not compare {era5_var}: {str(e)}\n\n"
                
                # Save comparison results
                if comparison_results:
                    import json
                    results_file = Path(output_dir) / "comparison_results.json"
                    with open(results_file, 'w') as f:
                        json.dump(comparison_results, f, indent=2)
                    output += f"✅ Comparison results saved to: {results_file}\n"
                
                output += "💡 Use 'execute_python_code' to create comparison visualizations.\n"
                
                return output
            finally:
                # Explicitly close datasets to free memory
                era5_ds.close()
                cmip6_ds.close()
        except Exception as e:
            import traceback
            return f"Error comparing datasets: {str(e)}\n{traceback.format_exc()}"


class TimeSeriesAnalysisTool(BaseTool):
    """Perform time series analysis on climate data (trends, seasonality, anomalies)"""
    name: str = "time_series_analysis"
    description: str = (
        "Perform comprehensive time series analysis on climate data files. "
        "Detects trends, seasonal patterns, anomalies, and calculates time series statistics. "
        "Input JSON: {'file_path': 'path', 'variable': 'temperature', 'output_dir': 'analysis_results'}. "
        "Returns analysis results and saves time series plots."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4"
        
        try:
            import warnings
            warnings.filterwarnings('ignore')
            import json
            
            params = json.loads(tool_input) if tool_input else {}
            file_path = params.get("file_path", "")
            variable = params.get("variable", None)
            output_dir = params.get("output_dir", "analysis_results")
            
            if not file_path:
                return "Error: file_path is required"
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Load file
            file_format = self._detect_file_format(Path(file_path))
            loader = LoadNetCDFDataTool()
            if file_format == "GRIB":
                try:
                    ds, method_used = loader._load_grib_file(file_path)
                except Exception as e:
                    error_msg = str(e)
                    return (
                        f"⚠️ Error loading GRIB file: {error_msg}\n\n"
                        f"💡 SUGGESTION: Try using 'execute_python_code' to:\n"
                        f"  1. Install missing dependencies (pip install eccodes)\n"
                        f"  2. Try alternative loading methods\n"
                        f"  3. Check and convert file format if needed\n"
                    )
            else:
                # Use chunks for CMIP6 files to reduce memory usage
                ds = xr.open_dataset(file_path, engine='netcdf4', chunks={'time': 100})
            
            try:
                # Select variable
                if variable and variable in ds.data_vars:
                    data_var = ds[variable]
                elif ds.data_vars:
                    data_var = ds[list(ds.data_vars)[0]]
                else:
                    return "Error: No data variables found"
                
                output = f"[TIME SERIES ANALYSIS]: {Path(file_path).name}\n"
                output += "=" * 60 + "\n\n"
                output += f"Variable: {data_var.name}\n\n"
                
                # Check if time dimension exists
                if 'time' not in data_var.coords:
                    return "Error: No time dimension found in data"
                
                # Calculate temporal mean (spatial average)
                if 'lat' in data_var.coords and 'lon' in data_var.coords:
                    time_series = data_var.mean(dim=['lat', 'lon'])
                else:
                    time_series = data_var
                
                # Convert to pandas for easier analysis
                import pandas as pd
                ts_df = pd.DataFrame({
                    'time': pd.to_datetime(time_series.time.values),
                    'value': time_series.values.flatten()
                })
                ts_df.set_index('time', inplace=True)
                
                # Calculate statistics
                mean_val = float(ts_df['value'].mean())
                std_val = float(ts_df['value'].std())
                min_val = float(ts_df['value'].min())
                max_val = float(ts_df['value'].max())
                
                output += "BASIC STATISTICS:\n"
                output += f"  Mean: {mean_val:.3f}\n"
                output += f"  Std: {std_val:.3f}\n"
                output += f"  Min: {min_val:.3f}\n"
                output += f"  Max: {max_val:.3f}\n\n"
                
                # Trend analysis (linear regression)
                try:
                    from scipy import stats
                    x = np.arange(len(ts_df))
                    slope, intercept, r_value, p_value, std_err = stats.linregress(x, ts_df['value'])
                    trend_per_year = slope * len(ts_df) / (ts_df.index[-1] - ts_df.index[0]).days * 365.25
                    
                    output += "TREND ANALYSIS:\n"
                    output += f"  Slope: {slope:.6f} per time step\n"
                    output += f"  Trend: {trend_per_year:.6f} per year\n"
                    output += f"  R-squared: {r_value**2:.4f}\n"
                    output += f"  P-value: {p_value:.4f}\n"
                    if p_value < 0.05:
                        output += f"  Significance: Statistically significant trend\n"
                    else:
                        output += f"  Significance: No significant trend\n"
                    output += "\n"
                except ImportError:
                    output += "  Trend analysis requires scipy (not available)\n\n"
                
                # Seasonal analysis
                try:
                    ts_df['month'] = ts_df.index.month
                    seasonal_means = ts_df.groupby('month')['value'].mean()
                    
                    output += "SEASONAL PATTERNS:\n"
                    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    for month_idx, mean_val in enumerate(seasonal_means, 1):
                        output += f"  {months[month_idx-1]}: {mean_val:.3f}\n"
                    output += "\n"
                except Exception as e:
                    output += f"  Seasonal analysis error: {str(e)}\n\n"
                
                # Anomaly calculation
                climatology = ts_df.groupby(ts_df.index.month)['value'].mean()
                anomalies = []
                for idx, row in ts_df.iterrows():
                    anomaly = row['value'] - climatology[idx.month]
                    anomalies.append(anomaly)
                ts_df['anomaly'] = anomalies
                
                output += "ANOMALY STATISTICS:\n"
                output += f"  Mean Anomaly: {ts_df['anomaly'].mean():.3f}\n"
                output += f"  Std Anomaly: {ts_df['anomaly'].std():.3f}\n"
                output += f"  Max Positive Anomaly: {ts_df['anomaly'].max():.3f}\n"
                output += f"  Max Negative Anomaly: {ts_df['anomaly'].min():.3f}\n\n"
                
                # Save results
                results_file = Path(output_dir) / f"timeseries_analysis_{Path(file_path).stem}.json"
                results = {
                    'file': file_path,
                    'variable': data_var.name,
                    'statistics': {
                        'mean': mean_val,
                        'std': std_val,
                        'min': min_val,
                        'max': max_val
                    },
                    'trend': {
                        'slope': float(slope) if 'slope' in locals() else None,
                        'trend_per_year': float(trend_per_year) if 'trend_per_year' in locals() else None,
                        'r_squared': float(r_value**2) if 'r_value' in locals() else None,
                        'p_value': float(p_value) if 'p_value' in locals() else None
                    },
                    'seasonal_means': {str(k): float(v) for k, v in seasonal_means.items()} if 'seasonal_means' in locals() else {}
                }
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                output += f"✅ Analysis results saved to: {results_file}\n"
                output += "💡 Use 'execute_python_code' to create time series plots.\n"
                
                return output
            finally:
                # Explicitly close dataset to free memory
                ds.close()
        except Exception as e:
            import traceback
            return f"Error in time series analysis: {str(e)}\n{traceback.format_exc()}"
    
    def _detect_file_format(self, file_path: Path) -> str:
        """Detect file format"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header.startswith(b'GRIB'):
                    return "GRIB"
                elif header.startswith(b'\x89HDF') or header.startswith(b'CDF'):
                    return "NetCDF"
                else:
                    return "NetCDF" if file_path.suffix.lower() == '.nc' else "Unknown"
        except:
            return "NetCDF" if file_path.suffix.lower() == '.nc' else "Unknown"


class SpatialAnalysisTool(BaseTool):
    """Perform spatial analysis on climate data (interpolation, aggregation, regional statistics)"""
    name: str = "spatial_analysis"
    description: str = (
        "Perform spatial analysis on climate data files. "
        "Includes spatial interpolation, regional aggregation, zonal statistics, "
        "and spatial correlation analysis. Input JSON: {'file_path': 'path', "
        "'variable': 'temperature', 'region': [lat_min, lat_max, lon_min, lon_max], "
        "'output_dir': 'analysis_results'}. Returns spatial statistics and saves maps."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4"
        
        try:
            import warnings
            warnings.filterwarnings('ignore')
            import json
            
            params = json.loads(tool_input) if tool_input else {}
            file_path = params.get("file_path", "")
            variable = params.get("variable", None)
            region = params.get("region", None)  # [lat_min, lat_max, lon_min, lon_max]
            output_dir = params.get("output_dir", "analysis_results")
            
            if not file_path:
                return "Error: file_path is required"
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            # Load file
            file_format = self._detect_file_format(Path(file_path))
            loader = LoadNetCDFDataTool()
            if file_format == "GRIB":
                try:
                    ds, method_used = loader._load_grib_file(file_path)
                except Exception as e:
                    error_msg = str(e)
                    return (
                        f"⚠️ Error loading GRIB file: {error_msg}\n\n"
                        f"💡 SUGGESTION: Try using 'execute_python_code' to:\n"
                        f"  1. Install missing dependencies (pip install eccodes)\n"
                        f"  2. Try alternative loading methods\n"
                        f"  3. Check and convert file format if needed\n"
                    )
            else:
                # Use chunks for CMIP6 files to reduce memory usage
                ds = xr.open_dataset(file_path, engine='netcdf4', chunks={'time': 100})
            
            try:
                # Select variable
                if variable and variable in ds.data_vars:
                    data_var = ds[variable]
                elif ds.data_vars:
                    data_var = ds[list(ds.data_vars)[0]]
                else:
                    return "Error: No data variables found"
                
                output = f"[SPATIAL ANALYSIS]: {Path(file_path).name}\n"
                output += "=" * 60 + "\n\n"
                output += f"Variable: {data_var.name}\n\n"
                
                # Check spatial coordinates
                has_lat = 'lat' in data_var.coords
                has_lon = 'lon' in data_var.coords
                
                if not (has_lat and has_lon):
                    return "Error: No spatial coordinates (lat/lon) found"
                
                # Regional subset if specified
                if region and len(region) == 4:
                    lat_min, lat_max, lon_min, lon_max = region
                    data_subset = data_var.sel(
                        lat=slice(lat_min, lat_max),
                        lon=slice(lon_min, lon_max)
                    )
                    output += f"Regional Subset: Lat [{lat_min}, {lat_max}], Lon [{lon_min}, {lon_max}]\n\n"
                else:
                    data_subset = data_var
                
                # Calculate spatial statistics
                if 'time' in data_subset.coords:
                    # Temporal mean for spatial analysis
                    spatial_data = data_subset.mean(dim='time')
                else:
                    spatial_data = data_subset
                
                # Global statistics
                global_mean = float(spatial_data.mean())
                global_std = float(spatial_data.std())
                global_min = float(spatial_data.min())
                global_max = float(spatial_data.max())
                
                output += "GLOBAL SPATIAL STATISTICS:\n"
                output += f"  Mean: {global_mean:.3f}\n"
                output += f"  Std: {global_std:.3f}\n"
                output += f"  Min: {global_min:.3f}\n"
                output += f"  Max: {global_max:.3f}\n\n"
                
                # Zonal statistics (latitude bands)
                try:
                    lat_coords = spatial_data.lat.values
                    zonal_means = spatial_data.mean(dim='lon')
                    
                    output += "ZONAL STATISTICS (Latitude Bands):\n"
                    output += f"  Equator (0°): {float(zonal_means.sel(lat=0, method='nearest')):.3f}\n"
                    if lat_coords.min() < -30:
                        output += f"  Southern Mid-latitudes (-30°): {float(zonal_means.sel(lat=-30, method='nearest')):.3f}\n"
                    if lat_coords.max() > 30:
                        output += f"  Northern Mid-latitudes (30°): {float(zonal_means.sel(lat=30, method='nearest')):.3f}\n"
                    output += "\n"
                except Exception as e:
                    output += f"  Zonal statistics error: {str(e)}\n\n"
                
                # Regional aggregation examples
                if region:
                    regional_mean = float(spatial_data.mean())
                    regional_std = float(spatial_data.std())
                    
                    output += "REGIONAL STATISTICS:\n"
                    output += f"  Mean: {regional_mean:.3f}\n"
                    output += f"  Std: {regional_std:.3f}\n\n"
                
                # Save results
                results_file = Path(output_dir) / f"spatial_analysis_{Path(file_path).stem}.json"
                results = {
                    'file': file_path,
                    'variable': data_var.name,
                    'spatial_statistics': {
                        'global_mean': global_mean,
                        'global_std': global_std,
                        'global_min': global_min,
                        'global_max': global_max
                    },
                    'region': region if region else 'global'
                }
                with open(results_file, 'w') as f:
                    json.dump(results, f, indent=2)
                
                output += f"✅ Spatial analysis results saved to: {results_file}\n"
                output += "💡 Use 'execute_python_code' to create spatial maps.\n"
                
                return output
            finally:
                # Explicitly close dataset to free memory
                ds.close()
        except Exception as e:
            import traceback
            return f"Error in spatial analysis: {str(e)}\n{traceback.format_exc()}"
    
    def _detect_file_format(self, file_path: Path) -> str:
        """Detect file format"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header.startswith(b'GRIB'):
                    return "GRIB"
                elif header.startswith(b'\x89HDF') or header.startswith(b'CDF'):
                    return "NetCDF"
                else:
                    return "NetCDF" if file_path.suffix.lower() == '.nc' else "Unknown"
        except:
            return "NetCDF" if file_path.suffix.lower() == '.nc' else "Unknown"


class BatchProcessFilesTool(BaseTool):
    """Process multiple climate data files in batch"""
    name: str = "batch_process_files"
    description: str = (
        "Process multiple climate data files in batch. "
        "Applies the same analysis operations to multiple files. "
        "Input JSON: {'file_paths': ['path1', 'path2', ...], 'operation': 'process', "
        "'output_dir': 'analysis_results'}. "
        "Operations: 'process' (basic processing), 'validate' (quality check), "
        "'timeseries' (time series analysis), 'spatial' (spatial analysis)."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import json
            params = json.loads(tool_input) if tool_input else {}
            file_paths = params.get("file_paths", [])
            operation = params.get("operation", "process")
            output_dir = params.get("output_dir", "analysis_results")
            
            if not file_paths:
                return "Error: file_paths list is required"
            
            if not isinstance(file_paths, list):
                return "Error: file_paths must be a list"
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            output = f"[BATCH PROCESSING]\n"
            output += "=" * 60 + "\n\n"
            output += f"Files to process: {len(file_paths)}\n"
            output += f"Operation: {operation}\n"
            output += f"Output directory: {output_dir}\n\n"
            
            results = []
            successful = 0
            failed = 0
            
            for i, file_path in enumerate(file_paths, 1):
                output += f"Processing {i}/{len(file_paths)}: {Path(file_path).name}\n"
                
                try:
                    if operation == "process":
                        # Basic processing
                        if "era5" in file_path.lower():
                            result = ProcessERA5DataTool()._run(file_path)
                        elif "cmip6" in file_path.lower():
                            result = ProcessCMIP6DataTool()._run(file_path)
                        else:
                            result = LoadNetCDFDataTool()._run(file_path)
                    elif operation == "validate":
                        result = ValidateDataQualityTool()._run(file_path)
                    elif operation == "timeseries":
                        result = TimeSeriesAnalysisTool()._run(json.dumps({"file_path": file_path, "output_dir": output_dir}))
                    elif operation == "spatial":
                        result = SpatialAnalysisTool()._run(json.dumps({"file_path": file_path, "output_dir": output_dir}))
                    else:
                        result = f"Unknown operation: {operation}"
                    
                    results.append({"file": file_path, "status": "success", "result": result[:200]})
                    successful += 1
                    output += f"  ✓ Success\n"
                except Exception as e:
                    results.append({"file": file_path, "status": "failed", "error": str(e)})
                    failed += 1
                    output += f"  ✗ Failed: {str(e)[:50]}\n"
            
            output += f"\nSUMMARY:\n"
            output += f"  Successful: {successful}/{len(file_paths)}\n"
            output += f"  Failed: {failed}/{len(file_paths)}\n"
            
            # Save batch results
            results_file = Path(output_dir) / "batch_processing_results.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            output += f"\n✅ Batch processing results saved to: {results_file}\n"
            
            return output
        except Exception as e:
            import traceback
            return f"⚠️ Error in batch processing: {str(e)}\n{traceback.format_exc()}\n\n💡 SUGGESTION: Use 'execute_python_code' to process files individually or fix the issue."


class ExportDataTool(BaseTool):
    """Export processed climate data in standardized formats"""
    name: str = "export_data"
    description: str = (
        "Export processed climate data to standardized formats. "
        "Supports NetCDF (CF conventions), CSV, JSON, and GeoTIFF formats. "
        "Input JSON: {'file_path': 'input.nc', 'output_file': 'output.csv', "
        "'format': 'csv', 'variable': 'temperature', 'region': [lat_min, lat_max, lon_min, lon_max]}. "
        "Formats: 'netcdf', 'csv', 'json', 'geotiff'."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if not XARRAY_AVAILABLE:
            return "Error: xarray not available. Install with: pip install xarray netcdf4"
        
        try:
            import warnings
            warnings.filterwarnings('ignore')
            import json
            
            params = json.loads(tool_input) if tool_input else {}
            file_path = params.get("file_path", "")
            output_file = params.get("output_file", "")
            format_type = params.get("format", "csv").lower()
            variable = params.get("variable", None)
            region = params.get("region", None)
            
            if not file_path:
                return "Error: file_path is required"
            
            if not output_file:
                # Generate default output filename
                base_name = Path(file_path).stem
                ext_map = {'netcdf': '.nc', 'csv': '.csv', 'json': '.json', 'geotiff': '.tif'}
                output_file = f"{base_name}_exported{ext_map.get(format_type, '.csv')}"
            
            # Load file
            file_format = self._detect_file_format(Path(file_path))
            loader = LoadNetCDFDataTool()
            if file_format == "GRIB":
                try:
                    ds, method_used = loader._load_grib_file(file_path)
                except Exception as e:
                    error_msg = str(e)
                    return (
                        f"⚠️ Error loading GRIB file: {error_msg}\n\n"
                        f"💡 SUGGESTION: Try using 'execute_python_code' to:\n"
                        f"  1. Install missing dependencies (pip install eccodes)\n"
                        f"  2. Try alternative loading methods\n"
                        f"  3. Check and convert file format if needed\n"
                    )
            else:
                # Use chunks for CMIP6 files to reduce memory usage
                ds = xr.open_dataset(file_path, engine='netcdf4', chunks={'time': 100})
            
            try:
                # Select variable
                if variable and variable in ds.data_vars:
                    data_var = ds[variable]
                elif ds.data_vars:
                    data_var = ds[list(ds.data_vars)[0]]
                else:
                    return "Error: No data variables found"
                
                # Regional subset if specified
                if region and len(region) == 4:
                    lat_min, lat_max, lon_min, lon_max = region
                    data_var = data_var.sel(
                        lat=slice(lat_min, lat_max),
                        lon=slice(lon_min, lon_max)
                    )
                
                output = f"[DATA EXPORT]\n"
                output += "=" * 60 + "\n\n"
                output += f"Input: {Path(file_path).name}\n"
                output += f"Output: {output_file}\n"
                output += f"Format: {format_type}\n\n"
                
                # Export based on format
                if format_type == "netcdf":
                    # Export as NetCDF with CF conventions
                    data_var.to_netcdf(output_file)
                    output += f"✅ Exported to NetCDF: {output_file}\n"
                    
                elif format_type == "csv":
                    # Export as CSV (flatten spatial dimensions)
                    if 'time' in data_var.coords:
                        # Time series export
                        if 'lat' in data_var.coords and 'lon' in data_var.coords:
                            # Spatial average time series
                            ts_data = data_var.mean(dim=['lat', 'lon'])
                        else:
                            ts_data = data_var
                        
                        df = pd.DataFrame({
                            'time': pd.to_datetime(ts_data.time.values if not (hasattr(ts_data.time, 'chunks') and ts_data.time.chunks) else ts_data.time.compute().values),
                            'value': ts_data.values.flatten() if not (hasattr(ts_data, 'chunks') and ts_data.chunks) else ts_data.compute().values.flatten()
                        })
                        df.to_csv(output_file, index=False)
                    else:
                        # Spatial data export (flatten to lat/lon/value)
                        if 'lat' in data_var.coords and 'lon' in data_var.coords:
                            df = data_var.to_dataframe().reset_index()
                            df.to_csv(output_file, index=False)
                        else:
                            return "Error: Cannot export to CSV - no time or spatial dimensions"
                    
                    output += f"✅ Exported to CSV: {output_file}\n"
                    
                elif format_type == "json":
                    # Export as JSON
                    if 'time' in data_var.coords:
                        # Time series
                        if 'lat' in data_var.coords and 'lon' in data_var.coords:
                            ts_data = data_var.mean(dim=['lat', 'lon'])
                        else:
                            ts_data = data_var
                        
                        time_values = ts_data.time.values if not (hasattr(ts_data.time, 'chunks') and ts_data.time.chunks) else ts_data.time.compute().values
                        data_values = ts_data.values.flatten() if not (hasattr(ts_data, 'chunks') and ts_data.chunks) else ts_data.compute().values.flatten()
                        
                        json_data = {
                            'time': [str(t) for t in pd.to_datetime(time_values)],
                            'values': data_values.tolist(),
                            'variable': data_var.name,
                            'units': data_var.attrs.get('units', 'N/A')
                        }
                    else:
                        # Spatial data
                        json_data = {
                            'lat': data_var.lat.values.tolist() if 'lat' in data_var.coords else [],
                            'lon': data_var.lon.values.tolist() if 'lon' in data_var.coords else [],
                            'values': data_var.values.flatten().tolist() if not (hasattr(data_var, 'chunks') and data_var.chunks) else data_var.compute().values.flatten().tolist(),
                            'variable': data_var.name,
                            'units': data_var.attrs.get('units', 'N/A')
                        }
                    
                    with open(output_file, 'w') as f:
                        json.dump(json_data, f, indent=2)
                    
                    output += f"✅ Exported to JSON: {output_file}\n"
                    
                elif format_type == "geotiff":
                    # Export as GeoTIFF (requires rasterio)
                    try:
                        import rasterio
                        from rasterio.transform import from_bounds
                        
                        if 'lat' not in data_var.coords or 'lon' not in data_var.coords:
                            return "Error: GeoTIFF export requires lat/lon coordinates"
                        
                        # Get spatial bounds
                        lat_min = float(data_var.lat.min())
                        lat_max = float(data_var.lat.max())
                        lon_min = float(data_var.lon.min())
                        lon_max = float(data_var.lon.max())
                        
                        # Select first time step if time dimension exists
                        if 'time' in data_var.coords:
                            spatial_data = data_var.isel(time=0)
                        else:
                            spatial_data = data_var
                        
                        # Compute if chunked
                        if hasattr(spatial_data, 'chunks') and spatial_data.chunks:
                            spatial_data = spatial_data.compute()
                        
                        # Create transform
                        transform = from_bounds(lon_min, lat_min, lon_max, lat_max,
                                              spatial_data.sizes['lon'], spatial_data.sizes['lat'])
                        
                        # Write GeoTIFF
                        with rasterio.open(
                            output_file,
                            'w',
                            driver='GTiff',
                            height=spatial_data.sizes['lat'],
                            width=spatial_data.sizes['lon'],
                            count=1,
                            dtype=str(spatial_data.dtype),
                            crs='EPSG:4326',
                            transform=transform
                        ) as dst:
                            dst.write(spatial_data.values, 1)
                        
                        output += f"✅ Exported to GeoTIFF: {output_file}\n"
                    except ImportError:
                        return "Error: rasterio not installed. Install with: pip install rasterio"
                else:
                    return f"Error: Unsupported format: {format_type}. Supported: netcdf, csv, json, geotiff"
                
                output += f"\nFile size: {Path(output_file).stat().st_size / (1024*1024):.2f} MB\n"
                
                return output
            finally:
                # Explicitly close dataset to free memory
                ds.close()
        except Exception as e:
            import traceback
            return f"Error exporting data: {str(e)}\n{traceback.format_exc()}"
    
    def _detect_file_format(self, file_path: Path) -> str:
        """Detect file format"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header.startswith(b'GRIB'):
                    return "GRIB"
                elif header.startswith(b'\x89HDF') or header.startswith(b'CDF'):
                    return "NetCDF"
                else:
                    return "NetCDF" if file_path.suffix.lower() == '.nc' else "Unknown"
        except:
            return "NetCDF" if file_path.suffix.lower() == '.nc' else "Unknown"


class GenerateAnalysisReportTool(BaseTool):
    """Generate comprehensive analysis reports with statistics, plots, and summaries"""
    name: str = "generate_analysis_report"
    description: str = (
        "Generate comprehensive analysis reports from climate data analysis results. "
        "Creates Markdown reports with statistics, visualizations, and summaries. "
        "Input JSON: {'analysis_results_dir': 'analysis_results', 'output_file': 'report.md', "
        "'format': 'markdown'}. Formats: 'markdown', 'html', 'pdf'."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import json
            from datetime import datetime
            
            params = json.loads(tool_input) if tool_input else {}
            analysis_dir = params.get("analysis_results_dir", "analysis_results")
            output_file = params.get("output_file", f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
            format_type = params.get("format", "markdown").lower()
            
            analysis_path = Path(analysis_dir)
            if not analysis_path.exists():
                return f"Error: Analysis results directory not found: {analysis_dir}"
            
            output = f"[GENERATING ANALYSIS REPORT]\n"
            output += "=" * 60 + "\n\n"
            output += f"Analysis directory: {analysis_dir}\n"
            output += f"Output file: {output_file}\n"
            output += f"Format: {format_type}\n\n"
            
            # Collect analysis results
            json_files = list(analysis_path.glob("*.json"))
            png_files = list(analysis_path.glob("*.png"))
            
            # Generate report content
            report_content = f"""# Climate Data Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analysis Directory:** {analysis_dir}

## Summary

This report summarizes the analysis of climate simulation data (ERA5 and CMIP6).

### Analysis Files Found
- JSON Results: {len(json_files)}
- Visualization Plots: {len(png_files)}

"""
            
            # Add JSON results summary
            if json_files:
                report_content += "## Analysis Results\n\n"
                for json_file in json_files[:10]:  # Limit to first 10
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            report_content += f"### {json_file.name}\n\n"
                            report_content += f"```json\n{json.dumps(data, indent=2)[:500]}...\n```\n\n"
                    except:
                        report_content += f"### {json_file.name}\n\n(Error reading file)\n\n"
            
            # Add visualization references
            if png_files:
                report_content += "## Visualizations\n\n"
                for png_file in png_files:
                    report_content += f"![{png_file.stem}]({png_file.relative_to(Path(output_file).parent)})\n\n"
            
            # Add statistics summary
            report_content += "## Statistics Summary\n\n"
            report_content += f"- Total analysis files: {len(json_files)}\n"
            report_content += f"- Total visualizations: {len(png_files)}\n"
            report_content += f"- Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            report_content += "## Notes\n\n"
            report_content += "This report was automatically generated by the Simulation Data Acquisition Agent.\n"
            report_content += "For detailed analysis, refer to the individual JSON result files.\n"
            
            # Write report
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            output += f"✅ Report generated: {output_file}\n"
            output += f"  - JSON results: {len(json_files)}\n"
            output += f"  - Visualizations: {len(png_files)}\n"
            
            if format_type == "html":
                # Convert markdown to HTML (basic conversion)
                html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Climate Data Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
{report_content.replace('```json', '<pre>').replace('```', '</pre>').replace('#', '<h1>').replace('##', '<h2>')}
</body>
</html>"""
                html_file = output_file.replace('.md', '.html')
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                output += f"✅ HTML report also generated: {html_file}\n"
            
            return output
        except Exception as e:
            import traceback
            return f"Error generating report: {str(e)}\n{traceback.format_exc()}"


class ListDownloadedFilesTool(BaseTool):
    """List all downloaded NetCDF files in era5_data and cmip6_data directories"""
    name: str = "list_downloaded_files"
    description: str = (
        "List all downloaded NetCDF files in the era5_data and cmip6_data directories. "
        "Shows file names, sizes, and modification dates. Useful for finding files to analyze."
    )

    def _run(self, family: str = "all", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            output = f"[DOWNLOADED FILES LIST]\n"
            output += "=" * 60 + "\n\n"
            
            era5_dir = Path("era5_data")
            cmip6_dir = Path("cmip6_data")
            
            files_found = []
            
            if family.lower() in ["all", "era5"]:
                if era5_dir.exists():
                    era5_files = list(era5_dir.glob("*.nc"))
                    for f in era5_files:
                        size_mb = f.stat().st_size / (1024 * 1024)
                        files_found.append({
                            "path": str(f),
                            "name": f.name,
                            "size_mb": size_mb,
                            "family": "ERA5",
                            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                        })
            
            if family.lower() in ["all", "cmip6"]:
                if cmip6_dir.exists():
                    cmip6_files = list(cmip6_dir.glob("*.nc"))
                    for f in cmip6_files:
                        size_mb = f.stat().st_size / (1024 * 1024)
                        files_found.append({
                            "path": str(f),
                            "name": f.name,
                            "size_mb": size_mb,
                            "family": "CMIP6",
                            "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                        })
            
            if not files_found:
                output += f"No downloaded files found in era5_data/ or cmip6_data/ directories.\n"
                output += f"Use 'download_era5_data' or 'download_cmip6_data' to download files first.\n"
                return output
            
            # Group by family
            era5_files = [f for f in files_found if f["family"] == "ERA5"]
            cmip6_files = [f for f in files_found if f["family"] == "CMIP6"]
            
            if era5_files:
                output += f"ERA5 FILES ({len(era5_files)}):\n"
                total_era5 = sum(f["size_mb"] for f in era5_files)
                for f in era5_files:
                    output += f"  • {f['name']} ({f['size_mb']:.2f} MB)\n"
                output += f"  Total: {total_era5:.2f} MB\n\n"
            
            if cmip6_files:
                output += f"CMIP6 FILES ({len(cmip6_files)}):\n"
                total_cmip6 = sum(f["size_mb"] for f in cmip6_files)
                for f in cmip6_files:
                    output += f"  • {f['name']} ({f['size_mb']:.2f} MB)\n"
                output += f"  Total: {total_cmip6:.2f} MB\n\n"
            
            output += f"TOTAL: {len(files_found)} files, {sum(f['size_mb'] for f in files_found):.2f} MB\n\n"
            output += f"Use 'load_netcdf_data' with file path to analyze any file.\n"
            output += f"Example: load_netcdf_data era5_data/{era5_files[0]['name'] if era5_files else 'file.nc'}\n"
            
            return output
        except Exception as e:
            return f"⚠️ Error listing downloaded files: {str(e)}\n\n💡 SUGGESTION: Use 'execute_python_code' to manually list files or check directory permissions."


class AskDataProcessingFollowUpTool(BaseTool):
    """Ask follow-up questions about data processing and analysis"""
    name: str = "ask_data_processing_followup"
    description: str = (
        "Ask the user follow-up questions about how they want to process, analyze, "
        "visualize, or use the downloaded simulation data. Use this whenever you need clarification."
    )

    def _run(self, question_context: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        output = f"🤔 DATA PROCESSING CLARIFICATION\n"
        output += "=" * 50 + "\n\n"
        output += f"Context: {question_context}\n\n"
        output += "To help you process the simulation data effectively, I need some information:\n\n"
        output += "1. What type of analysis do you need? (time series, spatial maps, statistics, etc.)\n"
        output += "2. Do you need to compare ERA5 and CMIP6 data?\n"
        output += "3. What geographic region or time period should I focus on?\n"
        output += "4. Do you need specific variables extracted or aggregated?\n"
        output += "5. What output format do you prefer? (plots, CSV, NetCDF, etc.)\n\n"
        output += "🔴 WAITING FOR USER INPUT 🔴\n"
        output += "Please provide your preferences:\n"
        
        print(output)
        user_response = input("\n>>> Your response: ")
        
        return f"User provided: {user_response}\n\nNow I can proceed with processing the data accordingly."


# --- Create Agent ---
def create_simulation_data_acquisition_agent() -> AgentExecutor:
    """Create the Simulation Data Acquisition Agent"""
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain is not installed")
    
    tools = [
        AskDataProcessingFollowUpTool(),
        AnalyzeDatasetBeforeDownloadTool(),  # Analyze before downloading
        ListStoredSimulationDatasetsTool(),
        QueryStoredSimulationDatasetTool(),
        DownloadERA5DataTool(),
        DownloadCMIP6DataTool(),
        ListDownloadedFilesTool(),  # List downloaded files
        LoadNetCDFDataTool(),  # Enhanced: Supports both GRIB and NetCDF
        ProcessERA5DataTool(),  # Specialized ERA5 processing
        ProcessCMIP6DataTool(),  # Specialized CMIP6 processing
        ValidateDataQualityTool(),  # Data quality validation
        CompareERA5CMIP6Tool(),  # NEW: Compare ERA5 and CMIP6 datasets
        TimeSeriesAnalysisTool(),  # NEW: Time series analysis (trends, seasonality)
        SpatialAnalysisTool(),  # NEW: Spatial analysis (interpolation, aggregation)
        BatchProcessFilesTool(),  # NEW: Batch processing multiple files
        ExportDataTool(),  # NEW: Export data in standardized formats
        GenerateAnalysisReportTool(),  # NEW: Generate comprehensive reports
        ExecutePythonCodeTool(),  # Enhanced: Suppressed warnings, supports cfgrib
    ]
    
    template = """You are a Simulation Data Acquisition Assistant specialized in downloading and processing ERA5 and CMIP6 climate simulation datasets stored by the simulation_kg_agent.

                DATABASE-FIRST STRATEGY:
                🥇 PRIMARY: Stored Simulation Datasets Database - Work with datasets already discovered by simulation_kg_agent
                🥈 SECONDARY: Direct API Downloads - Download actual data files using appropriate methods

                DATA SOURCE METHODS:
                🌍 ERA5: Use CDS API (cdsapi library) - asynchronous download, requires .cdsapirc configuration
                🌐 CMIP6: Use ESGF HTTP - direct file download from ESGF nodes, may require authentication

                CORE MISSION: Download actual data files for stored simulation datasets and enable data analysis!

                CAPABILITIES:
                - List stored simulation datasets from SQLite database
                - Analyze datasets BEFORE downloading (estimate size, variables, requirements)
                - Query stored dataset metadata and relationships
                - Download ERA5 data using cdsapi (saves to era5_data/ directory)
                - Download CMIP6 data files via ESGF HTTP (saves to cmip6_data/ directory)
                - List all downloaded files in era5_data/ and cmip6_data/ directories
                - Load and preview data files (automatically detects GRIB for ERA5, NetCDF for CMIP6)
                - Process ERA5 GRIB files with specialized ERA5 handling (use 'process_era5_data')
                - Process CMIP6 NetCDF files with specialized CMIP6 handling (use 'process_cmip6_data')
                - Validate data quality (missing values, ranges, consistency checks)
                - Compare ERA5 and CMIP6 datasets side-by-side (temporal/spatial alignment, bias, correlation)
                - Time series analysis (trends, seasonality, anomalies, statistical significance)
                - Spatial analysis (interpolation, regional aggregation, zonal statistics)
                - Batch process multiple files (apply same operations to multiple files)
                - Export data in standardized formats (NetCDF CF conventions, CSV, JSON, GeoTIFF)
                - Generate comprehensive analysis reports (Markdown, HTML with statistics and visualizations)
                - Execute Python code for custom analysis and visualization (xarray, matplotlib, pandas, seaborn, cfgrib)

                DATA PROCESSING PRIORITY:
                🥇 USE PRESET TOOLS FIRST: Always prefer specialized tools over custom Python code
                - For ERA5 files: Use 'process_era5_data' (handles GRIB format automatically)
                - For CMIP6 files: Use 'process_cmip6_data' (handles NetCDF format automatically)
                - For quality checks: Use 'validate_data_quality'
                - For file loading: Use 'load_netcdf_data' (auto-detects format)
                - For comparisons: Use 'compare_era5_cmip6' (ERA5 vs CMIP6 comparison)
                - For time series: Use 'time_series_analysis' (trends, seasonality, anomalies)
                - For spatial analysis: Use 'spatial_analysis' (interpolation, aggregation)
                - For batch processing: Use 'batch_process_files' (process multiple files)
                - For data export: Use 'export_data' (standardized formats)
                - For reports: Use 'generate_analysis_report' (comprehensive reports)
                🥈 FALLBACK TO PYTHON: Use 'execute_python_code' when:
                   - Preset tools fail or encounter errors (IMMEDIATELY try Python code to fix!)
                   - Preset tools don't cover your specific needs
                   - You need custom analysis or visualization
                   - You need to install packages or fix dependencies
                   - You need to download datasets that aren't in the database
                
                CRITICAL ERROR HANDLING RULE:
                ⚠️ If ANY tool returns an error (especially file loading, format issues, missing dependencies):
                1. DO NOT stop or give up - this is a signal to self-correct!
                2. IMMEDIATELY use 'execute_python_code' to diagnose and fix the issue
                3. Common fixes:
                   - Install packages: import subprocess; subprocess.run(['pip', 'install', 'eccodes'])
                   - Try alternative loading: Use netcdf4/scipy engines instead of cfgrib
                   - Check file format: Read file header to verify format
                   - Convert formats: Use Python to convert GRIB to NetCDF if needed
                   - Download missing data: Use Python to download datasets if not in database
                4. After fixing, retry the operation or continue with Python code
                5. Be proactive - errors are solvable, not endpoints!

                WORKFLOW:
                0. ASK FOR CLARIFICATION: Use 'ask_data_processing_followup' when you need details about analysis goals
                1. LIST DATASETS: Use 'list_stored_simulation_datasets' to see available datasets
                2. ANALYZE BEFORE DOWNLOAD: Use 'analyze_dataset_before_download' to check size and requirements
                3. QUERY DATASET: Use 'query_stored_simulation_dataset' to get full metadata
                4. DOWNLOAD DATA:
                - For ERA5: Use 'download_era5_data' with dataset_id (automatically saves to era5_data/)
                - For CMIP6: Use 'download_cmip6_data' with dataset_id (automatically saves to cmip6_data/)
                5. LIST DOWNLOADED FILES: Use 'list_downloaded_files' to see what's been downloaded
                6. LOAD DATA: Use 'load_netcdf_data' with file path (auto-detects GRIB/NetCDF format)
                7. PROCESS DATA:
                - For ERA5: Use 'process_era5_data' for specialized GRIB processing
                - For CMIP6: Use 'process_cmip6_data' for specialized NetCDF processing
                8. VALIDATE QUALITY: Use 'validate_data_quality' to check data quality
                9. ADVANCED ANALYSIS:
                - Compare datasets: Use 'compare_era5_cmip6' to compare ERA5 and CMIP6
                - Time series: Use 'time_series_analysis' for trends and seasonality
                - Spatial analysis: Use 'spatial_analysis' for regional statistics
                - Batch processing: Use 'batch_process_files' for multiple files
                10. EXPORT & REPORT:
                - Export data: Use 'export_data' to save in standardized formats
                - Generate report: Use 'generate_analysis_report' for comprehensive reports
                11. CUSTOM ANALYSIS: Use 'execute_python_code' only if preset tools don't meet needs

                DOWNLOAD DIRECTORY STRUCTURE:
                - ERA5 files are ALWAYS saved to: era5_data/ directory
                - CMIP6 files are ALWAYS saved to: cmip6_data/ directory
                - Use 'list_downloaded_files' to see all downloaded files

                ERA5 DOWNLOAD NOTES:
                - Requires .cdsapirc file with CDS API credentials
                - Parameters can override defaults (variable, year, month, area, etc.)
                - Download is asynchronous - may take time for large requests
                - Output is NetCDF format, saved to era5_data/ directory
                - Use 'analyze_dataset_before_download' to estimate file size before downloading
                
                ERA5 SPATIAL SUBSETTING (CRITICAL FOR REDUCING DOWNLOAD SIZE):
                - ERA5 supports 'area' parameter for spatial filtering: [north, west, south, east]
                - Format: [north_latitude, west_longitude, south_latitude, east_longitude]
                - Example: [40.8, -74.0, 40.7, -73.9] for New York City
                - This reduces download size from GBs (global) to MBs (city-scale regions)
                - ALWAYS extract location information from user input (city, country, region names)
                - When user mentions a location, IMMEDIATELY use 'execute_python_code' to query coordinates:
                  Example Python code:
                  ```python
                  try:
                      from geopy.geocoders import Nominatim
                      geolocator = Nominatim(user_agent="climate_data_agent")
                      location = geolocator.geocode("New York City")
                      if location:
                          # Add buffer (e.g., 0.1 degrees ≈ 11km)
                          north = location.latitude + 0.1
                          south = location.latitude - 0.1
                          east = location.longitude + 0.1
                          west = location.longitude - 0.1
                          area_coords = [north, west, south, east]
                          print(f"Area coordinates: {{area_coords}}")
                      else:
                          print("Location not found")
                  except ImportError:
                      # Fallback: use requests to query Nominatim API
                      import requests
                      url = "https://nominatim.openstreetmap.org/search"
                      params = {{"q": "New York City", "format": "json", "limit": 1}}
                      response = requests.get(url, params=params)
                      data = response.json()
                      if data:
                          lat = float(data[0]["lat"])
                          lon = float(data[0]["lon"])
                          area_coords = [lat + 0.1, lon - 0.1, lat - 0.1, lon + 0.1]
                          print(f"Area coordinates: {{area_coords}}")
                  ```
                - After obtaining coordinates, include 'area' parameter in download_era5_data parameters
                - If geocoding fails, inform user and proceed with global data (but warn about large size)
                - For countries/regions, use bounding box coordinates (can query via geopy or online APIs)
                - ALWAYS apply spatial filtering when location is mentioned - this is critical for efficient downloads!

                CMIP6 DOWNLOAD NOTES:
                - Downloads actual NetCDF files from ESGF nodes
                - May require ESGF OpenID authentication for some files
                - Can download multiple files per dataset (use limit parameter)
                - Files are typically large (hundreds of MB to GB)
                - All files saved to cmip6_data/ directory
                - Use 'analyze_dataset_before_download' to check available files and sizes

                You have access to these tools:
                {tools}

                EXAMPLE WORKFLOWS:

                WORKFLOW A - Download ERA5 Data:
                User: "Download ERA5 temperature data for NYC in 2020"
                1. Extract location "NYC" from user input
                2. Use execute_python_code to query coordinates for "NYC" (e.g., using geopy.geocoders.Nominatim)
                3. Obtain area coordinates: [40.8, -74.0, 40.7, -73.9]
                4. list_stored_simulation_datasets: {{"family": "ERA5", "limit": 10}}
                5. analyze_dataset_before_download: [selected_dataset_id]  # Check size and requirements
                6. query_stored_simulation_dataset: [selected_dataset_id]
                7. download_era5_data: {{"dataset_id": "...", "parameters": {{"variable": "2m_temperature", "year": "2020", "area": [40.8, -74.0, 40.7, -73.9]}}}}  # Auto-saves to era5_data/
                8. list_downloaded_files: "era5"  # Verify download
                9. load_netcdf_data: "era5_data/[filename].nc"

                WORKFLOW B - Download CMIP6 Data:
                User: "Download CMIP6 temperature data"
                1. list_stored_simulation_datasets: {{"family": "CMIP6", "limit": 10}}
                2. analyze_dataset_before_download: [selected_dataset_id]  # Check file sizes
                3. query_stored_simulation_dataset: [selected_dataset_id]
                4. download_cmip6_data: {{"dataset_id": "...", 100}}  # Auto-saves to cmip6_data/
                5. list_downloaded_files: "cmip6"  # Verify download
                6. load_netcdf_data: "cmip6_data/[filename].nc"

                WORKFLOW C - Data Analysis (After Download):
                User: "Analyze the downloaded data"
                1. list_downloaded_files: "all"  # See what files are available
                2. load_netcdf_data: "era5_data/[filename].nc"  # Preview data structure (auto-detects GRIB/NetCDF)
                3. process_era5_data: "era5_data/[filename].nc"  # Use specialized ERA5 processing tool
                4. process_cmip6_data: "cmip6_data/[filename].nc"  # Use specialized CMIP6 processing tool
                5. validate_data_quality: "era5_data/[filename].nc"  # Check data quality
                6. time_series_analysis: {{"file_path": "cmip6_data/[filename].nc", "variable": "tas", "output_dir": "analysis_results"}}  # Time series analysis
                7. spatial_analysis: {{"file_path": "era5_data/[filename].nc", "region": [40, 45, -75, -70], "output_dir": "analysis_results"}}  # Spatial analysis
                8. compare_era5_cmip6: {{"era5_file": "era5_data/[filename].nc", "cmip6_file": "cmip6_data/[filename].nc", "output_dir": "analysis_results"}}  # Compare datasets
                9. export_data: {{"file_path": "era5_data/[filename].nc", "output_file": "exported_data.csv", "format": "csv"}}  # Export data
                10. generate_analysis_report: {{"analysis_results_dir": "analysis_results", "output_file": "report.md", "format": "markdown"}}  # Generate report
                11. execute_python_code: [Python code ONLY if preset tools don't meet needs]

                WORKFLOW D - Batch Processing:
                User: "Process all downloaded files"
                1. list_downloaded_files: "all"  # Get all file paths
                2. batch_process_files: {{"file_paths": ["era5_data/file1.nc", "cmip6_data/file2.nc"], "operation": "validate", "output_dir": "analysis_results"}}  # Batch validate
                3. batch_process_files: {{"file_paths": ["..."], "operation": "timeseries", "output_dir": "analysis_results"}}  # Batch time series analysis
                4. generate_analysis_report: {{"analysis_results_dir": "analysis_results"}}  # Generate comprehensive report

                Use the following format:
                Question: the input question you must answer
                Thought: you should always think about what the user wants to accomplish
                Action: the action to take, should be one of [{tool_names}]
                Action Input: the input to the action
                Observation: the result of the action
                ... (this Thought/Action/Action Input/Observation can repeat N times)
                
                ⚠️ CRITICAL ERROR HANDLING:
                When you see error messages (⚠️ Error, Error loading, Error downloading, etc.):
                1. DO NOT stop - these are signals to self-correct!
                2. IMMEDIATELY use 'execute_python_code' to diagnose and fix:
                   - Install missing packages (pip install ...)
                   - Try alternative methods (different engines, formats)
                   - Debug issues (check formats, test imports)
                   - Download missing data if needed
                3. After fixing, retry the tool or continue with Python code
                4. Be proactive - errors are solvable problems, not endpoints!
                
                Thought: I now know the final answer
                Final Answer: the final answer to the original input question

                Begin!

                Question: {input}
                Thought:{agent_scratchpad}
                """

    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        template=template,
    )
    tools_str = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    tool_names_str = ", ".join([tool.name for tool in tools])
    prompt = prompt.partial(tools=tools_str, tool_names=tool_names_str)

    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=50,
    )
    return executor


def get_simulation_data_acquisition_agent() -> Optional[AgentExecutor]:
    """Get the simulation data acquisition agent"""
    try:
        return create_simulation_data_acquisition_agent()
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        return None


# Test
if __name__ == "__main__":
    print("Simulation Data Acquisition Agent")
    print("=" * 80)
    print("\n Using AWS Bedrock Claude Sonnet for reasoning")
    print(" Using SQLite database for stored datasets")
    print(" Using cdsapi for ERA5 downloads")
    print(" Using ESGF HTTP for CMIP6 downloads")
    print(" Using LangChain for agent framework")
    
    print("\n" + "="*80)
    print(" TESTING Simulation Data Acquisition Agent")
    print("="*80)
    
    try:
        agent = get_simulation_data_acquisition_agent()
        if agent:
            print("\n Agent initialized successfully!")
            
            # Test query
            test_query = "List all stored ERA5 datasets and download one dataset from both era5 and cmip6 datasets for the year 2020 for the variable 2m_temperature for the region of the NYC"

            print(f"\nTest Query: {test_query}")
            response = agent.invoke({"input": test_query})
            print(f"\nAgent Response:\n{response.get('output', 'No output')}")
        else:
            print("\n Agent initialization failed")
    except Exception as e:
        print(f"\n TEST FAILED: {str(e)}")
        traceback.print_exc()

