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
def get_simulation_kg_agent():
    """Get Simulation Knowledge Graph agent - works with .py files or same kernel"""
    if 'get_simulation_agent' in globals():
        return globals()['get_simulation_agent']()
    
    try:
        from simulation_kg_agent import get_simulation_agent
        return get_simulation_agent()
    except ImportError:
        pass
    
    # Fallback to Mock if file not found (for testing/safety)
    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "Simulation KG Agent (Mock): Would query ERA5/CMIP6 metadata."}
    return WorkingMockAgent()

def get_simulation_data_agent():
    """Get Simulation Data Acquisition agent - works with .py files or same kernel"""
    if 'get_simulation_data_acquisition_agent' in globals():
        return globals()['get_simulation_data_acquisition_agent']()
    
    try:
        from simulation_data_acquisition_agent import get_simulation_data_acquisition_agent
        return get_simulation_data_acquisition_agent()
    except ImportError:
        pass
    
    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "Simulation Data Agent (Mock): Would download ERA5/CMIP6 data."}
    return WorkingMockAgent()

def get_nasa_cmr_agent():
    """Get NASA CMR agent - works with .py files or same kernel"""
    if 'create_nasa_cmr_agent' in globals():
        return globals()['create_nasa_cmr_agent']()
    
    try:
        # Try importing the V1 version first (prioritized for Streamlit app)
        from nasa_cmr_data_acquisition_agent_V1 import create_nasa_cmr_agent
        return create_nasa_cmr_agent()
    except ImportError:
        pass

    try:
        from nasa_cmr_data_acquisition_agent import create_nasa_cmr_agent
        return create_nasa_cmr_agent()
    except ImportError:
        pass
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython and hasattr(ipython, 'user_ns'):
            if 'create_nasa_cmr_agent' in ipython.user_ns:
                return ipython.user_ns['create_nasa_cmr_agent']()
    except:
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
    except ImportError:
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
    except ImportError:
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
    except ImportError:
        pass
    
    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "FEMA Agent (Mock): Would search/download FEMA data."}
    return WorkingMockAgent()

def get_us_311_agent():
    """Get US 311 Data Agent - works with .py files or same kernel"""
    if 'get_311_agent' in globals():
        return globals()['get_311_agent']()
    
    try:
        from us_city_311_data_acquisition_agent import get_311_agent
        return get_311_agent()
    except ImportError:
        pass
    
    class WorkingMockAgent:
        def invoke(self, inputs):
            return {"output": "US 311 Agent (Mock): Would search/download 311 data."}
    return WorkingMockAgent()


BEDROCK_REGION = "us-east-2"
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

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
    description: str = "Ask specific, targeted questions to gather missing research details. Examples: 'What geographic coordinates?', 'What time period?', 'Which variables?'. Use this to ask NEW questions."
    
    def _run(self, query_prompt: str = "What climate research question would you like to investigate?",  run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
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
            response = agent.invoke({"input": query})
            return response.get('output', 'No output from FEMA agent')
        except Exception as e:
            return f" FEMA Agent error: {str(e)}"

class CallUs311Agent(BaseTool):
    """Call US 311 Data Acquisition Agent to search and download service request data."""
    name: str = "acquire_311_data"
    description: str = "Call US 311 Agent to find and download CITY SERVICE REQUEST data (Complaints, Noise, Potholes, etc.) for supported US cities (NYC, Chicago, SF, Austin). Input: 'Find 311 noise complaints in Chicago for 2023'."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_us_311_agent()
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
    description: str = "Execute custom Python code for climate data analysis using REAL climate data only. NEVER create fake data. Load data first using specialized agents."
    
    def _run(self, code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            output = f" CLIMATE ANALYSIS CODE EXECUTION\n"
            output += "=" * 50 + "\n\n"
            
            # Security checks
            forbidden_patterns = ['fake_data', 'placeholder', 'dummy_data', 'simulated_data']
            if any(p in code.lower() for p in forbidden_patterns):
                return "REJECTED: usage of placeholder/fake data patterns detected."

            # Execution
            import io
            from contextlib import redirect_stdout, redirect_stderr
            import traceback
            
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            exec_namespace = {'__builtins__': __builtins__}
            # Add common libs if available
            for lib in ['numpy', 'xarray', 'pandas', 'matplotlib.pyplot']:
                try:
                    if lib == 'matplotlib.pyplot':
                        import matplotlib
                        matplotlib.use('Agg')
                        import matplotlib.pyplot as plt
                        exec_namespace['plt'] = plt
                    else:
                        mod = __import__(lib.split('.')[0])
                        if '.' in lib:
                            mod = getattr(mod, lib.split('.')[1])
                        exec_namespace[lib.split('.')[-1]] = mod
                except ImportError:
                    pass

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, exec_namespace)
            
            # --- Auto-Save Plots Fix ---
            # If the user created a plot but didn't save it (or tried plt.show()), save it now.
            if 'plt' in exec_namespace:
                plt = exec_namespace['plt']
                if plt.get_fignums():
                    import time
                    timestamp = int(time.time())
                    # Save all open figures
                    for i, fignum in enumerate(plt.get_fignums()):
                        fig = plt.figure(fignum)
                        filename = f"analysis_plot_{timestamp}_{i}.png"
                        fig.savefig(filename)
                        output += f"\n[System] Auto-saved plot to: {filename}\n"
                        plt.close(fig) # Close to potential memory leaks
            
            val_out = stdout_capture.getvalue()
            val_err = stderr_capture.getvalue()

            
            if val_out: output += f"STDOUT:\n{val_out}\n"
            if val_err: output += f"STDERR:\n{val_err}\n"
            
            return output
        except Exception as e:
            import traceback
            return f"Error executing code: {e}\n{traceback.format_exc()}"


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
- query_nasa_cmr_datasets (NASA CMR Agent): Search and load OBSERVATIONAL satellite data (MODIS, GOES, etc.) from NASA CMR.
- acquire_fema_data (FEMA Agent): Search and download DISASTER data (Floods, Declarations) from OpenFEMA.
- acquire_311_data (US 311 Agent): Search and download 311 SERVICE REQUEST data (Noise, Potholes, etc.) from NYC, Chicago, SF, Austin.

 **ANALYSIS AGENTS:**
- compare_simulation_obs: Compare simulation (ERA5/CMIP6) vs observations.
- verify_research_workflow: Validate scientific rigor.
- execute_analysis_code: specialized Python execution for analysis.

 CRITICAL DATA ACQUISITION WORKFLOW (SIMULATION):
1. **query_simulation_metadata**: Find "ERA5 temperature 2020" -> Returns IDs (e.g., "ERA5::...").
2. **acquire_simulation_data**: "Download ERA5::... for [region]" -> Downloads NetCDF files.
3. **execute_analysis_code**: Load and analyze the downloaded NetCDF files.

 INTELLIGENT AGENT SELECTION GUIDELINES:
- For HISTORY/REANALYSIS (Past weather/climate) → Use **ERA5** (via Simulation Agents).
- For FUTURE PROJECTIONS (Climate Change) → Use **CMIP6** (via Simulation Agents).
- For SATELLITE IMAGERY/OBSERVATIONS → Use **NASA CMR Agent**.
- For DISASTER/EMERGENCY DATA → Use **FEMA Agent**.
- For URBAN/CITY COMPLAINTS (311) → Use **US 311 Agent**.
- For COMPARING Models vs Sats → Use **Comparison Agent**.

FLEXIBLE WORKFLOW PHILOSOPHY:
- START with specific queries to the relevant agents.
- USE 'capture_user_query' if details (region, year, variable) are missing.
- COORDINATE the flow: Metadata -> Download -> Analysis.

ERROR HANDLING & CLARIFICATION:
- If a tool fails with a recoverable error (e.g., "License required", "Missing credentials"):
  1. EXPLAIN to the user exactly what they need to do.
  2. STOP and Ask the user to confirm using 'Final Answer'.
- If a tool returns "STOP_EXECUTION_AND_ASK_USER":
  1. This means the tool needs user input (e.g., choice of year/location) and cannot proceed.
  2. IMMEDIATELY output the tool's question as your 'Final Answer'.
  3. Do NOT make up an answer. STOP effectively so the user can reply.

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
        max_iterations=150,
        max_execution_time=900
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
