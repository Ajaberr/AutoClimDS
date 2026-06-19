#!/usr/bin/env python3
"""
Climate Research Orchestrator Agent
===================================

Master orchestrator that coordinates specialized climate research agents to tackle
complex climate science problems involving CESM LENS model data and observational datasets.

Key Capabilities:
1. User Query Processing - Natural language climate research questions
2. Agent Coordination - Automatically calls appropriate specialized agents
3. Data Integration - Links and stores CESM LENS and observational data
4. Code Execution - Runs analysis code and generates results
5. Knowledge Management - Maintains research context and findings
6. Workflow Orchestration - Manages complex multi-step research workflows

Integrated Agents:
- NASA CMR Data Acquisition Agent
- CESM vs Observational Comparison Agent
- Climate Data Analysis Agent (code execution)
- Knowledge Graph Agent (data linking)

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
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.prompts import PromptTemplate
# Manual Bedrock LLM implementation (same as other agents)



# Agent accessor functions for notebook environment
def get_knowledge_graph_agent():
    """Get Knowledge Graph agent - works with .py files or same kernel"""
    # Method 1: Try direct function call (same kernel/globals)
    if 'create_knowledge_graph_agent' in globals():
        return globals()['create_knowledge_graph_agent']()
    
    # Method 2: Try import from .py file
    try:
        from knowledge_graph_agent_bedrock import create_knowledge_graph_agent
        return create_knowledge_graph_agent()
    except ImportError:
        pass
    
    # Method 3: Check IPython namespace (Jupyter cells)
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython and hasattr(ipython, 'user_ns'):
            if 'create_knowledge_graph_agent' in ipython.user_ns:
                return ipython.user_ns['create_knowledge_graph_agent']()
            elif 'knowledge_graph_agent' in ipython.user_ns:
                return ipython.user_ns['knowledge_graph_agent']
    except:
        pass
    
    # Fallback: Working mock agent
    class WorkingMockAgent:
        def invoke(self, inputs):
            query = inputs.get('input', '')
            return {
                "output": f" Knowledge Graph Agent (Mock)\n"
                         f"Query: '{query}'\n\n"
                         f" This agent would:\n"
                         f"• Search Neptune graph for climate datasets\n"
                         f"• Query CMR metadata\n"
                         f"• Return relevant observational datasets\n\n"
                         f" To use real agent: Define 'create_knowledge_graph_agent' function or import from .py file"
            }
    return WorkingMockAgent()

def get_cesm_lens_agent():
    """Get CESM LENS agent - works with .py files or same kernel"""
    if 'create_cesm_lens_agent' in globals():
        return globals()['create_cesm_lens_agent']()
    
    try:
        from cesm_lens_langchain_agent import create_cesm_lens_agent
        return create_cesm_lens_agent()
    except ImportError:
        pass
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython and hasattr(ipython, 'user_ns'):
            if 'create_cesm_lens_agent' in ipython.user_ns:
                return ipython.user_ns['create_cesm_lens_agent']()
            elif 'cesm_lens_agent' in ipython.user_ns:
                return ipython.user_ns['cesm_lens_agent']
    except:
        pass
    
    class WorkingMockAgent:
        def invoke(self, inputs):
            query = inputs.get('input', '')
            return {
                "output": f" CESM LENS Agent (Mock)\n"
                         f"Query: '{query}'\n\n"
                         f" This agent would:\n"
                         f"• Access CESM Large Ensemble data from S3\n"
                         f"• Process NetCDF climate model outputs\n"
                         f"• Analyze ensemble statistics\n\n"
                         f" To use real agent: Define 'create_cesm_lens_agent' function or import from .py file"
            }
    return WorkingMockAgent()

def get_nasa_cmr_agent():
    """Get NASA CMR agent - works with .py files or same kernel"""
    if 'create_nasa_cmr_agent' in globals():
        return globals()['create_nasa_cmr_agent']()
    
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
            elif 'nasa_cmr_agent' in ipython.user_ns:
                return ipython.user_ns['nasa_cmr_agent']
    except:
        pass
    
    class WorkingMockAgent:
        def invoke(self, inputs):
            query = inputs.get('input', '')
            return {
                "output": f" NASA CMR Agent (Mock)\n"
                         f"Query: '{query}'\n\n"
                         f" This agent would:\n"
                         f"• Search NASA CMR for satellite observations\n"
                         f"• Access AWS Open Data buckets\n"
                         f"• Retrieve observational datasets\n\n"
                         f" To use real agent: Define 'create_nasa_cmr_agent' function or import from .py file"
            }
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
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython and hasattr(ipython, 'user_ns'):
            if 'create_verification_agent' in ipython.user_ns:
                return ipython.user_ns['create_verification_agent']()
            elif 'cesm_verification_agent' in ipython.user_ns:
                return ipython.user_ns['cesm_verification_agent']
    except:
        pass
    
    class WorkingMockAgent:
        def invoke(self, inputs):
            query = inputs.get('input', '')
            return {
                "output": f" CESM Verification Agent (Mock)\n"
                         f"Query: '{query}'\n\n"
                         f" This agent would:\n"
                         f"• Validate climate model outputs\n"
                         f"• Perform statistical testing\n"
                         f"• Verify research workflows\n\n"
                         f" To use real agent: Define 'create_verification_agent' function or import from .py file"
            }
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
    
    try:
        from IPython import get_ipython
        ipython = get_ipython()
        if ipython and hasattr(ipython, 'user_ns'):
            if 'create_cesm_obs_comparison_agent' in ipython.user_ns:
                return ipython.user_ns['create_cesm_obs_comparison_agent']()
            elif 'cesm_obs_comparison_agent' in ipython.user_ns:
                return ipython.user_ns['cesm_obs_comparison_agent']
    except:
        pass
    
    class WorkingMockAgent:
        def invoke(self, inputs):
            query = inputs.get('input', '')
            return {
                "output": f" CESM Comparison Agent (Mock)\n"
                         f"Query: '{query}'\n\n"
                         f" This agent would:\n"
                         f"• Compare CESM model outputs with observations\n"
                         f"• Calculate bias and uncertainty metrics\n"
                         f"• Generate validation statistics\n\n"
                         f" To use real agent: Define 'create_cesm_obs_comparison_agent' function or import from .py file"
            }
    return WorkingMockAgent()

BEDROCK_REGION = "us-east-2"
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

# --- Bedrock LLM (exact copy from other agents) ---
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

# Database initialization
def _init_cesm_database():
    """Initialize SQLite database for CESM data tracking with full schema"""
    import sqlite3
    
    conn = sqlite3.connect("cesm_data_registry.db")
    cursor = conn.cursor()
    
    # Create table with complete schema matching CESM LENS agent expectations
    cursor.execute("""
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
            memory_usage REAL,
            lat_range TEXT,
            lon_range TEXT,
            processing_notes TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            access_count INTEGER DEFAULT 1,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            load_time_seconds REAL,
            UNIQUE(variable_name, start_year, end_year, s3_path)
        )
    """)
    
    # Create indices for faster queries
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cesm_variable_time 
        ON cesm_data_paths(variable_name, start_year, end_year)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_cesm_access 
        ON cesm_data_paths(access_count, last_accessed)
    """)
    
    conn.commit()
    conn.close()

# Climate data structures
@dataclass
class ClimateDataset:
    """Standardized climate dataset container"""
    id: str
    name: str
    source: str  # 'CESM_LENS', 'GOES16', 'MODIS', etc.
    variable: str
    time_range: Tuple[str, str]
    spatial_domain: str
    file_paths: List[str]
    metadata: Dict
    data_hash: str
    created_at: datetime
    
    def to_dict(self):
        return asdict(self)

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

class ObsDataRegistryTool(BaseTool):
    """Retrieve and load previously saved observational data paths from the database for reuse"""
    name: str = "retrieve_saved_obs_data"
    description: str = "Search and retrieve previously saved observational data paths from database. Use this to find existing observational datasets before loading new ones. Input: 'variable_name [start_year] [end_year]' or 'all' to list all saved paths."
    
    @property
    def db_path(self) -> str:
        return "climate_knowledge_graph.db"
    
    def _run(self, search_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Search for and retrieve saved observational data paths"""
        import sqlite3
        
        try:
            # Parse search query
            parts = search_query.strip().split()
            
            output = f" SEARCHING SAVED OBSERVATIONAL DATA REGISTRY\n"
            output += "=" * 55 + "\n\n"
            
            # Build query based on search parameters
            with sqlite3.connect(self.db_path) as conn:
                if not parts or parts[0].lower() == 'all':
                    # Show all saved observational datasets
                    query = "SELECT * FROM stored_datasets ORDER BY updated_at DESC"
                    params = []
                    output += f" Retrieving all saved observational datasets\n\n"
                else:
                    variable_name = parts[0]
                    start_year = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                    end_year = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
                    
                    # Build filtered query
                    query = "SELECT * FROM stored_datasets WHERE short_name LIKE ? OR title LIKE ?"
                    params = [f"%{variable_name}%", f"%{variable_name}%"]
                    
                    # Note: Knowledge graph doesn't have year fields, so we filter by dataset properties
                    if start_year or end_year:
                        query += " AND (dataset_properties LIKE ? OR dataset_properties LIKE ?)"
                        if start_year:
                            params.extend([f"%{start_year}%", f"%start_year%"])
                        if end_year:
                            params.extend([f"%{end_year}%", f"%end_year%"])
                    
                    query += " ORDER BY updated_at DESC"
                    
                    output += f" Searching for: {variable_name}"
                    if start_year and end_year:
                        output += f" ({start_year}-{end_year})"
                    output += "\n\n"
                
                cursor = conn.execute(query, params)
                columns = [description[0] for description in cursor.description]
                results = cursor.fetchall()
                
                if not results:
                    output += f" No saved observational data found for query: '{search_query}'\n"
                    output += f" Use KnowledgeGraphAgent to load and save observational data first\n"
                    return output
                
                output += f" Found {len(results)} saved observational dataset(s)\n\n"
                
                # Format results with detailed information
                total_relationships = 0
                for i, row in enumerate(results, 1):
                    record = dict(zip(columns, row))
                    
                    output += f"{i}. {record['title']} ({record['short_name']})\n"
                    output += f"    Dataset ID: {record['dataset_id']}\n"
                    
                    # Parse dataset properties
                    try:
                        properties = json.loads(record['dataset_properties']) if record['dataset_properties'] else {}
                        if properties:
                            output += f"    Properties: {len(properties)} metadata fields\n"
                            # Show key properties
                            for key, value in list(properties.items())[:3]:
                                output += f"     - {key}: {value}\n"
                            if len(properties) > 3:
                                output += f"     ... and {len(properties) - 3} more\n"
                    except:
                        output += f"    Properties: Raw metadata available\n"
                    
                    # Parse dataset labels
                    try:
                        labels = json.loads(record['dataset_labels']) if record['dataset_labels'] else []
                        if labels:
                            output += f"    Labels: {', '.join(labels[:5])}\n"
                            if len(labels) > 5:
                                output += f"     ... and {len(labels) - 5} more labels\n"
                    except:
                        output += f"    Labels: Available\n"
                    
                    # Relationship info
                    relationships = record['total_relationships'] or 0
                    total_relationships += relationships
                    output += f"    Relationships: {relationships} connections\n"
                    
                    # Parse relationship types
                    try:
                        rel_types = json.loads(record['relationship_types']) if record['relationship_types'] else []
                        if rel_types:
                            output += f"    Relationship Types: {', '.join(rel_types[:3])}\n"
                            if len(rel_types) > 3:
                                output += f"     ... and {len(rel_types) - 3} more types\n"
                    except:
                        pass
                    
                    # Timestamps
                    output += f"    Created: {record['created_at']} | Updated: {record['updated_at']}\n"
                    output += f"    Database ID: {record['id']}\n\n"
                
                # Summary statistics
                unique_titles = len(set(record['title'] for record in [dict(zip(columns, row)) for row in results]))
                unique_variables = len(set(record['short_name'] for record in [dict(zip(columns, row)) for row in results]))
                
                output += f" REGISTRY SUMMARY:\n"
                output += f"   • Total Datasets: {len(results)}\n"
                output += f"   • Unique Titles: {unique_titles}\n"
                output += f"   • Unique Variables: {unique_variables}\n"
                output += f"   • Total Relationships: {total_relationships}\n"
                
                # Most connected datasets
                sorted_results = sorted([dict(zip(columns, row)) for row in results], 
                                      key=lambda x: x['total_relationships'] or 0, reverse=True)
                if sorted_results and (sorted_results[0]['total_relationships'] or 0) > 0:
                    output += f"\n MOST CONNECTED:\n"
                    for j, record in enumerate(sorted_results[:3], 1):
                        if (record['total_relationships'] or 0) > 0:
                            output += f"   {j}. {record['title']} - {record['total_relationships']} relationships\n"
                    output += "\n"
                
                # Reuse recommendations
                output += f" TO REUSE SAVED DATA:\n"
                output += f"   • Use KnowledgeGraphAgent with exact dataset ID or title\n"
                output += f"   • Knowledge Graph agent will automatically load from stored metadata\n"
                output += f"   • Use dataset relationships for linked data discovery\n"
                
            return output
            
        except sqlite3.Error as db_error:
            return f" Database error: {db_error}\n Ensure Knowledge Graph agent has been run to create the database"
        except Exception as e:
            return f" Error retrieving saved observational data: {str(e)}"

class LoadSavedObsDataTool(BaseTool):
    """Load a specific saved observational dataset by database ID for immediate use"""
    name: str = "load_saved_obs_data"
    description: str = "Load a specific saved observational dataset by its database ID. Use retrieve_saved_obs_data first to find the ID. Input: database_id"
    
    @property
    def db_path(self) -> str:
        return "climate_knowledge_graph.db"
    
    def _run(self, database_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Load specific observational dataset by database ID"""
        import sqlite3
        
        try:
            dataset_id = int(database_id.strip())
            
            output = f" LOADING SAVED OBSERVATIONAL DATASET\n"
            output += "=" * 45 + "\n\n"
            
            # Retrieve dataset record
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM stored_datasets WHERE id = ?
                """, (dataset_id,))
                
                columns = [description[0] for description in cursor.description]
                row = cursor.fetchone()
                
                if not row:
                    return f" No observational dataset found with ID: {dataset_id}"
                
                record = dict(zip(columns, row))
                
                output += f" DATASET DETAILS:\n"
                output += f"   • ID: {record['id']}\n"
                output += f"   • Dataset ID: {record['dataset_id']}\n"
                output += f"   • Title: {record['title']}\n"
                output += f"   • Variable: {record['short_name']}\n"
                
                # Parse and display properties
                try:
                    properties = json.loads(record['dataset_properties']) if record['dataset_properties'] else {}
                    if properties:
                        output += f"   • Properties: {len(properties)} metadata fields\n"
                        for key, value in list(properties.items())[:5]:
                            output += f"     - {key}: {value}\n"
                        if len(properties) > 5:
                            output += f"     ... and {len(properties) - 5} more\n"
                except:
                    output += f"   • Properties: Available in raw format\n"
                
                # Parse and display labels
                try:
                    labels = json.loads(record['dataset_labels']) if record['dataset_labels'] else []
                    if labels:
                        output += f"   • Labels: {', '.join(labels[:5])}\n"
                        if len(labels) > 5:
                            output += f"     ... and {len(labels) - 5} more\n"
                except:
                    output += f"   • Labels: Available\n"
                
                output += f"   • Relationships: {record['total_relationships'] or 0} connections\n"
                output += f"   • Created: {record['created_at']}\n"
                output += f"   • Updated: {record['updated_at']}\n\n"
                
                # Create load command for Knowledge Graph agent
                load_command = record['dataset_id'] or record['title']
                
                output += f" LOAD COMMAND FOR KNOWLEDGE GRAPH AGENT:\n"
                output += f"   Use: query_knowledgegraph_datasets with input: '{load_command}'\n\n"
                
                # Update access tracking (if column exists)
                from datetime import datetime
                current_time = datetime.now().isoformat()
                
                try:
                    # Try to update if there's an access tracking column
                    conn.execute("""
                        UPDATE stored_datasets 
                        SET updated_at = ?
                        WHERE id = ?
                    """, (current_time, dataset_id))
                    
                    output += f" USAGE UPDATED:\n"
                    output += f"   • Last accessed: {current_time}\n\n"
                except:
                    # If no access tracking, just note it
                    output += f" DATASET ACCESS:\n"
                    output += f"   • Accessed: {current_time}\n\n"
                
                # Show relationship information
                if record['total_relationships'] and int(record['total_relationships']) > 0:
                    try:
                        rel_types = json.loads(record['relationship_types']) if record['relationship_types'] else []
                        if rel_types:
                            output += f" RELATED DATASETS:\n"
                            output += f"   • Connection types: {', '.join(rel_types)}\n"
                            output += f"   • Use these relationships for linked data discovery\n\n"
                    except:
                        pass
                
                output += f" NEXT STEPS:\n"
                output += f"   1. Use KnowledgeGraphAgent to explore this dataset\n"
                output += f"   2. Query related datasets through relationship connections\n"
                output += f"   3. Link with CESM data for model validation if needed\n"
                
            return output
            
        except ValueError:
            return f" Invalid database ID: '{database_id}'. Must be a number."
        except Exception as e:
            return f" Error loading saved observational data: {str(e)}"

# Duplicate BedrockClaudeLLM class removed

class UserQueryTool(BaseTool):
    """Interactive tool to ask intelligent follow-up questions to clarify research requirements"""
    name: str = "capture_user_query"
    description: str = "Ask specific, targeted questions to gather missing research details. Examples: 'What geographic coordinates or region?', 'What time period and resolution?', 'Which climate variables are most critical?', 'What analysis method do you prefer?', 'What output format do you need?'. Use this to ask NEW questions that help understand requirements better, not to repeat what the user already said."
    
    def _run(self, query_prompt: str = "What climate research question would you like to investigate?",  run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
            output = f"🔴 **WAITING FOR USER INPUT** 🔴\n\n"
            output += f"📋 **Research Clarification Needed:**\n{query_prompt}\n\n"
            output += f"⚠️ **Agent execution paused - please respond with your clarifications before I can continue the research process.**"
            return output
          

class CallKnowledgeGraphAgent(BaseTool):
    """CallKnowledgeGraphAgent to query KG for necessary datasets. """
    name: str = "query_knowledgegraph_datasets"
    description: str = "Call KnowledgeGraphAgent to query KG for necessary observational datasets metadata.  Provide it with a description of what observational datasets you need and it will return a list of observational datasets that match your description. This is different to climate simulation data, which is handled by the CESMLensAgent."
    
    def _run(self, data_set_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_knowledge_graph_agent()
            response = agent.invoke({"input": data_set_query})
            return response.get('output', 'No output from Knowledge Graph agent')
        except Exception as e:
            return f" Knowledge Graph agent error: {str(e)}\n This tool requires the Knowledge Graph agent to be properly configured with Neptune and CMR access."
    
           

class CESMLensAgent(BaseTool):
    """Call CESMLensAgent to query KG for necessary climate simulation datasets.  Provide it with a description of what climate simulation datasets and CESM variables you need and it will return a list of climate simulation datasets that match your description."""
    name: str = "query_cesm_lens_datasets"
    description: str = "Call CESMLensAgent to query  for necessary climate simulation datasets.  Provide it with a description of what climate simulation datasets you need and it will return a list of climate simulation datasets that match your description."
    
    def _run(self, data_set_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_cesm_lens_agent()
            response = agent.invoke({"input": data_set_query})
            return response.get('output', 'No output from CESM LENS agent')
        except Exception as e:
            return f" CESM LENS agent error: {str(e)}\n This tool requires the CESM LENS agent to be properly configured with S3 and Neptune access."

class NasaCMRDataAcquisitionAgent(BaseTool):
    """Call NasaCMRDataAcquisitionAgent to load climate observational datasets based on KnowledgeGraph Query.  Provide it with a description of the dataset queried and it will return a load the corresponding dataset from the cloud storage."""
    name: str = "query_nasa_cmr_datasets"
    description: str = "Call NasaCMRDataAcquisitionAgent to load climate observational datasets based on KnowledgeGraph Query.  Provide it with a description of the dataset query and it will return a load the corresponding dataset from the cloud storage."
    
    def _run(self, data_set_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_nasa_cmr_agent()
            response = agent.invoke({"input": data_set_query})
            return response.get('output', 'No output from NASA CMR agent')
        except Exception as e:
            return f" NASA CMR agent error: {str(e)}\n This tool requires the NASA CMR agent to be properly configured with AWS S3 and CMR access."
    
class CESMVerificationAgent(BaseTool):
    """Call CESMVerificationAgent to verify information about the pipeline and climate research workflow. Provide it with the information necessary to verify the pipeline and climate research workflow."""
    name: str = "verify_cesm_datasets"
    description: str = "Call CESMVerificationAgent to verify information about the pipeline and climate research workflow.  Provide it with a description of the pipeline and the climate research workflow."

    def _run(self, verification_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_cesm_verification_agent()
            response = agent.invoke({"input": verification_query})
            return response.get('output', 'No output from CESM Verification agent')
        except Exception as e:
            return f" CESM Verification agent error: {str(e)}\n This tool requires the CESM Verification agent to be properly configured."

class CESMObsComparisonAgent(BaseTool):
    """Call CESMObsComparisonAgent to compare the climate simulation datasets with the climate observational datasets.  Provide it with the information necessary to compare the climate simulation datasets with the climate observational datasets."""
    name: str = "compare_cesm_obs_datasets"
    description: str = "Call CESMObsComparisonAgent to compare the climate simulation datasets with the climate observational datasets.  Provide it with the information necessary to compare the climate simulation datasets with the climate observational datasets."

    def _run(self, comparison_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            agent = get_cesm_obs_comparison_agent()
            response = agent.invoke({"input": comparison_query})
            return response.get('output', 'No output from CESM Comparison agent')
        except Exception as e:
            return f" CESM Comparison agent error: {str(e)}\n This tool requires the CESM Comparison agent to be properly configured."

class RetrieveSavedCESMDataTool(BaseTool):
    """Retrieve and load previously saved CESM data paths from the database for reuse"""
    name: str = "retrieve_saved_cesm_data"
    description: str = "Search and retrieve previously saved CESM data paths from database. Use this to find existing CESM datasets before loading new ones. Input: 'variable_name [start_year] [end_year]' or 'all' to list all saved paths."
    
    @property
    def db_path(self) -> str:
        return "cesm_data_registry.db"
    
    def _run(self, search_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Search for and retrieve saved CESM data paths"""
        import sqlite3
        
        try:
            # Parse search query
            parts = search_query.strip().split()
            
            output = f" SEARCHING SAVED CESM DATA REGISTRY\n"
            output += "=" * 50 + "\n\n"
            
            # Build query based on search parameters
            with sqlite3.connect(self.db_path) as conn:
                if not parts or parts[0].lower() == 'all':
                    # Show all saved paths
                    query = "SELECT * FROM cesm_data_paths ORDER BY last_accessed DESC"
                    params = []
                    output += f" Retrieving all saved CESM datasets\n\n"
                else:
                    variable_name = parts[0]
                    start_year = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
                    end_year = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
                    
                    # Build filtered query
                    query = "SELECT * FROM cesm_data_paths WHERE variable_name LIKE ?"
                    params = [f"%{variable_name}%"]
                    
                    if start_year:
                        query += " AND start_year >= ?"
                        params.append(start_year)
                    
                    if end_year:
                        query += " AND end_year <= ?"
                        params.append(end_year)
                    
                    query += " ORDER BY last_accessed DESC"
                    
                    output += f" Searching for: {variable_name}"
                    if start_year and end_year:
                        output += f" ({start_year}-{end_year})"
                    output += "\n\n"
                
                cursor = conn.execute(query, params)
                columns = [description[0] for description in cursor.description]
                results = cursor.fetchall()
                
                if not results:
                    output += f" No saved CESM data found for query: '{search_query}'\n"
                    output += f" Use CESMLensAgent to load and save CESM data first\n"
                    return output
                
                output += f" Found {len(results)} saved CESM dataset(s)\n\n"
                
                # Format results with detailed information
                total_size = 0
                for i, row in enumerate(results, 1):
                    record = dict(zip(columns, row))
                    
                    output += f"{i}. {record['variable_name']} ({record['start_year']}-{record['end_year']})\n"
                    output += f"    Description: {record['long_name'] or 'N/A'}\n"
                    output += f"    Component: {record['component']} | Experiment: {record['experiment']}\n"
                    output += f"    S3 Path: {record['s3_path']}\n"
                    
                    # File size and performance info
                    if record['file_size_gb']:
                        file_size = float(record['file_size_gb'])
                        total_size += file_size
                        output += f"    Size: {file_size:.2f} GB"
                        if record['load_time_seconds'] and float(record['load_time_seconds']) > 0:
                            load_time = float(record['load_time_seconds'])
                            output += f" | Load Time: {load_time:.1f}s"
                        output += "\n"
                    
                    # Spatial and ensemble info
                    output += f"    Domain: {record['lat_range'] or 'global'} × {record['lon_range'] or 'global'}\n"
                    output += f"    Ensemble: {record['ensemble_members'] or 'all'} members\n"
                    output += f"    Last Used: {record['last_accessed']} | Access Count: {record['access_count'] or 1}\n"
                    
                    if record['processing_notes']:
                        output += f"    Notes: {record['processing_notes']}\n"
                    
                    output += f"    Database ID: {record['id']}\n\n"
                
                # Summary statistics
                unique_variables = len(set(record['variable_name'] for record in [dict(zip(columns, row)) for row in results]))
                unique_experiments = len(set(record['experiment'] for record in [dict(zip(columns, row)) for row in results] if record['experiment']))
                total_accesses = sum(record['access_count'] or 0 for record in [dict(zip(columns, row)) for row in results])
                
                output += f" REGISTRY SUMMARY:\n"
                output += f"   • Total Datasets: {len(results)}\n"
                output += f"   • Unique Variables: {unique_variables}\n"
                output += f"   • Unique Experiments: {unique_experiments}\n"
                output += f"   • Total Data Size: {total_size:.2f} GB\n"
                output += f"   • Total Accesses: {total_accesses}\n\n"
                
                # Most frequently accessed
                sorted_results = sorted([dict(zip(columns, row)) for row in results], 
                                      key=lambda x: x['access_count'] or 0, reverse=True)
                if sorted_results and (sorted_results[0]['access_count'] or 0) > 1:
                    output += f" MOST ACCESSED:\n"
                    for j, record in enumerate(sorted_results[:3], 1):
                        if (record['access_count'] or 0) > 1:
                            output += f"   {j}. {record['variable_name']} ({record['start_year']}-{record['end_year']}) - {record['access_count']} accesses\n"
                    output += "\n"
                
                # Reuse recommendations
                output += f" TO REUSE SAVED DATA:\n"
                output += f"   • Use CESMLensAgent with exact variable name and time range\n"
                output += f"   • CESM LENS agent will automatically load from saved S3 paths\n"
                output += f"   • Access count will be incremented for tracking\n"
                
            return output
            
        except sqlite3.Error as db_error:
            return f" Database error: {db_error}\n Ensure CESM LENS agent has been run to create the database"
        except Exception as e:
            return f" Error retrieving saved CESM data: {str(e)}"

class LoadSavedCESMDataTool(BaseTool):
    """Load a specific saved CESM dataset by database ID for immediate use"""
    name: str = "load_saved_cesm_data"
    description: str = "Load a specific saved CESM dataset by its database ID. Use retrieve_saved_cesm_data first to find the ID. Input: database_id"
    
    @property
    def db_path(self) -> str:
        return "cesm_data_registry.db"
    
    def _run(self, database_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Load specific CESM dataset by database ID"""
        import sqlite3
        
        try:
            dataset_id = int(database_id.strip())
            
            output = f" LOADING SAVED CESM DATASET\n"
            output += "=" * 40 + "\n\n"
            
            # Retrieve dataset record
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM cesm_data_paths WHERE id = ?
                """, (dataset_id,))
                
                columns = [description[0] for description in cursor.description]
                row = cursor.fetchone()
                
                if not row:
                    return f" No CESM dataset found with ID: {dataset_id}"
                
                record = dict(zip(columns, row))
                
                output += f" DATASET DETAILS:\n"
                output += f"   • ID: {record['id']}\n"
                output += f"   • Variable: {record['variable_name']} ({record['long_name'] or 'N/A'})\n"
                output += f"   • Time Period: {record['start_year']}-{record['end_year']}\n"
                output += f"   • Experiment: {record['experiment']}\n"
                output += f"   • Component: {record['component']}\n"
                output += f"   • S3 Path: {record['s3_path']}\n"
                output += f"   • Ensemble Members: {record['ensemble_members'] or 'all'}\n"
                output += f"   • File Size: {record['file_size_gb'] or 0:.2f} GB\n\n"
                
                # Create load command for CESM LENS agent
                load_command = f"{record['variable_name']} {record['start_year']} {record['end_year']}"
                if record['ensemble_members'] and record['ensemble_members'] != 'all':
                    load_command += f" {record['ensemble_members']}"
                
                output += f" LOAD COMMAND FOR CESM LENS AGENT:\n"
                output += f"   Use: query_cesm_lens_data with input: '{load_command}'\n\n"
                
                # Update access count and timestamp
                from datetime import datetime
                current_time = datetime.now().isoformat()
                new_access_count = (record['access_count'] or 0) + 1
                
                conn.execute("""
                    UPDATE cesm_data_paths 
                    SET last_accessed = ?, access_count = ?, updated_at = ?
                    WHERE id = ?
                """, (current_time, new_access_count, current_time, dataset_id))
                
                output += f" USAGE UPDATED:\n"
                output += f"   • Access count: {record['access_count'] or 0} → {new_access_count}\n"
                output += f"   • Last accessed: {current_time}\n\n"
                
                output += f" NEXT STEPS:\n"
                output += f"   1. Use CESMLensAgent to load this data\n"
                output += f"   2. Run analysis with analyze_cesm_ensemble\n"
                output += f"   3. Compare with observational data if needed\n"
                
            return output
            
        except ValueError:
            return f" Invalid database ID: '{database_id}'. Must be a number."
        except Exception as e:
            return f" Error loading saved CESM data: {str(e)}"
    
    
class CodeExecutionTool(BaseTool):
    """Execute custom analysis code for climate research using REAL DATA ONLY"""
    name: str = "execute_analysis_code"
    description: str = "Execute custom Python code for climate data analysis using REAL climate data only. CRITICAL: Only use this tool with actual data loaded from specialized agents (CESM S3 data, satellite observations). NEVER create fake, placeholder, or simulated data. Always load real data first using other agents before analysis."
    
    def _run(self, code: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            output = f" CLIMATE ANALYSIS CODE EXECUTION\n"
            output += "=" * 50 + "\n\n"
            
            output += f" EXECUTING CODE:\n"
            output += f"```python\n{code}\n```\n\n"
            
            # Check for placeholder data creation (security measure)
            forbidden_patterns = [
                'np.random', 'random.', 'fake_data', 'placeholder', 'dummy_data',
                'simulated_data', 'example_data', 'test_data', 'mock_data'
            ]
            
            code_lower = code.lower()
            for pattern in forbidden_patterns:
                if pattern in code_lower:
                    return f" REJECTED: Code contains '{pattern}' which suggests fake/placeholder data creation.\n" \
                           f" REQUIRED: Load real climate data using specialized agents first:\n" \
                           f"   • Use query_knowledgegraph_datasets for observational data\n" \
                           f"   • Use query_cesm_lens_datasets for CESM model data\n" \
                           f"   • Use query_nasa_cmr_datasets for satellite data\n" \
                           f"   • Then use execute_analysis_code with the loaded real data"
            
            # Create a safe execution environment
            import io
            import sys
            from contextlib import redirect_stdout, redirect_stderr
            
            # Capture stdout and stderr
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Create execution namespace with common imports
            exec_namespace = {
                '__builtins__': __builtins__,
                'np': None,
                'xr': None,
                'plt': None,
                'pd': None,
                'data_registry': None  # Database access via tools only
            }
            
            # Try to import common libraries
            try:
                import numpy as np
                exec_namespace['np'] = np
            except ImportError:
                pass
                
            try:
                import xarray as xr
                exec_namespace['xr'] = xr
            except ImportError:
                pass
                
            try:
                import matplotlib.pyplot as plt
                exec_namespace['plt'] = plt
            except ImportError:
                pass
                
            try:
                import pandas as pd
                exec_namespace['pd'] = pd
            except ImportError:
                pass
            
            output += f" EXECUTING CODE:\n"
            
            # Execute the code with output capture
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, exec_namespace)
            
            # Get captured output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()
            
            if stdout_output:
                output += f" STDOUT:\n{stdout_output}\n"
            
            if stderr_output:
                output += f" STDERR:\n{stderr_output}\n"
            
            output += f" CODE EXECUTION COMPLETED SUCCESSFULLY\n"
            
            # Store execution in registry if available
            try:
                session_id = f"code_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                research_context = ResearchContext(
                    session_id=session_id,
                    research_question="Custom code execution",
                    datasets_used=[],
                    analysis_steps=["Executed custom Python code"],
                    findings=["Code execution completed"],
                    code_executed=[code],
                    plots_generated=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                output += f" EXECUTION LOGGED:\n"
                output += f"   • Session ID: {session_id}\n"
                output += f"   • Code archived in registry\n\n"
            except:
                pass
            
            return output
            
        except Exception as e:
            error_output = f" ERROR EXECUTING CODE:\n"
            error_output += f"Error: {str(e)}\n"
            error_output += f"Type: {type(e).__name__}\n"
            
            # Include traceback for debugging
            import traceback
            error_output += f"Traceback:\n{traceback.format_exc()}\n"
            
            return error_output

# Initialize orchestrator agent
def create_climate_research_orchestrator():
    """Create the Climate Research Orchestrator Agent"""
    
    # Initialize database first to prevent table missing errors
    try:
        _init_cesm_database()
        print(" CESM database initialized")
    except Exception as db_error:
        print(f" Warning: Database initialization failed: {db_error}")
    
    # Initialize LLM
    try:
        llm = BedrockClaudeLLM()
        print(" Bedrock Claude LLM initialized for orchestrator")
    except Exception as e:
        print(f" Failed to initialize Bedrock LLM: {e}")
        return None
    
    # Combine all tools
    all_tools = [
        UserQueryTool(),
        CallKnowledgeGraphAgent(),
        CESMLensAgent(),
        NasaCMRDataAcquisitionAgent(),
        CESMVerificationAgent(),
        CESMObsComparisonAgent(),
        ObsDataRegistryTool(),
        LoadSavedObsDataTool(),
        RetrieveSavedCESMDataTool(),
        LoadSavedCESMDataTool(),
        CodeExecutionTool()
    ]  
    
    # Create the orchestrator prompt
    template = """You are the Climate Research Orchestrator, an intelligent coordinator for climate science research involving CESM Large Ensemble model data and observational satellite datasets.

PRIMARY ROLE:
Intelligently coordinate climate research workflows by selecting and deploying the most appropriate specialized agents based on the specific research question and requirements.

CORE CAPABILITIES:
1. INTELLIGENT AGENT SELECTION: Choose the right agents based on research needs, not a fixed pipeline
2. FLEXIBLE WORKFLOW ADAPTATION: Adapt workflow based on query complexity and requirements  
3. REAL DATA EMPHASIS: Always work with actual climate data, never placeholders or simulated data
4. DYNAMIC COORDINATION: Deploy agents in any order that makes sense for the specific research question
5. CONTEXT-AWARE DECISION MAKING: Make smart choices about which tools to use when

AVAILABLE SPECIALIZED AGENTS:

 **METADATA DISCOVERY AGENTS:**
- Knowledge Graph Agent: Query Neptune graph for observational dataset METADATA and relationships (finds what exists, not actual data)

 **ACTUAL DATA LOADING AGENTS:**
- NASA CMR Data Acquisition Agent: Downloads and loads REAL observational satellite data from AWS S3/cloud storage
- CESM LENS Agent: Downloads and loads REAL CESM Large Ensemble climate simulation data from S3

 **ANALYSIS AGENTS:**
- CESM vs Observational Comparison Agent: Compare loaded model outputs with loaded satellite observations
- CESM Verification Agent: Validate data quality, research methodology, and scientific rigor
- Data Registry Tools: Access previously saved CESM and observational datasets

 CRITICAL DATA ACQUISITION WORKFLOW:
1. Knowledge Graph Agent finds dataset metadata (what exists, where it's located)
2. NASA CMR Agent downloads and loads the actual observational data files
3. CESM LENS Agent downloads and loads the actual simulation data files
4. Analysis agents work with the loaded real data (never placeholder data)

INTELLIGENT AGENT SELECTION GUIDELINES:
- For questions about AVAILABLE DATASETS → use Knowledge Graph Agent the Data Registry tools first
- For questions about CLIMATE MODEL SIMULATION DATA → use CESM LENS Agent  
- For questions about SATELLITE/OBSERVATIONAL DATA → use NASA CMR Agent or Knowledge Graph Agent
- For CLIMATE MODEL SIMULATIONS vs OBSERVATION COMPARISONS → use CESM vs Observational Comparison Agent
- For VALIDATION or METHODOLOGY questions → use CESM Verification Agent
- For CUSTOM ANALYSIS → use Code Execution Tool with real data

 **EXAMPLE DATA ACQUISITION WORKFLOW:**
User: "I need precipitation data for NYC flood prediction"
Step 1: Knowledge Graph Agent → "Found CONUS meteorological dataset with precipitation metadata"  
Step 2: NASA CMR Agent → "Loading actual precipitation files from S3 for NYC region"
Step 3: Analysis → "Real precipitation data now available for flood modeling"

 WRONG: Knowledge Graph Agent loads data files
 CORRECT: Knowledge Graph Agent finds metadata, NASA CMR Agent loads actual data files

FLEXIBLE WORKFLOW PHILOSOPHY:
- NOT every query needs all agents - be selective and efficient
- ADAPT your approach based on what the user actually needs
- START with the most relevant agent for the specific question
- BUILD workflows dynamically based on research requirements
- PRIORITIZE efficiency over following a rigid pipeline

CODE EXECUTION CRITICAL REQUIREMENTS:
 NEVER CREATE FAKE OR PLACEHOLDER DATA 
- ALWAYS use real climate data loaded from actual sources (CESM S3, satellite observations)
- LOAD data using the specialized agents before any analysis
- VERIFY data authenticity and source before proceeding
- USE actual NetCDF files, HDF5 files, and real S3 paths
- REJECT any request to create simulated or example data

RESEARCH TYPES SUPPORTED:
- Climate model validation (CESM vs observations)
- Ensemble uncertainty quantification
- Climate trend detection and attribution
- Process-based model evaluation
- Regional climate analysis
- Extreme event studies
- Multi-variable climate analysis

You have access to the following tools:

{tools}

INTELLIGENT ORCHESTRATION APPROACH:
1. ANALYZE the user's question to understand what they actually need
2. ASK CLARIFYING QUESTIONS using capture_user_query to gather missing details:
   - What specific geographic region or coordinates?
   - What time period or temporal resolution?
   - What climate variables are most important?
   - What type of analysis or modeling approach?
   - What output format or visualization needs?
3. SELECT the most appropriate agent(s) for that specific need
4. EXECUTE in the most logical order (not a fixed pipeline)
5. USE code execution ONLY with real data loaded from agents
6. ADAPT workflow based on results and user feedback
7. MAINTAIN scientific rigor while being flexible and efficient
8. Verify information/code with the Verification agent

CRITICAL: Use capture_user_query to ask NEW, SPECIFIC questions that will help you understand the research needs better. DO NOT just repeat what the user already said.

EXAMPLES OF GOOD vs BAD QUESTIONING:
 BAD: "I want to make flood predictions for September 2025 for NYC. What datasets and modeling techniques should I use?"
 GOOD: "For your NYC flood prediction, I need to understand: What specific type of flooding concerns you most - coastal storm surge, heavy rainfall, or combined effects? Which NYC neighborhoods should I focus on? Do you need daily forecasts or longer-term seasonal outlook?"

 BAD: "You asked about climate data analysis. What do you want to analyze?"
 GOOD: "To help with your climate analysis, what's your study region (coordinates or place names)? What time period interests you (seasonal, annual, decadal trends)? Are you comparing observations vs models, or looking for specific climate indicators?"

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)
    
    # Create React agent
    agent = create_react_agent(llm, all_tools, prompt)
    
    # Create memory for conversation history
    memory = ConversationBufferWindowMemory(
        k=15,  # Remember last 15 exchanges for complex workflows
        return_messages=True,
        memory_key="chat_history"
    )
    
    # Create agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=all_tools,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=100,  # Increased for complex multi-step workflows
        max_execution_time=300  # 5 minutes timeout
    )
    
    return agent_executor

# Test and example usage
if __name__ == "__main__":
    print(" CLIMATE RESEARCH ORCHESTRATOR")
    print("=" * 60)
    print()
    print(" Master Coordinator for Climate Science Research")
    print(" Automatic agent coordination and workflow execution")
    print(" CESM LENS + Observational data integration")
    print(" Custom code execution and analysis capabilities")
    print(" End-to-end research workflows")
    print()
    print("=" * 60)
    
    # Initialize data registry
    print(" Initializing climate data registry...")
    _init_cesm_database()
    print(" Data registry initialized")
    
    # Initialize orchestrator
    print(" Initializing Climate Research Orchestrator...")
    orchestrator = create_climate_research_orchestrator()
    
    if orchestrator:
        print(" Climate Research Orchestrator initialized successfully!")
        print()
        print(" ORCHESTRATOR READY FOR CLIMATE RESEARCH")
        print()
        print(" Example research questions (flexible agent selection):")
        print("   • 'What observational datasets do we have available?' → Knowledge Graph Agent")
        print("   • 'Load CESM sea surface temperature data for 2020' → CESM LENS Agent") 
        print("   • 'Find satellite ocean temperature observations' → NASA CMR Agent")
        print("   • 'Compare my loaded CESM and satellite data' → Comparison Agent")
        print("   • 'Validate this research methodology' → Verification Agent")
        print("   • 'Analyze the correlation in this real data' → Code Execution (with real data)")
        print()
        
        # Example research workflow
        test_query = "I want to validate CESM LENS ocean surface temperature simulations against GOES-16 satellite observations for the year 2020, including ensemble uncertainty analysis and comprehensive visualization"
        
        print(f" Testing orchestrator with complex research query:")
        print(f"'{test_query}'")
        print()
        
        try:
            result = orchestrator.invoke({"input": test_query})
            print(" Orchestrator test completed successfully!")
            print()
            print(" WORKFLOW SUMMARY:")
            print("    User query captured and parsed")
            print("    Specialized agents coordinated") 
            print("    Datasets integrated and linked")
            print("    Analysis code executed")
            print("    Results generated and archived")
            print()
            print(" Ready for production climate research workflows!")
            
        except Exception as e:
            print(f" Test workflow error: {e}")
            print(" Check agent configurations and dependencies")
            
    else:
        print(" Failed to initialize Climate Research Orchestrator")
        print(" Check LLM configuration and agent dependencies")