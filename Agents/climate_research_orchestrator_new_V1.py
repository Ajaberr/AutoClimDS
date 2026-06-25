#!/usr/bin/env python3
"""
Climate Research Orchestrator Agent (Updated)
=============================================

Master orchestrator that coordinates specialized climate research agents to tackle
complex climate science problems involving ERA5, CMIP6, and observational datasets.

Key Capabilities:
1. User Query Processing - Natural language climate research questions
2. Agent Coordination - Automatically calls specialized agents (Simulation KG, Data Acquisition, NASA CMR)
3. Data Integration - Links and stores simulation and observational data
4. Code Execution - Runs analysis code and generates results
5. Knowledge Management - Maintains research context and findings
6. Workflow Orchestration - Manages complex multi-step research workflows

Integrated Agents:
- Simulation Knowledge Graph Agent (Metadata for ERA5/CMIP6)
- Simulation Data Acquisition Agent (Downloads/Processing for ERA5/CMIP6)
- NASA CMR Data Acquisition Agent (Observational Satellite Data)
- FEMA Data Acquisition Agent (Disaster/Emergency Data)
- CESM vs Observational Comparison Agent
- Climte Data Analysis Agent (code execution)

Research Problem Integration:
Provides unified interface for climate model validation, data comparison,
and scientific analysis workflows.
"""

import os
import sys
import json
import sqlite3
import warnings
import boto3
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
import pickle
import hashlib
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain.llms.base import BaseLLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import LLMResult, Generation

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.prompts import PromptTemplate

# Agent Accessors (Dynamic Imports)
def _make_cdsapi_fallback(label: str):
    class CdsApiFallback:
        def invoke(self, inputs):
            return {
                "output": (
                    f"{label} is unavailable (initialization failed). "
                    "FALLBACK: Use execute_analysis_code with cdsapi directly. "
                    "Example: import cdsapi; c = cdsapi.Client(); c.retrieve('reanalysis-era5-single-levels', {{...}}, 'output.nc')"
                )
            }
    return CdsApiFallback()

def get_simulation_kg_agent():
    """Get Simulation Knowledge Graph agent - works with .py files or same kernel"""
    if 'get_simulation_agent' in globals():
        agent = globals()['get_simulation_agent']()
        if agent is not None:
            return agent

    try:
        from simulation_kg_agent import get_simulation_agent
        agent = get_simulation_agent()
        if agent is not None:
            return agent
    except Exception:
        pass

    return _make_cdsapi_fallback("Simulation KG Agent")

def get_simulation_data_agent():
    """Get Simulation Data Acquisition agent - works with .py files or same kernel"""
    if 'get_simulation_data_acquisition_agent' in globals():
        agent = globals()['get_simulation_data_acquisition_agent']()
        if agent is not None:
            return agent

    try:
        from simulation_data_acquisition_agent import get_simulation_data_acquisition_agent
        agent = get_simulation_data_acquisition_agent()
        if agent is not None:
            return agent
    except Exception:
        pass

    return _make_cdsapi_fallback("Simulation Data Agent")

def get_nasa_cmr_agent():
    """Get NASA CMR agent - works with .py files or same kernel"""
    if 'create_nasa_cmr_agent' in globals():
        agent = globals()['create_nasa_cmr_agent']()
        if agent is not None:
            return agent

    try:
        from nasa_cmr_data_acquisition_agent_V1 import create_nasa_cmr_agent
        agent = create_nasa_cmr_agent()
        if agent is not None:
            return agent
    except Exception:
        pass

    try:
        from nasa_cmr_data_acquisition_agent import create_nasa_cmr_agent
        agent = create_nasa_cmr_agent()
        if agent is not None:
            return agent
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "NASA CMR Agent (Mock): Would search/load observational data."}
    return WorkingMockAgent()

def get_cesm_verification_agent():
    """Get CESM Verification agent - works with .py files or same kernel"""
    if 'create_verification_agent' in globals():
        return globals()['create_verification_agent']()

    try:
        from cesm_verification_agent import create_verification_agent
        return create_verification_agent()
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "CESM Verification Agent (Mock): Would verify workflow."}
    return WorkingMockAgent()

def get_cesm_obs_comparison_agent():
    """Get CESM Comparison agent - works with .py files or same kernel"""
    if 'create_cesm_obs_comparison_agent' in globals():
        return globals()['create_cesm_obs_comparison_agent']()

    try:
        from cesm_obs_comparison_agent import create_cesm_obs_comparison_agent
        return create_cesm_obs_comparison_agent()
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "CESM Comparison Agent (Mock): Would compare models and obs."}
    return WorkingMockAgent()

def get_fema_data_agent():
    """Get FEMA Data Agent - works with .py files or same kernel"""
    if 'get_fema_agent' in globals():
        return globals()['get_fema_agent']()

    try:
        from fema_data_acquisition_agent import get_fema_agent
        return get_fema_agent()
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "FEMA Agent (Mock): Would search/download FEMA data."}
    return WorkingMockAgent()

def get_floodnet_agent():
    """Get FloodNet Data Agent - works with .py files or same kernel"""
    try:
        from floodnet_data_acquisition_agent import get_floodnet_agent as _get
        return _get()
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "FloodNet Agent (Mock): Would search/download NYC FloodNet sensor data."}
    return WorkingMockAgent()

def get_floodsimbench_agent():
    """Get FloodSimBench Data Agent - works with .py files or same kernel"""
    try:
        from floodsimbench_data_acquisition_agent import get_floodsimbench_agent as _get
        return _get()
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "FloodSimBench Agent (Mock): Would search/download FloodSimBench data."}
    return WorkingMockAgent()

def get_mrms_agent():
    """Get MRMS Data Agent - works with .py files or same kernel"""
    try:
        from mrms_data_acquisition_agent import get_mrms_agent as _get
        return _get()
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "MRMS Agent (Mock): Would search/download MRMS radar products."}
    return WorkingMockAgent()

def get_us_311_agent():
    """Get US 311 Data Agent - works with .py files or same kernel"""
    if 'get_311_agent' in globals():
        return globals()['get_311_agent']()

    try:
        from us_city_311_data_acquisition_agent import get_311_agent
        return get_311_agent()
    except Exception:
        pass

    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "US 311 Agent (Mock): Would search/download 311 data."}
    return WorkingMockAgent()


BEDROCK_REGION = "us-east-2"
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

# Shared conversation context for LAMBDA repair loop
_LAMBDA_CONTEXT: list = []

# --- Bedrock LLM (exact copy from other agents) ---
class BedrockClaudeLLM(BaseLLM):
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

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None, **kwargs) -> LLMResult:
        if not self.bedrock:
            return LLMResult(generations=[[Generation(text="DUMMY LLM RESPONSE: Bedrock is not configured.")]])

        stop_sequences = stop or ["\nObservation:"]
        generations = []
        
        # Bedrock invoke_model doesn't support batching natively in this simple wrapper, loop if needed
        # But typically LangChain calls with 1 prompt
        prompt = prompts[0]

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
            # Capture headers for usage if available, but for Claude 3/Sonnet, usage is often in the body or headers
            # Note: As of early 2024, Bedrock InvokeModel API might return usage in headers 'x-amzn-bedrock-input-token-count'
            
            response_body = json.loads(response["body"].read())
            output_text = response_body["content"][0]["text"].strip()
            
            # Attempt to get token usage from headers or response body
            # Claude 3 on Bedrock usually has usage in the response body now or headers
            # We will try to get it from headers if captured, but boto3 invoke_model response object has 'ResponseMetadata'
            
            token_usage = {}
            if 'usage' in response_body:
                 token_usage = response_body['usage'] # e.g. {'input_tokens': 15, 'output_tokens': 12}
            else:
                # Fallback to headers if not in body
                headers = response.get('ResponseMetadata', {}).get('HTTPHeaders', {})
                if 'x-amzn-bedrock-input-token-count' in headers:
                     token_usage['input_tokens'] = int(headers['x-amzn-bedrock-input-token-count'])
                if 'x-amzn-bedrock-output-token-count' in headers:
                     token_usage['output_tokens'] = int(headers['x-amzn-bedrock-output-token-count'])

            gen = Generation(text=output_text)
            return LLMResult(generations=[[gen]], llm_output={"token_usage": token_usage, "model_id": self.model_id})

        except Exception as e:
            raise e


# Database initialization (Keeping original structure for Observational Data Registry)
# Note: Simulation agents manage their own DB (climate_knowledge_graph.db)
def _init_obs_database():
    """Initialize SQLite database for Observational data tracking"""
    # Assuming the original functionality for observational data needs to be preserved
    # If the new simulation_kg_agent uses climate_knowledge_graph.db for everything, 
    # we might just rely on that. But for safety, we keep this if it differs.
    # The original file called _init_cesm_database which created 'cesm_data_paths'.
    # Since we are moving to ERA5/CMIP6, we probably rely on the new agents' DB.
    # We will keep this for backward compatibility if needed, but the main robust DB is in agents.
    pass 

@dataclass
class ResearchContext:
    """Research session context and state"""
    session_id: str
    research_question: str
    datasets_used: List[str]
    analysis_steps: List[str]
    findings: List[str]
    code_executed: List[str]
    plots_generated: List[str]
    created_at: datetime
    updated_at: datetime


# --- TOOLS ---

class UserQueryTool(BaseTool):
    """Interactive tool to ask intelligent follow-up questions to clarify research requirements"""
    name: str = "capture_user_query"
    description: str = "Ask specific, targeted questions to gather missing research details. Examples: 'What geographic coordinates?', 'What time period?', 'Which variables?'. Use this ONLY ONCE per conversation turn, and NEVER if the user has already said 'Approve', 'Proceed', 'Yes', or 'Continue' — in that case use reasonable defaults and proceed immediately."

    def _run(self, query_prompt: str = "What climate research question would you like to investigate?", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        output = f"🔴 **WAITING FOR USER INPUT** 🔴\n\n"
        output += f"📋 **Research Clarification Needed:**\n{query_prompt}\n\n"
        output += f"⚠️ **Agent execution paused - please respond with your clarifications.**"
        return output

class CallSimulationKGAgent(BaseTool):
    """Call Simulation Knowledge Graph Agent to query metadata for ERA5 and CMIP6 datasets."""
    name: str = "query_simulation_metadata"
    description: str = "Call Simulation Knowledge Graph Agent to find ERA5 and CMIP6 dataset METADATA. Provide a description of what you need (e.g., 'ERA5 temperature for 2020', 'CMIP6 projections'). Returns list of available datasets and their IDs."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_simulation_kg_agent()
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from Simulation KG agent')
        except Exception as e:
            return f" Simulation KG Agent error: {str(e)}"

class CallSimulationDataAgent(BaseTool):
    """Call Simulation Data Acquisition Agent to download and process ERA5/CMIP6 data."""
    name: str = "acquire_simulation_data"
    description: str = "Call Simulation Data Acquisition Agent to DOWNLOAD and PROCESS ERA5/CMIP6 data. Use this AFTER finding dataset IDs with query_simulation_metadata. Input: 'Download dataset [ID] for [region/time]'."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_simulation_data_agent()
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from Simulation Data agent')
        except Exception as e:
            return f" Simulation Data Agent error: {str(e)}"

class NasaCMRDataAcquisitionAgent(BaseTool):
    """Call NasaCMRDataAcquisitionAgent to load climate observational datasets based on KnowledgeGraph Query."""
    name: str = "query_nasa_cmr_datasets"
    description: str = "Call NasaCMRDataAcquisitionAgent to search and load OBSERVATIONAL SATELLITE datasets from NASA CMR. Use this for actual satellite data (MODIS, GOES, etc.)."

    def _run(self, data_set_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_nasa_cmr_agent()
            response = agent.invoke({"input": data_set_query})
            return response.get('output', 'No output from NASA CMR agent')
        except Exception as e:
            return f" NASA CMR agent error: {str(e)}"

class CESMVerificationAgent(BaseTool):
    """Call CESMVerificationAgent to verify information about the pipeline and climate research workflow."""
    name: str = "verify_research_workflow"
    description: str = "Call Verification Agent to verify information about the pipeline and scientific rigour. Useful for checking methodology."

    def _run(self, verification_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_cesm_verification_agent()
            response = agent.invoke({"input": verification_query})
            return response.get('output', 'No output from Verification agent')
        except Exception as e:
            return f" Verification agent error: {str(e)}"

class CESMObsComparisonAgent(BaseTool):
    """Call CESMObsComparisonAgent to compare simulation datasets with observational datasets."""
    name: str = "compare_simulation_obs"
    description: str = "Call Comparison Agent to compare simulation datasets (ERA5/CMIP6) with observational datasets. Calculates bias, uncertainty, stats."

    def _run(self, comparison_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_cesm_obs_comparison_agent()
            response = agent.invoke({"input": comparison_query})
            return response.get('output', 'No output from Comparison agent')
        except Exception as e:
            return f" Comparison agent error: {str(e)}"

class CallFemaAgent(BaseTool):
    """Call FEMA Data Acquisition Agent to search and download disaster data."""
    name: str = "acquire_fema_data"
    description: str = "Call FEMA Agent to find and download DISASTER and EMERGENCY data (floods, declarations, assistance) from OpenFEMA. Input: 'Find disaster declarations for NY in 2020'."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_fema_data_agent()
            if "download" not in query.lower() and "save" not in query.lower():
                query = query + " Download and save the results to a CSV file."
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from FEMA agent')
        except Exception as e:
            return f" FEMA Agent error: {str(e)}"

class CallFloodNetAgent(BaseTool):
    """Call FloodNet Data Acquisition Agent to search and download NYC street flood sensor data."""
    name: str = "acquire_floodnet_data"
    description: str = "Call FloodNet Agent to find and download NYC STREET FLOOD SENSOR data from the FloodNet IoT network (NYC DEP). Covers real flood events measured at street level across NYC boroughs. Input: 'Download FloodNet data for Brooklyn sensors in August 2021'."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_floodnet_agent()
            if "download" not in query.lower() and "save" not in query.lower():
                query = query + " Download and save the results to a CSV file."
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from FloodNet agent')
        except Exception as e:
            return f" FloodNet Agent error: {str(e)}"

class CallFloodSimBenchAgent(BaseTool):
    """Call FloodSimBench Data Acquisition Agent to search and download flood simulation benchmark data."""
    name: str = "acquire_floodsimbench_data"
    description: str = "Call FloodSimBench Agent to find and download FLOOD SIMULATION BENCHMARK data from Hugging Face (chrimerss/FloodSimBench). Covers 10 US flood-prone cities with 1-m DEM, water depth time series, and flood severity maps for 10/25/50/100-year storms. Input: 'Download FloodSimBench data for Houston 100-year return period'."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_floodsimbench_agent()
            if "download" not in query.lower() and "save" not in query.lower():
                query = query + " Download and save the results to a file."
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from FloodSimBench agent')
        except Exception as e:
            return f" FloodSimBench Agent error: {str(e)}"

class CallMRMSAgent(BaseTool):
    """Call MRMS Data Acquisition Agent to search and download NOAA radar/precipitation products."""
    name: str = "acquire_mrms_data"
    description: str = "Call MRMS Agent to find and download MRMS (Multi-Radar/Multi-Sensor System) radar and precipitation products from NOAA NSSL/NCEP. Covers QPE, reflectivity, rotation/shear, hail (MESH), and lightning at ~1 km / 2-min resolution over CONUS. Input: 'Download the latest MRMS hourly QPE product'."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_mrms_agent()
            if "download" not in query.lower() and "save" not in query.lower():
                query = query + " Download and save the results to a file."
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from MRMS agent')
        except Exception as e:
            return f" MRMS Agent error: {str(e)}"

class CallUs311Agent(BaseTool):
    """Call US 311 Data Acquisition Agent to search and download service request data."""
    name: str = "acquire_311_data"
    description: str = "Call US 311 Agent to find and download CITY SERVICE REQUEST data (Complaints, Noise, Potholes, etc.) for supported US cities (NYC, Chicago, SF, Austin). Input: 'Find 311 noise complaints in Chicago for 2023'."

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_us_311_agent()
            if "download" not in query.lower() and "save" not in query.lower():
                query = query + " Download and save the results to a CSV file."
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from 311 agent')
        except Exception as e:
            return f" 311 Agent error: {str(e)}"

class ObsDataRegistryTool(BaseTool):
    """Retrieve and load previously saved observational data paths from the database for reuse"""
    name: str = "retrieve_saved_obs_data"
    description: str = "Search for previously saved OBSERVATIONAL data paths. Input: 'variable_name [start_year] [end_year]' or 'all'."
    
    @property
    def db_path(self) -> str:
        return "climate_knowledge_graph.db"
    
    def _run(self, search_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        import sqlite3
        try:
            # Simple wrapper to query stored_datasets table if it exists
            # This logic mimics the original tool but connects to the shared DB
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stored_datasets'")
                if not cursor.fetchone():
                    return "No stored_datasets table found. Use NASA CMR agent to load data first."
                
                parts = search_query.strip().split()
                if not parts or parts[0].lower() == 'all':
                     query = "SELECT * FROM stored_datasets ORDER BY updated_at DESC LIMIT 10"
                     params = []
                else:
                    var_name = parts[0]
                    query = "SELECT * FROM stored_datasets WHERE short_name LIKE ? OR title LIKE ? LIMIT 10"
                    params = [f"%{var_name}%", f"%{var_name}%"]
                
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                if not results:
                    return "No saved observational data found."
                return f"Found {len(results)} saved observational datasets. details: {results}"
        except Exception as e:
            return f"Error retrieving registry: {e}"

class LoadSavedObsDataTool(BaseTool):
    name: str = "load_saved_obs_data"
    description: str = "Load a specific saved observational dataset by database ID."
    def _run(self, database_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        return f"Please use 'query_nasa_cmr_datasets' with the ID {database_id} to reload it."


class CodeExecutionTool(BaseTool):
    """Execute custom analysis code for climate research using REAL DATA ONLY"""
    name: str = "execute_analysis_code"
    description: str = "Execute custom Python code for climate data analysis using REAL climate data only. NEVER create fake data. Load data first using specialized agents. IMPORTANT: Save all output files (plots, CSVs) to the 'outputs/' subdirectory."

    def _run(self, code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            output = f" CLIMATE ANALYSIS CODE EXECUTION\n"
            output += "=" * 50 + "\n\n"

            # Strip markdown code fences if LLM wrapped the code
            code = code.strip()
            if code.startswith("```"):
                first_newline = code.find("\n")
                if first_newline != -1:
                    code = code[first_newline + 1:]
                if code.endswith("```"):
                    code = code[:-3].strip()

            # Security checks
            forbidden_patterns = ['fake_data', 'placeholder', 'dummy_data', 'simulated_data']
            if any(p in code.lower() for p in forbidden_patterns):
                return "REJECTED: usage of placeholder/fake data patterns detected."

            # Quick cdsapi pre-check: verify credentials and connectivity before running
            if 'cdsapi' in code:
                try:
                    import cdsapi as _cdsapi_test
                    import requests as _req_test
                    _resp = _req_test.get("https://cds.climate.copernicus.eu/api", timeout=10)
                    if _resp.status_code == 404:
                        pass  # 404 is OK - endpoint exists
                except Exception as _conn_err:
                    return (
                        f"Error executing code (cdsapi pre-check failed): Cannot reach CDS API server.\n"
                        f"Connection error: {_conn_err}\n\n"
                        f"ACTION REQUIRED: CDS API is unreachable. Show this error to the user. "
                        f"Do NOT call simulation agents as fallback."
                    )

            # Execution
            import io
            import glob
            from contextlib import redirect_stdout, redirect_stderr
            import traceback

            # Snapshot files before exec so we can detect new ones after
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            _pre_exec_files = set(
                glob.glob(os.path.join(output_dir, "*.png")) +
                glob.glob(os.path.join(output_dir, "*.csv")) +
                glob.glob(os.path.join(output_dir, "*.nc")) +
                glob.glob("*.png") +
                glob.glob("*.csv")
            )

            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            exec_namespace = {
                '__builtins__': __builtins__,
            }
            # Add common libs if available
            for lib in ['numpy', 'xarray', 'pandas', 'matplotlib.pyplot']:
                try:
                    if lib == 'matplotlib.pyplot':
                        import matplotlib
                        matplotlib.use('Agg')
                        import matplotlib.pyplot as plt

                        # Monkey-patch plt.savefig: redirect relative paths to outputs/
                        original_savefig = plt.savefig
                        def patched_savefig(*args, **kwargs):
                            fname = args[0] if args else kwargs.get('fname')
                            if fname and not os.path.isabs(str(fname)):
                                os.makedirs(output_dir, exist_ok=True)
                                new_fname = os.path.join(output_dir, os.path.basename(str(fname)))
                                if args:
                                    args = (new_fname,) + args[1:]
                                else:
                                    kwargs['fname'] = new_fname
                                fname = new_fname
                            # Auto-fix suptitle overlap
                            try:
                                fig = plt.gcf()
                                if fig._suptitle and fig._suptitle.get_text():
                                    fig.tight_layout(rect=[0, 0, 1, 0.95])
                            except Exception:
                                pass
                            result = original_savefig(*args, **kwargs)
                            try:
                                setattr(plt.gcf(), '_has_been_saved', True)
                            except Exception:
                                pass
                            return result
                        plt.savefig = patched_savefig
                        exec_namespace['plt'] = plt

                    elif lib == 'pandas':
                        import pandas as pd
                        # Monkey-patch read_csv: search known data directories for relative paths
                        if not getattr(pd.read_csv, '_autoclimds_patched', False):
                            _original_read_csv = pd.read_csv
                            _known_data_dirs = [
                                ".",
                                "outputs",
                                "us_311_data",
                                "fema_data",
                                "floodnet_downloads",
                                "mrms_downloads",
                                "floodsimbench_downloads",
                                "era5_data",
                                "cmip6_out",
                                "downloads",
                            ]
                            def _patched_read_csv(filepath_or_buffer, *args, **kwargs):
                                if isinstance(filepath_or_buffer, str) and not os.path.isabs(filepath_or_buffer):
                                    if not os.path.exists(filepath_or_buffer):
                                        fname = os.path.basename(filepath_or_buffer)
                                        for search_dir in _known_data_dirs:
                                            candidate = os.path.join(search_dir, fname)
                                            if os.path.exists(candidate):
                                                filepath_or_buffer = candidate
                                                break
                                return _original_read_csv(filepath_or_buffer, *args, **kwargs)
                            _patched_read_csv._autoclimds_patched = True
                            pd.read_csv = _patched_read_csv

                        # Monkey-patch to_csv: redirect relative paths to outputs/
                        original_to_csv = pd.DataFrame.to_csv
                        def patched_to_csv(df_self, path_or_buf=None, **kwargs):
                            if path_or_buf and isinstance(path_or_buf, str) and not os.path.isabs(path_or_buf):
                                if os.path.dirname(path_or_buf) == "":
                                    os.makedirs(output_dir, exist_ok=True)
                                    path_or_buf = os.path.join(output_dir, path_or_buf)
                            return original_to_csv(df_self, path_or_buf, **kwargs)
                        pd.DataFrame.to_csv = patched_to_csv
                        exec_namespace['pandas'] = pd
                        exec_namespace['pd'] = pd

                    else:
                        mod = __import__(lib.split('.')[0])
                        if '.' in lib:
                            mod = getattr(mod, lib.split('.')[1])
                        exec_namespace[lib.split('.')[-1]] = mod
                except ImportError:
                    pass

            # --- LAMBDA repair loop ---

            _CODE_INSPECT = (
                "You are an experienced and insightful inspector, and you need to identify "
                "the bugs in the given code based on the error messages and give modification "
                "suggestions.\n\n- bug code:\n{bug_code}\n\nWhen executing above code, errors "
                "occurred: {error_message}.\nPlease check the implementation of the function "
                "and provide a method for modification based on the error message. No need to "
                "provide the modified code.\n\nModification method:"
            )
            _CODE_FIX = (
                "You should attempt to fix the bugs in the bellow code based on the provided "
                "error information and the method for modification. Please make sure to carefully "
                "check every potentially problematic area and make appropriate adjustments and "
                "corrections.\nIf the error is due to missing packages, you can install packages "
                "in the environment by \"!pip install package_name\".\n\n- bug code:\n{bug_code}"
                "\n\nWhen executing above code, errors occurred: {error_message}.\nPlease check "
                "and fix the code based on the modification method.\n\n- modification method:"
                "\n{fix_method}\n\nThe code you modified (should be wrapped in ```python```):"
            )
            _RESULT_PROMPT = (
                "This is the executing result by computer:\n{}.\n\nNow: You should reformat "
                "the tabular result (if any) in MarkDown format. Then, you should use 1-3 "
                "sentences to explain the results. Finally, You should give suggestions for "
                "next step based on the chat history. You should list at least 3 points with "
                "format like:\n Next, you can:\n[1]Standardize the data in the next step.\n"
                "[2]Do outlier detection for the data.\n[3]Train a neural network model."
            )

            def _lambda_bedrock_chat(messages):
                try:
                    _cl = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
                    _body = json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 4096,
                        "messages": messages,
                        "temperature": 0.1,
                    })
                    _resp = _cl.invoke_model(modelId=BEDROCK_MODEL_ID, body=_body)
                    return json.loads(_resp["body"].read())["content"][0]["text"].strip()
                except Exception as _e:
                    return f"[LLM Error] {_e}"

            class _LambdaProgrammer:
                def __init__(self):
                    self.messages = []
                def _call_chat_model(self):
                    return _lambda_bedrock_chat(self.messages)
                def clear(self):
                    self.messages = []

            class _LambdaInspector:
                def __init__(self):
                    self.messages = []
                def _call_chat_model(self):
                    return _lambda_bedrock_chat(self.messages)
                def clear(self):
                    self.messages = []

            def _lambda_extract_code(text):
                if "```python" in text:
                    part = text.split("```python", 1)[1].split("```")[0].strip()
                    return True, part
                elif "```" in text:
                    part = text.split("```", 1)[1].split("```")[0].strip()
                    return True, part
                return False, text

            def _lambda_run_code(code_str, ns):
                import traceback as _tb
                _so = io.StringIO()
                _se = io.StringIO()
                try:
                    with redirect_stdout(_so), redirect_stderr(_se):
                        exec(code_str, ns)
                    return "success", "", _so, _se
                except Exception:
                    err = _tb.format_exc()
                    return f"error: {err}", err, _so, _se

            def _lambda_run_code_jupyter(code_str):
                import queue, re as _re
                try:
                    import jupyter_client
                except ImportError:
                    return _lambda_run_code(code_str, exec_namespace)

                km = jupyter_client.KernelManager(kernel_name='python3')
                km.start_kernel()
                kc = km.client()
                kc.start_channels()
                try:
                    kc.wait_for_ready(timeout=30)
                except Exception as _ke:
                    try:
                        kc.stop_channels(); km.shutdown_kernel()
                    except Exception:
                        pass
                    _err = f"Jupyter kernel failed to start: {_ke}"
                    _so, _se = io.StringIO(), io.StringIO()
                    _se.write(_err)
                    return f"error: {_err}", _err, _so, _se

                _so = io.StringIO()
                _se = io.StringIO()
                _errs = []

                def _drain_until_idle(timeout=15):
                    while True:
                        try:
                            _m = kc.get_iopub_msg(timeout=timeout)
                            if _m['msg_type'] == 'status' and _m['content'].get('execution_state') == 'idle':
                                break
                        except queue.Empty:
                            break

                # Kernel init: output dir, savefig and read_csv patches
                _known_dirs = [".", "outputs", "us_311_data", "fema_data", "floodnet_downloads",
                               "mrms_downloads", "floodsimbench_downloads", "era5_data", "cmip6_out", "downloads"]
                _init = f"""
import os, warnings; warnings.filterwarnings('ignore')
os.makedirs({repr(output_dir)}, exist_ok=True)
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
_orig_sf = plt.savefig
def _psf(fname, *a, **kw):
    if isinstance(fname, str) and not os.path.isabs(fname) and os.path.dirname(fname) == '':
        fname = os.path.join({repr(output_dir)}, fname)
    return _orig_sf(fname, *a, **kw)
plt.savefig = _psf
try:
    import pandas as pd
    _orig_read_csv = pd.read_csv
    _search_dirs = {repr(_known_dirs)}
    def _patched_read_csv(fp, *a, **kw):
        if isinstance(fp, str) and not os.path.isabs(fp) and not os.path.exists(fp):
            _fn = os.path.basename(fp)
            for _d in _search_dirs:
                _c = os.path.join(_d, _fn)
                if os.path.exists(_c):
                    fp = _c; break
        return _orig_read_csv(fp, *a, **kw)
    pd.read_csv = _patched_read_csv
    _orig_to_csv = pd.DataFrame.to_csv
    def _patched_to_csv(self, path=None, **kw):
        if path and isinstance(path, str) and not os.path.isabs(path) and os.path.dirname(path) == '':
            os.makedirs({repr(output_dir)}, exist_ok=True)
            path = os.path.join({repr(output_dir)}, path)
        return _orig_to_csv(self, path, **kw)
    pd.DataFrame.to_csv = _patched_to_csv
except ImportError:
    pass
"""
                kc.execute(_init, silent=True)
                _drain_until_idle(timeout=15)

                kc.execute(code_str)
                while True:
                    try:
                        _msg = kc.get_iopub_msg(timeout=120)
                        _mt = _msg['msg_type']
                        _mc = _msg['content']
                        if _mt == 'stream':
                            (_so if _mc['name'] == 'stdout' else _se).write(_mc['text'])
                        elif _mt == 'error':
                            _tb_lines = _mc.get('traceback', [])
                            _tb_clean = '\n'.join(_re.sub(r'\x1b\[[0-9;]*m', '', l) for l in _tb_lines)
                            _errs.append(_tb_clean)
                            _se.write(_tb_clean + '\n')
                        elif _mt == 'execute_result':
                            _txt = _mc.get('data', {}).get('text/plain', '')
                            if _txt:
                                _so.write(_txt + '\n')
                        elif _mt == 'status' and _mc.get('execution_state') == 'idle':
                            break
                    except queue.Empty:
                        break
                    except Exception:
                        break

                try:
                    kc.stop_channels(); km.shutdown_kernel()
                except Exception:
                    pass

                if _errs:
                    _err_text = '\n'.join(_errs)
                    return f"error: {_err_text}", _err_text, _so, _se
                return "success", "", _so, _se

            _use_jupyter = os.environ.get("AUTOCLIMDS_JUPYTER_MODE") == "1"

            if not _use_jupyter:
                # Standard exec() path
                output += "[Mode: exec / LAMBDA OFF]\n"
                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()
                try:
                    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                        exec(code, exec_namespace)
                except Exception:
                    import traceback as _tb
                    _last_error = _tb.format_exc()
                    if "cdsapi" in _last_error.lower():
                        return (
                            f"Error executing code (cdsapi failed):\n{_last_error}\n\n"
                            f"ACTION REQUIRED: CDS API error. Do NOT call simulation agents as fallback. "
                            f"Show this exact error to the user."
                        )
                    return f"Error executing code:\n{_last_error}"

            else:
                # LAMBDA repair loop with Jupyter kernel
                output += "[Mode: Jupyter kernel / LAMBDA ON]\n"
                programmer = _LambdaProgrammer()
                inspector = _LambdaInspector()

                # Include conversation history for repair context
                _ctx = [
                    {"role": m["role"], "content": m["content"]}
                    for m in _LAMBDA_CONTEXT[-12:]
                    if m.get("role") in ("user", "assistant") and m.get("content", "").strip()
                ]
                if _ctx:
                    programmer.messages = _ctx + [
                        {"role": "user", "content": f"Now execute this analysis code:\n```python\n{code}\n```"},
                        {"role": "assistant", "content": f"```python\n{code}\n```"},
                    ]
                else:
                    programmer.messages = [
                        {"role": "user", "content": f"Write and execute this code:\n```python\n{code}\n```"},
                        {"role": "assistant", "content": f"```python\n{code}\n```"},
                    ]

                current_code = code
                _max_attempts = 5
                _round = 0

                sign, _last_error, stdout_capture, stderr_capture = _lambda_run_code_jupyter(current_code)

                while 'error' in sign and _round < _max_attempts:
                    output += f"\n[LAMBDA] Attempt {_round + 1} failed. Running Inspector...\n"
                    inspector.messages.append({
                        "role": "user",
                        "content": _CODE_INSPECT.format(bug_code=current_code, error_message=_last_error)
                    })
                    if _round == 3:
                        insp_response = "Try other packages or methods."
                    else:
                        insp_response = inspector._call_chat_model()
                    inspector.messages.append({"role": "assistant", "content": insp_response})

                    programmer.messages.append({
                        "role": "user",
                        "content": _CODE_FIX.format(bug_code=current_code, error_message=_last_error, fix_method=insp_response)
                    })
                    prog_response = programmer._call_chat_model()
                    programmer.messages.append({"role": "assistant", "content": prog_response})

                    is_python, fixed_code = _lambda_extract_code(prog_response)
                    if is_python:
                        current_code = fixed_code
                        sign, _last_error, stdout_capture, stderr_capture = _lambda_run_code_jupyter(current_code)
                        if sign and 'error' not in sign:
                            output += f"[LAMBDA] Code repaired on attempt {_round + 1}.\n"
                            break
                    _round += 1

                if 'error' in sign:
                    if "cdsapi" in _last_error.lower():
                        return (
                            f"Error executing code (cdsapi failed after {_max_attempts} attempts):\n{_last_error}\n\n"
                            f"ACTION REQUIRED: CDS API error. Do NOT call simulation agents as fallback. "
                            f"Show this exact error to the user."
                        )
                    return f"Error executing code (after {_max_attempts} attempts):\n{_last_error}"

                _exec_stdout = stdout_capture.getvalue()
                if _exec_stdout.strip():
                    programmer.messages.append({
                        "role": "user",
                        "content": _RESULT_PROMPT.format(_exec_stdout[:2000])
                    })
                    _interp = programmer._call_chat_model()
                    output += f"\n[Result Interpretation]\n{_interp}\n"
            # -----------------------------------------------------------------

            # --- Auto-Save Plots Fix ---
            if 'plt' in exec_namespace:
                plt = exec_namespace['plt']
                if plt.get_fignums():
                    import time
                    timestamp = int(time.time())
                    for i, fignum in enumerate(plt.get_fignums()):
                        fig = plt.figure(fignum)

                        has_content = False
                        if fig.axes:
                            for ax in fig.axes:
                                if (ax.lines or ax.collections or ax.patches or
                                        ax.texts or ax.tables or ax.images or
                                        (hasattr(ax, 'containers') and ax.containers)):
                                    has_content = True
                                    break

                        if getattr(fig, '_has_been_saved', False):
                            plt.close(fig)
                            continue

                        if not has_content:
                            plt.close(fig)
                            continue

                        os.makedirs(output_dir, exist_ok=True)
                        filename = os.path.join(output_dir, f"analysis_plot_{timestamp}_{i}.png")
                        fig.savefig(filename)
                        output += f"\n[System] Auto-saved plot to: {filename}\n"
                        plt.close(fig)

            val_out = stdout_capture.getvalue()
            val_err = stderr_capture.getvalue()

            # Filter benign stderr warnings
            ignore_keywords = [
                "DeprecationWarning", "UserWarning", "FutureWarning",
                "findfont: Font family", "Missing credentials"
            ]
            if val_err:
                filtered_lines = [line for line in val_err.split('\n') if not any(k in line for k in ignore_keywords)]
                val_err = '\n'.join(filtered_lines).strip()

            def smart_truncate(content, max_length=4000):
                if not content: return ""
                if len(content) <= max_length:
                    return content
                half = max_length // 2
                return content[:half] + f"\n... [TRUNCATED {len(content)-max_length} CHARS] ...\n" + content[-half:]

            if val_out:
                val_out = smart_truncate(val_out)
                output += f"OUTPUT:\n{val_out}\n"
            if val_err:
                val_err = smart_truncate(val_err)
                output += f"WARNINGS/ERRORS:\n{val_err}\n"

            # Detect new files created during exec
            _post_exec_files = set(
                glob.glob(os.path.join(output_dir, "*.png")) +
                glob.glob(os.path.join(output_dir, "*.csv")) +
                glob.glob(os.path.join(output_dir, "*.nc")) +
                glob.glob("*.png") +
                glob.glob("*.csv")
            )
            new_files = _post_exec_files - _pre_exec_files
            if new_files:
                output += "\nNew files created: " + " | ".join(sorted(new_files)) + "\n"

            # Explicit cleanup
            del exec_namespace
            import gc
            gc.collect()

            return output
        except Exception as e:
            import traceback as _tb
            err_str = str(e)
            tb_str = _tb.format_exc()
            # Surface cdsapi errors clearly
            if "cdsapi" in tb_str.lower() or "cdsapi" in err_str.lower():
                return (
                    f"Error executing code (cdsapi download failed):\n{err_str}\n\n"
                    f"Full traceback:\n{tb_str}\n\n"
                    f"ACTION REQUIRED: CDS API error. Do NOT call simulation agents as fallback. "
                    f"Show this exact error to the user."
                )
            return f"Error executing code: {err_str}\n{tb_str}"


# Initialize orchestrator
def create_climate_research_orchestrator():
    """Create the Climate Research Orchestrator Agent (V2)"""

    try:
        llm = BedrockClaudeLLM()
        print(" Bedrock Claude LLM initialized for orchestrator")
    except Exception as e:
        print(f" Failed to initialize Bedrock LLM: {e}")
        return None

    all_tools = [
        UserQueryTool(),
        CallSimulationKGAgent(),       # ERA5/CMIP6 Metadata
        CallSimulationDataAgent(),     # ERA5/CMIP6 Data Download/Process
        NasaCMRDataAcquisitionAgent(), # Observational Data
        CallFemaAgent(),               # FEMA Disaster Data
        CallUs311Agent(),              # US 311 Service Data
        CallFloodNetAgent(),           # FloodNet NYC Street Flood Sensors
        CallFloodSimBenchAgent(),      # FloodSimBench Flood Simulation Benchmark
        CallMRMSAgent(),               # MRMS Radar/Precipitation Products
        CESMVerificationAgent(),
        CESMObsComparisonAgent(),
        CodeExecutionTool(),
        ObsDataRegistryTool()
    ]

    template = """You are the Climate Research Orchestrator, an intelligent coordinator for climate science research involving ERA5 Reanalysis, CMIP6 Projections, and Observational Satellite data.

PRIMARY ROLE:
Intelligently coordinate climate research workflows by selecting and deploying the most appropriate specialized agents.

CORE CAPABILITIES:
1. INTELLIGENT AGENT SELECTION: Choose the right agents based on research needs.
2. REAL DATA EMPHASIS: Always work with actual climate data (ERA5, CMIP6, Satellite).
3. DYNAMIC COORDINATION: Deploy agents in any logical order.

AVAILABLE SPECIALIZED AGENTS:

 **SIMULATION DATA AGENTS (ERA5 & CMIP6):**
- query_simulation_metadata (Simulation KG Agent): QUERY local knowledge graph for ERA5/CMIP6 metadata. Use this FIRST to find available simulation datasets.
- acquire_simulation_data (Simulation Data Agent): DOWNLOAD and PROCESS the actual ERA5/CMIP6 files found by the metadata agent.

 **OBSERVATIONAL DATA AGENTS (SATELLITE & DISASTER):**
- query_nasa_cmr_datasets (NASA CMR Agent): Search and load OBSERVATIONAL satellite data (MODIS, GOES, etc.) from NASA CMR.
- acquire_fema_data (FEMA Agent): Search and download DISASTER data (Floods, Declarations) from OpenFEMA.
- acquire_311_data (US 311 Agent): Search and download 311 SERVICE REQUEST data (Noise, Potholes, etc.) from NYC, Chicago, SF, Austin.
- acquire_floodnet_data (FloodNet Agent): Search and download NYC STREET FLOOD SENSOR data (real measured flood depth events, IoT sensors, NYC DEP).
- acquire_floodsimbench_data (FloodSimBench Agent): Search and download FLOOD SIMULATION BENCHMARK data for 10 US cities (GeoTIFF DEM + water depth, Hugging Face).
- acquire_mrms_data (MRMS Agent): Search and download MRMS RADAR/PRECIPITATION products from NOAA NSSL (QPE, reflectivity, hail, rotation, lightning, GRIB2).

 **ANALYSIS AGENTS:**
- compare_simulation_obs: Compare simulation (ERA5/CMIP6) vs observations.
- verify_research_workflow: Validate scientific rigor.
- execute_analysis_code: specialized Python execution for analysis.

 CRITICAL DATA ACQUISITION WORKFLOW (SIMULATION):
1. **query_simulation_metadata**: Find "ERA5 temperature 2020" -> Returns IDs (e.g., "ERA5::...").
2. **acquire_simulation_data**: "Download ERA5::... for [region]" -> Downloads NetCDF files.
3. **execute_analysis_code**: Load and analyze the downloaded NetCDF files.

SIMULATION AGENT FALLBACK RULE (CRITICAL):
- If query_simulation_metadata or acquire_simulation_data returns ANY of these signals:
  - Contains a cdsapi Python code block
  - Says "FALLBACK" or "Use execute_analysis_code"
  - Says "empty catalog", "no datasets found", "no ERA5 datasets", "empty ERA5", "dataset_ids: None", "Stored dataset_ids: None"
  Then you MUST:
  1. DO NOT show the response as a Final Answer. DO NOT tell the user to go to a website.
  2. IMMEDIATELY write a cdsapi Python script yourself based on what the user requested.
  3. Pass that script to **execute_analysis_code** to actually download the data.
  4. Use this template (fill in the actual values from the user request):
  import cdsapi, os
  os.makedirs('era5_data', exist_ok=True)
  c = cdsapi.Client()
  c.retrieve('reanalysis-era5-single-levels', dict(
      product_type='reanalysis',
      variable=[LIST_OF_VARIABLES],
      year='YEAR', month='MONTH',
      day=[LIST_OF_DAYS],
      time=[str(h).zfill(2)+':00' for h in range(24)],
      area=[NORTH, WEST, SOUTH, EAST],
      format='netcdf'
  ), 'era5_data/OUTPUT_FILENAME.nc')
  print('Downloaded: era5_data/OUTPUT_FILENAME.nc')
  5. Report the actual downloaded file path in the Final Answer.

 INTELLIGENT AGENT SELECTION GUIDELINES:
- For HISTORY/REANALYSIS (Past weather/climate) → Use **ERA5** (via Simulation Agents).
- For FUTURE PROJECTIONS (Climate Change) → Use **CMIP6** (via Simulation Agents).
- For SATELLITE IMAGERY/OBSERVATIONS → Use **NASA CMR Agent**.
- For DISASTER/EMERGENCY DATA → Use **FEMA Agent**.
- For URBAN/CITY COMPLAINTS (311) → Use **US 311 Agent**.
- For NYC STREET FLOOD SENSOR readings → Use **FloodNet Agent**.
- For FLOOD SIMULATION / BENCHMARK data (ML training) → Use **FloodSimBench Agent**.
- For RADAR PRECIPITATION / QPE / SEVERE WEATHER products → Use **MRMS Agent**.
- For COMPARING Models vs Sats → Use **Comparison Agent**.

FLEXIBLE WORKFLOW PHILOSOPHY:
- START with specific queries to the relevant agents.
- USE 'capture_user_query' ONLY ONCE if critical details (region, year, variable) are missing AND the user has NOT already approved or said to proceed.
- If the user says "I Approve", "Proceed", "Yes", "Continue", or any approval message: DO NOT ask for clarification again. Immediately proceed using REASONABLE DEFAULTS (e.g., last 5 years, contiguous US, common variables like temperature/precipitation). Never loop asking the same questions after an approval.
- COORDINATE the flow: Metadata -> Download -> Analysis.

ERROR HANDLING & CLARIFICATION:
- If a tool fails with a recoverable error (e.g., "License required", "Missing credentials"):
  1. EXPLAIN to the user exactly what they need to do.
  2. STOP and Ask the user to confirm using 'Final Answer'.
- If a tool returns "STOP_EXECUTION_AND_ASK_USER":
  1. This means the tool needs user input (e.g., choice of year/location) and cannot proceed.
  2. IMMEDIATELY output the tool's question as your 'Final Answer'.
  3. Do NOT make up an answer. STOP effectively so the user can reply.
- If execute_analysis_code returns "Error executing code:" or any Python traceback:
  1. Show the EXACT error message to the user in your Final Answer. Do NOT hide it.
  2. Do NOT call acquire_simulation_data or query_simulation_metadata as a fallback.
  3. If the error mentions "cdsapi", "401", "403", "connection", or "authentication":
     - Tell the user the CDS API request failed and show the error.
     - Suggest they verify their CDS API key at https://cds.climate.copernicus.eu/
  4. If the error mentions "FileNotFoundError":
     - IDENTIFY which data source the file likely came from.
     - Use the appropriate data acquisition agent to download the data first.
     - Then re-run execute_analysis_code with the correct file path.
- If execute_analysis_code returns output containing "Downloaded:" or file paths:
  1. The download succeeded. Report the file paths to the user as Final Answer.

NEGATIVE CONSTRAINTS (STRICT):
1. **NO UNREQUESTED FALLBACKS**: If a specialized agent says it cannot support a city/region, DO NOT attempt to query a different city.
   - *Bad*: "Miami is not supported, so here is data for NYC instead."
   - *Good*: "The 311 Agent currently only supports NYC, Chicago, SF, and Austin. I cannot provide data for Miami."
2. **NO SUBSTITUTIONS**: If the user asks for City A, and it is not supported, DO NOT switch to City B.
   - *Bad*: "Florida is not supported. I will check NYC instead."
   - *Good*: "Florida is not supported. Stopping."

**HUMAN-IN-THE-LOOP (MANDATORY):**
- Before performing any **complex data acquisition** (downloading large files, running long analysis) or if the request is ambiguous:
  1. **STOP** execution.
  2. **PROPOSE** a concrete plan to the user.
  3. Use the special Final Answer format: `STOP_EXECUTION_AND_ASK_USER: <Your Plan Here>`
  4. Wait for the user to click "Approve" or provide feedback.
  - Example: `STOP_EXECUTION_AND_ASK_USER: I plan to download ERA5 temperature data for NYC (2020-2021). Approximate size: 50MB. Do you approve?`

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous Conversation:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)

    agent = create_react_agent(llm, all_tools, prompt)

    memory = ConversationBufferWindowMemory(
        k=15,
        return_messages=True,
        memory_key="chat_history"
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=100,
        max_execution_time=1200
    )

    return agent_executor

if __name__ == "__main__":
    print(" CLIMATE RESEARCH ORCHESTRATOR (UPDATED)")
    print("=" * 60)
    print(" Master Coordinator for ERA5, CMIP6, and Observational Data")
    
    orchestrator = create_climate_research_orchestrator()
    
    if orchestrator:
        print(" Orchestrator initialized successfully!")
        #test_query = "Find and download FEMA flood data for New York City in 2021"
        test_query = "Find and download ERA5 temperature data for New York City in 2020"
        print(f"\n Testing with query: '{test_query}'")
        
        try:
            result = orchestrator.invoke({"input": test_query})
            print("\n Orchestrator execution complete.")
            print(f" Result: {result.get('output')}")
        except Exception as e:
            print(f" Execution error: {e}")
    else:
        print(" Failed to initialize orchestrator.")
