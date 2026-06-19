#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CESM LENS LangChain Agent

Based on the original agentic_climate_ai.py CESM LENS implementation.
This agent queries CESM LENS ensemble data and performs climate analysis.

CESM LENS Details:
- 40-member ensemble (1920-2100)
- Historical: 1920-2005, RCP8.5: 2006-2100
- AWS S3: s3://ncar-cesm-lens/{component}/{frequency}/cesmLE-{experiment}-{variable}.zarr
- Components: atm, ocn, ice, lnd
- Variables: TREFHT, PRECC, PSL, TS, etc.
"""

import json
import uuid
import os
import sys
import subprocess
import traceback
import boto3
from typing import Dict, List, Any, Optional, Tuple
import logging
import warnings
import numpy as np
from datetime import datetime
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
from pathlib import Path

# Climate data handling
import xarray as xr
import s3fs
import cftime
import netCDF4

# LangChain imports (EXACTLY like original)
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain.tools import DuckDuckGoSearchRun
from langchain.utilities import DuckDuckGoSearchAPIWrapper

# Additional imports for SaveCESMDataPathTool
import sqlite3
import json
from datetime import datetime



# AWS imports for Neptune connection (reuse from KG agent)
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress xarray warnings
warnings.filterwarnings("ignore", category=UserWarning, module="xarray")

def setup_dual_logging(log_file="climate_sim_log.txt"):
    """Setup logging to both console and file with print statement capture"""
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Update existing logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Add file handler if not already present
    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Capture print statements to both console and file
    class TeeOutput:
        def __init__(self, *files):
            self.files = files
        def write(self, text):
            for file in self.files:
                file.write(text)
                file.flush()
        def flush(self):
            for file in self.files:
                file.flush()
    
    # Redirect stdout to both console and file
    log_file_handle = open(log_file, 'a', encoding='utf-8')
    sys.stdout = TeeOutput(sys.__stdout__, log_file_handle)
    
    print(f"🔬 CESM LENS Analysis Started - {datetime.now().isoformat()}")
    print("=" * 70)
    
    return logger, log_file_handle

# --- Configuration Constants ---
BEDROCK_REGION = "us-east-2"
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
NEPTUNE_REGION = "us-east-2" 
GRAPH_ID = "g-kn6xkxo6r5"

# --- Bedrock LLM (same as KG agent) ---
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

# --- Neptune KG Connector (for CESM variable validation) ---
class KGConnector:
    """Simple connector to query CESM variables from Knowledge Graph"""
    def __init__(self):
        self.region = NEPTUNE_REGION
        self.graph_id = GRAPH_ID
        try:
            self.neptune = boto3.client("neptune-graph", region_name=self.region)
            print(f" Neptune client initialized for graph: {self.graph_id}")
        except Exception as e:
            print(f" Neptune client failed: {e}")
            self.neptune = None

    def execute_query(self, query: str) -> Dict:
        """Execute Cypher query"""
        if not self.neptune:
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

# --- Efficient Data Loading Functions ---

def load_cesm_data_via_catalog(
    variable_name: str,
    experiment: str = "RCP85",
    frequency: str = "monthly",
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    lat_range: Optional[Tuple[float, float]] = None,
    lon_range: Optional[Tuple[float, float]] = None
) -> Optional[xr.Dataset]:
    """
    Load CESM LENS data using the official Intake catalog.
    This is the recommended approach for accessing CESM LENS data.
    """
    try:
        import intake
        print(f" Loading data via Intake catalog for {variable_name}")
        
        # Open the official CESM LENS catalog
        catalog_url = "https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json"
        col = intake.open_esm_datastore(catalog_url)
        
        print(f" Searching catalog for: experiment={experiment}, frequency={frequency}, variable={variable_name}")
        
        # Search for the specific variable
        col_subset = col.search(
            experiment=experiment,
            frequency=frequency,
            variable=variable_name
        )
        
        if len(col_subset.df) == 0:
            print(f" ❌ Variable {variable_name} not found in catalog for experiment {experiment}")
            return None
        
        print(f" ✅ Found {len(col_subset.df)} datasets for {variable_name}")
        
        # Load the datasets
        dsets = col_subset.to_dataset_dict(
            zarr_kwargs={"consolidated": True},
            storage_options={"anon": True}
        )
        
        # Get the first dataset (there should usually be one per variable/experiment/frequency)
        dataset_key = list(dsets.keys())[0]
        ds = dsets[dataset_key]
        
        print(f" Loaded dataset: {dataset_key}")
        print(f" Available variables: {list(ds.data_vars)}")
        print(f" Dataset shape: {ds[variable_name].shape}")
        print(f" Coordinates: {list(ds.coords)}")
        if 'time' in ds.coords:
            print(f" Time range: {ds.time.min().values} to {ds.time.max().values}")
        if 'lat' in ds.coords:
            print(f" Latitude range: {ds.lat.min().values} to {ds.lat.max().values}")
        if 'lon' in ds.coords:
            print(f" Longitude range: {ds.lon.min().values} to {ds.lon.max().values}")
        
        # Apply temporal subsetting
        if start_year and end_year and 'time' in ds.coords:
            try:
                time_mask = (ds.time.dt.year >= start_year) & (ds.time.dt.year <= end_year)
                ds = ds.sel(time=time_mask)
                print(f" Applied temporal subset: {start_year}-{end_year}")
            except Exception as e:
                print(f" Warning: Could not apply temporal subsetting: {e}")
        
        # Apply spatial subsetting
        if lat_range and 'lat' in ds.coords:
            try:
                lat_mask = (ds.lat >= lat_range[0]) & (ds.lat <= lat_range[1])
                ds = ds.sel(lat=lat_mask)
                print(f" Applied latitude subset: {lat_range}")
            except Exception as e:
                print(f" Warning: Could not apply latitude subsetting: {e}")
                
        if lon_range and 'lon' in ds.coords:
            try:
                # Handle longitude convention - CESM often uses 0-360, we might get -180 to 180
                lon_min, lon_max = lon_range

                # Check if dataset uses 0-360 convention and we have negative longitudes
                if ds.lon.min() >= 0 and ds.lon.max() > 180 and (lon_min < 0 or lon_max < 0):
                    # Convert negative longitudes to 0-360 convention
                    if lon_min < 0:
                        lon_min = lon_min + 360
                    if lon_max < 0:
                        lon_max = lon_max + 360
                    print(f" Converting longitude range to 0-360°: {lon_range} -> ({lon_min}, {lon_max})")

                lon_mask = (ds.lon >= lon_min) & (ds.lon <= lon_max)
                ds = ds.sel(lon=lon_mask)
                print(f" Applied longitude subset: ({lon_min}, {lon_max})")
            except Exception as e:
                print(f" Warning: Could not apply longitude subsetting: {e}")
        
        return ds
        
    except ImportError:
        print(" ❌ Intake not available. Install with: pip install intake-esm")
        return None
    except Exception as e:
        print(f" ❌ Error loading data via catalog: {e}")
        return None


def check_cesm_variable_availability(variable_name: str, component: str = "atm", frequency: str = "daily") -> Optional[str]:
    """
    Check if a CESM variable is available using the Intake catalog.
    Returns the experiment name if found, None otherwise.
    """
    try:
        import intake
        
        catalog_url = "https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json"
        col = intake.open_esm_datastore(catalog_url)
        
        experiments = ["RCP85", "20C", "HIST"]
        
        for experiment in experiments:
            col_subset = col.search(
                experiment=experiment,
                frequency=frequency,
                variable=variable_name
            )
            
            if len(col_subset.df) > 0:
                print(f" ✅ Found {variable_name} in experiment {experiment}")
                return experiment
        
        print(f" ❌ Variable {variable_name} not found in any experiment")
        return None
        
    except ImportError:
        print(" ❌ Intake not available for variable checking")
        return None
    except Exception as e:
        print(f" ❌ Error checking variable availability: {e}")
        return None


def load_cesm_data_efficient(
    s3_path: str,
    variable_name: str,
    start_year: int,
    end_year: int,
    ensemble_members: str = "all",
    lat_range: Optional[Tuple[float, float]] = None,
    lon_range: Optional[Tuple[float, float]] = None,
    spatial_subsample: int = 1
) -> Optional[xr.Dataset]:
    """
    Efficiently load CESM data with proper calendar handling and memory optimization.
    
    Args:
        s3_path: S3 path to the zarr dataset
        variable_name: CESM variable name
        start_year: Start year for temporal subsetting
        end_year: End year for temporal subsetting
        ensemble_members: Ensemble members to load ("all", "single", or comma-separated list)
        lat_range: Optional latitude range (min, max)
        lon_range: Optional longitude range (min, max)
        spatial_subsample: Spatial subsampling factor (1=no subsampling)
    
    Returns:
        xarray Dataset or None if loading fails
    """
    print(f" Loading CESM data from: {s3_path}")
    
    try:
        # Initialize S3 filesystem
        fs = s3fs.S3FileSystem(anon=True)
        
        # Check if path exists
        if not fs.exists(s3_path):
            print(f" S3 path does not exist: {s3_path}")
            return None
        
        print(" S3 path verified, opening dataset...")
        
        # Open with proper calendar handling
        mapper = fs.get_mapper(s3_path)
        
        # Load with decode_times=False to handle calendar issues manually
        ds = xr.open_zarr(
            mapper,
            consolidated=True,
            decode_times=False,  # Handle time manually to avoid calendar issues
            chunks=None  # Load efficiently without complex chunking
        )
        
        print(f" Original dataset shape: {ds[variable_name].shape}")
        print(f" Dimensions: {list(ds[variable_name].dims)}")
        
        # Handle time coordinate properly with cftime
        if 'time' in ds.coords:
            try:
                # Decode time using cftime for CESM calendars
                time_attrs = ds.time.attrs
                units = time_attrs.get('units', 'days since 1850-01-01')
                calendar = time_attrs.get('calendar', 'noleap')
                
                print(f"⏰ Decoding time with units: {units}, calendar: {calendar}")
                
                # Use cftime to handle CESM's noleap calendar
                decoded_times = cftime.num2date(
                    ds.time.values,
                    units=units,
                    calendar=calendar
                )
                
                # Convert to pandas datetime for easier handling
                pd_times = pd.to_datetime([str(t) for t in decoded_times])
                
                # Replace time coordinate
                ds = ds.assign_coords(time=pd_times)
                print(" Time coordinate successfully decoded")
                
            except Exception as time_error:
                print(f" Time decoding failed: {time_error}")
                print(" Using raw time values...")
        
        # Apply temporal subsetting early
        if 'time' in ds.coords and start_year and end_year:
            try:
                time_mask = (
                    (ds.time.dt.year >= start_year) & 
                    (ds.time.dt.year <= end_year)
                )
                ds = ds.sel(time=time_mask)
                print(f"⏰ Temporal subset: {start_year}-{end_year}")
            except Exception as temporal_error:
                print(f" Temporal subsetting failed: {temporal_error}")
        
        # Apply spatial subsetting early with validation
        if lat_range and 'lat' in ds.coords:
            lat_mask = (ds.lat >= lat_range[0]) & (ds.lat <= lat_range[1])
            if lat_mask.sum() > 0:
                ds = ds.where(lat_mask, drop=True)
                print(f" Latitude subset: {lat_range[0]} to {lat_range[1]} ({lat_mask.sum().values} points)")
            else:
                print(f" Warning: No latitude points found in range {lat_range[0]} to {lat_range[1]}")
        
        if lon_range and 'lon' in ds.coords:
            # Handle longitude wrapping (e.g., -180 to 180 vs 0 to 360)
            lon_coords = ds.lon.values
            if lon_range[0] < 0 and lon_coords.max() > 180:
                # Convert longitude range to 0-360 if dataset uses 0-360
                lon_range = (lon_range[0] + 360, lon_range[1] + 360)
            
            lon_mask = (ds.lon >= lon_range[0]) & (ds.lon <= lon_range[1])
            if lon_mask.sum() > 0:
                ds = ds.where(lon_mask, drop=True)
                print(f" Longitude subset: {lon_range[0]} to {lon_range[1]} ({lon_mask.sum().values} points)")
            else:
                print(f" Warning: No longitude points found in range {lon_range[0]} to {lon_range[1]}")
                print(f" Dataset longitude range: {lon_coords.min():.2f} to {lon_coords.max():.2f}")
                # Try to find closest points instead
                closest_lon_idx = np.argmin(np.abs(lon_coords.reshape(-1, 1) - np.array(lon_range).reshape(1, -1)), axis=0)
                if len(closest_lon_idx) >= 2:
                    lon_start, lon_end = sorted(closest_lon_idx)
                    ds = ds.isel(lon=slice(lon_start, lon_end+1))
                    print(f" Using closest longitude points: indices {lon_start} to {lon_end}")
                else:
                    print(" Using single closest longitude point")
                    ds = ds.isel(lon=closest_lon_idx[0])
        
        # Apply spatial subsampling if requested
        if spatial_subsample > 1:
            if 'lat' in ds.coords:
                ds = ds.isel(lat=slice(None, None, spatial_subsample))
            if 'lon' in ds.coords:
                ds = ds.isel(lon=slice(None, None, spatial_subsample))
            print(f" Spatial subsampling: factor of {spatial_subsample}")
        
        # Check for empty spatial dimensions after subsetting
        if 'lat' in ds.coords and ds.lat.size == 0:
            print(" Error: No latitude points remain after spatial subsetting")
            return None
        if 'lon' in ds.coords and ds.lon.size == 0:
            print(" Error: No longitude points remain after spatial subsetting")
            return None
        
        # Handle ensemble member selection
        if 'member_id' in ds.dims:
            if ensemble_members == 'single':
                ds = ds.isel(member_id=0)
                print(" Selected single ensemble member (member 0)")
            elif ensemble_members != 'all':
                try:
                    member_list = [int(m)-1 for m in ensemble_members.split(',')]  # Convert to 0-indexed
                    ds = ds.isel(member_id=member_list)
                    print(f" Selected ensemble members: {ensemble_members}")
                except Exception as member_error:
                    print(f" Ensemble member selection failed: {member_error}, using all")
        
        # Optimize memory usage with smart loading
        data_size_gb = ds[variable_name].nbytes / 1e9
        print(f" Final dataset size: {data_size_gb:.2f} GB")
        
        # Memory optimization strategy
        if data_size_gb > 8.0:
            print(" Very large dataset (>8GB). Using lazy loading with spatial subsampling.")
            # Apply additional spatial subsampling for very large datasets
            if 'lat' in ds.coords and 'lon' in ds.coords:
                ds = ds.isel(lat=slice(None, None, 2), lon=slice(None, None, 2))
                print(" Applied 2x spatial subsampling to reduce memory usage")
            return ds  # Return lazy dataset
        elif data_size_gb > 4.0:
            print(" Large dataset (4-8GB). Using lazy loading.")
            return ds  # Return lazy dataset
        elif data_size_gb > 2.0:
            print(" Medium dataset (2-4GB). Loading with memory monitoring...")
            try:
                ds = ds.load()  # Load into memory
                print(" Successfully loaded into memory")
            except MemoryError:
                print(" Memory error during loading, using lazy dataset")
                return ds
        else:
            print(" Small dataset (<2GB). Loading into memory for optimal performance...")
            ds = ds.load()  # Load into memory for fast access
        
        print(f" Successfully loaded CESM data: {ds[variable_name].shape}")
        return ds
        
    except Exception as e:
        print(f" Failed to load CESM data: {e}")
        return None


def climate_to_tabular(ds: xr.Dataset, variable_name: str, chunk_size: int = 1000000) -> pl.DataFrame:
    """
    Convert multidimensional climate data to efficient tabular format using chunked processing.
    
    Args:
        ds: xarray Dataset with climate data
        variable_name: Name of the variable to convert
        chunk_size: Maximum number of rows to process at once (default: 1M)
    
    Returns:
        Polars DataFrame with columns: time, lat, lon, member_id, value
    """
    print(f" Converting {variable_name} to tabular format with chunked processing...")
    
    try:
        data_var = ds[variable_name]
        
        # Estimate total size first
        total_elements = data_var.size
        print(f" Total data elements: {total_elements:,}")
        
        # Check for empty dataset
        if total_elements == 0:
            print(" Dataset is empty (0 elements). Cannot process.")
            return None
        
        # If dataset is too large, use spatial subsampling
        if total_elements > 10_000_000:  # 10M elements
            print(" Very large dataset detected. Applying automatic spatial subsampling...")
            
            # Apply 2x spatial subsampling
            if 'lat' in ds.coords and 'lon' in ds.coords:
                ds = ds.isel(lat=slice(None, None, 2), lon=slice(None, None, 2))
                data_var = ds[variable_name]
                print(f" Applied 2x spatial subsampling. New size: {data_var.size:,} elements")
        
        # Check if still too large
        if data_var.size > 20_000_000:  # 20M elements
            print(" Dataset still very large. Applying temporal subsampling...")
            
            # Apply temporal subsampling (every 3rd time step)
            if 'time' in ds.coords:
                ds = ds.isel(time=slice(None, None, 3))
                data_var = ds[variable_name]
                print(f" Applied 3x temporal subsampling. New size: {data_var.size:,} elements")
        
        # Get coordinate arrays
        coords_dict = {}
        for dim in data_var.dims:
            if dim in ds.coords:
                coords_dict[dim] = ds.coords[dim].values
        
        # Process data in chunks by ensemble member to avoid memory issues
        df_chunks = []
        
        if 'member_id' in data_var.dims:
            members = coords_dict.get('member_id', [0])
            print(f" Processing {len(members)} ensemble members in chunks...")
            
            for member_idx, member_id in enumerate(members):
                print(f"  Processing member {member_idx + 1}/{len(members)} (ID: {member_id})")
                
                try:
                    member_data = data_var.isel(member_id=member_idx)
                    
                    # Process this member's data
                    if 'time' in member_data.dims and 'lat' in member_data.dims and 'lon' in member_data.dims:
                        # Get coordinates for this member
                        time_coords = coords_dict['time']
                        lat_coords = coords_dict['lat']
                        lon_coords = coords_dict['lon']
                        
                        # Create data in chunks to avoid memory issues
                        n_time = len(time_coords)
                        n_spatial = len(lat_coords) * len(lon_coords)
                        
                        # Safety check to prevent division by zero
                        if n_spatial == 0:
                            print(f"  Warning: Empty spatial grid for member {member_id}, skipping...")
                            continue
                        
                        # Process in time chunks
                        time_chunk_size = max(1, chunk_size // n_spatial)
                        
                        for t_start in range(0, n_time, time_chunk_size):
                            t_end = min(t_start + time_chunk_size, n_time)
                            
                            # Extract chunk data
                            time_chunk = member_data.isel(time=slice(t_start, t_end))
                            
                            # Create coordinate arrays for this chunk
                            time_vals, lat_vals, lon_vals = np.meshgrid(
                                time_coords[t_start:t_end],
                                lat_coords,
                                lon_coords,
                                indexing='ij'
                            )
                            
                            # Handle cftime objects properly
                            time_flat = time_vals.flatten()
                            if hasattr(time_flat[0], 'strftime'):  # cftime object
                                time_strings = [t.strftime('%Y-%m-%d %H:%M:%S') for t in time_flat]
                                time_converted = pd.to_datetime(time_strings)
                            else:
                                time_converted = pd.to_datetime(time_flat)

                            # Create chunk DataFrame
                            chunk_df = pl.DataFrame({
                                'time': time_converted,
                                'lat': lat_vals.flatten().astype(np.float32),
                                'lon': lon_vals.flatten().astype(np.float32),
                                'member_id': np.full(time_vals.size, member_id, dtype=np.int16),
                                'value': time_chunk.values.flatten().astype(np.float32)
                            })
                            
                            # Remove invalid values
                            chunk_df = chunk_df.filter(
                                pl.col('value').is_not_nan() & 
                                pl.col('value').is_finite()
                            )
                            
                            df_chunks.append(chunk_df)
                            
                            # Memory management
                            del time_vals, lat_vals, lon_vals, chunk_df
                    
                except Exception as member_error:
                    print(f" Error processing member {member_id}: {member_error}")
                    continue
        
        else:
            # Single member case
            print(" Processing single member dataset...")
            
            if 'time' in data_var.dims and 'lat' in data_var.dims and 'lon' in data_var.dims:
                time_coords = coords_dict['time']
                lat_coords = coords_dict['lat']
                lon_coords = coords_dict['lon']
                
                n_time = len(time_coords)
                n_spatial = len(lat_coords) * len(lon_coords)
                
                # Safety check to prevent division by zero
                if n_spatial == 0:
                    print("  Warning: Empty spatial grid, cannot process dataset")
                    return None
                
                time_chunk_size = max(1, chunk_size // n_spatial)
                
                for t_start in range(0, n_time, time_chunk_size):
                    t_end = min(t_start + time_chunk_size, n_time)
                    
                    time_chunk = data_var.isel(time=slice(t_start, t_end))
                    
                    time_vals, lat_vals, lon_vals = np.meshgrid(
                        time_coords[t_start:t_end],
                        lat_coords,
                        lon_coords,
                        indexing='ij'
                    )
                    
                    # Handle cftime objects properly
                    time_flat = time_vals.flatten()
                    if hasattr(time_flat[0], 'strftime'):  # cftime object
                        time_strings = [t.strftime('%Y-%m-%d %H:%M:%S') for t in time_flat]
                        time_converted = pd.to_datetime(time_strings)
                    else:
                        time_converted = pd.to_datetime(time_flat)

                    chunk_df = pl.DataFrame({
                        'time': time_converted,
                        'lat': lat_vals.flatten().astype(np.float32),
                        'lon': lon_vals.flatten().astype(np.float32),
                        'member_id': np.ones(time_vals.size, dtype=np.int16),
                        'value': time_chunk.values.flatten().astype(np.float32)
                    })
                    
                    chunk_df = chunk_df.filter(
                        pl.col('value').is_not_nan() & 
                        pl.col('value').is_finite()
                    )
                    
                    df_chunks.append(chunk_df)
                    del time_vals, lat_vals, lon_vals, chunk_df
        
        # Combine all chunks
        if not df_chunks:
            print(" No valid data chunks created")
            return None
        
        print(f" Combining {len(df_chunks)} data chunks...")
        
        # Combine chunks efficiently
        try:
            df = pl.concat(df_chunks)
            
            print(f" Converted to tabular format: {df.shape[0]:,} rows, {df.shape[1]} columns")
            memory_mb = df.estimated_size() / 1e6
            print(f" Memory usage: {memory_mb:.1f} MB")
            
            # Memory usage recommendations
            if memory_mb > 2000:  # 2GB
                print(f" Very large DataFrame ({memory_mb:.0f} MB). Consider further subsetting.")
            elif memory_mb > 1000:  # 1GB
                print(f" Large DataFrame ({memory_mb:.0f} MB). Processing may be slow.")
            
            return df
            
        except MemoryError:
            print(" Memory error during chunk combination. Dataset too large even with chunking.")
            print(" Try: Smaller time range, fewer ensemble members, or coarser spatial resolution")
            return None
        finally:
            # Clean up chunks
            del df_chunks
            
    except Exception as e:
        print(f" Chunked tabular conversion failed: {e}")
        traceback.print_exc()
        return None

# --- Initialize services ---
kg_connector = KGConnector()
llm = BedrockClaudeLLM()

# --- CESM LENS Tools (based on original agentic_climate_ai.py) ---

class CESMLENSDataTool(BaseTool):
    """Query CESM-LENS ensemble data using efficient Polars-based processing"""
    name: str = "query_cesm_lens_data"
    description: str = "Query CESM-LENS ensemble data efficiently using Polars dataframes. Handles memory optimization and proper calendar decoding. Input format: 'variable_name start_year end_year ensemble_members [lat_min,lat_max] [lon_min,lon_max]'. Example: 'TREFHT 2010 2020 all' or 'TREFHT 2010 2020 1,2,3 30,60 -120,-60'"
    
    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Query CESM-LENS data from S3 with efficient processing"""
        
        try:
            # Parse the input string with support for spatial subsetting
            parts = tool_input.strip().split()
            if len(parts) < 3:
                return " Error: Input must have at least 3 parts: 'variable_name start_year end_year [ensemble_members] [lat_range] [lon_range]'. Example: 'TREFHT 2010 2020 all'"
            
            variable_name = parts[0]
            start_year = int(parts[1])
            end_year = int(parts[2])
            ensemble_members = parts[3] if len(parts) > 3 else "all"
            
            # Parse optional spatial subsetting
            lat_range = None
            lon_range = None
            if len(parts) > 4:
                lat_parts = parts[4].split(',')
                if len(lat_parts) == 2:
                    lat_range = (float(lat_parts[0]), float(lat_parts[1]))
            if len(parts) > 5:
                lon_parts = parts[5].split(',')
                if len(lon_parts) == 2:
                    lon_range = (float(lon_parts[0]), float(lon_parts[1]))
            
        except (ValueError, IndexError) as e:
            return f" Error parsing input '{tool_input}'. Expected format: 'variable_name start_year end_year [ensemble_members]'. Example: 'TREFHT 2010 2020 all'. Error: {e}"
        
        print(f" Querying CESM-LENS data for {variable_name} ({start_year}-{end_year})")
        
        # Validate CESM variable name through knowledge graph
        try:
            cesm_check_query = f"""
            MATCH (v:CESMVariable)
            WHERE v.name = '{variable_name}' OR v.`~id` CONTAINS '{variable_name}'
            RETURN v.name as variable_name, v.long_name as long_name, v.units as units, v.component as component
            LIMIT 1
            """
            
            cesm_result = kg_connector.execute_query(cesm_check_query)
            
            if not cesm_result.get("results"):
                return f" Variable '{variable_name}' not found in CESM knowledge graph. Please use search_by_variable to find available CESM variables first."
            
            # Get variable metadata
            var_info = cesm_result["results"][0]
            # Use the exact variable name requested, not the KG match
            # This prevents TREFHT -> TREFHTMX mapping issues
            validated_var_name = variable_name
            
            # Only use KG name if exact match
            kg_var_name = var_info.get("variable_name", "")
            if kg_var_name.lower() == variable_name.lower():
                validated_var_name = kg_var_name
            long_name = var_info.get("long_name", "")
            units = var_info.get("units", "")
            # Map component correctly for CESM LENS S3 structure
            raw_component = var_info.get("component", "std")
            # CESM LENS on AWS uses specific component names:
            # atm, ocn, lnd, ice_nh, ice_sh
            component_mapping = {
                "std": "atm",  # Standard atmospheric variables -> atm
                "atmosphere": "atm",
                "ocean": "ocn",
                "land": "lnd",
                "ice": "ice_nh"  # Default to northern hemisphere ice
            }
            component = component_mapping.get(raw_component, "atm")
            
            print(f" Found CESM variable: {validated_var_name} ({long_name})")
            
        except Exception as e:
            print(f" Could not validate variable through knowledge graph: {e}")
            validated_var_name = variable_name
            long_name = "Unknown"
            units = "Unknown"
            component = "atm"  # Default to atmospheric component
        
        # Handle time range and experiment selection properly
        # CESM LENS experiments:
        # - HIST: Historical runs (1850-2005)
        # - 20C: 20th century runs (1920-2005)  
        # - RCP85: Future scenario (2006-2100)
        # - CTRL: Control runs
        
        if start_year >= 1920 and end_year <= 2005:
            experiment = "20C"  # 20th century historical
        elif start_year >= 2006:
            experiment = "RCP85"  # Future scenario
        elif start_year <= 2005 and end_year > 2005:
            # Spanning experiments - prioritize based on more data coverage
            if (2005 - start_year) >= (end_year - 2006):
                experiment = "20C"  # More historical data
            else:
                experiment = "RCP85"  # More future data
            print(f" Time range {start_year}-{end_year} spans experiments. Using {experiment}")
        else:
            experiment = "20C"  # Default to historical
        
        # Query knowledge graph for component information using both direct property and relationships
        component_query = f"""
        MATCH (v:CESMVariable)
        WHERE toLower(v.name) = toLower('{validated_var_name}') 
           OR toLower(v.standard_name) = toLower('{validated_var_name}')
        OPTIONAL MATCH (v)-[:hasComponent]->(c:Component)
        RETURN v.component as direct_component, v.domain as domain, 
               collect(c.name) as related_components
        LIMIT 1
        """
        
        # Determine frequency based on known CESM patterns (precipitation vars are daily)
        precipitation_vars = ['PRECT', 'PRECC', 'PRECL', 'PRECTMX', 'PRECSC', 'PRECSL', 'TMQ']
        if validated_var_name.upper() in [v.upper() for v in precipitation_vars]:
            frequency = "daily"
            print(f" Using daily frequency for precipitation variable: {validated_var_name}")
        else:
            frequency = "daily"  # Default to daily as most CESM variables are daily
            print(f" Using default daily frequency for: {validated_var_name}")
        
        try:
            component_result = kg_connector.execute_query(component_query)
            if component_result.get("results") and len(component_result["results"]) > 0:
                kg_data = component_result["results"][0]
                direct_comp = kg_data.get('direct_component')
                domain = kg_data.get('domain') 
                related_comps = kg_data.get('related_components', [])
                
                # Use direct component property first, then related components, then domain
                if direct_comp and direct_comp.strip():
                    component = direct_comp.strip()
                    print(f" Using direct component from KG: {component}")
                elif related_comps and len(related_comps) > 0 and related_comps[0]:
                    component = related_comps[0]
                    print(f" Using related component from KG: {component}")
                elif domain and domain.strip() and domain.strip().lower() in ['atmosphere', 'ocean', 'land', 'ice']:
                    # Map domain to component
                    domain_map = {'atmosphere': 'atm', 'ocean': 'ocn', 'land': 'lnd', 'ice': 'ice'}
                    component = domain_map.get(domain.strip().lower(), 'atm')
                    print(f" Using component from domain mapping: {domain} -> {component}")
                else:
                    print(f" No component info in KG for {validated_var_name}, using default: {component}")
            else:
                print(f" No metadata in KG for {validated_var_name}, using default component: {component}")
        except Exception as e:
            print(f" Error querying KG for component: {e}")
            # Keep default component = "atm"
        
        # CESM-LENS S3 path format - try different experiment variations
        cesm_s3_path = f"ncar-cesm-lens/{component}/{frequency}/cesmLE-{experiment}-{validated_var_name}.zarr"
        
        # Keep track of attempted paths for debugging
        attempted_paths = [cesm_s3_path]
        
        
        # Efficiently load CESM data using optimized functions
        print(f" Loading CESM-LENS data for {validated_var_name} ({start_year}-{end_year})")
        
        try:
            # First, try loading data using the official Intake catalog approach
            print(f" Checking variable availability for {validated_var_name}...")
            available_experiment = check_cesm_variable_availability(validated_var_name, component, frequency)
            
            if available_experiment:
                print(f" Using Intake catalog with experiment: {available_experiment}")
                cesm_dataset = load_cesm_data_via_catalog(
                    validated_var_name,
                    available_experiment,
                    frequency,
                    start_year,
                    end_year,
                    lat_range,
                    lon_range
                )
            else:
                print(f" Variable {validated_var_name} not found in catalog, trying fallback S3 approach...")
                cesm_dataset = None
                
            # If catalog approach fails, fall back to direct S3 path approach
            if cesm_dataset is None:
                print(f" Falling back to direct S3 access: {cesm_s3_path}")
                cesm_dataset = load_cesm_data_efficient(
                    cesm_s3_path,
                    validated_var_name,
                    start_year,
                    end_year,
                    ensemble_members,
                    lat_range,
                    lon_range,
                    spatial_subsample=3  # 3x subsampling for memory safety
                )
            
            # If primary path fails, try alternative experiments and then similar variables
            if cesm_dataset is None:
                print(f" Primary path failed: {cesm_s3_path}")
                print(f" Trying alternative experiments...")
                
                # Try alternative experiments based on what's commonly available
                alternative_experiments = []
                if experiment == "20C":
                    alternative_experiments = ["RCP85", "HIST"]
                elif experiment == "RCP85":
                    alternative_experiments = ["20C", "HIST"]
                else:
                    alternative_experiments = ["20C", "RCP85", "HIST"]
                
                for alt_experiment in alternative_experiments:
                    alt_path = f"ncar-cesm-lens/{component}/{frequency}/cesmLE-{alt_experiment}-{validated_var_name}.zarr"
                    attempted_paths.append(alt_path)
                    print(f" Trying experiment {alt_experiment}: {alt_path}")
                    
                    cesm_dataset = load_cesm_data_efficient(
                        alt_path,
                        validated_var_name,
                        start_year,
                        end_year,
                        ensemble_members,
                        lat_range,
                        lon_range,
                        spatial_subsample=3
                    )
                    
                    if cesm_dataset is not None:
                        print(f" ✅ Successfully loaded with experiment {alt_experiment}")
                        cesm_s3_path = alt_path
                        experiment = alt_experiment
                        break
                
                # If experiments fail, try similar variables
                if cesm_dataset is None:
                    print(f" Variable {validated_var_name} not found in any standard experiments")
                    print(f" Searching for similar variables using Knowledge Graph relationships...")
                    
                    # Get similar variables from knowledge graph and test each one
                    similar_vars = self._get_similar_variables_from_kg(validated_var_name)
                    
                    for similar_var in similar_vars:
                        print(f" Testing similar variable: {similar_var}")
                        for test_exp in [experiment] + alternative_experiments:
                            alternative_path = f"ncar-cesm-lens/{component}/{frequency}/cesmLE-{test_exp}-{similar_var}.zarr"
                            attempted_paths.append(alternative_path)
                            cesm_dataset = load_cesm_data_efficient(
                                alternative_path,
                                similar_var,
                                start_year,
                                end_year,
                                ensemble_members,
                                lat_range,
                                lon_range,
                                spatial_subsample=3
                            )
                            if cesm_dataset is not None:
                                print(f" ✅ Successfully loaded similar variable: {similar_var} with experiment {test_exp}")
                                validated_var_name = similar_var
                                cesm_s3_path = alternative_path
                                experiment = test_exp
                                break
                        if cesm_dataset is not None:
                            break  # Exit outer loop once we find a working combination
                
                if cesm_dataset is None:
                    print(f" ❌ No similar variables found that work in S3")
                    print(f" 🔍 Attempted paths:")
                    for path in attempted_paths[-5:]:  # Show last 5 attempts
                        print(f"   - {path}")
                    print(f" 💡 Use 'smart_cesm_variable_selection' to find available variables for your research")
            
            if cesm_dataset is not None:
                print(" Successfully loaded real CESM data")
                
                # Estimate memory requirements before conversion
                data_var = cesm_dataset[validated_var_name]
                estimated_size_gb = data_var.size * 4 * 5 / 1e9  # 4 bytes per float32, 5 columns, rough estimate
                print(f" Estimated tabular memory requirement: {estimated_size_gb:.2f} GB")
                
                if estimated_size_gb > 4.0:
                    print(" Very large conversion expected. Using reduced chunk size...")
                    chunk_size = 500000  # Smaller chunks
                else:
                    chunk_size = 1000000  # Default chunk size
                
                # Convert to efficient tabular format
                cesm_df = climate_to_tabular(cesm_dataset, validated_var_name, chunk_size=chunk_size)
                
                if cesm_df is not None:
                    # Store both xarray and polars versions globally
                    globals()['cesm_data'] = cesm_dataset
                    globals()['cesm_df'] = cesm_df
                    globals()['current_variable'] = validated_var_name
                    
                    success_message = "Real CESM-LENS data loaded and converted to efficient format"
                else:
                    raise Exception("Failed to convert to tabular format")
            else:
                raise Exception("Failed to load real CESM data")
                
        except Exception as load_error:
            print(f" Real data loading failed: {load_error}")
            # Return error message if both real and simulated loading failed
            return f" Failed to load CESM LENS data for {variable_name} ({start_year}-{end_year}): {load_error}"
        
        # If we successfully loaded data, save the path automatically
        try:
            save_tool = SaveCESMDataPathTool()
            
            # Extract current data metadata for saving
            current_data_metadata = save_tool._extract_current_data_metadata()
            
            # Create metadata from the loaded data
            metadata = {
                'frequency': frequency,
                'ensemble_members': ensemble_members,
                'file_size_gb': current_data_metadata.get('file_size_gb', 0.0),
                'memory_usage': current_data_metadata.get('memory_usage', 0.0),
                'lat_range': lat_range if lat_range else current_data_metadata.get('lat_range', 'global'),
                'lon_range': lon_range if lon_range else current_data_metadata.get('lon_range', 'global'),
                'notes': f'Auto-saved from successful data loading. Spatial subsample: 3x'
            }
            
            # Save the path
            save_input = f"{validated_var_name} {start_year} {end_year} {cesm_s3_path} {json.dumps(metadata)}"
            save_result = save_tool._run(save_input)
            print(f" Auto-saved data path: {save_result.split('Database ID:')[1].split()[0] if 'Database ID:' in save_result else 'success'}")
            
        except Exception as save_error:
            print(f" Could not auto-save data path: {save_error}")
        
        # Return success message with data summary
        output = f" CESM LENS DATA LOADING COMPLETE\n"
        output += "=" * 50 + "\n\n"
        output += f" DATASET SUMMARY:\n"
        output += f"   • Variable: {validated_var_name} ({long_name})\n"
        output += f"   • Time Period: {start_year}-{end_year} ({experiment})\n"
        output += f"   • Component: {component}\n"
        output += f"   • S3 Path: {cesm_s3_path}\n"
        output += f"   • Ensemble Members: {ensemble_members}\n"
        
        if cesm_df is not None:
            output += f"   • Tabular Format: {cesm_df.shape[0]:,} rows, {cesm_df.shape[1]} columns\n"
            output += f"   • Memory Usage: {cesm_df.estimated_size() / 1e6:.1f} MB\n"
        
        if lat_range or lon_range:
            output += f"   • Spatial Subset: {lat_range} × {lon_range}\n"
        
        # Save data locally
        if cesm_df is not None:
            try:
                # Create filename based on variable and time range
                safe_var_name = validated_var_name.replace('/', '_').replace('\\', '_')
                local_filename = f"cesm_{safe_var_name}_{start_year}_{end_year}_texas.csv"
                local_path = os.path.join(os.getcwd(), local_filename)

                # Save to CSV for easy analysis
                cesm_df.write_csv(local_path)
                output += f"   • Data saved locally: {local_filename}\n"

                # Also save as parquet for efficiency
                parquet_filename = f"cesm_{safe_var_name}_{start_year}_{end_year}_texas.parquet"
                parquet_path = os.path.join(os.getcwd(), parquet_filename)
                cesm_df.write_parquet(parquet_path)
                output += f"   • Data saved (parquet): {parquet_filename}\n"

            except Exception as save_error:
                output += f"   • Warning: Could not save locally: {save_error}\n"

        output += f"\n📁 DATA READY FOR ANALYSIS\n"
        output += f"   • Use 'analyze_cesm_ensemble' for ensemble statistics\n"
        output += f"   • Global variables 'cesm_data' and 'cesm_df' available\n"
        output += f"   • Data path automatically saved to database\n"
        output += f"\n🤔 ASKING FOLLOW-UP QUESTION...\n"

        # Automatically call the follow-up tool as part of the workflow
        try:
            followup_tool = AskDataProcessingFollowUpTool()
            context = f"Successfully loaded {validated_var_name} data for {start_year}-{end_year} covering Texas region. Data contains {cesm_df.shape[0]:,} rows with {cesm_df.shape[1]} columns (time, lat, lon, member_id, value). Files saved as CSV and Parquet formats locally."
            followup_response = followup_tool._run(context)
            output += f"\n{followup_response}\n"
        except Exception as e:
            output += f"\n⚠️  Could not ask follow-up automatically: {e}\n"
            output += f"⚠️  Please specify what you'd like to do with this precipitation data!\n"

        return output
    
    def _suggest_alternative_variable(self, requested_var: str, available_vars: list) -> str:
        """Suggest alternative CESM variable using similarCESMVariable relationships from Knowledge Graph"""
        
        # Use the new method to get similar variables from KG
        similar_vars = self._get_similar_variables_from_kg(requested_var)
        
        # Return the first similar variable found (will be tested individually in the calling code)
        if similar_vars:
            return similar_vars[0]
        
        return None
    
    def _get_similar_variables_from_kg(self, requested_var: str) -> list:
        """Get similar variables from Knowledge Graph using similarCESMVariable relationships"""
        try:
            # Query for variables with similarCESMVariable relationships
            similar_query = f"""
            MATCH (v1:CESMVariable)-[:similarCESMVariable]->(v2:CESMVariable)
            WHERE v1.name = '{requested_var}' 
               OR v1.`~id` CONTAINS '{requested_var}'
               OR v2.name = '{requested_var}'
               OR v2.`~id` CONTAINS '{requested_var}'
            RETURN DISTINCT 
                CASE 
                    WHEN v1.name = '{requested_var}' OR v1.`~id` CONTAINS '{requested_var}' THEN v2.name
                    ELSE v1.name
                END as similar_var,
                CASE 
                    WHEN v1.name = '{requested_var}' OR v1.`~id` CONTAINS '{requested_var}' THEN v2.long_name
                    ELSE v1.long_name
                END as long_name
            ORDER BY similar_var
            LIMIT 5
            """
            
            from knowledge_graph_agent_bedrock import kg_connector
            result = kg_connector.execute_query(similar_query)
            
            similar_vars = []
            if result.get("results"):
                print(f" Found {len(result['results'])} similar variables from Knowledge Graph")
                for var_info in result["results"]:
                    similar_var = var_info.get('similar_var', '')
                    long_name = var_info.get('long_name', '')
                    if similar_var and similar_var != requested_var:
                        print(f"   • {similar_var}: {long_name}")
                        similar_vars.append(similar_var)
            else:
                print(f" No similarCESMVariable relationships found for '{requested_var}'")
            
            return similar_vars
            
        except Exception as e:
            print(f" Error querying Knowledge Graph for similar variables: {e}")
            return []
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using simple character overlap"""
        if not str1 or not str2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # Bonus for substring matches
        substring_bonus = 0.0
        if str1.lower() in str2.lower() or str2.lower() in str1.lower():
            substring_bonus = 0.3
        
        # Bonus for common prefixes
        prefix_bonus = 0.0
        min_len = min(len(str1), len(str2))
        for i in range(min(4, min_len)):  # Check first 4 characters
            if str1[i].lower() == str2[i].lower():
                prefix_bonus += 0.1
            else:
                break
        
        return min(1.0, jaccard_similarity + substring_bonus + prefix_bonus)
            
class CESMEnsembleAnalysisTool(BaseTool):
    """Perform efficient ensemble analysis using Polars operations"""
    name: str = "analyze_cesm_ensemble"
    description: str = "Efficiently analyze CESM LENS ensemble data using Polars operations. Supports ensemble statistics, trends, and uncertainty quantification. Input: analysis_type (e.g., 'ensemble_mean', 'uncertainty', 'trend_analysis')"
    
    def _run(self, analysis_type: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Perform efficient ensemble analysis using Polars operations"""
        
        print(f" Performing efficient CESM LENS ensemble analysis: {analysis_type}")
        
        # Check if Polars DataFrame is available
        if 'cesm_df' not in globals():
            return " No CESM data loaded. Please run query_cesm_lens_data first."
        
        df = globals()['cesm_df']
        variable_name = globals().get('current_variable', 'unknown')
        
        print(f" Analyzing {variable_name} with {df.shape[0]} data points")
        print(f" {df['member_id'].n_unique()} ensemble members")
        print(f" Time range: {df['time'].min()} to {df['time'].max()}")
        
        try:
            if analysis_type == 'ensemble_mean':
                return self._analyze_ensemble_mean_polars(df, variable_name)
            elif analysis_type == 'trend_analysis':
                return self._analyze_trends_polars(df, variable_name)
            elif analysis_type == 'uncertainty':
                return self._analyze_uncertainty_polars(df, variable_name)
            else:
                return f" Unknown analysis type: {analysis_type}. Available: ensemble_mean, trend_analysis, uncertainty"
                
        except Exception as e:
            return f" Analysis failed: {e}"
    
    def _analyze_ensemble_mean_polars(self, df: pl.DataFrame, variable_name: str) -> str:
        """Efficient ensemble mean analysis using Polars"""
        print(" Computing ensemble statistics with Polars...")
        
        # Global mean time series for each member
        global_ts = df.group_by(['time', 'member_id']).agg([
            pl.col('value').mean().alias('global_mean')
        ]).sort(['time', 'member_id'])
        
        # Ensemble statistics over time
        ensemble_stats = global_ts.group_by('time').agg([
            pl.col('global_mean').mean().alias('ensemble_mean'),
            pl.col('global_mean').std().alias('ensemble_std'),
            pl.col('global_mean').min().alias('ensemble_min'),
            pl.col('global_mean').max().alias('ensemble_max'),
            pl.col('global_mean').quantile(0.025).alias('p025'),
            pl.col('global_mean').quantile(0.975).alias('p975')
        ]).sort('time')
        
        # Convert to pandas for plotting
        ensemble_pd = ensemble_stats.to_pandas()
        ensemble_pd['time'] = pd.to_datetime(ensemble_pd['time'])
        
        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Ensemble mean time series
        axes[0,0].plot(ensemble_pd['time'], ensemble_pd['ensemble_mean'], 'red', linewidth=2)
        axes[0,0].fill_between(ensemble_pd['time'], 
                              ensemble_pd['p025'], ensemble_pd['p975'], 
                              alpha=0.3, color='red', label='95% CI')
        axes[0,0].set_title('Global Ensemble Mean Time Series')
        axes[0,0].set_ylabel(f'{variable_name}')
        axes[0,0].legend()
        axes[0,0].grid(True, alpha=0.3)
        
        # Ensemble spread time series
        axes[0,1].plot(ensemble_pd['time'], ensemble_pd['ensemble_std'], 'blue', linewidth=2)
        axes[0,1].set_title('Ensemble Standard Deviation')
        axes[0,1].set_ylabel('Std Dev')
        axes[0,1].grid(True, alpha=0.3)
        
        # Spatial ensemble mean (time average)
        spatial_mean = df.group_by(['lat', 'lon']).agg([
            pl.col('value').mean().alias('time_mean')
        ])
        spatial_pivot = spatial_mean.to_pandas().pivot(index='lat', columns='lon', values='time_mean')
        
        im1 = axes[1,0].contourf(spatial_pivot.columns, spatial_pivot.index, spatial_pivot.values, 
                                levels=20, cmap='RdYlBu_r')
        axes[1,0].set_title('Time-Mean Spatial Pattern')
        axes[1,0].set_xlabel('Longitude')
        axes[1,0].set_ylabel('Latitude')
        plt.colorbar(im1, ax=axes[1,0])
        
        # Ensemble range by latitude
        lat_stats = df.group_by(['lat', 'member_id']).agg([
            pl.col('value').mean().alias('lat_mean')
        ]).group_by('lat').agg([
            pl.col('lat_mean').mean().alias('ensemble_mean'),
            pl.col('lat_mean').std().alias('ensemble_std')
        ]).sort('lat')
        
        lat_pd = lat_stats.to_pandas()
        axes[1,1].plot(lat_pd['lat'], lat_pd['ensemble_mean'], 'red', linewidth=2, label='Mean')
        axes[1,1].fill_between(lat_pd['lat'], 
                              lat_pd['ensemble_mean'] - lat_pd['ensemble_std'],
                              lat_pd['ensemble_mean'] + lat_pd['ensemble_std'],
                              alpha=0.3, color='red', label='±1σ')
        axes[1,1].set_title('Latitudinal Mean and Spread')
        axes[1,1].set_xlabel('Latitude')
        axes[1,1].set_ylabel(f'{variable_name}')
        axes[1,1].legend()
        axes[1,1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('ensemble_analysis_polars.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Summary statistics
        mean_trend = float(ensemble_pd['ensemble_mean'].iloc[-1] - ensemble_pd['ensemble_mean'].iloc[0])
        mean_spread = float(ensemble_pd['ensemble_std'].mean())
        
        return f""" Ensemble Mean Analysis Complete (Polars-optimized):
 Global ensemble mean trend: {mean_trend:.3f} {variable_name} units over period
 Average ensemble spread: {mean_spread:.3f} {variable_name} units
 Analysis plots saved to: ensemble_analysis_polars.png
 Efficient computation using Polars aggregations"""
    
    def _analyze_trends_polars(self, df: pl.DataFrame, variable_name: str) -> str:
        """Efficient trend analysis using Polars"""
        print(" Computing trends with Polars...")
        
        # Global mean time series for each member
        global_ts = df.group_by(['time', 'member_id']).agg([
            pl.col('value').mean().alias('global_mean')
        ]).sort(['time', 'member_id'])
        
        # Convert time to numeric for trend calculation
        global_ts = global_ts.with_columns([
            pl.col('time').dt.year().alias('year'),
            pl.col('time').dt.ordinal_day().alias('day_of_year')
        ])
        global_ts = global_ts.with_columns([
            (pl.col('year') + pl.col('day_of_year') / 365.25).alias('time_numeric')
        ])
        
        # Calculate trends for each ensemble member using Polars
        member_trends = []
        members = global_ts['member_id'].unique().sort()
        
        for member in members:
            member_data = global_ts.filter(pl.col('member_id') == member)
            
            # Simple linear regression: y = ax + b
            n = len(member_data)
            if n < 2:
                continue
                
            x = member_data['time_numeric'].to_numpy()
            y = member_data['global_mean'].to_numpy()
            
            # Calculate trend (slope)
            x_mean = np.mean(x)
            y_mean = np.mean(y)
            slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
            
            member_trends.append({
                'member_id': member,
                'trend_per_year': slope,
                'start_value': y[0],
                'end_value': y[-1]
            })
        
        # Convert to DataFrame for analysis
        trends_df = pl.DataFrame(member_trends)
        
        # Trend statistics
        trend_stats = trends_df.select([
            pl.col('trend_per_year').mean().alias('mean_trend'),
            pl.col('trend_per_year').std().alias('trend_std'),
            pl.col('trend_per_year').min().alias('min_trend'),
            pl.col('trend_per_year').max().alias('max_trend'),
            pl.col('trend_per_year').quantile(0.025).alias('trend_p025'),
            pl.col('trend_per_year').quantile(0.975).alias('trend_p975')
        ])
        
        stats = trend_stats.to_pandas().iloc[0]
        
        # Create plots
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Time series with trends
        for i, member in enumerate(members[:10]):  # Plot first 10 members
            member_data = global_ts.filter(pl.col('member_id') == member).to_pandas()
            axes[0].plot(member_data['time'], member_data['global_mean'], alpha=0.3, color='blue')
        
        # Ensemble mean
        ensemble_mean = global_ts.group_by('time').agg([
            pl.col('global_mean').mean().alias('ensemble_mean')
        ]).sort('time').to_pandas()
        ensemble_mean['time'] = pd.to_datetime(ensemble_mean['time'])
        axes[0].plot(ensemble_mean['time'], ensemble_mean['ensemble_mean'], 
                    color='red', linewidth=3, label='Ensemble Mean')
        axes[0].set_title('Global Mean Time Series with Trends')
        axes[0].set_ylabel(f'{variable_name}')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Trend distribution
        trends_pd = trends_df.to_pandas()
        axes[1].hist(trends_pd['trend_per_year'], bins=20, alpha=0.7, edgecolor='black')
        axes[1].axvline(stats['mean_trend'], color='red', linestyle='--', linewidth=2, 
                       label=f'Mean: {stats["mean_trend"]:.4f}/yr')
        axes[1].set_xlabel('Trend (units/year)')
        axes[1].set_ylabel('Frequency')
        axes[1].set_title('Distribution of Trends Across Ensemble')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('trend_analysis_polars.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        return f""" Trend Analysis Complete (Polars-optimized):
 Mean trend: {stats['mean_trend']:.4f} ± {stats['trend_std']:.4f} {variable_name}/year
 Trend range: {stats['min_trend']:.4f} to {stats['max_trend']:.4f} {variable_name}/year
 95% confidence interval: {stats['trend_p025']:.4f} to {stats['trend_p975']:.4f} {variable_name}/year
 {len(member_trends)} ensemble members analyzed
 Analysis plots saved to: trend_analysis_polars.png"""
    
    def _analyze_uncertainty_polars(self, df: pl.DataFrame, variable_name: str) -> str:
        """Efficient uncertainty analysis using Polars"""
        print(" Computing uncertainty with Polars...")
        
        # Global mean time series with uncertainty bands
        global_ts = df.group_by(['time', 'member_id']).agg([
            pl.col('value').mean().alias('global_mean')
        ]).sort(['time', 'member_id'])
        
        # Compute uncertainty metrics by time
        uncertainty = global_ts.group_by('time').agg([
            pl.col('global_mean').mean().alias('ensemble_mean'),
            pl.col('global_mean').std().alias('ensemble_std'),
            pl.col('global_mean').quantile(0.025).alias('p025'),
            pl.col('global_mean').quantile(0.975).alias('p975'),
            pl.col('global_mean').quantile(0.05).alias('p05'),
            pl.col('global_mean').quantile(0.95).alias('p95'),
            pl.col('global_mean').min().alias('min_val'),
            pl.col('global_mean').max().alias('max_val')
        ]).sort('time')
        
        uncertainty_pd = uncertainty.to_pandas()
        uncertainty_pd['time'] = pd.to_datetime(uncertainty_pd['time'])
        
        # Plot uncertainty
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # Main uncertainty plot
        axes[0].fill_between(uncertainty_pd['time'], uncertainty_pd['min_val'], uncertainty_pd['max_val'],
                           alpha=0.2, color='lightblue', label='Full Range')
        axes[0].fill_between(uncertainty_pd['time'], uncertainty_pd['p05'], uncertainty_pd['p95'],
                           alpha=0.4, color='blue', label='90% Range')
        axes[0].fill_between(uncertainty_pd['time'], uncertainty_pd['p025'], uncertainty_pd['p975'],
                           alpha=0.6, color='darkblue', label='95% Range')
        axes[0].plot(uncertainty_pd['time'], uncertainty_pd['ensemble_mean'], 
                    color='red', linewidth=3, label='Ensemble Mean')
        
        axes[0].set_title('CESM LENS Ensemble Uncertainty')
        axes[0].set_ylabel(f'{variable_name}')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Uncertainty evolution over time
        axes[1].plot(uncertainty_pd['time'], uncertainty_pd['ensemble_std'], 
                    color='purple', linewidth=2, label='Standard Deviation')
        axes[1].plot(uncertainty_pd['time'], uncertainty_pd['p975'] - uncertainty_pd['p025'], 
                    color='orange', linewidth=2, label='95% Range Width')
        axes[1].set_title('Uncertainty Evolution')
        axes[1].set_ylabel('Uncertainty Magnitude')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('uncertainty_analysis_polars.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Summary statistics
        mean_uncertainty = float(uncertainty_pd['ensemble_std'].mean())
        max_uncertainty = float(uncertainty_pd['ensemble_std'].max())
        range_95 = float((uncertainty_pd['p975'] - uncertainty_pd['p025']).mean())
        
        return f""" Uncertainty Analysis Complete (Polars-optimized):
 Average ensemble uncertainty (std): {mean_uncertainty:.3f} {variable_name}
 Maximum ensemble uncertainty: {max_uncertainty:.3f} {variable_name}
 Average 95% confidence range: {range_95:.3f} {variable_name}
 Analysis plots saved to: uncertainty_analysis_polars.png
 Efficient computation using Polars aggregations"""


class SaveCESMDataPathTool(BaseTool):
    """Save CESM data paths and metadata to SQLite database for tracking and reuse"""
    name: str = "save_cesm_data_path"
    description: str = "Save CESM data S3 path and metadata to database for tracking. Input: 'variable_name start_year end_year s3_path [additional_metadata]'"
    
    @property
    def db_path(self) -> str:
        return "cesm_data_registry.db"
    
    def _init_database(self):
        """Initialize SQLite database for CESM data tracking"""
        import sqlite3
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cesm_data_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    variable_name TEXT NOT NULL,
                    long_name TEXT,
                    units TEXT,
                    component TEXT,
                    experiment TEXT,
                    frequency TEXT,
                    start_year INTEGER,
                    end_year INTEGER,
                    ensemble_members TEXT,
                    s3_path TEXT NOT NULL,
                    file_size_gb REAL,
                    spatial_resolution TEXT,
                    temporal_resolution TEXT,
                    lat_range TEXT,
                    lon_range TEXT,
                    data_hash TEXT,
                    last_accessed TEXT,
                    access_count INTEGER DEFAULT 1,
                    load_time_seconds REAL,
                    memory_usage_gb REAL,
                    processing_notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(variable_name, start_year, end_year, s3_path)
                )
            """)
            
            # Create index for faster queries
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cesm_variable_time 
                ON cesm_data_paths(variable_name, start_year, end_year)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_cesm_s3_path 
                ON cesm_data_paths(s3_path)
            """)
    
    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Save CESM data path and metadata to database"""
        import sqlite3
        import json
        from datetime import datetime
        
        # Initialize database on first use
        self._init_database()
        
        try:
            # Parse input string
            parts = tool_input.strip().split()
            if len(parts) < 4:
                return " Error: Input must have at least 4 parts: 'variable_name start_year end_year s3_path [metadata]'"
            
            variable_name = parts[0]
            start_year = int(parts[1])
            end_year = int(parts[2])
            s3_path = parts[3]
            
            # Parse additional metadata if provided
            additional_metadata = {}
            if len(parts) > 4:
                try:
                    additional_metadata = json.loads(' '.join(parts[4:]))
                except:
                    # If not JSON, treat as simple key-value pairs
                    for i in range(4, len(parts), 2):
                        if i + 1 < len(parts):
                            additional_metadata[parts[i]] = parts[i + 1]
            
            print(f" Saving CESM data path for {variable_name} ({start_year}-{end_year})")
            
            # Get variable metadata from knowledge graph if available
            variable_metadata = self._get_variable_metadata(variable_name)
            
            # Extract metadata from current loaded data if available
            data_metadata = self._extract_current_data_metadata()
            
            # Determine experiment based on time range
            if start_year >= 1920 and end_year <= 2005:
                experiment = "20C"
            elif start_year >= 2006:
                experiment = "RCP85"
            elif start_year <= 2005 and end_year > 2005:
                experiment = "20C+RCP85"
            else:
                experiment = "HIST"
            
            # Prepare database record
            current_time = datetime.now().isoformat()
            
            record = {
                'variable_name': variable_name,
                'long_name': variable_metadata.get('long_name', additional_metadata.get('long_name', '')),
                'units': variable_metadata.get('units', additional_metadata.get('units', '')),
                'component': variable_metadata.get('component', additional_metadata.get('component', 'atm')),
                'experiment': experiment,
                'frequency': additional_metadata.get('frequency', 'monthly'),
                'start_year': start_year,
                'end_year': end_year,
                'ensemble_members': additional_metadata.get('ensemble_members', data_metadata.get('ensemble_members', 'all')),
                's3_path': s3_path,
                'file_size_gb': additional_metadata.get('file_size_gb', data_metadata.get('file_size_gb', 0.0)),
                'spatial_resolution': additional_metadata.get('spatial_resolution', '~1 degree'),
                'temporal_resolution': additional_metadata.get('temporal_resolution', 'monthly'),
                'lat_range': additional_metadata.get('lat_range', data_metadata.get('lat_range', 'global')),
                'lon_range': additional_metadata.get('lon_range', data_metadata.get('lon_range', 'global')),
                'data_hash': additional_metadata.get('data_hash', ''),
                'last_accessed': current_time,
                'load_time_seconds': additional_metadata.get('load_time', data_metadata.get('load_time', 0.0)),
                'memory_usage_gb': additional_metadata.get('memory_usage', data_metadata.get('memory_usage', 0.0)),
                'processing_notes': additional_metadata.get('notes', ''),
                'created_at': current_time,
                'updated_at': current_time
            }
            
            # Save to database
            with sqlite3.connect(self.db_path) as conn:
                # Check if record already exists
                cursor = conn.execute("""
                    SELECT id, access_count FROM cesm_data_paths 
                    WHERE variable_name = ? AND start_year = ? AND end_year = ? AND s3_path = ?
                """, (variable_name, start_year, end_year, s3_path))
                
                existing_record = cursor.fetchone()
                
                if existing_record:
                    # Update existing record
                    record_id, access_count = existing_record
                    record['access_count'] = access_count + 1
                    
                    conn.execute("""
                        UPDATE cesm_data_paths SET
                            long_name = ?, units = ?, component = ?, experiment = ?,
                            frequency = ?, ensemble_members = ?, file_size_gb = ?,
                            spatial_resolution = ?, temporal_resolution = ?, lat_range = ?,
                            lon_range = ?, data_hash = ?, last_accessed = ?, access_count = ?,
                            load_time_seconds = ?, memory_usage_gb = ?, processing_notes = ?,
                            updated_at = ?
                        WHERE id = ?
                    """, (
                        record['long_name'], record['units'], record['component'], record['experiment'],
                        record['frequency'], record['ensemble_members'], record['file_size_gb'],
                        record['spatial_resolution'], record['temporal_resolution'], record['lat_range'],
                        record['lon_range'], record['data_hash'], record['last_accessed'], record['access_count'],
                        record['load_time_seconds'], record['memory_usage_gb'], record['processing_notes'],
                        record['updated_at'], record_id
                    ))
                    
                    action = "updated"
                    record_id = record_id
                else:
                    # Insert new record
                    cursor = conn.execute("""
                        INSERT INTO cesm_data_paths (
                            variable_name, long_name, units, component, experiment, frequency,
                            start_year, end_year, ensemble_members, s3_path, file_size_gb,
                            spatial_resolution, temporal_resolution, lat_range, lon_range,
                            data_hash, last_accessed, access_count, load_time_seconds,
                            memory_usage_gb, processing_notes, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        record['variable_name'], record['long_name'], record['units'], record['component'],
                        record['experiment'], record['frequency'], record['start_year'], record['end_year'],
                        record['ensemble_members'], record['s3_path'], record['file_size_gb'],
                        record['spatial_resolution'], record['temporal_resolution'], record['lat_range'],
                        record['lon_range'], record['data_hash'], record['last_accessed'], 1,  # Set access_count to 1 for new records
                        record['load_time_seconds'], record['memory_usage_gb'], record['processing_notes'],
                        record['created_at'], record['updated_at']
                    ))
                    
                    action = "created"
                    record_id = cursor.lastrowid
            
            # Generate summary report
            output = f" CESM Data Path {action.capitalize()}\n"
            output += "=" * 40 + "\n\n"
            output += f" RECORD DETAILS:\n"
            output += f"   • Database ID: {record_id}\n"
            output += f"   • Variable: {record['variable_name']} ({record['long_name']})\n"
            output += f"   • Time Period: {record['start_year']}-{record['end_year']}\n"
            output += f"   • Experiment: {record['experiment']}\n"
            output += f"   • Component: {record['component']}\n"
            output += f"   • S3 Path: {record['s3_path']}\n\n"
            
            output += f" DATA CHARACTERISTICS:\n"
            output += f"   • Ensemble Members: {record['ensemble_members']}\n"
            output += f"   • Spatial Resolution: {record['spatial_resolution']}\n"
            output += f"   • Temporal Resolution: {record['temporal_resolution']}\n"
            output += f"   • Spatial Domain: {record['lat_range']} × {record['lon_range']}\n"
            output += f"   • Units: {record['units']}\n\n"
            
            if record['file_size_gb'] > 0:
                output += f" PERFORMANCE METRICS:\n"
                output += f"   • File Size: {record['file_size_gb']:.2f} GB\n"
                if record['load_time_seconds'] > 0:
                    output += f"   • Load Time: {record['load_time_seconds']:.1f} seconds\n"
                if record['memory_usage_gb'] > 0:
                    output += f"   • Memory Usage: {record['memory_usage_gb']:.2f} GB\n"
                output += f"   • Access Count: {record['access_count']}\n\n"
            
            output += f"⏰ TIMESTAMPS:\n"
            output += f"   • Created: {record['created_at']}\n"
            output += f"   • Last Accessed: {record['last_accessed']}\n"
            
            if record['processing_notes']:
                output += f"\n NOTES:\n   {record['processing_notes']}\n"
            
            output += f"\n Record saved to database: {self.db_path}"
            
            return output
            
        except Exception as e:
            return f" Error saving CESM data path: {str(e)}"
    
    def _get_variable_metadata(self, variable_name: str) -> dict:
        """Get variable metadata from knowledge graph"""
        try:
            cesm_check_query = f"""
            MATCH (v:CESMVariable)
            WHERE v.name = '{variable_name}' OR v.`~id` CONTAINS '{variable_name}'
            RETURN v.name as variable_name, v.long_name as long_name, 
                   v.units as units, v.component as component
            LIMIT 1
            """
            
            result = kg_connector.execute_query(cesm_check_query)
            
            if result.get("results"):
                return result["results"][0]
            else:
                return {}
                
        except Exception as e:
            print(f" Could not get variable metadata: {e}")
            return {}
    
    def _extract_current_data_metadata(self) -> dict:
        """Extract metadata from currently loaded data if available"""
        metadata = {}
        
        try:
            # Check if we have currently loaded CESM data
            if 'cesm_data' in globals():
                dataset = globals()['cesm_data']
                
                # Calculate size
                if hasattr(dataset, 'nbytes'):
                    metadata['file_size_gb'] = dataset.nbytes / 1e9
                
                # Get spatial information
                if 'lat' in dataset.coords and 'lon' in dataset.coords:
                    lat_min, lat_max = float(dataset.lat.min()), float(dataset.lat.max())
                    lon_min, lon_max = float(dataset.lon.min()), float(dataset.lon.max())
                    metadata['lat_range'] = f"{lat_min:.1f},{lat_max:.1f}"
                    metadata['lon_range'] = f"{lon_min:.1f},{lon_max:.1f}"
                
                # Get ensemble information
                if 'member_id' in dataset.dims:
                    n_members = dataset.sizes['member_id']
                    metadata['ensemble_members'] = f"1-{n_members}"
            
            # Check if we have the polars dataframe
            if 'cesm_df' in globals():
                df = globals()['cesm_df']
                metadata['memory_usage'] = df.estimated_size() / 1e9
                
        except Exception as e:
            print(f" Could not extract current data metadata: {e}")
        
        return metadata
    
    def get_saved_paths(self, variable_name: Optional[str] = None, 
                       start_year: Optional[int] = None, 
                       end_year: Optional[int] = None) -> list:
        """Retrieve saved CESM data paths from database"""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM cesm_data_paths WHERE 1=1"
                params = []
                
                if variable_name:
                    query += " AND variable_name = ?"
                    params.append(variable_name)
                
                if start_year:
                    query += " AND start_year >= ?"
                    params.append(start_year)
                
                if end_year:
                    query += " AND end_year <= ?"
                    params.append(end_year)
                
                query += " ORDER BY created_at DESC"
                
                cursor = conn.execute(query, params)
                columns = [description[0] for description in cursor.description]
                
                results = []
                for row in cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                
                return results
                
        except Exception as e:
            print(f" Error retrieving saved paths: {e}")
            return []

class RunCESMSimulationFromObsTool(BaseTool):
    """Run CESM simulations using variables from observational datasets"""
    name: str = "run_cesm_simulation_from_obs"
    description: str = "Run CESM LENS simulations using variables found in observational datasets. Input: 'dataset_id variable_name start_year end_year [analysis_type]'. This tool finds observational data, maps to CESM variables, runs simulation, and compares results."
    
    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Run CESM simulation based on observational dataset variables"""
        
        try:
            # Parse input
            parts = tool_input.strip().split()
            if len(parts) < 4:
                return " Error: Input must have at least 4 parts: 'dataset_id variable_name start_year end_year [analysis_type]'. Example: 'dataset_GGD222_756 TREFHT 1990 2010 ensemble_mean'"
            
            dataset_id = parts[0]
            variable_name = parts[1]
            start_year = int(parts[2])
            end_year = int(parts[3])
            analysis_type = parts[4] if len(parts) > 4 else "ensemble_mean"
            
            print(f" Running CESM simulation from observational dataset: {dataset_id}")
            print(f" Variable: {variable_name}, Period: {start_year}-{end_year}")
            
            # Step 1: Query observational dataset information from Knowledge Graph
            obs_dataset_info = self._get_observational_dataset_info(dataset_id)
            if not obs_dataset_info:
                return f" Observational dataset {dataset_id} not found in Knowledge Graph"
            
            # Step 2: Use the variable name directly - if it's not a valid CESM variable, the simulation will fail gracefully
            # This is much simpler and more reliable than trying to guess mappings
            
            # Step 3: Run CESM LENS simulation directly with the requested variable
            cesm_simulation_result = self._run_cesm_simulation(
                variable_name,  # Use as-is - let CESM validation handle it
                start_year, end_year, 
                obs_dataset_info  # Pass full dataset info instead of "characteristics"
            )
            
            if not cesm_simulation_result['success']:
                return f" CESM simulation failed: {cesm_simulation_result['error']}"
            
            # Step 4: Perform analysis
            analysis_result = self._perform_simulation_analysis(analysis_type, variable_name)
            
            # Step 5: Generate simple, useful report
            return self._generate_simple_report(
                dataset_id, variable_name, start_year, end_year,
                obs_dataset_info, cesm_simulation_result, analysis_result
            )
            
        except Exception as e:
            return f" Error running CESM simulation from observations: {str(e)}"
    
    def _get_observational_dataset_info(self, dataset_id: str) -> dict:
        """Get observational dataset information from both Knowledge Graph and SQLite database"""
        try:
            dataset_info = {
                'dataset_id': dataset_id,
                'properties': {},
                'variables': [],
                'cesm_variables': [],
                'locations': [],
                'temporal_extent': {},
                'organizations': [],
                'platforms': [],
                'source': 'unknown'
            }
            
            # First, try to get from SQLite database (stored by Knowledge Graph agent)
            sqlite_info = self._get_from_sqlite_db(dataset_id)
            if sqlite_info:
                print(f" Found dataset in SQLite database: {dataset_id}")
                dataset_info.update(sqlite_info)
                dataset_info['source'] = 'sqlite'
                return dataset_info
            
            # If not in SQLite, query Knowledge Graph directly
            print(f" Querying Knowledge Graph directly for: {dataset_id}")
            kg_info = self._get_from_knowledge_graph(dataset_id)
            if kg_info:
                dataset_info.update(kg_info)
                dataset_info['source'] = 'knowledge_graph'
                return dataset_info
            
            print(f" Dataset {dataset_id} not found in either SQLite or Knowledge Graph")
            return {}
            
        except Exception as e:
            print(f" Error getting observational dataset info: {e}")
            return {}
    
    def _get_from_sqlite_db(self, dataset_id: str) -> dict:
        """Get dataset info from SQLite database (stored by Knowledge Graph agent)"""
        try:
            import sqlite3
            import json
            
            db_path = "climate_knowledge_graph.db"
            
            with sqlite3.connect(db_path) as conn:
                # Get dataset basic info
                cursor = conn.execute("""
                    SELECT title, short_name, dataset_properties, dataset_labels
                    FROM stored_datasets WHERE dataset_id = ?
                """, (dataset_id,))
                
                dataset_row = cursor.fetchone()
                if not dataset_row:
                    return {}
                
                title, short_name, dataset_props_json, dataset_labels_json = dataset_row
                
                # Parse JSON properties
                try:
                    dataset_properties = json.loads(dataset_props_json) if dataset_props_json else {}
                    dataset_labels = json.loads(dataset_labels_json) if dataset_labels_json else []
                except:
                    dataset_properties = {}
                    dataset_labels = []
                
                # Get relationships, specifically looking for CESM variables
                cursor = conn.execute("""
                    SELECT relationship_type, connected_id, connected_labels, connected_properties
                    FROM dataset_relationships WHERE dataset_id = ?
                """, (dataset_id,))
                
                relationships = cursor.fetchall()
                
                # Process relationships
                cesm_variables = []
                variables = []
                locations = []
                organizations = []
                platforms = []
                temporal_extent = {}
                
                for rel_type, connected_id, connected_labels_json, connected_props_json in relationships:
                    try:
                        connected_labels = json.loads(connected_labels_json) if connected_labels_json else []
                        connected_props = json.loads(connected_props_json) if connected_props_json else {}
                    except:
                        connected_labels = []
                        connected_props = {}
                    
                    # Categorize relationships
                    if rel_type == "hasCESMVariable" or "CESMVariable" in connected_labels:
                        cesm_variables.append({
                            'id': connected_id,
                            'labels': connected_labels,
                            'properties': connected_props
                        })
                    elif "Variable" in connected_labels:
                        variables.append({
                            'id': connected_id,
                            'labels': connected_labels,
                            'properties': connected_props
                        })
                    elif "Location" in connected_labels:
                        locations.append(connected_props)
                    elif "TemporalExtent" in connected_labels:
                        temporal_extent = connected_props
                    elif "organization" in connected_labels:
                        organizations.append(connected_props)
                    elif "platform" in connected_labels:
                        platforms.append(connected_props)
                
                return {
                    'properties': dataset_properties,
                    'labels': dataset_labels,
                    'variables': variables,
                    'cesm_variables': cesm_variables,  # This is the key addition!
                    'locations': locations,
                    'temporal_extent': temporal_extent,
                    'organizations': organizations,
                    'platforms': platforms
                }
                
        except Exception as e:
            print(f" Error querying SQLite database: {e}")
            return {}
    
    def _get_from_knowledge_graph(self, dataset_id: str) -> dict:
        """Get dataset info directly from Knowledge Graph"""
        try:
            # Query for dataset properties and relationships
            dataset_query = f"""
            MATCH (d:Dataset)-[r]-(connected)
            WHERE d.`~id` = '{dataset_id}'
            RETURN 
                d as dataset,
                type(r) as relationship_type,
                labels(connected) as connected_labels,
                connected as connected_node
            """
            
            result = kg_connector.execute_query(dataset_query)
            
            if not result.get("results"):
                return {}
            
            # Process results
            variables = []
            cesm_variables = []
            locations = []
            temporal_extent = {}
            organizations = []
            platforms = []
            properties = {}
            
            for res in result["results"]:
                rel_type = res.get("relationship_type", "")
                connected_labels = res.get("connected_labels", [])
                connected_node = res.get("connected_node", {})
                
                # Extract dataset properties
                if res.get("dataset"):
                    properties = res["dataset"]
                
                # Extract connected information
                if rel_type == "hasCESMVariable" or "CESMVariable" in connected_labels:
                    cesm_variables.append(connected_node)
                elif "Variable" in connected_labels:
                    variables.append(connected_node)
                elif "Location" in connected_labels:
                    locations.append(connected_node)
                elif "TemporalExtent" in connected_labels:
                    temporal_extent = connected_node
                elif "organization" in connected_labels:
                    organizations.append(connected_node)
                elif "platform" in connected_labels:
                    platforms.append(connected_node)
            
            return {
                'properties': properties,
                'variables': variables,
                'cesm_variables': cesm_variables,  # This is the key addition!
                'locations': locations,
                'temporal_extent': temporal_extent,
                'organizations': organizations,
                'platforms': platforms
            }
            
        except Exception as e:
            print(f" Error querying Knowledge Graph: {e}")
            return {}
    

    
    def _run_cesm_simulation(self, variable_name: str, start_year: int, end_year: int, obs_dataset_info: dict) -> dict:
        """Run CESM LENS simulation - simple and direct"""
        try:
            print(f" Running CESM LENS simulation for {variable_name}")
            
            # Use the existing CESM LENS data tool - it already handles validation
            cesm_tool = CESMLENSDataTool()
            
            # Simple tool input - let the CESM tool handle everything
            tool_input = f"{variable_name} {start_year} {end_year} all"
            
            # Run the simulation
            result = cesm_tool._run(tool_input)
            
            if " CESM LENS DATA LOADING COMPLETE" in result:
                return {
                    'success': True,
                    'result': result,
                    'variable_name': variable_name
                }
            else:
                return {
                    'success': False,
                    'error': result,
                    'variable_name': variable_name
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'variable_name': variable_name
            }
    
    def _perform_simulation_analysis(self, analysis_type: str, variable_name: str) -> dict:
        """Perform the requested analysis on the CESM simulation"""
        try:
            print(f" Performing {analysis_type} analysis on CESM simulation")
            
            # Use the existing ensemble analysis tool
            analysis_tool = CESMEnsembleAnalysisTool()
            
            # Run the analysis
            result = analysis_tool._run(analysis_type)
            
            return {
                'success': True,
                'analysis_type': analysis_type,
                'result': result,
                'plots_generated': 'png' in result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_type': analysis_type
            }
    

    
    def _generate_simple_report(self, dataset_id: str, variable_name: str, start_year: int, end_year: int,
                               obs_dataset_info: dict, cesm_result: dict, analysis_result: dict) -> str:
        """Generate simple, useful report without over-engineering"""
        
        report = f" CESM SIMULATION FROM OBSERVATIONAL DATASET\n"
        report += "=" * 60 + "\n\n"
        
        # Basic info
        obs_props = obs_dataset_info.get('properties', {})
        report += f" SIMULATION OVERVIEW:\n"
        report += f"   • Source Dataset: {dataset_id}\n"
        report += f"   • Dataset Title: {obs_props.get('title', 'Unknown')}\n"
        report += f"   • Variable Requested: {variable_name}\n"
        report += f"   • Simulation Period: {start_year}-{end_year}\n"
        report += f"   • Analysis Type: {analysis_result.get('analysis_type', 'N/A')}\n"
        report += f"   • Data Source: {obs_dataset_info.get('source', 'unknown')}\n\n"
        
        # Show CESM variables found in the dataset
        cesm_variables = obs_dataset_info.get('cesm_variables', [])
        if cesm_variables:
            report += f" CESM VARIABLES FOUND IN DATASET:\n"
            for i, cesm_var in enumerate(cesm_variables[:5], 1):  # Show first 5
                var_props = cesm_var.get('properties', {})
                var_name = var_props.get('name', var_props.get('cesm_name', 'unknown'))
                var_long_name = var_props.get('long_name', 'No description')
                report += f"   {i}. {var_name} - {var_long_name}\n"
            
            if len(cesm_variables) > 5:
                report += f"   ... and {len(cesm_variables) - 5} more CESM variables\n"
            report += "\n"
        
        # CESM Simulation Results
        report += f" CESM LENS SIMULATION:\n"
        if cesm_result.get('success'):
            report += f"    Status: SUCCESS\n"
            report += f"   • Variable: {cesm_result.get('variable_name', 'N/A')}\n"
            report += f"   • Data Available: Global variables 'cesm_data' and 'cesm_df'\n"
        else:
            report += f"    Status: FAILED\n"
            report += f"   • Error: {cesm_result.get('error', 'Unknown error')}\n"
            
            # If simulation failed but we have CESM variables, suggest alternatives
            if cesm_variables:
                report += f"    Try these CESM variables from the dataset instead:\n"
                for cesm_var in cesm_variables[:3]:
                    var_props = cesm_var.get('properties', {})
                    var_name = var_props.get('name', var_props.get('cesm_name', 'unknown'))
                    report += f"      • {var_name}\n"
        report += "\n"
        
        # Analysis Results
        report += f" ANALYSIS RESULTS:\n"
        if analysis_result.get('success'):
            report += f"    Analysis Status: SUCCESS\n"
            report += f"   • Type: {analysis_result.get('analysis_type', 'N/A')}\n"
            if analysis_result.get('plots_generated'):
                report += f"   • Plots Generated: Yes (PNG files saved)\n"
        else:
            report += f"    Analysis Status: FAILED\n"
            report += f"   • Error: {analysis_result.get('error', 'Unknown error')}\n"
        
        report += f"\n SUMMARY:\n"
        if cesm_result.get('success') and analysis_result.get('success'):
            report += f"    Successfully ran CESM LENS simulation and analysis\n"
            report += f"    Data ready for comparison with observational dataset\n"
        else:
            report += f"    Check error messages above and verify variable name\n"
            if cesm_variables:
                report += f"    Dataset contains {len(cesm_variables)} CESM variables for alternative simulations\n"
        
        return report


class SearchSavedCESMPathsTool(BaseTool):
    """Search and retrieve saved CESM data paths from database"""
    name: str = "search_saved_cesm_paths"
    description: str = "Search for previously saved CESM data paths in database. Input: 'variable_name [start_year] [end_year]' or 'all' to list all saved paths"
    
    def _run(self, search_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Search for saved CESM data paths"""
        
        try:
            # Initialize database if it doesn't exist
            _init_cesm_database()
            
            # Create save tool instance for database access
            save_tool = SaveCESMDataPathTool()
            
            # Parse search query
            parts = search_query.strip().split()
            
            if not parts or parts[0].lower() == 'all':
                # Show all saved paths
                saved_paths = save_tool.get_saved_paths()
                variable_filter = None
                start_year_filter = None
                end_year_filter = None
            else:
                variable_filter = parts[0] if parts[0].lower() != 'all' else None
                start_year_filter = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                end_year_filter = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
                
                # Search with filters
                saved_paths = save_tool.get_saved_paths(
                    variable_name=variable_filter,
                    start_year=start_year_filter,
                    end_year=end_year_filter
                )
            
            if not saved_paths:
                return f" No saved CESM data paths found for query: '{search_query}'"
            
            # Format results
            output = f" SAVED CESM DATA PATHS SEARCH RESULTS\n"
            output += "=" * 50 + "\n\n"
            output += f" Found {len(saved_paths)} saved path(s)\n\n"
            
            for i, path_record in enumerate(saved_paths, 1):
                output += f"{i}. {path_record['variable_name']} ({path_record['start_year']}-{path_record['end_year']})\n"
                output += f"    Description: {path_record['long_name']}\n"
                output += f"    Component: {path_record['component']} | Experiment: {path_record['experiment']}\n"
                output += f"    S3 Path: {path_record['s3_path']}\n"
                output += f"    Size: {path_record['file_size_gb']:.2f} GB | Members: {path_record['ensemble_members']}\n"
                output += f"    Domain: {path_record['lat_range']} × {path_record['lon_range']}\n"
                output += f"   ⏰ Last Accessed: {path_record['last_accessed']} | Access Count: {path_record['access_count']}\n"
                
                if path_record['load_time_seconds'] and path_record['load_time_seconds'] > 0:
                    output += f"    Load Time: {path_record['load_time_seconds']:.1f}s"
                    if path_record['memory_usage_gb'] and path_record['memory_usage_gb'] > 0:
                        output += f" | Memory: {path_record['memory_usage_gb']:.2f} GB"
                    output += "\n"
                
                if path_record['processing_notes']:
                    output += f"    Notes: {path_record['processing_notes']}\n"
                
                output += f"    Database ID: {path_record['id']}\n\n"
            
            # Summary statistics
            total_size = sum(p['file_size_gb'] for p in saved_paths if p['file_size_gb'])
            unique_variables = len(set(p['variable_name'] for p in saved_paths))
            unique_experiments = len(set(p['experiment'] for p in saved_paths))
            total_accesses = sum(p['access_count'] for p in saved_paths if p['access_count'])
            
            output += f" SUMMARY STATISTICS:\n"
            output += f"   • Total Data Size: {total_size:.2f} GB\n"
            output += f"   • Unique Variables: {unique_variables}\n"
            output += f"   • Unique Experiments: {unique_experiments}\n"
            output += f"   • Total Accesses: {total_accesses}\n"
            
            # Most accessed datasets
            sorted_by_access = sorted(saved_paths, key=lambda x: x['access_count'] or 0, reverse=True)
            if sorted_by_access and sorted_by_access[0]['access_count'] > 1:
                output += f"\n MOST ACCESSED:\n"
                for i, path in enumerate(sorted_by_access[:3], 1):
                    if path['access_count'] > 1:
                        output += f"   {i}. {path['variable_name']} ({path['start_year']}-{path['end_year']}) - {path['access_count']} accesses\n"
            
            return output
            
        except Exception as e:
            return f" Error searching saved CESM paths: {str(e)}"

# --- Create LangChain Agent ---


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
    """Download data directly from S3 or URL and save to local file in one step with optional spatial/temporal subsetting"""
    name: str = "download_and_save_data"
    description: str = "Download data directly from S3 URL or other data sources and save to local file immediately. Supports spatial and temporal subsetting for CESM data. Format: 'source_type:S3 url:[s3_path] filename:data.nc lat_range:30,60 lon_range:-120,-60 start_year:2000 end_year:2010 ensemble:1,2,3' OR 'source_type:URL url:[http_url] filename:data.csv'. Use for downloading CESM LENS data or other climate datasets."

    def _run(self, download_params: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import pandas as pd
            import requests
            from datetime import datetime
            import os
            import xarray as xr
            import numpy as np
            
            output = f"⬇️ DOWNLOAD AND SAVE DATA\n"
            output += "=" * 40 + "\n\n"
            
            # Parse parameters
            params = {}
            for param in download_params.split():
                if ':' in param:
                    key, value = param.split(':', 1)
                    params[key] = value
            
            source_type = params.get('source_type', 'S3').upper()
            filename = params.get('filename', 'climate_data.nc')
            
            # Parse spatial and temporal subsetting parameters
            lat_range = None
            lon_range = None
            start_year = None
            end_year = None
            ensemble_members = None
            
            if 'lat_range' in params:
                try:
                    lat_parts = params['lat_range'].split(',')
                    if len(lat_parts) == 2:
                        lat_range = (float(lat_parts[0]), float(lat_parts[1]))
                        output += f"🌍 Latitude range: {lat_range[0]}° to {lat_range[1]}°\n"
                except ValueError:
                    output += f"⚠️ Invalid lat_range format: {params['lat_range']}\n"
            
            if 'lon_range' in params:
                try:
                    lon_parts = params['lon_range'].split(',')
                    if len(lon_parts) == 2:
                        lon_range = (float(lon_parts[0]), float(lon_parts[1]))
                        output += f"🌍 Longitude range: {lon_range[0]}° to {lon_range[1]}°\n"
                except ValueError:
                    output += f"⚠️ Invalid lon_range format: {params['lon_range']}\n"
            
            if 'start_year' in params:
                try:
                    start_year = int(params['start_year'])
                    output += f"📅 Start year: {start_year}\n"
                except ValueError:
                    output += f"⚠️ Invalid start_year: {params['start_year']}\n"
            
            if 'end_year' in params:
                try:
                    end_year = int(params['end_year'])
                    output += f"📅 End year: {end_year}\n"
                except ValueError:
                    output += f"⚠️ Invalid end_year: {params['end_year']}\n"
            
            if 'ensemble' in params:
                ensemble_members = params['ensemble']
                output += f"🎯 Ensemble members: {ensemble_members}\n"
            
            output += f"📡 Source: {source_type}\n"
            output += f"💾 Target file: {filename}\n\n"
            
            if source_type == 'S3':
                url = params.get('url', '')
                if url:
                    try:
                        # Use S3FS for direct S3 access
                        import s3fs
                        fs = s3fs.S3FileSystem(anon=True)
                        
                        output += f"📥 Downloading from S3: {url}\n"
                        
                        # Remove s3:// prefix if present
                        s3_path = url.replace('s3://', '')
                        
                        # Check if subsetting is needed and file is netCDF/zarr
                        apply_subsetting = (lat_range or lon_range or start_year or end_year or ensemble_members) and \
                                         (filename.endswith('.nc') or '.zarr' in s3_path)
                        
                        if apply_subsetting:
                            output += f"🔧 Applying spatial/temporal subsetting during download\n"
                            
                            # Open dataset directly from S3 with xarray
                            if '.zarr' in s3_path:
                                ds = xr.open_zarr(fs.get_mapper(s3_path))
                            else:
                                ds = xr.open_dataset(fs.open(s3_path))
                            
                            output += f"📊 Original dataset shape: {dict(ds.sizes)}\n"
                            
                            # Apply temporal subsetting
                            if start_year and end_year and 'time' in ds.coords:
                                try:
                                    time_mask = (ds.time.dt.year >= start_year) & (ds.time.dt.year <= end_year)
                                    ds = ds.sel(time=time_mask)
                                    output += f"⏰ Temporal subset: {start_year}-{end_year}\n"
                                except Exception as temporal_error:
                                    output += f"⚠️ Temporal subsetting failed: {temporal_error}\n"
                            
                            # Apply spatial subsetting (using same logic as load_cesm_data_efficient)
                            if lat_range and 'lat' in ds.coords:
                                lat_mask = (ds.lat >= lat_range[0]) & (ds.lat <= lat_range[1])
                                if lat_mask.sum() > 0:
                                    ds = ds.where(lat_mask, drop=True)
                                    output += f"🌍 Latitude subset: {lat_range[0]} to {lat_range[1]} ({lat_mask.sum().values} points)\n"
                                else:
                                    output += f"⚠️ No latitude points found in range {lat_range[0]} to {lat_range[1]}\n"
                            
                            if lon_range and 'lon' in ds.coords:
                                # Handle longitude wrapping (e.g., -180 to 180 vs 0 to 360)
                                lon_coords = ds.lon.values
                                if lon_range[0] < 0 and lon_coords.max() > 180:
                                    # Convert longitude range to 0-360 if dataset uses 0-360
                                    lon_range = (lon_range[0] + 360, lon_range[1] + 360)
                                
                                lon_mask = (ds.lon >= lon_range[0]) & (ds.lon <= lon_range[1])
                                if lon_mask.sum() > 0:
                                    ds = ds.where(lon_mask, drop=True)
                                    output += f"🌍 Longitude subset: {lon_range[0]} to {lon_range[1]} ({lon_mask.sum().values} points)\n"
                                else:
                                    output += f"⚠️ No longitude points found in range {lon_range[0]} to {lon_range[1]}\n"
                                    # Try to find closest points instead
                                    closest_lon_idx = np.argmin(np.abs(lon_coords.reshape(-1, 1) - np.array(lon_range).reshape(1, -1)), axis=0)
                                    if len(closest_lon_idx) >= 2:
                                        lon_start, lon_end = sorted(closest_lon_idx)
                                        ds = ds.isel(lon=slice(lon_start, lon_end+1))
                                        output += f"🌍 Using closest longitude points: indices {lon_start} to {lon_end}\n"
                            
                            # Apply ensemble member selection
                            if ensemble_members and 'member_id' in ds.coords:
                                try:
                                    if ensemble_members.lower() != 'all':
                                        if ',' in ensemble_members:
                                            member_list = [int(m.strip()) for m in ensemble_members.split(',')]
                                            ds = ds.sel(member_id=member_list)
                                            output += f"🎯 Selected ensemble members: {member_list}\n"
                                        else:
                                            member_num = int(ensemble_members)
                                            ds = ds.sel(member_id=member_num)
                                            output += f"🎯 Selected ensemble member: {member_num}\n"
                                except Exception as ensemble_error:
                                    output += f"⚠️ Ensemble selection failed: {ensemble_error}\n"
                            
                            output += f"📊 Subsetted dataset shape: {dict(ds.sizes)}\n"
                            
                            # Save subsetted dataset
                            ds.to_netcdf(filename)
                            ds.close()
                            
                        else:
                            # Download directly without subsetting
                            fs.download(s3_path, filename)
                        
                        # Verify download
                        if os.path.exists(filename):
                            file_size = os.path.getsize(filename)
                            output += f"✅ Successfully downloaded {file_size} bytes\n"
                            output += f"📁 File saved: {filename}\n"
                        else:
                            output += f"❌ File was not created: {filename}\n"
                            
                    except Exception as e:
                        output += f"❌ S3 download error: {str(e)}\n"
                else:
                    output += f"❌ No S3 URL provided\n"
                    
            elif source_type == 'URL' or source_type == 'HTTP':
                url = params.get('url', '')
                if url:
                    try:
                        output += f"📥 Downloading from URL: {url}\n"
                        
                        # Download using requests
                        response = requests.get(url, stream=True, timeout=30)
                        response.raise_for_status()
                        
                        # Save to file
                        with open(filename, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        
                        # Verify download
                        if os.path.exists(filename):
                            file_size = os.path.getsize(filename)
                            output += f"✅ Successfully downloaded {file_size} bytes\n"
                            output += f"📁 File saved: {filename}\n"
                        else:
                            output += f"❌ File was not created: {filename}\n"
                            
                    except Exception as e:
                        output += f"❌ URL download error: {str(e)}\n"
                else:
                    output += f"❌ No URL provided\n"
            
            else:
                output += f"❌ Unsupported source type: {source_type}\n"
                output += f"💡 Supported: S3, URL, HTTP\n"
            
            # Final file verification
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                output += f"🎯 File verification: {filename} ({file_size} bytes)\n"
                output += f"✅ Data successfully downloaded and saved!\n"
                output += f"\n✅ Data loaded successfully and ready for analysis!\n"
                
                # If it's a netCDF file, show basic info
                if filename.endswith('.nc'):
                    try:
                        ds_info = xr.open_dataset(filename)
                        output += f"📊 Dataset info: {dict(ds_info.sizes)}\n"
                        if hasattr(ds_info, 'data_vars'):
                            output += f"📈 Variables: {list(ds_info.data_vars.keys())}\n"
                        ds_info.close()
                    except Exception:
                        pass
            else:
                output += f"❌ Download failed - file not found: {filename}\n"
                
            return output
            
        except Exception as e:
            return f"❌ Download and save error: {str(e)}"

class LocationToCoordinatesTool(BaseTool):
    """Convert location names (city, state, country, continent) to latitude/longitude coordinates for spatial subsetting"""
    name: str = "location_to_coordinates"
    description: str = "Convert location names to lat/lon coordinates for spatial subsetting. Input: 'location_name' (e.g., 'Texas', 'New York City', 'United States', 'Europe', 'Amazon Basin'). Returns latitude and longitude ranges suitable for spatial subsetting of climate data."
    
    def _run(self, location_name: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            import requests
            global last_location_lookup
            
            output = f"🌍 LOCATION TO COORDINATES\n"
            output += "=" * 40 + "\n\n"
            output += f"📍 Looking up: {location_name}\n\n"
            
            # Use Nominatim (OpenStreetMap) geocoding API
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': location_name,
                'format': 'json',
                'limit': 1,
                'extratags': 1,
                'addressdetails': 1
            }
            headers = {'User-Agent': 'ClimateKGAgent/1.0'}
            
            response = requests.get(nominatim_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if not data:
                return f"❌ No location found for: {location_name}\n💡 Try a more specific location name or check spelling"
            
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            display_name = result.get('display_name', location_name)
            
            output += f"✅ Found: {display_name}\n"
            output += f"📍 Center coordinates: {lat:.4f}°, {lon:.4f}°\n"
            
            # Get bounding box if available
            if 'boundingbox' in result:
                bbox = result['boundingbox']
                # boundingbox format: [south, north, west, east]
                south, north, west, east = [float(x) for x in bbox]
                
                output += f"🗺️ Bounding box:\n"
                output += f"   • Latitude: {south:.4f}° to {north:.4f}°\n"
                output += f"   • Longitude: {west:.4f}° to {east:.4f}°\n"
                
                output += f"\n📊 SPATIAL SUBSETTING PARAMETERS:\n"
                output += f"   • For CESM data queries: '{south:.2f},{north:.2f} {west:.2f},{east:.2f}'\n"
                output += f"   • For download tool: 'lat_range:{south:.2f},{north:.2f} lon_range:{west:.2f},{east:.2f}'\n"
                
                # Store coordinates globally for other tools to access
                last_location_lookup = {
                    'location_name': location_name,
                    'center': (lat, lon),
                    'lat_range': (south, north),
                    'lon_range': (west, east)
                }
                
            else:
                # If no bounding box, create a small area around the point
                buffer = 0.5  # 0.5 degree buffer around point
                south, north = lat - buffer, lat + buffer
                west, east = lon - buffer, lon + buffer
                
                output += f"🗺️ Point location (with 0.5° buffer):\n"
                output += f"   • Latitude: {south:.4f}° to {north:.4f}°\n"
                output += f"   • Longitude: {west:.4f}° to {east:.4f}°\n"
                
                output += f"\n📊 SPATIAL SUBSETTING PARAMETERS:\n"
                output += f"   • For CESM data queries: '{south:.2f},{north:.2f} {west:.2f},{east:.2f}'\n"
                output += f"   • For download tool: 'lat_range:{south:.2f},{north:.2f} lon_range:{west:.2f},{east:.2f}'\n"
                
                last_location_lookup = {
                    'location_name': location_name,
                    'center': (lat, lon),
                    'lat_range': (south, north),
                    'lon_range': (west, east)
                }
            
            output += f"\n✅ Location data ready for spatial subsetting!\n"
            output += f"💡 Use these coordinates with query_cesm_lens_data or download_and_save_data\n"
            
            return output
            
        except Exception as e:
            return f"❌ Location lookup error: {str(e)}"

class SmartCESMVariableSelectionTool(BaseTool):
    """Use knowledge graph to find the most suitable CESM variables by searching datasets by category, then finding connected CESM variables"""
    name: str = "smart_cesm_variable_selection"
    description: str = "Find CESM variables by first searching for observational datasets, then discovering their CESM variable relationships. IMPORTANT: Frame your question as if you're searching for observational datasets that measure your phenomenon of interest (e.g., 'observational precipitation datasets for flooding', 'satellite temperature datasets for warming trends', 'weather station data for extreme events'). The tool will find observational datasets, then iteratively discover which CESM variables are related to those observational measurements until a working CESM variable is found."

    def _run(self, research_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Import the knowledge graph connector from the other agent
            import sys
            import os

            # Add the path to import the knowledge graph agent
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.append(current_dir)

            try:
                from knowledge_graph_agent_bedrock import kg_connector
            except ImportError:
                return f"❌ Knowledge graph not available. Please ensure knowledge_graph_agent_bedrock.py is accessible."

            output = f"🧠 SMART CESM VARIABLE SELECTION\n"
            output += "=" * 50 + "\n\n"
            output += f"🔍 Research Query: {research_description}\n\n"
            output += f"📋 **STRATEGY**: Finding CESM variables through observational dataset relationships\n"
            output += f"   1. Search for observational datasets that measure your phenomenon\n"
            output += f"   2. Identify CESM variables connected to those observational datasets\n"
            output += f"   3. Iteratively query until working CESM variables are found\n\n"

            # Step 1: Search for observational datasets first, then find CESM variable connections
            output += f"📊 Step 1: Searching for observational datasets that measure your phenomenon...\n"

            category_results = kg_connector.vector_search_by_type(research_description, "DataCategory", 5)

            if not category_results:
                output += f"❌ No relevant data categories found for '{research_description}'.\n"
                output += f"💡 Try describing your research using climate-related terms (temperature, precipitation, wind, etc.)\n"
                return output

            output += f"✅ Found {len(category_results)} relevant data categories:\n"
            for i, category in enumerate(category_results, 1):
                cat_id = category.get('~id', 'unknown')
                summary = category.get('summary', 'No summary available')
                summary_short = summary[:120] + "..." if len(summary) > 120 else summary
                output += f"   {i}. Category {cat_id}: {summary_short}\n"
            output += "\n"

            # Step 2: Find observational datasets connected to these categories
            output += f"📋 Step 2: Finding observational datasets connected to these categories...\n"

            all_datasets = set()
            for category in category_results:
                cat_id = category.get('~id', '')
                if cat_id:
                    # Query to find datasets connected to this category
                    dataset_query = f"""
                    MATCH (d:Dataset)-[:hasDataCategory]->(c:DataCategory)
                    WHERE c.`~id` = '{cat_id}'
                    RETURN d.`~id` as dataset_id, d.title as dataset_title
                    LIMIT 10
                    """

                    dataset_result = kg_connector.execute_query(dataset_query)
                    if dataset_result.get("results"):
                        for ds in dataset_result["results"]:
                            dataset_id = ds.get('dataset_id', '')
                            if dataset_id:
                                all_datasets.add(dataset_id)

            if not all_datasets:
                output += f"❌ No datasets found connected to the relevant data categories.\n"
                return output

            output += f"✅ Found {len(all_datasets)} connected datasets\n\n"

            # Step 3: Find CESM variables connected to these observational datasets
            output += f"🔗 Step 3: Mapping observational datasets to their connected CESM variables...\n"

            cesm_variables = []
            for dataset_id in list(all_datasets)[:20]:  # Limit to first 20 datasets to avoid overwhelming output
                # Query to find CESM variables connected to this dataset
                cesm_query = f"""
                MATCH (d:Dataset)-[:hasCESMVariable]->(v:CESMVariable)
                WHERE d.`~id` = '{dataset_id}'
                RETURN v.`~id` as var_id, v.cesm_name as name, v.description as description,
                       v.long_name as long_name, v.units as units, v.component as component,
                       v.domain as domain
                """

                cesm_result = kg_connector.execute_query(cesm_query)
                if cesm_result.get("results"):
                    cesm_variables.extend(cesm_result["results"])

            # Remove duplicates based on variable name
            seen_vars = set()
            unique_cesm_vars = []
            for var in cesm_variables:
                var_name = var.get('name', 'Unknown')
                if var_name not in seen_vars and var_name != 'Unknown':
                    seen_vars.add(var_name)
                    unique_cesm_vars.append(var)

            if not unique_cesm_vars:
                output += f"❌ No CESM variables found connected to the relevant datasets.\n"
                output += f"💡 The datasets may not have CESM variable relationships or may be different types of climate data.\n"
                return output

            # Limit to top 10 for readability
            cesm_results = unique_cesm_vars[:10]

            output += f"✅ Found {len(cesm_results)} relevant CESM variables:\n\n"

            # Display results
            for i, result in enumerate(cesm_results, 1):
                name = result.get('name', 'Unknown')
                long_name = result.get('long_name', '')
                description = result.get('description', '')
                units = result.get('units', '')
                component = result.get('component', '')
                domain = result.get('domain', '')

                output += f"🏆 #{i}. {name}\n"
                if long_name:
                    output += f"   📝 Description: {long_name}\n"
                if units:
                    output += f"   📏 Units: {units}\n"
                if component:
                    output += f"   🧩 Component: {component}\n"
                if domain:
                    output += f"   🌍 Domain: {domain}\n"
                if description and description != long_name:
                    output += f"   💡 Details: {description}\n"
                output += "\n"

            # Provide recommendations for top 3 variables
            top_3 = cesm_results[:3]
            if len(top_3) >= 1:
                output += f"💡 RECOMMENDATIONS:\n"
                output += f"🥇 Primary Variable: {top_3[0].get('name', 'Unknown')}\n"
                output += f"   → Use this for your main analysis\n"

                if len(top_3) >= 2:
                    output += f"🥈 Secondary Variable: {top_3[1].get('name', 'Unknown')}\n"
                    output += f"   → Consider for additional insights\n"

                if len(top_3) >= 3:
                    output += f"🥉 Supporting Variable: {top_3[2].get('name', 'Unknown')}\n"
                    output += f"   → Useful for context or validation\n"

            output += f"\n📋 NEXT STEPS - ITERATIVE OBSERVATIONAL-TO-CESM APPROACH:\n"
            output += f"1. **Try First**: Use 'query_cesm_lens_data' with the top recommended variable\n"
            output += f"2. **If Failed**: Re-run smart_cesm_variable_selection with more specific observational dataset terms\n"
            output += f"3. **Keep Iterating**: Refine your search terms until you find a working CESM variable\n"
            output += f"4. Apply spatial subsetting if needed with 'location_to_coordinates'\n"
            output += f"5. Use 'analyze_cesm_ensemble' for statistical analysis\n\n"
            output += f"💡 **REMEMBER**: Frame future searches as 'observational [phenomenon] datasets' to find CESM connections\n\n"
            if recommended_vars:
                top_var = recommended_vars[0].get('name', recommended_vars[0].get('cesm_name', 'first_variable'))
                output += f"🚨 **NEXT MANDATORY ACTION**: Use query_cesm_lens_data with the recommended variable '{top_var}' to load the actual data and proceed with the analysis. Do not stop here!"
            else:
                output += f"🚨 **NEXT MANDATORY ACTION**: Use query_cesm_lens_data with one of the found variables to load the actual data and proceed with the analysis. Do not stop here!"

            return output

        except Exception as e:
            return f"❌ Smart variable selection error: {str(e)}"

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

def create_cesm_lens_agent():
    """Create the CESM LENS LangChain agent"""
    
    # Define all available tools (prioritized order)
    tools = [
        CESMLENSDataTool(),
        CESMEnsembleAnalysisTool(),
        SaveCESMDataPathTool(),
        SearchSavedCESMPathsTool(),
        RunCESMSimulationFromObsTool(),
        ExecutePythonCodeTool(),              # Execute Python code for analysis
        DownloadAndSaveDataTool(),           # Download and save data directly
        LocationToCoordinatesTool(),         # Convert location names to lat/lon coordinates
        SmartCESMVariableSelectionTool(),    # AI-powered variable selection based on research description
        AskDataProcessingFollowUpTool()      # Only use if absolutely necessary for clarification
    ]
    # Create the CESM LENS focused prompt
    template = """You are a CESM LENS Climate Ensemble Modeling Assistant with access to the NCAR CESM Large Ensemble dataset.

🚨 CRITICAL: When smart_cesm_variable_selection returns variables, you MUST immediately proceed to step 3 and use query_cesm_lens_data with the recommended variable. DO NOT STOP after variable selection - this is only step 2 of the workflow. Continue with data loading and analysis.

CESM LENS DATASET OVERVIEW:
- 40-member ensemble simulations (1920-2100)
- Historical experiment: 1920-2005
- RCP8.5 future scenario: 2006-2100  
- Components: atmosphere (atm), ocean (ocn), ice, land (lnd)
- Resolution: ~1 degree globally
- AWS S3 Storage: s3://ncar-cesm-lens/

CESM LENS WORKFLOW:
1. LOCATION LOOKUP (if needed): Use 'location_to_coordinates' to convert place names (e.g., "Texas", "Amazon Basin") to lat/lon coordinates for spatial subsetting
2. SMART VARIABLE SELECTION: Use 'smart_cesm_variable_selection' by framing your question as searching for observational datasets first (e.g., 'observational precipitation datasets for flooding analysis'), then the tool will find connected CESM variables iteratively
3. QUERY DATA: Use query_cesm_lens_data to access ensemble data directly with the variables found (use spatial subsetting with coordinates from step 1)
4. ANALYZE: Use analyze_cesm_ensemble for ensemble statistics and trends
5. DOWNLOAD DATA: Use download_and_save_data to download CESM data files locally for analysis (with optional spatial/temporal subsetting)
6. CODE ANALYSIS: Use execute_python_code to run custom Python analysis, create plots, and process saved data
7. ANALYSIS: Use execute_python_code to create visualizations and perform analysis with loaded data

🚨 MANDATORY WORKFLOW COMPLETION:
1. Variable selection is NOT the end - it's just finding the right tool
2. After smart_cesm_variable_selection, immediately use query_cesm_lens_data
3. After loading data, create the requested analysis/visualization
4. NEVER stop after just finding variables - complete the full workflow

ANALYSIS WORKFLOW: After successful data operations (loading, querying, downloading), proceed directly with the user's intended analysis. Create appropriate visualizations, statistical analysis, or custom processing based on the user's request.

DIRECT PROCESSING: When data is loaded successfully, proceed immediately with the analysis or visualization the user requested. Do not ask unnecessary follow-up questions if the user's intent is clear.

NATURAL LANGUAGE QUERIES (Frame as searching for observational datasets first):
You can handle research-based requests like:
- "Find precipitation in Texas" → Use smart_cesm_variable_selection('observational precipitation datasets for Texas flooding risk') + location_to_coordinates('Texas') then query with spatial subsetting
- "Temperature trends in Europe" → Use smart_cesm_variable_selection('satellite temperature datasets for European warming trends') + location_to_coordinates('Europe') then analyze
- "Drought analysis for agricultural regions" → Use smart_cesm_variable_selection('agricultural drought monitoring datasets') to find relevant variables
- "Ocean warming studies" → Use smart_cesm_variable_selection('ocean temperature observational datasets for warming analysis') to get ocean variables

KEY PRINCIPLE: Always frame your smart_cesm_variable_selection queries as if you're looking for observational datasets that measure the phenomenon, then the tool will iteratively find the corresponding CESM variables through knowledge graph relationships.

CESM2-LENS VARIABLES:
- Use 'smart_cesm_variable_selection' to discover variables for your research topic
- Use 'smart_cesm_variable_selection' for AI-powered variable recommendations
- Use 'query_cesm_lens_data' to directly access CESM variable data
- Complete variable list: https://www.cesm.ucar.edu/community-projects/lens2/output-variables
- Components: atmosphere (atm), ocean (ocn), land (lnd), ice (ice)
- All variables from official CESM2-LENS documentation are supported

ENSEMBLE ANALYSIS TYPES:
- ensemble_mean: Compute ensemble statistics and spatial patterns
- trend_analysis: Analyze temporal trends across ensemble members
- uncertainty: Quantify ensemble spread and confidence intervals

OBSERVATIONAL-MODEL INTEGRATION:
- Use run_cesm_simulation_from_obs to bridge observational datasets with CESM LENS
- Automatically maps observational variables to CESM variables
- Applies spatial/temporal constraints from observational data
- Compares model output with observational characteristics
- Example: 'dataset_GGD222_756 TREFHT 1990 2010 ensemble_mean'

You have access to these tools:
{tools}

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)

IMPORTANT: Only provide a Final Answer when you have COMPLETED the full workflow:
1. Found variables with smart_cesm_variable_selection
2. Loaded data with query_cesm_lens_data
3. Created the requested analysis/visualization

Do not stop after just finding variables - complete the entire request!

Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad"],
        template=template,
        partial_variables={"tools": "\n".join([f"{tool.name}: {tool.description}" for tool in tools]),
                          "tool_names": ", ".join([tool.name for tool in tools])}
    )
    
    # Create the ReAct agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create memory
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=5,
        return_messages=True
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=500,  # Significantly increased for complex workflows
        max_execution_time=3600  # 30 minutes timeout for thorough analysis
    )
    
    return agent_executor

# Orchestrator integration functions
def get_cesm_lens_tools():
    """Get CESM LENS tools for orchestrator integration"""
    try:
        # Import tools from the agent module
        from types import ModuleType
        current_module = sys.modules[__name__]
        
        # Get all tool classes from this module
        tools = []
        for name in dir(current_module):
            obj = getattr(current_module, name)
            if (isinstance(obj, type) and 
                issubclass(obj, BaseTool) and 
                obj != BaseTool and
                name.endswith('Tool')):
                tools.append(obj())
        
        return tools
    except Exception as e:
        print(f" Error loading CESM LENS tools: {e}")
        return []

def get_cesm_lens_agent():
    """Get CESM LENS agent for orchestrator coordination"""
    try:
        # Return agent creation function if available
        if 'create_cesm_lens_agent' in globals():
            return create_cesm_lens_agent()
        else:
            return None
    except Exception as e:
        print(f" Error creating CESM LENS agent: {e}")
        return None

# Test and example usage
if __name__ == "__main__":
    # Setup dual logging to both console and file
    logger, log_file_handle = setup_dual_logging("climate_sim_log.txt")
    
    try:
        print(" CESM LENS Climate Ensemble Modeling Agent")
        print("=" * 60)
        print("\n Using AWS Bedrock Claude Sonnet for reasoning")
        print(" Using NCAR CESM Large Ensemble dataset")  
        print(" Accessing data from AWS S3: s3://ncar-cesm-lens/")
        print(" Using LangChain for agent framework")
        
        print("\n" + "="*60)
        print(" TESTING CESM LENS Agent")
        print("="*60)
        
        # Create the agent
        print("\n Initializing CESM LENS LangChain agent...")
        agent = create_cesm_lens_agent()
        print(" Agent initialized successfully!")
        
        # Test with a CESM LENS research question
        research_question = """Flood Risk Analysis for Texas – July 2025 (CESM-LENS)

Analyze Texas flooding risk for July 2025 using CESM-LENS ensemble data. Focus primarily on precipitation as the main variable, with the option to incorporate other relevant CESM variables (e.g., soil moisture, runoff, temperature) for more detailed insights.

Tasks:

Load CESM-LENS Data

Main variable: Precipitation for the Texas region for July 2025.

Optional: Include additional CESM variables such as soil moisture, runoff, or temperature.

Visualizations

Ensemble mean flooding likelihood maps for Texas (using precipitation as primary input).

Precipitation anomaly maps compared to historical July averages.

Time series of daily precipitation for major Texas cities (Houston, Dallas, Austin, San Antonio).

Box plots showing ensemble spread and uncertainty.

Extreme precipitation probability maps.

Optional: Visualize additional variables to support flood risk interpretation.

Flood Risk Analysis

Calculate precipitation percentiles across the ensemble.

Identify areas with >90th percentile precipitation likelihood.

Compare July 2025 predictions to historical extreme events.

Quantify flood risk probability for major watersheds.

Generate uncertainty bounds for precipitation forecasts.

Optional: Include other variables (soil moisture, runoff) to refine risk assessment."""
        print(f"\n Research Question: {research_question}")
        
        print("\n Running agent...")
        response = agent.invoke({"input": research_question})
        
        print(f"\n Agent Response:")
        print("-" * 50)
        print(response.get('output', 'No output'))
        
    except Exception as e:
        print(f"\n TEST FAILED: {str(e)}")
        print(" Error details:")
        traceback.print_exc()
    
    finally:
        # Clean up logging
        print(f"\n🔬 CESM LENS Analysis Completed - {datetime.now().isoformat()}")
        print("=" * 70)
        if 'log_file_handle' in locals():
            log_file_handle.close()
        # Restore original stdout
        sys.stdout = sys.__stdout__
        
        print(f"\n This might be expected if:")
        print("   - AWS Bedrock credentials are not configured")
        print("   - Neptune Analytics is not accessible") 
        print("   - CESM LENS S3 access requires authentication")
        print("   - LangChain dependencies are missing")