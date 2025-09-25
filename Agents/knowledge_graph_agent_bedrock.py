#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
KnowledgeGraphAgent - PROPER Implementation with Bedrock and LangChain

This matches the EXACT architecture of agentic_climate_ai.py:
- AWS Bedrock for LLM (Claude Sonnet)
- LangChain for agent framework
- Real tools with proper integration
- sentence-transformers for embeddings only
"""

import json
import uuid
import traceback
import requests
import boto3
import sqlite3
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging
import sys
import os

# AWS imports for Neptune connection
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest

# LangChain imports (EXACTLY like original)
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.callbacks import CallbackManagerForToolRun

# Sentence transformers for embeddings (EXACTLY like original)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

# Load .env if present (harmless in prod CI as well)
load_dotenv()


# --- Configuration Constants (EXACTLY like original) ---
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")
NEPTUNE_REGION = os.getenv("NEPTUNE_REGION", "us-east-2")
GRAPH_ID = os.getenv("GRAPH_ID", "g-xxxx")
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'

# --- Neptune Graph Schema Constants ---
# All available node types from Neptune CSVs
NODES = [
            "Dataset",
            "DataCategory",
            "DataFormat",
            "CoordinateSystem",
            "Location",
            "Station",
            "Organization",
            "Platform",
            "Consortium",
            "TemporalExtent",
            "Variable",          # NASA CMR variables
            "CESMVariable",      # CESM variables
            "Component",         # CESM components
            "Contact",           # Contact information
            "Project",           # Project information
            "SpatialResolution", # Spatial resolution info
            "TemporalResolution", # Temporal resolution info
            "Instrument",        # Instrument information
            "ScienceKeyword",    # Science keywords
            "ProcessingLevel",   # Processing levels
            
            # Climate ML workflow nodes
            "SurrogateModelingWorkflow",        # Physics-first: neural operators as surrogates
            "HybridMLPhysicsWorkflow",          # Physics-first: hybrid ML-physics simulations  
            "EquationDiscoveryWorkflow",        # Physics-first: discovering governing equations
            "ParameterizationBenchmarkWorkflow", # Physics-first: benchmarking ML parameterizations
            "UncertaintyQuantificationWorkflow", # Data-first: simulation-based uncertainty quantification
            "ParameterInferenceWorkflow",       # Data-first: probabilistic parameter inference
            "SubseasonalForecastingWorkflow",   # ML-first: subseasonal forecasting
            "TransferLearningWorkflow"          # ML-first: transfer learning for sparse predictions
        ]
        
        # Define relationship mapping
RELATIONSHIPS = {
# Dataset relationships (order-based)
"hasDataCategory": ("Dataset", "DataCategory"),
"hasDataFormat": ("Dataset", "DataFormat"),
"usesCoordinateSystem": ("Dataset", "CoordinateSystem"),
"hasLocation": ("Dataset", "Location"),
"hasStation": ("Dataset", "Station"),
"hasOrganization": ("Dataset", "Organization"),
"hasPlatform": ("Dataset", "Platform"),
"hasConsortium": ("Dataset", "Consortium"),
"hasTemporalExtent": ("Dataset", "TemporalExtent"),
"hasContact": ("Dataset", "Contact"),
"hasProject": ("Dataset", "Project"),
"hasRelatedUrl": ("Dataset", "RelatedUrl"),
"hasSpatialResolution": ("Dataset", "SpatialResolution"),
"hasTemporalResolution": ("Dataset", "TemporalResolution"),
"hasGranule": ("Dataset", "Granule"),
"hasInstrument": ("Dataset", "Instrument"),
"hasScienceKeyword": ("Dataset", "ScienceKeyword"),
"hasProcessingLevel": ("Dataset", "ProcessingLevel"),

# Variable relationships
"hasVariable": ("Dataset", "Variable"),           # Dataset -> NASA CMR Variable
# "hasCESMVariable": ("Dataset", "CESMVariable"), # REMOVED: Created separately via ML predictions
"belongsToComponent": ("CESMVariable", "Component"),  # CESM Variable -> Component
"similarCESMVariable": ("CESMVariable", "CESMVariable"), # CESMVariable -> CESMVariable (string similarity based grouping)

# Climate research workflow relationships
"measuredByInstrument": ("Variable", "Instrument"),    # Variable -> Instrument (data provenance)
"deployedOnPlatform": ("Instrument", "Platform"),     # Instrument -> Platform (measurement chain)
"operatesAtLocation": ("Platform", "Location"),       # Platform -> Location (spatial context)
"worksForOrganization": ("Contact", "Organization"),  # Contact -> Organization (data stewardship)
"belongsToConsortium": ("Organization", "Consortium"), # Organization -> Consortium (collaboration)
"describesVariable": ("ScienceKeyword", "CESMVariable"),  # ScienceKeyword -> CESMVariable (semantic linking)
"producesFormat": ("Instrument", "DataFormat"),       # Instrument -> DataFormat (technical specs)

# Physics-First Workflow Relationships (based on high-resolution simulation data)

# SurrogateModelingWorkflow: Neural operators for PDE solving
"SurrogateModelingWorkflow_usesDataset": ("SurrogateModelingWorkflow", "Dataset"),
"SurrogateModelingWorkflow_requiresHighResData": ("SurrogateModelingWorkflow", "SpatialResolution"),  # High-resolution simulation data
"SurrogateModelingWorkflow_requiresTemporalData": ("SurrogateModelingWorkflow", "TemporalResolution"), # Time-series training data
"SurrogateModelingWorkflow_appliesTo": ("SurrogateModelingWorkflow", "Component"),  # Atmosphere, ocean, land components

# HybridMLPhysicsWorkflow: CRM-based ML surrogates
"HybridMLPhysicsWorkflow_usesDataset": ("HybridMLPhysicsWorkflow", "Dataset"),
"HybridMLPhysicsWorkflow_requiresAtmosphericData": ("HybridMLPhysicsWorkflow", "Variable"),  # Atmospheric state variables
"HybridMLPhysicsWorkflow_appliesTo": ("HybridMLPhysicsWorkflow", "Component"),  # Atmosphere component
"HybridMLPhysicsWorkflow_requiresOrganization": ("HybridMLPhysicsWorkflow", "Organization"), # E3SM-MMF data

# EquationDiscoveryWorkflow: Sparse equation discovery
"EquationDiscoveryWorkflow_usesDataset": ("EquationDiscoveryWorkflow", "Dataset"),
"EquationDiscoveryWorkflow_requiresHighResSimulations": ("EquationDiscoveryWorkflow", "SpatialResolution"),
"EquationDiscoveryWorkflow_appliesTo": ("EquationDiscoveryWorkflow", "Component"),  # Ocean, atmosphere, land
"EquationDiscoveryWorkflow_requiresOrganization": ("EquationDiscoveryWorkflow", "Organization"), # MITgcm simulations

# ParameterizationBenchmarkWorkflow: Systematic ML parameterization testing
"ParameterizationBenchmarkWorkflow_usesDataset": ("ParameterizationBenchmarkWorkflow", "Dataset"),
"ParameterizationBenchmarkWorkflow_requiresSimulationData": ("ParameterizationBenchmarkWorkflow", "Variable"),
"ParameterizationBenchmarkWorkflow_appliesTo": ("ParameterizationBenchmarkWorkflow", "Component"), # QG model testing

# Data-First Workflow Relationships (based on observations)

# UncertaintyQuantificationWorkflow: Satellite retrieval uncertainty
"UncertaintyQuantificationWorkflow_usesDataset": ("UncertaintyQuantificationWorkflow", "Dataset"),
"UncertaintyQuantificationWorkflow_requiresInstrument": ("UncertaintyQuantificationWorkflow", "Instrument"),  # EMIT satellite
"UncertaintyQuantificationWorkflow_requiresSpectra": ("UncertaintyQuantificationWorkflow", "Variable"),  # Electromagnetic spectra
"UncertaintyQuantificationWorkflow_requiresOrganization": ("UncertaintyQuantificationWorkflow", "Organization"), # NASA JPL
"UncertaintyQuantificationWorkflow_appliesTo": ("UncertaintyQuantificationWorkflow", "Component"), # Atmosphere, land, ocean

# ParameterInferenceWorkflow: Probabilistic parameter estimation
"ParameterInferenceWorkflow_usesDataset": ("ParameterInferenceWorkflow", "Dataset"),
"ParameterInferenceWorkflow_requiresInstrument": ("ParameterInferenceWorkflow", "Instrument"), # For observed distributions
"ParameterInferenceWorkflow_requiresVariable": ("ParameterInferenceWorkflow", "Variable"), # System state variables
"ParameterInferenceWorkflow_requiresOrganization": ("ParameterInferenceWorkflow", "Organization"), # Model parameters
"ParameterInferenceWorkflow_appliesTo": ("ParameterInferenceWorkflow", "Component"), # Land, ocean, atmosphere

# ML-First Workflow Relationships (pure ML approaches)

# SubseasonalForecastingWorkflow: 2-6 week forecasting
"SubseasonalForecastingWorkflow_usesDataset": ("SubseasonalForecastingWorkflow", "Dataset"),
"SubseasonalForecastingWorkflow_requiresReanalysisData": ("SubseasonalForecastingWorkflow", "Variable"), # ERA5 reanalysis
"SubseasonalForecastingWorkflow_requiresPlatform": ("SubseasonalForecastingWorkflow", "Platform"), # Global atmospheric data
"SubseasonalForecastingWorkflow_requiresOrganization": ("SubseasonalForecastingWorkflow", "Organization"), # ECMWF ERA5
"SubseasonalForecastingWorkflow_appliesTo": ("SubseasonalForecastingWorkflow", "Component"), # Atmosphere

# TransferLearningWorkflow: Sparse observation extrapolation
"TransferLearningWorkflow_usesDataset": ("TransferLearningWorkflow", "Dataset"),
"TransferLearningWorkflow_requiresSparseObservations": ("TransferLearningWorkflow", "Variable"), # Limited real observations
"TransferLearningWorkflow_requiresLocation": ("TransferLearningWorkflow", "Location"), # Cross-domain applications
"TransferLearningWorkflow_requiresOrganization": ("TransferLearningWorkflow", "Organization"), # SOCAT data
"TransferLearningWorkflow_appliesTo": ("TransferLearningWorkflow", "Component") # Atmosphere, land, ocean
}

# Define property types for CSV headers
property_types = {
"id": "String",
"type": "String",
"short_name": "String",
"title": "String",
"links": "String",
"summary": "String",
"original_format": "String",
"data_format": "String",
"format_source": "String",
"category": "String",
"boxes": "String",
"polygons": "String",
"points": "String",
"place_names": "String",
# Enhanced Dataset properties
"data_center": "String",
"dataset_id": "String",
"entry_id": "String",
"version_id": "String",
"processing_level_id": "String",
"online_access_flag": "Boolean",
"browse_flag": "Boolean",
"science_keywords": "String",
"doi": "String",
"doi_authority": "String",
"collection_data_type": "String",
"data_set_language": "String",
"archive_center": "String",
"native_id": "String",
"granule_count": "Integer",
"day_night_flag": "String",
"cloud_cover": "String",
# CoordinateSystem properties
"name": "String",
"projection_type": "String",
"datum": "String",
"units": "String",
# Variable properties
"variable_id": "String",
"cesm_name": "String",
"standard_name": "String",
"long_name": "String",
"description": "String",
"domain": "String",
"component": "String",
"source_dataset": "String",
"match_confidence": "Double",
"match_type": "String",
"matched_term": "String",
"variable_type": "String",
"source": "String",
# Component properties
"component_id": "String",
"component_name": "String",
"full_name": "String",
"abbreviation": "String",
# Contact properties
"contact_id": "String",
"contact_type": "String",
"contact_name": "String",
"roles": "String",
"email": "String",
"organization": "String",
"phone": "String",
# Project properties
"project_id": "String",
"project_name": "String",
"project_description": "String",
# RelatedUrl properties
"url_id": "String",
"url": "String",
"type": "String",
"subtype": "String",
"url_description": "String",
"url_format": "String",
# Resolution properties
"spatial_id": "String",
"spatial_resolution": "String",
"spatial_units": "String",
"temporal_id": "String",
"temporal_resolution": "String",
"temporal_frequency": "String",
# ScienceKeyword properties
"keyword_id": "String",
"category": "String",
"topic": "String",
"term": "String",
"variable_level_1": "String",
"variable_level_2": "String",
"variable_level_3": "String",
"detailed_variable": "String",
# ProcessingLevel properties
"processing_level_id": "String",
"id": "String",
"level_description": "String",
# Other properties
"platforms": "String",
"start_time": "String",
"end_time": "String",
"updated": "String",
# Workflow properties
"workflow_id": "String",
"workflow_name": "String",
"workflow_type": "String",
"workflow_description": "String",
"methodology": "String",
"primary_approach": "String",
"key_techniques": "String",
"data_requirements": "String",
"computational_complexity": "String",
"typical_timescales": "String",
"strengths": "String",
"limitations": "String",
"example_applications": "String",
"maturity_level": "String",
"target_domain": "String",
# Embedding property
"embedding": "List"
}

# Initialize embedding model (EXACTLY like original)
if SENTENCE_TRANSFORMERS_AVAILABLE:
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(" Embedding model loaded.")
else:
    print("Sentence transformers not available - vector search will be disabled")
    embedding_model = None

# --- AWS Bedrock LLM (EXACT COPY from original) ---
class BedrockClaudeLLM(LLM):
    """LangChain wrapper for AWS Bedrock using the Claude Sonnet model - EXACT COPY"""
    bedrock: Any = None
    model_id: str = BEDROCK_MODEL_ID

    def __init__(self):
        super().__init__()
        try:
            self.bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
            print("Bedrock Claude LLM initialized successfully")
        except Exception as e:
            print(f"Bedrock client failed to initialize: {e}. LLM calls will use a fallback.")
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

class ClimateGraphConnector:
    """Connector to the real ClimaGraph on AWS Neptune Analytics - EXACT COPY"""
    def __init__(self):
        self.region = NEPTUNE_REGION
        self.graph_id = GRAPH_ID
        try:
            self.neptune = boto3.client("neptune-graph", region_name=self.region)
            print(f" Successfully initialized Neptune client for graph: {self.graph_id}")
        except Exception as e:
            print(f" Neptune client failed to initialize: {e}. Graph queries will be mocked.")
            self.neptune = None

    def execute_query(self, query: str) -> Dict:
        """Execute Cypher query - EXACT COPY from original"""
        if not self.neptune:
            print(f"--- MOCK NEPTUNE QUERY ---\n{query}\n-------------------------")
            return {"results": []}
        try:
            print(f"Executing Neptune Analytics Query on {self.graph_id}...")
            
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
            print(f" Neptune Analytics query failed: {e}")
            raise e
    
    def vector_search_by_type(self, query_text: str, node_type: str, top_k: int = 10) -> List[Dict]:
        """Smart search - vector for nodes with embeddings, text for nodes without"""
        
        # Node types with embeddings (from json_to_csvs.py analysis)
        vector_enabled_types = {
            "DataCategory", "Variable", "CESMVariable", "ScienceKeyword", "Location",
            "TemporalResolution", "SpatialResolution",
            "SurrogateModelingWorkflow", "HybridMLPhysicsWorkflow", "EquationDiscoveryWorkflow",
            "ParameterizationBenchmarkWorkflow", "UncertaintyQuantificationWorkflow", 
            "ParameterInferenceWorkflow", "SubseasonalForecastingWorkflow", "TransferLearningWorkflow"
        }
        
        if node_type in vector_enabled_types:
            print(f" Using vector search on '{node_type}' nodes for: '{query_text}'")
            return self._vector_search_with_fallback(query_text, node_type, top_k)
        else:
            print(f" Using text search on '{node_type}' nodes for: '{query_text}' (no embeddings)")
            return self._text_search_only(query_text, node_type, top_k)
    
    def _text_search_only(self, query_text: str, node_type: str, top_k: int) -> List[Dict]:
        """Text search only for nodes without embeddings"""
        try:
            search_props = {
                "CESMVariable": ["name", "long_name", "description", "cesm_name"],
                "Variable": ["name", "long_name", "description"],
                "Dataset": ["title", "short_name"],
                "DataCategory": ["summary"],
                "Location": ["name", "place_names", "title", "scope", "countries", "continents"]
            }
            props = search_props.get(node_type, ["name", "title"])
            where_conditions = [f"toLower(coalesce(n.{prop}, '')) CONTAINS toLower('{query_text}')" for prop in props]
            where_clause = " OR ".join(where_conditions)
            
            text_query = f"""
            MATCH (n:{node_type})
            WHERE {where_clause}
            RETURN n as node, 0.75 as score
            ORDER BY n.name, n.title
            LIMIT {top_k}
            """
            result = self.execute_query(text_query)
            
            formatted_results = []
            for res in result.get("results", []):
                node_properties = res.get('node', {})
                node_properties['score'] = res.get('score', 0.75)
                formatted_results.append(node_properties)
            return formatted_results
            
        except Exception as e:
            print(f" Text search failed: {e}")
            return []
    
    def _vector_search_with_fallback(self, query_text: str, node_type: str, top_k: int) -> List[Dict]:
        """Vector search with text fallback for nodes with embeddings"""
        try:
            if not embedding_model:
                print(" Embedding model not available, using text search")
                return self._text_search_only(query_text, node_type, top_k)
                
            vec = embedding_model.encode(query_text).tolist()
            vec_str = "[" + ",".join(map(str, vec)) + "]"
            
            cypher_query = f"""
            CALL neptune.algo.vectors.topKByEmbedding(
            {vec_str}, {{topK: {top_k}}}
            ) YIELD node, score
            WHERE '{node_type}' IN labels(node)
            RETURN node, score, labels(node) as node_labels
            ORDER BY score DESC
            """
            result = self.execute_query(cypher_query)
            
            if not result.get("results"):
                print(f" Vector search returned 0 results, falling back to text search...")
                return self._text_search_only(query_text, node_type, top_k)
            
            formatted_results = []
            for res in result.get("results", []):
                node_properties = res.get('node', {})
                node_properties['score'] = res.get('score')
                formatted_results.append(node_properties)
            return formatted_results
       
        except Exception as e:
            print(f" Vector search failed: {e}")
            return []

    def inspect_node(self, node_id: str) -> Dict:
        """Inspect node and relationships - EXACT COPY from original"""
        print(f"🕵️ Inspecting node and its relationships: {node_id}")
        props_query = f"MATCH (n) WHERE n.`~id` = '{node_id}' RETURN properties(n) as properties, labels(n) as labels"
        props_result = self.execute_query(props_query)
        
        rels_query = f"""
        MATCH (n)-[r]-(m)
        WHERE n.`~id` = '{node_id}'
        RETURN type(r) as relationship_type, labels(m) as neighbor_labels, m.`~id` as neighbor_id, m.title as neighbor_title, m.name as neighbor_name
        """
        rels_result = self.execute_query(rels_query)

        return {
            "properties": props_result.get("results", [{}])[0],
            "relationships": rels_result.get("results", [])
        }

# --- Initialize Real Services (EXACTLY like original) ---
kg_connector = ClimateGraphConnector()
llm = BedrockClaudeLLM()

# --- LANGCHAIN TOOLS (EXACTLY like original) ---

class SearchByVariableTool(BaseTool):
    """Search for climate variables - Enhanced to support Variable and CESMVariable types"""
    name: str = "search_by_variable"
    description: str = "Search for variables. Input: 'variable_name' or 'variable_name|type' where type is 'Variable', 'CESMVariable', or 'both'. Searches both Variable and CESMVariable types by default."
    
    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        parts = tool_input.split('|')
        variable_name = parts[0].strip()
        search_type = parts[1].strip() if len(parts) > 1 else 'both'
        
        all_results = []
        
        if search_type in ['both', 'Variable'] and 'Variable' in NODES:
            var_results = kg_connector.vector_search_by_type(variable_name, "Variable", 10)
            for result in var_results:
                result['node_type'] = 'Variable'
                all_results.append(result)
                
        if search_type in ['both', 'CESMVariable'] and 'CESMVariable' in NODES:
            cesm_results = kg_connector.vector_search_by_type(variable_name, "CESMVariable", 10)
            for result in cesm_results:
                result['node_type'] = 'CESMVariable'  
                all_results.append(result)
        
        if not all_results:
            available_types = [node for node in ['Variable', 'CESMVariable'] if node in NODES]
            return f"No variables found for '{variable_name}' in types {available_types}. Try standard CESM variable names for the corresponding variable.."
        
        # Sort by score
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        results = all_results[:10]
        
        output = f"Found {len(results)} variables for '{variable_name}':\n"
        for i, var in enumerate(results):
            var_id = var.get('~id', 'unknown')
            name = var.get('name', var.get('cesm_name', 'unnamed'))
            node_type = var.get('node_type', 'Variable')
            score = var.get('score', 'N/A')
            
            output += f"{i+1}. {name} ({node_type})\n"
            output += f"   ID: {var_id}"
            if score != 'N/A':
                output += f" | Score: {score:.3f}"
            
            # Show key properties based on available fields
            if var.get('units'):
                output += f" | Units: {var['units']}"
            if var.get('long_name'):
                long_name = var['long_name'][:50] + "..." if len(var['long_name']) > 50 else var['long_name']
                output += f" | Description: {long_name}"
            elif var.get('description'):
                desc = var['description'][:50] + "..." if len(var['description']) > 50 else var['description']
                output += f" | Description: {desc}"
            output += "\n"
        
        return output

class SearchByKeywordTool(BaseTool):
    """Search for science keywords - Enhanced with better output"""
    name: str = "search_by_keyword" 
    description: str = "Search for science keywords by term, category, or topic (e.g., 'ATMOSPHERE', 'SNOW/ICE', 'temperature'). Returns matching science keywords with detailed information."
    
    def _run(self, keyword: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if 'ScienceKeyword' not in NODES:
            return "ScienceKeyword node type not available in current graph schema."
            
        results = kg_connector.vector_search_by_type(keyword, "ScienceKeyword", 10)
        if not results:
            return f"No science keywords found for '{keyword}'. Try generic terms related to the keyword."
        
        output = f"Found {len(results)} science keywords for '{keyword}':\n"
        for i, kw in enumerate(results):
            kw_id = kw.get('~id', 'unknown')
            term = kw.get('term', 'unnamed')
            score = kw.get('score', 'N/A')
            category = kw.get('category', '')
            topic = kw.get('topic', '')
            
            output += f"{i+1}. {term}\n"
            output += f"   ID: {kw_id}"
            if score != 'N/A':
                output += f" | Score: {score:.3f}"
            
            # Show hierarchical structure
            hierarchy_parts = []
            if category:
                hierarchy_parts.append(f"Category: {category}")
            if topic:
                hierarchy_parts.append(f"Topic: {topic}")
            
            if hierarchy_parts:
                output += f" | {' | '.join(hierarchy_parts)}"
            
            # Show additional levels if available
            levels = []
            for level_key in ['variable_level_1', 'variable_level_2', 'variable_level_3']:
                if kw.get(level_key):
                    levels.append(kw[level_key])
            if levels:
                output += f" | Levels: {' > '.join(levels)}"
            
            output += "\n"
        
        return output

class SearchByDataCategoryTool(BaseTool):
    """🥇 PRIMARY DATASET DISCOVERY TOOL - DataCategories are the BEST way to find datasets with comprehensive summaries!"""
    name: str = "search_by_data_category"
    description: str = "🥇 BEST TOOL FOR FINDING DATASETS! DataCategories provide comprehensive summaries of dataset content and are the most effective starting point for dataset discovery. Search by topic/type (e.g., 'atmospheric measurements', 'temperature data', 'satellite data', 'sea ice', 'precipitation'). After finding relevant categories, inspect them to discover connected datasets."
    
    def _run(self, category_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if 'DataCategory' not in NODES:
            return "DataCategory node type not available in current graph schema."
            
        results = kg_connector.vector_search_by_type(category_description, "DataCategory", 10)
        if not results:
            return f"No data categories found for '{category_description}'. Try generic terms related to the category."
        
        output = f"Found {len(results)} data categories for '{category_description}':\n"
        for i, cat in enumerate(results):
            cat_id = cat.get('~id', 'unknown')
            score = cat.get('score', 'N/A')
            
            # Try to get a good name/title for the category
            name = cat.get('category', cat.get('name', cat.get('title', 'unnamed')))
            summary = cat.get('summary', '')
            
            output += f"{i+1}. {name}\n"
            output += f"   ID: {cat_id}"
            if score != 'N/A':
                output += f" | Score: {score:.3f}"
            
            # Show summary if available
            if summary:
                summary_short = summary[:120] + "..." if len(summary) > 120 else summary
                output += f"\n   Summary: {summary_short}"
            
            output += "\n"
        
        return output

class SearchByTemporalResolutionTool(BaseTool):
    """Search for temporal resolutions - Enhanced with vector search"""
    name: str = "search_by_temporal_resolution"
    description: str = "Search for temporal resolutions by description (e.g., 'daily', 'monthly', 'annual', 'hourly'). Uses vector search to find matching temporal resolution specifications."
    
    def _run(self, resolution_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if 'TemporalResolution' not in NODES:
            return "TemporalResolution node type not available in current graph schema."
            
        results = kg_connector.vector_search_by_type(resolution_description, "TemporalResolution", 10)
        if not results:
            return f"No temporal resolutions found for '{resolution_description}'. Try terms like 'daily', 'monthly', 'annual', 'hourly'."
        
        output = f"Found {len(results)} temporal resolutions for '{resolution_description}':\n"
        for i, tr in enumerate(results):
            tr_id = tr.get('~id', 'unknown')
            score = tr.get('score', 'N/A')
            
            # Try to get a good name/title for the temporal resolution
            name = tr.get('resolution', tr.get('name', tr.get('title', tr.get('frequency', 'unnamed'))))
            description = tr.get('description', '')
            
            output += f"{i+1}. {name}\n"
            output += f"   ID: {tr_id}"
            if score != 'N/A':
                output += f" | Score: {score:.3f}"
            
            # Show description if available
            if description:
                desc_short = description[:120] + "..." if len(description) > 120 else description
                output += f"\n   Description: {desc_short}"
            
            output += "\n"
        
        return output

class SearchBySpatialResolutionTool(BaseTool):
    """Search for spatial resolutions - Enhanced with vector search"""
    name: str = "search_by_spatial_resolution"
    description: str = "Search for spatial resolutions by description (e.g., '1km', '10m', 'high resolution', 'coarse grid'). Uses vector search to find matching spatial resolution specifications."
    
    def _run(self, resolution_description: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if 'SpatialResolution' not in NODES:
            return "SpatialResolution node type not available in current graph schema."
            
        results = kg_connector.vector_search_by_type(resolution_description, "SpatialResolution", 10)
        if not results:
            return f"No spatial resolutions found for '{resolution_description}'. Try terms like '1km', '10m', 'high resolution', 'coarse'."
        
        output = f"Found {len(results)} spatial resolutions for '{resolution_description}':\n"
        for i, sr in enumerate(results):
            sr_id = sr.get('~id', 'unknown')
            score = sr.get('score', 'N/A')
            
            # Try to get a good name/title for the spatial resolution
            name = sr.get('resolution', sr.get('name', sr.get('title', sr.get('grid_spacing', 'unnamed'))))
            description = sr.get('description', '')
            
            output += f"{i+1}. {name}\n"
            output += f"   ID: {sr_id}"
            if score != 'N/A':
                output += f" | Score: {score:.3f}"
            
            # Show description if available
            if description:
                desc_short = description[:120] + "..." if len(description) > 120 else description
                output += f"\n   Description: {desc_short}"
            
            output += "\n"
        
        return output

class InspectGraphNodeTool(BaseTool):
    """Inspect node details and relationships with limited scope to prevent excessive inspections"""
    name: str = "inspect_graph_node"
    description: str = "Get detailed information about a specific node using its ID. Shows properties and relationships. IMPORTANT: Only inspect 10 most relevant nodes per query to avoid overwhelming output."
    
    def _run(self, node_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Get node properties
            props_query = f"MATCH (n) WHERE n.`~id` = '{node_id}' RETURN n as node, labels(n) as labels"
            props_result = kg_connector.execute_query(props_query)
            
            if not props_result.get("results"):
                return f"Node {node_id} not found"
            
            node_data = props_result["results"][0]
            node_props = node_data.get("node", {})
            node_labels = node_data.get("labels", [])
            
            # Get relationships with ALL connected node properties
            rels_query = f"""
            MATCH (n)-[r]-(m)
            WHERE n.`~id` = '{node_id}'
            RETURN 
                type(r) as relationship_type,
                m as connected_node,
                labels(m) as connected_labels,
                m.`~id` as connected_id
            ORDER BY relationship_type
            """
            rels_result = kg_connector.execute_query(rels_query)
            relationships = rels_result.get("results", [])
            
            # Build comprehensive output
            output = f" NODE INSPECTION: {node_id}\n"
            output += "=" * 50 + "\n\n"
            
            # Node info
            output += f" Node Type: {', '.join(node_labels)}\n"
            output += f" Node ID: {node_id}\n\n"
            
            # ALL node properties
            output += " NODE PROPERTIES:\n"
            if node_props:
                for key, value in node_props.items():
                    if key != '~id':  # Skip the ID since we already show it
                        output += f"  • {key}: {value}\n"
            else:
                output += "  (No properties)\n"
            output += "\n"
            
            # ALL relationships with connected node properties
            output += f" RELATIONSHIPS ({len(relationships)} total):\n"
            
            if relationships:
                for i, rel in enumerate(relationships):
                    rel_type = rel.get('relationship_type', 'unknown')
                    connected_node = rel.get('connected_node', {})
                    connected_labels = rel.get('connected_labels', [])
                    connected_id = rel.get('connected_id', 'unknown')
                    
                    output += f"\n  {i+1}. --{rel_type}--> {', '.join(connected_labels)} (ID: {connected_id})\n"
                    
                    # Show ALL properties of connected node
                    if connected_node:
                        for key, value in connected_node.items():
                            if key != '~id':  # Skip ID since we show it above
                                # Truncate very long values
                                if isinstance(value, str) and len(value) > 200:
                                    value = value[:200] + "..."
                                output += f"     {key}: {value}\n"
                    else:
                        output += f"     (No properties available)\n"
            else:
                output += "  (No relationships found)\n"
                
            return output
            
        except Exception as e:
            return f"Error inspecting node {node_id}: {str(e)}"

class ExploreGraphStructureTool(BaseTool):
    """Explore graph structure using NODES array and RELATIONSHIPS dictionary"""
    name: str = "explore_graph_structure"
    description: str = "Discover what node types exist using the NODES array, test vector search based on embedding property, and show RELATIONSHIPS patterns."
    
    def _run(self, query: str = "explore", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Get actual node counts from graph
            node_types_query = """
            MATCH (n)
            RETURN DISTINCT labels(n) as node_labels, count(*) as count
            ORDER BY count DESC
            """
            
            result = kg_connector.execute_query(node_types_query)
            actual_types = {}
            for res in result.get("results", []):
                labels = res.get("node_labels", [])
                count = res.get("count", 0)
                for label in labels:
                    if label not in actual_types:
                        actual_types[label] = 0
                    actual_types[label] += count
            
            output = f" GRAPH SCHEMA EXPLORATION\n"
            output += "=" * 40 + "\n\n"
            
            # Show NODES array vs actual
            output += f" DEFINED NODES ({len(NODES)} total):\n"
            for node_type in NODES:
                count = actual_types.get(node_type, 0)
                has_embedding = "embedding" in property_types and property_types["embedding"] == "List"
                search_type = " Vector" if has_embedding else " Text"
                
                if count > 0:
                    output += f"   {node_type}: {count} nodes ({search_type})\n"
                else:
                    output += f"  ⚪ {node_type}: Not found ({search_type})\n"
            
            # Test vector search on nodes that exist and have embeddings
            output += f"\n VECTOR SEARCH TEST:\n"
            for node_type in NODES:
                if node_type in actual_types and actual_types[node_type] > 0:
                    try:
                        results = kg_connector.vector_search_by_type("climate", node_type, 2)
                        if results:
                            sample = results[0]
                            name = (sample.get('name') or sample.get('title') or 
                                   sample.get('term') or sample.get('short_name') or 'unnamed')
                            score = sample.get('score', 'N/A')
                            output += f"   {node_type}: Vector works! Sample: {name} (Score: {score})\n"
                        else:
                            output += f"  🔸 {node_type}: No vector results\n"
                    except Exception as e:
                        output += f"   {node_type}: Error - {str(e)[:50]}...\n"
            
            # Show RELATIONSHIPS patterns
            output += f"\n RELATIONSHIPS ({len(RELATIONSHIPS)} defined):\n"
            for rel_name, (source, target) in list(RELATIONSHIPS.items())[:10]:
                output += f"  • {source} --{rel_name}--> {target}\n"
            
            if len(RELATIONSHIPS) > 10:
                output += f"  ... and {len(RELATIONSHIPS) - 10} more\n"
            
            return output
            
        except Exception as e:
            return f"Error exploring graph structure: {str(e)}"

class SearchAnyNodeTypeTool(BaseTool):
    """Search any node type from the NODES array"""
    name: str = "search_any_node_type"
    description: str = "Search any node type from the schema. Input: 'node_type|search_query' where node_type is from NODES array. Uses vector search if embeddings available, text search otherwise."
    
    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            parts = tool_input.split('|', 1)
            if len(parts) != 2:
                return f"Format: 'node_type|search_query'\nAvailable types: {', '.join(NODES[:10])}..."
            
            node_type, search_query = parts[0].strip(), parts[1].strip()
            
            if node_type not in NODES:
                return f"Unknown node type: {node_type}\nAvailable: {', '.join(NODES)}"
            
            # Use kg_connector's smart search (vector or text based on node type)
            results = kg_connector.vector_search_by_type(search_query, node_type, 10)
            
            if not results:
                return f"No {node_type} nodes found for '{search_query}'"
            
            output = f" Found {len(results)} {node_type} nodes for '{search_query}':\n\n"
            
            for i, node in enumerate(results):
                node_id = node.get('~id', 'unknown')
                # Get best name using property_types keys
                name = (node.get('name') or node.get('title') or node.get('term') or 
                       node.get('short_name') or node.get('workflow_name') or 'unnamed')
                score = node.get('score', 'N/A')
                
                output += f"{i+1}. {name}\n"
                output += f"   ID: {node_id}"
                if score != 'N/A':
                    output += f" | Score: {score:.3f}"
                
                # Show relevant properties from property_types
                key_props = []
                for prop in ['description', 'summary', 'long_name', 'units', 'methodology', 'category']:
                    if prop in node and node[prop]:
                        value = str(node[prop])[:80] + ("..." if len(str(node[prop])) > 80 else "")
                        key_props.append(f"{prop}: {value}")
                        if len(key_props) >= 2:
                            break
                
                if key_props:
                    output += f"\n   {' | '.join(key_props)}"
                output += "\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching {node_type if 'node_type' in locals() else 'node'}: {str(e)}"

class SearchByLocationTool(BaseTool):
    """Enhanced location search with smart aliases and geographic intelligence"""
    name: str = "search_by_location"
    description: str = "🥈 SINGLE-CRITERION SEARCH - Use only when searching JUST locations without other criteria. For multi-criteria searches (location + time/variable/etc.), use 'multi_criteria_dataset_search' instead! IMPORTANT: When searching for a specific location (e.g., 'California'), also search for broader geographic coverage by including the country ('USA', 'United States') and continent ('North America') to find datasets that cover the area."
    
    def _run(self, location_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            if 'Location' not in NODES:
                return "Location node type not available in current graph schema."
            
            # Use vector search for Location nodes (they have embeddings)
            results = kg_connector.vector_search_by_type(location_query, "Location", 10)
            
            if not results:
                return f"No Location nodes found for '{location_query}'. Try geographic terms or place names"
            
            output = f" Found {len(results)} locations for '{location_query}':\n"
            
            for i, location in enumerate(results):
                loc_id = location.get('~id', 'unknown')
                name = location.get('name', location.get('place_names', 'unnamed'))
                
                output += f"{i+1}. {name}\n"
                output += f"   ID: {loc_id}"
                
                # Show location-specific properties
                location_props = []
                if location.get('boxes'):
                    location_props.append(f"Bounds: {location['boxes']}")
                if location.get('points'):
                    location_props.append(f"Points: {location['points']}")
                if location.get('polygons'):
                    location_props.append(f"Polygons: Available")
                
                if location_props:
                    output += f" | {' | '.join(location_props)}"
                
                output += "\n"
            
            return output
            
        except Exception as e:
            return f"Error searching locations: {str(e)}"

class SearchByTemporalExtentTool(BaseTool):
    """Search for datasets by temporal extent using overlap logic to always include datasets with broader coverage"""
    name: str = "search_by_temporal_extent"
    description: str = "🥈 SINGLE-CRITERION SEARCH - Use only when searching JUST temporal coverage without other criteria. For multi-criteria searches (time + location/variable/etc.), use 'multi_criteria_dataset_search' instead! Supports: 'after:YYYY-MM-DD', 'before:YYYY-MM-DD', 'between:YYYY-MM-DD:YYYY-MM-DD', 'year:YYYY'. Always accepts subsets."
    
    def _run(self, temporal_query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            if 'TemporalExtent' not in NODES:
                return "TemporalExtent node type not available in current graph schema."
            
            # Parse temporal query and build openCypher conditions using native date functions
            cypher_conditions = []
            query_description = ""
            
            if temporal_query.startswith("after:"):
                # After specific date - use date() function for comparison
                date_str = temporal_query.replace("after:", "").strip()
                cypher_conditions.append(f"(date(te.start_time) >= date('{date_str}') OR date(te.end_time) >= date('{date_str}'))")
                query_description = f"data after {date_str}"
                
            elif temporal_query.startswith("before:"):
                # Before specific date - find datasets that have data before this date
                date_str = temporal_query.replace("before:", "").strip()
                cypher_conditions.append(f"date(te.start_time) <= date('{date_str}')")
                query_description = f"data before {date_str}"
                
            elif temporal_query.startswith("between:"):
                # Between two dates - overlap query (allows subsets)
                parts = temporal_query.replace("between:", "").strip().split(":")
                if len(parts) == 2:
                    start_date, end_date = parts
                    # Overlap condition: dataset_start <= query_end AND dataset_end >= query_start
                    cypher_conditions.append(f"(date(te.start_time) <= date('{end_date}') AND date(te.end_time) >= date('{start_date}'))")
                    query_description = f"data overlapping {start_date} to {end_date}"
                else:
                    return "Invalid between format. Use 'between:YYYY-MM-DD:YYYY-MM-DD'"
                    
            elif temporal_query.startswith("year:"):
                # Specific year - overlap query (allows subsets)
                year = temporal_query.replace("year:", "").strip()
                # Overlap condition: dataset_start <= year_end AND dataset_end >= year_start
                cypher_conditions.append(f"(date(te.start_time) <= date('{year}-12-31') AND date(te.end_time) >= date('{year}-01-01'))")
                query_description = f"data overlapping year {year}"
                
            elif temporal_query.startswith("overlaps:"):
                # Check if dataset temporal range overlaps with query range
                parts = temporal_query.replace("overlaps:", "").strip().split(":")
                if len(parts) == 2:
                    query_start, query_end = parts
                    # Overlap condition: dataset_start <= query_end AND dataset_end >= query_start
                    cypher_conditions.append(f"(date(te.start_time) <= date('{query_end}') AND date(te.end_time) >= date('{query_start}'))")
                    query_description = f"data overlapping {query_start} to {query_end}"
                else:
                    return "Invalid overlaps format. Use 'overlaps:YYYY-MM-DD:YYYY-MM-DD'"
                    
            elif len(temporal_query) == 4 and temporal_query.isdigit():
                # Simple year query - overlap query (allows subsets)
                year = temporal_query
                # Overlap condition: dataset_start <= year_end AND dataset_end >= year_start
                cypher_conditions.append(f"(date(te.start_time) <= date('{year}-12-31') AND date(te.end_time) >= date('{year}-01-01'))")
                query_description = f"data overlapping year {year}"
                
            else:
                return f"Invalid temporal query. Use: 'after:YYYY-MM-DD', 'before:YYYY-MM-DD', 'between:YYYY-MM-DD:YYYY-MM-DD', 'overlaps:YYYY-MM-DD:YYYY-MM-DD', 'year:YYYY', or just 'YYYY' for year."
            
            # Build openCypher query using proper temporal functions
            where_clause = " AND ".join(cypher_conditions)
            cypher_query = f"""
            MATCH (d:Dataset)-[:hasTemporalExtent]-(te:TemporalExtent)
            WHERE {where_clause}
            RETURN d.`~id` as dataset_id, d.title as title, d.short_name as short_name,
                   te.start_time as start_time, te.end_time as end_time, te.updated as updated
            ORDER BY date(te.start_time) DESC
            LIMIT 20
            """
            
            result = kg_connector.execute_query(cypher_query)
            
            if not result.get("results"):
                return f"No datasets found with {query_description}. Try 'year:2023', 'after:2020-01-01', or 'between:2020-01-01:2023-12-31'."
            
            datasets = result["results"]
            output = f" Found {len(datasets)} datasets with {query_description}:\n\n"
            
            for i, dataset in enumerate(datasets, 1):
                dataset_id = dataset.get('dataset_id', 'unknown')
                title = dataset.get('title', 'Untitled')
                short_name = dataset.get('short_name', '')
                start_time = dataset.get('start_time', 'Unknown')
                end_time = dataset.get('end_time', 'Unknown')
                updated = dataset.get('updated', '')
                
                output += f"{i}. {title}\n"
                output += f"   ID: {dataset_id}\n"
                if short_name:
                    output += f"   Short Name: {short_name}\n"
                output += f"   Temporal Coverage: {start_time} to {end_time}\n"
                if updated:
                    output += f"   Last Updated: {updated}\n"
                output += "\n"
            
            output += f" Use 'inspect_graph_node' with dataset IDs for more details."
            return output
            
        except Exception as e:
            return f"Error searching temporal extents: {str(e)}"

class MultiCriteriaDatasetSearchTool(BaseTool):
    """🥈 MULTI-CRITERIA SEARCH TOOL - Use for searches with 2+ criteria, always include DataCategory when possible!"""
    name: str = "multi_criteria_dataset_search"
    description: str = "🥈 MULTI-CRITERIA SEARCH - Use for searches with multiple criteria! Automatically combines vector search, temporal filtering, and relationship matching. IMPORTANT: Always include DataCategory in your search when possible since it provides the best dataset summaries! Perfect for requests like 'Arctic temperature data 2000-2020' → 'DataCategory: temperature, Location: Arctic, TemporalExtent: between:2000-01-01:2020-12-31'. LOCATION TIP: Include broader geographic coverage (California → USA → North America). Format: 'TemporalExtent: after:2020-01-01, Location: Arctic, DataCategory: atmospheric, Organization: NASA'. Use exact node names: TemporalExtent, Location, TemporalResolution, SpatialResolution, Organization, Variable, DataCategory, Project, Contact, Instrument, ScienceKeyword."
    
    def _run(self, criteria_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Parse input format: "NodeName: value, NodeName: value, ..."
            if not criteria_input.strip():
                return "Please provide search criteria. Format: 'TemporalExtent: after:2020-01-01, Location: Arctic, Organization: NASA'"
            
            # Valid node names from the schema
            valid_node_names = {
                'TemporalExtent': 'temporal',
                'Location': 'location', 
                'TemporalResolution': 'temporal_resolution',
                'SpatialResolution': 'spatial_resolution',
                'Organization': 'organization',
                'Variable': 'variable',
                'DataCategory': 'category',
                'Project': 'project',
                'Contact': 'contact',
                'Instrument': 'instrument',
                'ScienceKeyword': 'keyword'
            }
            
            # Parse comma-separated criteria
            criteria_parts = criteria_input.split(',')
            search_filters = {}
            used_node_names = []
            
            # Parse each criterion
            for part in criteria_parts:
                part = part.strip()
                if ':' not in part:
                    continue
                    
                node_name, value = part.split(':', 1)
                node_name = node_name.strip()
                value = value.strip()
                
                # Validate node name
                if node_name not in valid_node_names:
                    return f"Invalid node name '{node_name}'. Valid names: {', '.join(valid_node_names.keys())}"
                
                # Convert to internal filter name
                filter_name = valid_node_names[node_name]
                search_filters[filter_name] = value
                used_node_names.append(node_name)
            
            if not search_filters:
                return f"No valid criteria found. Use format: 'TemporalExtent: after:2020-01-01, Location: Arctic'\nValid node names: {', '.join(valid_node_names.keys())}"
            
            # Node types that support vector search embeddings
            vector_enabled_nodes = {
                'location': 'Location',
                'variable': 'Variable', 
                'category': 'DataCategory',
                'keyword': 'ScienceKeyword',
                'temporal_resolution': 'TemporalResolution',
                'spatial_resolution': 'SpatialResolution'
            }
            
            # Build complex query with vector search for embedded nodes and text search for others
            cypher_conditions = []
            relationship_matches = []
            filter_descriptions = []
            vector_filter_nodes = []  # Track nodes found via vector search
            
            # Handle temporal criteria
            if 'temporal' in search_filters:
                temporal_value = search_filters['temporal']
                if temporal_value.startswith('after:'):
                    date_str = temporal_value.replace('after:', '').strip()
                    relationship_matches.append("(d)-[:hasTemporalExtent]-(te:TemporalExtent)")
                    cypher_conditions.append(f"date(te.start_time) >= date('{date_str}')")
                    filter_descriptions.append(f"temporal coverage after {date_str}")
                elif temporal_value.startswith('before:'):
                    date_str = temporal_value.replace('before:', '').strip()
                    relationship_matches.append("(d)-[:hasTemporalExtent]-(te:TemporalExtent)")
                    cypher_conditions.append(f"date(te.start_time) <= date('{date_str}')")
                    filter_descriptions.append(f"temporal coverage before {date_str}")
            
            # Handle location criteria with vector search
            if 'location' in search_filters:
                location_value = search_filters['location']
                # Use vector search to find matching locations
                location_results = kg_connector.vector_search_by_type(location_value, "Location", 5)
                if location_results:
                    location_ids = [loc.get('~id') for loc in location_results if loc.get('~id')]
                    if location_ids:
                        relationship_matches.append("(d)-[:hasLocation]-(loc:Location)")
                        id_list = "', '".join(location_ids)
                        cypher_conditions.append(f"loc.`~id` IN ['{id_list}']")
                        filter_descriptions.append(f"location (vector): {location_value}")
                        vector_filter_nodes.extend(location_ids)
                    else:
                        # Fallback to text search
                        relationship_matches.append("(d)-[:hasLocation]-(loc:Location)")
                        cypher_conditions.append(f"(toLower(loc.name) CONTAINS toLower('{location_value}') OR toLower(loc.place_names) CONTAINS toLower('{location_value}') OR toLower(loc.scope) CONTAINS toLower('{location_value}'))")
                        filter_descriptions.append(f"location (text): {location_value}")
                else:
                    # Fallback to text search
                    relationship_matches.append("(d)-[:hasLocation]-(loc:Location)")
                    cypher_conditions.append(f"(toLower(loc.name) CONTAINS toLower('{location_value}') OR toLower(loc.place_names) CONTAINS toLower('{location_value}') OR toLower(loc.scope) CONTAINS toLower('{location_value}'))")
                    filter_descriptions.append(f"location (text): {location_value}")
            
            # Handle temporal resolution criteria with vector search
            if 'resolution' in search_filters or 'temporal_resolution' in search_filters:
                resolution_value = search_filters.get('resolution', search_filters.get('temporal_resolution'))
                # Use vector search for temporal resolution
                tr_results = kg_connector.vector_search_by_type(resolution_value, "TemporalResolution", 5)
                if tr_results:
                    tr_ids = [tr.get('~id') for tr in tr_results if tr.get('~id')]
                    if tr_ids:
                        relationship_matches.append("(d)-[:hasTemporalResolution]-(tr:TemporalResolution)")
                        id_list = "', '".join(tr_ids)
                        cypher_conditions.append(f"tr.`~id` IN ['{id_list}']")
                        filter_descriptions.append(f"temporal resolution (vector): {resolution_value}")
                        vector_filter_nodes.extend(tr_ids)
                    else:
                        # Fallback to text search
                        relationship_matches.append("(d)-[:hasTemporalResolution]-(tr:TemporalResolution)")
                        cypher_conditions.append(f"toLower(tr.resolution) CONTAINS toLower('{resolution_value}')")
                        filter_descriptions.append(f"temporal resolution (text): {resolution_value}")
                else:
                    # Fallback to text search
                    relationship_matches.append("(d)-[:hasTemporalResolution]-(tr:TemporalResolution)")
                    cypher_conditions.append(f"toLower(tr.resolution) CONTAINS toLower('{resolution_value}')")
                    filter_descriptions.append(f"temporal resolution (text): {resolution_value}")
            
            # Handle spatial resolution criteria with vector search
            if 'spatial_resolution' in search_filters:
                spatial_value = search_filters['spatial_resolution']
                # Use vector search for spatial resolution
                sr_results = kg_connector.vector_search_by_type(spatial_value, "SpatialResolution", 5)
                if sr_results:
                    sr_ids = [sr.get('~id') for sr in sr_results if sr.get('~id')]
                    if sr_ids:
                        relationship_matches.append("(d)-[:hasSpatialResolution]-(sr:SpatialResolution)")
                        id_list = "', '".join(sr_ids)
                        cypher_conditions.append(f"sr.`~id` IN ['{id_list}']")
                        filter_descriptions.append(f"spatial resolution (vector): {spatial_value}")
                        vector_filter_nodes.extend(sr_ids)
                    else:
                        # Fallback to text search
                        relationship_matches.append("(d)-[:hasSpatialResolution]-(sr:SpatialResolution)")
                        cypher_conditions.append(f"toLower(sr.resolution) CONTAINS toLower('{spatial_value}')")
                        filter_descriptions.append(f"spatial resolution (text): {spatial_value}")
                else:
                    # Fallback to text search
                    relationship_matches.append("(d)-[:hasSpatialResolution]-(sr:SpatialResolution)")
                    cypher_conditions.append(f"toLower(sr.resolution) CONTAINS toLower('{spatial_value}')")
                    filter_descriptions.append(f"spatial resolution (text): {spatial_value}")
            
            # Handle organization criteria (no vector search)
            if 'organization' in search_filters:
                org_value = search_filters['organization']
                relationship_matches.append("(d)-[:hasOrganization]-(org:Organization)")
                cypher_conditions.append(f"toLower(org.name) CONTAINS toLower('{org_value}')")
                filter_descriptions.append(f"organization: {org_value}")
            
            # Handle variable criteria with vector search
            if 'variable' in search_filters:
                var_value = search_filters['variable']
                # Use vector search for variables
                var_results = kg_connector.vector_search_by_type(var_value, "Variable", 5)
                if var_results:
                    var_ids = [var.get('~id') for var in var_results if var.get('~id')]
                    if var_ids:
                        relationship_matches.append("(d)-[:hasVariable]-(var:Variable)")
                        id_list = "', '".join(var_ids)
                        cypher_conditions.append(f"var.`~id` IN ['{id_list}']")
                        filter_descriptions.append(f"variable (vector): {var_value}")
                        vector_filter_nodes.extend(var_ids)
                    else:
                        # Fallback to text search
                        relationship_matches.append("(d)-[:hasVariable]-(var:Variable)")
                        cypher_conditions.append(f"(toLower(var.name) CONTAINS toLower('{var_value}') OR toLower(var.long_name) CONTAINS toLower('{var_value}'))")
                        filter_descriptions.append(f"variable (text): {var_value}")
                else:
                    # Fallback to text search
                    relationship_matches.append("(d)-[:hasVariable]-(var:Variable)")
                    cypher_conditions.append(f"(toLower(var.name) CONTAINS toLower('{var_value}') OR toLower(var.long_name) CONTAINS toLower('{var_value}'))")
                    filter_descriptions.append(f"variable (text): {var_value}")
            
            # Handle data category criteria with vector search
            if 'category' in search_filters:
                cat_value = search_filters['category']
                # Use vector search for data categories
                cat_results = kg_connector.vector_search_by_type(cat_value, "DataCategory", 5)
                if cat_results:
                    cat_ids = [cat.get('~id') for cat in cat_results if cat.get('~id')]
                    if cat_ids:
                        relationship_matches.append("(d)-[:hasDataCategory]-(dc:DataCategory)")
                        id_list = "', '".join(cat_ids)
                        cypher_conditions.append(f"dc.`~id` IN ['{id_list}']")
                        filter_descriptions.append(f"data category (vector): {cat_value}")
                        vector_filter_nodes.extend(cat_ids)
                    else:
                        # Fallback to text search
                        relationship_matches.append("(d)-[:hasDataCategory]-(dc:DataCategory)")
                        cypher_conditions.append(f"toLower(dc.summary) CONTAINS toLower('{cat_value}')")
                        filter_descriptions.append(f"data category (text): {cat_value}")
                else:
                    # Fallback to text search
                    relationship_matches.append("(d)-[:hasDataCategory]-(dc:DataCategory)")
                    cypher_conditions.append(f"toLower(dc.summary) CONTAINS toLower('{cat_value}')")
                    filter_descriptions.append(f"data category (text): {cat_value}")
            
            # Handle science keyword criteria with vector search
            if 'keyword' in search_filters:
                keyword_value = search_filters['keyword']
                # Use vector search for science keywords
                kw_results = kg_connector.vector_search_by_type(keyword_value, "ScienceKeyword", 5)
                if kw_results:
                    kw_ids = [kw.get('~id') for kw in kw_results if kw.get('~id')]
                    if kw_ids:
                        relationship_matches.append("(d)-[:hasScienceKeyword]-(sk:ScienceKeyword)")
                        id_list = "', '".join(kw_ids)
                        cypher_conditions.append(f"sk.`~id` IN ['{id_list}']")
                        filter_descriptions.append(f"science keyword (vector): {keyword_value}")
                        vector_filter_nodes.extend(kw_ids)
                    else:
                        # Fallback to text search
                        relationship_matches.append("(d)-[:hasScienceKeyword]-(sk:ScienceKeyword)")
                        cypher_conditions.append(f"(toLower(sk.category) CONTAINS toLower('{keyword_value}') OR toLower(sk.topic) CONTAINS toLower('{keyword_value}') OR toLower(sk.term) CONTAINS toLower('{keyword_value}'))")
                        filter_descriptions.append(f"science keyword (text): {keyword_value}")
                else:
                    # Fallback to text search
                    relationship_matches.append("(d)-[:hasScienceKeyword]-(sk:ScienceKeyword)")
                    cypher_conditions.append(f"(toLower(sk.category) CONTAINS toLower('{keyword_value}') OR toLower(sk.topic) CONTAINS toLower('{keyword_value}') OR toLower(sk.term) CONTAINS toLower('{keyword_value}'))")
                    filter_descriptions.append(f"science keyword (text): {keyword_value}")
            
            # Handle project criteria (no vector search)
            if 'project' in search_filters:
                proj_value = search_filters['project']
                relationship_matches.append("(d)-[:hasProject]-(proj:Project)")
                cypher_conditions.append(f"toLower(proj.name) CONTAINS toLower('{proj_value}')")
                filter_descriptions.append(f"project: {proj_value}")
            
            if not cypher_conditions:
                return "No valid search criteria recognized. Supported: temporal, location, resolution, organization, variable, category, project"
            
            # Build the complete Cypher query
            match_clauses = ["(d:Dataset)"] + list(set(relationship_matches))
            match_clause = "MATCH " + ", ".join(match_clauses)
            where_clause = "WHERE " + " AND ".join(cypher_conditions)
            
            cypher_query = f"""
            {match_clause}
            {where_clause}
            RETURN DISTINCT d.`~id` as dataset_id, d.title as title, d.short_name as short_name
            ORDER BY d.title
            LIMIT 20
            """
            
            result = kg_connector.execute_query(cypher_query)
            
            if not result.get("results"):
                criteria_desc = ", ".join(filter_descriptions)
                return f"No datasets found matching ALL criteria: {criteria_desc}. Try relaxing some criteria or use individual search tools."
            
            datasets = result["results"]
            criteria_desc = ", ".join(filter_descriptions)
            
            # Add vector search info
            vector_info = ""
            if vector_filter_nodes:
                vector_count = len(vector_filter_nodes)
                vector_info = f" (🔍 {vector_count} semantic matches)"
            
            output = f"✅ Found {len(datasets)} datasets matching ALL criteria{vector_info}:\n"
            output += f"📋 Criteria: {criteria_desc}\n\n"
            
            for i, dataset in enumerate(datasets, 1):
                dataset_id = dataset.get('dataset_id', 'unknown')
                title = dataset.get('title', 'Untitled')
                short_name = dataset.get('short_name', '')
                
                output += f"{i}. {title}\n"
                output += f"   ID: {dataset_id}\n"
                if short_name:
                    output += f"   Short Name: {short_name}\n"
                output += "\n"
            
            output += f"💡 Use 'inspect_graph_node' with dataset IDs for detailed information about relationships."
            return output
            
        except Exception as e:
            return f"Error in multi-criteria search: {str(e)}"

class ConditionalRelationshipSearchTool(BaseTool):
    """Legacy conditional relationship search tool - kept for backward compatibility"""
    name: str = "conditional_relationship_search"
    description: str = "Search with conditional relationships using vector/text search. Format: 'target_node_type|condition1_type:condition1_value|condition2_type:condition2_value|...' (e.g., 'Dataset|Location:Arctic|Organization:NASA'). Uses vector search for vector-enabled node types."
    
    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        # Legacy implementation - redirect to new multi-criteria tool
        return f"Please use 'multi_criteria_dataset_search' instead. Convert your query:\n" + \
               f"'{tool_input}' → 'location:Arctic|organization:NASA'"

class StoreDatasetRelationshipsTool(BaseTool):
    """🚨 MANDATORY STORAGE TOOL - ALWAYS use this for EVERY dataset found! Stores complete dataset info in SQLite database."""
    name: str = "store_dataset_relationships"
    description: str = "🚨 REQUIRED FOR ALL DATASETS - You MUST use this tool for EVERY relevant dataset you find! Given a dataset ID, retrieve and store ALL its relationships and properties (data formats, variables, locations, organizations, etc.) in SQLite database. This ensures all discovered datasets are saved for the user. Returns comprehensive stored information."
    
    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        import sqlite3
        import json
        from datetime import datetime
        
        try:
            # Initialize SQLite database
            db_path = "climate_knowledge_graph.db"
            
            with sqlite3.connect(db_path) as conn:
                # Create tables if they don't exist
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS stored_datasets (
                        dataset_id TEXT PRIMARY KEY,
                        title TEXT,
                        short_name TEXT,
                        dataset_properties TEXT,
                        dataset_labels TEXT,
                        total_relationships INTEGER,
                        relationship_types TEXT,
                        links TEXT,
                        created_at TEXT,
                        updated_at TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS dataset_relationships (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dataset_id TEXT,
                        relationship_type TEXT,
                        connected_id TEXT,
                        connected_labels TEXT,
                        connected_properties TEXT,
                        created_at TEXT,
                        FOREIGN KEY (dataset_id) REFERENCES stored_datasets (dataset_id)
                    )
                """)
                
                conn.commit()
            
            # Get dataset's links via hasLink relationship
            links_query = f"""
            MATCH (d:Dataset)-[:hasLink]-(link)
            WHERE d.`~id` = '{dataset_id}' OR d.id = '{dataset_id}'
            RETURN properties(link) as link_properties
            """
            
            # Get complete dataset relationships with all properties
            relationships_query = f"""
            MATCH (d:Dataset)-[r]-(connected)
            WHERE d.`~id` = '{dataset_id}' OR d.id = '{dataset_id}'
            RETURN 
                type(r) as relationship_type,
                labels(connected) as connected_labels,
                COALESCE(connected.`~id`, connected.id) as connected_id,
                properties(connected) as connected_properties
            ORDER BY relationship_type
            """
            
            # Also get dataset's own properties
            dataset_query = f"""
            MATCH (d:Dataset)
            WHERE d.`~id` = '{dataset_id}' OR d.id = '{dataset_id}'
            RETURN properties(d) as dataset_properties, labels(d) as dataset_labels
            """
            
            links_result = kg_connector.execute_query(links_query)
            rel_result = kg_connector.execute_query(relationships_query)
            dataset_result = kg_connector.execute_query(dataset_query)
            
            if not dataset_result.get("results"):
                return f"Dataset {dataset_id} not found"
            
            # Store dataset properties
            dataset_info = dataset_result["results"][0]
            dataset_props = dataset_info.get("dataset_properties", {})
            
            # Process links
            links_data = []
            for link_result in links_result.get("results", []):
                link_props = link_result.get("link_properties", {})
                if link_props:
                    links_data.append(link_props)
            
            # Store all relationships with their properties
            relationships = rel_result.get("results", [])
            stored_relationships = {}
            
            # Also extract links from relationships if links_data is empty
            if not links_data:
                for rel in relationships:
                    rel_type = rel.get("relationship_type", "unknown")
                    connected_labels = rel.get("connected_labels", [])
                    connected_props = rel.get("connected_properties", {})
                    
                    # Check if this is a Link relationship
                    if rel_type == "hasLink" and "Link" in connected_labels:
                        if connected_props:
                            links_data.append(connected_props)
            
            for rel in relationships:
                rel_type = rel.get("relationship_type", "unknown")
                connected_id = rel.get("connected_id", "unknown")
                connected_labels = rel.get("connected_labels", [])
                connected_props = rel.get("connected_properties", {})
                
                if rel_type not in stored_relationships:
                    stored_relationships[rel_type] = []
                
                stored_relationships[rel_type].append({
                    "id": connected_id,
                    "labels": connected_labels,
                    "properties": connected_props
                })
            
            # Store in SQLite database
            current_time = datetime.now().isoformat()
            title = dataset_props.get('title', 'Unknown Dataset')
            short_name = dataset_props.get('short_name', 'Unknown')
            
            with sqlite3.connect(db_path) as conn:
                # Check if dataset already exists
                cursor = conn.execute("SELECT dataset_id FROM stored_datasets WHERE dataset_id = ?", (dataset_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update existing record
                    conn.execute("""
                        UPDATE stored_datasets 
                        SET title = ?, short_name = ?, dataset_properties = ?, dataset_labels = ?,
                            total_relationships = ?, relationship_types = ?, links = ?, updated_at = ?
                        WHERE dataset_id = ?
                    """, (
                        title, short_name, json.dumps(dataset_props), json.dumps(dataset_info.get("dataset_labels", [])),
                        len(relationships), json.dumps(list(stored_relationships.keys())), json.dumps(links_data), current_time, dataset_id
                    ))
                    
                    # Delete existing relationships and insert new ones
                    conn.execute("DELETE FROM dataset_relationships WHERE dataset_id = ?", (dataset_id,))
                else:
                    # Insert new record
                    conn.execute("""
                        INSERT INTO stored_datasets 
                        (dataset_id, title, short_name, dataset_properties, dataset_labels, 
                         total_relationships, relationship_types, links, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        dataset_id, title, short_name, json.dumps(dataset_props), 
                        json.dumps(dataset_info.get("dataset_labels", [])),
                        len(relationships), json.dumps(list(stored_relationships.keys())), 
                        json.dumps(links_data), current_time, current_time
                    ))
                
                # Insert all relationships
                for rel in relationships:
                    conn.execute("""
                        INSERT INTO dataset_relationships 
                        (dataset_id, relationship_type, connected_id, connected_labels, connected_properties, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        dataset_id,
                        rel.get("relationship_type", "unknown"),
                        rel.get("connected_id", "unknown"),
                        json.dumps(rel.get("connected_labels", [])),
                        json.dumps(rel.get("connected_properties", {})),
                        current_time
                    ))
                
                conn.commit()
            
            # Generate comprehensive output
            output = f" STORED DATASET RELATIONSHIPS: {dataset_id}\n"
            output += "=" * 60 + "\n"
            
            # Dataset basic info
            output += f" Dataset: {title} ({short_name})\n"
            output += f" ID: {dataset_id}\n"
            output += f"💽 Database: {db_path}\n"
            
            # Links information
            if links_data:
                output += f" Links Found: {len(links_data)} data access links stored\n"
                for i, link in enumerate(links_data[:3]):  # Show first 3 links
                    link_url = link.get('url', 'No URL')
                    link_type = link.get('type', 'Unknown type')
                    output += f"   {i+1}. {link_type}: {link_url[:60]}{'...' if len(link_url) > 60 else ''}\n"
                if len(links_data) > 3:
                    output += f"   ... and {len(links_data) - 3} more links stored\n"
            else:
                output += f" Links: No data access links found\n"
            output += "\n"
            
            # Relationship summary
            output += f" STORED RELATIONSHIPS ({len(relationships)} total):\n"
            
            for rel_type, connections in stored_relationships.items():
                output += f"  • {rel_type}: {len(connections)} items\n"
                
                # Show samples with key properties
                for i, conn in enumerate(connections[:3]):  # Show first 3
                    conn_props = conn["properties"]
                    name = (conn_props.get('title') or 
                           conn_props.get('name') or 
                           conn_props.get('original_format') or
                           conn_props.get('term') or 'unnamed')
                    
                    # Key properties based on type
                    key_props = []
                    if 'units' in conn_props:
                        key_props.append(f"Units: {conn_props['units']}")
                    if 'original_format' in conn_props:
                        key_props.append(f"Format: {conn_props['original_format']}")
                    if 'description' in conn_props:
                        desc = str(conn_props['description'])[:50] + "..." if len(str(conn_props['description'])) > 50 else conn_props['description']
                        key_props.append(f"Desc: {desc}")
                    
                    prop_str = f" | {' | '.join(key_props)}" if key_props else ""
                    output += f"    {i+1}. {name} (ID: {conn['id']}){prop_str}\n"
                
                if len(connections) > 3:
                    output += f"    ... and {len(connections) - 3} more stored\n"
                output += "\n"
            
            # Storage confirmation
            action = "UPDATED" if exists else "CREATED"
            output += f" STORAGE COMPLETE ({action}):\n"
            output += f"  • Dataset properties: {len(dataset_props)} fields stored\n"
            output += f"  • Data access links: {len(links_data)} links stored\n"
            output += f"  • Relationship types: {len(stored_relationships)} types stored\n"
            output += f"  • Total connected nodes: {len(relationships)} nodes stored\n"
            output += f"  • SQLite database: {db_path}\n"
            output += f"  • Storage timestamp: {current_time}\n"
            
            return output
            
        except Exception as e:
            return f"Error storing dataset relationships for {dataset_id}: {str(e)}"


class QueryDatasetByIdTool(BaseTool):
    """Query existing dataset by ID from the database"""
    name: str = "query_dataset_by_id"
    description: str = "Query an existing dataset by its ID from the knowledge graph database. Returns complete dataset information including data access links if available."
    
    def _run(self, dataset_id: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            db_path = "climate_knowledge_graph.db"
            
            with sqlite3.connect(db_path) as conn:
                # Get dataset information
                cursor = conn.execute("""
                    SELECT dataset_id, title, short_name, dataset_properties, dataset_labels,
                           total_relationships, relationship_types, links, 
                           created_at, updated_at
                    FROM stored_datasets WHERE dataset_id = ?
                """, (dataset_id.strip(),))
                
                result = cursor.fetchone()
                
                if not result:
                    return f" Dataset not found: {dataset_id}"
                
                columns = ['dataset_id', 'title', 'short_name', 'dataset_properties', 'dataset_labels',
                          'total_relationships', 'relationship_types', 'links', 
                          'created_at', 'updated_at']
                
                dataset = dict(zip(columns, result))
                
                output = f" DATASET INFORMATION\n"
                output += "=" * 35 + "\n\n"
                
                output += f" Basic Information:\n"
                output += f"   • ID: {dataset['dataset_id']}\n"
                output += f"   • Title: {dataset['title']}\n"
                output += f"   • Short Name: {dataset['short_name']}\n"
                output += f"   • Total Relationships: {dataset['total_relationships'] or 0}\n\n"
                
                # Dataset properties
                if dataset['dataset_properties']:
                    try:
                        props = json.loads(dataset['dataset_properties'])
                        output += f" Dataset Properties ({len(props)} fields):\n"
                        for key, value in list(props.items())[:5]:
                            output += f"   • {key}: {value}\n"
                        if len(props) > 5:
                            output += f"   ... and {len(props) - 5} more properties\n"
                    except:
                        output += f" Dataset Properties: Available (raw format)\n"
                    output += "\n"
                
                # Labels
                if dataset['dataset_labels']:
                    try:
                        labels = json.loads(dataset['dataset_labels'])
                        if labels:
                            output += f" Labels: {', '.join(labels[:5])}\n"
                            if len(labels) > 5:
                                output += f"   ... and {len(labels) - 5} more labels\n"
                    except:
                        output += f" Labels: Available\n"
                    output += "\n"
                
                # Links Information
                if dataset['links']:
                    try:
                        links_data = json.loads(dataset['links'])
                        if links_data:
                            output += f" DATA ACCESS LINKS ({len(links_data)} total):\n"
                            for i, link in enumerate(links_data[:5]):  # Show first 5 links
                                link_url = link.get('url', 'No URL')
                                link_type = link.get('type', 'Unknown type')
                                link_rel = link.get('rel', '')
                                output += f"   {i+1}. {link_type}: {link_url[:80]}{'...' if len(link_url) > 80 else ''}\n"
                                if link_rel:
                                    output += f"      Relation: {link_rel}\n"
                            if len(links_data) > 5:
                                output += f"   ... and {len(links_data) - 5} more links\n"
                        else:
                            output += f" DATA ACCESS LINKS: None available\n"
                    except:
                        output += f" DATA ACCESS LINKS: Available (raw format)\n"
                else:
                    output += f" DATA ACCESS LINKS: None found\n"
                
                output += "\n"
                
                # Relationship types
                if dataset['relationship_types']:
                    try:
                        rel_types = json.loads(dataset['relationship_types'])
                        if rel_types:
                            output += f" Relationship Types: {', '.join(rel_types)}\n"
                    except:
                        output += f" Relationship Types: Available\n"
                    output += "\n"
                
                # Timestamps
                output += f" Created: {dataset['created_at']}\n"
                output += f" Updated: {dataset['updated_at']}\n"
                output += f" Database: {db_path}\n"
                
                return output
                
        except Exception as e:
            return f" Error querying dataset: {str(e)}"

class SearchDatasetLinksTool(BaseTool):
    """Search for data access links associated with datasets"""
    name: str = "search_dataset_links"
    description: str = "Search for data access links (S3, Earthdata, DOI, etc.) associated with datasets. Can search by dataset ID or find all datasets with specific link types."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            connector = ClimateGraphConnector()
            
            # Parse query - check if it's a specific dataset ID or a general search
            query = query.strip()
            
            if query.startswith('dataset_'):
                # Search for links of a specific dataset
                cypher_query = """
                MATCH (d:Dataset {id: $dataset_id})-[:hasLink]->(l:Link)
                RETURN d.id, d.title, d.short_name, l.url, l.link_type, l.link_rel
                ORDER BY l.link_type, l.url
                """
                results = connector.execute_cypher(cypher_query, {"dataset_id": query})
                
                if not results:
                    return f" No links found for dataset: {query}"
                
                output = f" LINKS FOR DATASET: {query}\n"
                output += "=" * 50 + "\n\n"
                
                dataset_info = results[0]
                output += f" Dataset: {dataset_info.get('d.title', 'Unknown')}\n"
                output += f"🔖 Short Name: {dataset_info.get('d.short_name', 'Unknown')}\n\n"
                
                # Group links by type
                links_by_type = {}
                for result in results:
                    link_type = result.get('l.link_type', 'Other')
                    if link_type not in links_by_type:
                        links_by_type[link_type] = []
                    links_by_type[link_type].append({
                        'url': result.get('l.url', ''),
                        'rel': result.get('l.link_rel', '')
                    })
                
                # Display links grouped by type
                for link_type, links in links_by_type.items():
                    icon = {'S3': '', 'Earthdata': '', 'DOI': '', 'HTTP': ''}.get(link_type, '🔸')
                    output += f"{icon} {link_type.upper()} LINKS ({len(links)}):\n"
                    for link in links:
                        output += f"    {link['url']}\n"
                        if link['rel']:
                            output += f"       Relation: {link['rel']}\n"
                    output += "\n"
                
            else:
                # General search for datasets with links
                if query.lower() in ['earthdata', 's3', 'doi', 'http']:
                    # Search by link type
                    cypher_query = """
                    MATCH (d:Dataset)-[:hasLink]->(l:Link)
                    WHERE l.link_type =~ $link_type
                    RETURN d.id, d.title, d.short_name, count(l) as link_count, 
                           collect(l.url)[0..3] as sample_urls
                    ORDER BY link_count DESC
                    LIMIT 10
                    """
                    results = connector.execute_cypher(cypher_query, {"link_type": f"(?i).*{query}.*"})
                else:
                    # Search by URL content
                    cypher_query = """
                    MATCH (d:Dataset)-[:hasLink]->(l:Link)
                    WHERE l.url CONTAINS $search_term
                    RETURN d.id, d.title, d.short_name, l.url, l.link_type
                    ORDER BY d.title
                    LIMIT 10
                    """
                    results = connector.execute_cypher(cypher_query, {"search_term": query})
                
                if not results:
                    return f" No datasets found with links matching: {query}"
                
                output = f" DATASETS WITH LINKS MATCHING: {query}\n"
                output += "=" * 50 + "\n\n"
                
                for result in results:
                    output += f" {result.get('d.title', 'Unknown Title')}\n"
                    output += f"    ID: {result.get('d.id', 'Unknown')}\n"
                    output += f"   🔖 Short Name: {result.get('d.short_name', 'Unknown')}\n"
                    
                    if 'link_count' in result:
                        output += f"    Links: {result['link_count']} total\n"
                        sample_urls = result.get('sample_urls', [])
                        for url in sample_urls[:2]:
                            output += f"       {url}\n"
                    else:
                        output += f"    URL: {result.get('l.url', 'Unknown')}\n"
                        output += f"   🔸 Type: {result.get('l.link_type', 'Unknown')}\n"
                    
                    output += "\n"
            
            return output
                
        except Exception as e:
            return f" Error searching dataset links: {str(e)}"


class GeocodingTool(BaseTool):
    """Tool for geocoding coordinates to get location information using Nominatim API"""
    
    name: str = "geocoding_tool"
    description: str = """Geocode coordinates (lat,lon) to get more specific/accurate location names using Nominatim (OpenStreetMap).
    Use this tool when you need to find more precise geographic information or double-check location details for datasets.
    Input format: 'lat,lon' or 'lat lon' or provide bounding box coordinates (south_lat west_lon north_lat east_lon).
    Returns detailed location information including city, county, state, country, continent.
    Helpful for verifying dataset locations or getting additional geographic context."""
    
    def _run(self, coordinates: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Geocode coordinates to location information using Nominatim"""
        try:
            import requests
            import time
            
            # Parse coordinates
            coords_clean = coordinates.replace(',', ' ').strip()
            parts = coords_clean.split()
            
            if len(parts) == 2:
                # Single lat,lon point
                try:
                    lat, lon = map(float, parts)
                    
                    # Use Nominatim API
                    url = "https://nominatim.openstreetmap.org/reverse"
                    params = {
                        'lat': lat,
                        'lon': lon,
                        'format': 'json',
                        'addressdetails': 1,
                        'accept-language': 'en'
                    }
                    headers = {'User-Agent': 'Climate-KG-Agent/1.0'}
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'error' in data:
                        return f" Could not geocode coordinates: {coordinates}"
                    
                    address = data.get('address', {})
                    
                    result = f" LOCATION INFO FOR {lat}, {lon}\n"
                    result += "=" * 40 + "\n"
                    result += f"🏙️  City: {address.get('city', address.get('town', address.get('village', 'Unknown')))}\n"
                    result += f"🏛️  County: {address.get('county', 'Unknown')}\n"
                    result += f"🗺️  State: {address.get('state', 'Unknown')}\n"
                    result += f" Country: {address.get('country', 'Unknown')}\n"
                    
                    # Add continent based on country code
                    country_code = address.get('country_code', '').lower()
                    continent_map = {
                        'us': 'North America', 'ca': 'North America', 'mx': 'North America',
                        'gb': 'Europe', 'de': 'Europe', 'fr': 'Europe', 'it': 'Europe', 'es': 'Europe',
                        'au': 'Oceania', 'nz': 'Oceania',
                        'br': 'South America', 'ar': 'South America', 'cl': 'South America',
                        'cn': 'Asia', 'jp': 'Asia', 'in': 'Asia', 'kr': 'Asia',
                        'za': 'Africa', 'eg': 'Africa', 'ng': 'Africa', 'ke': 'Africa'
                    }
                    continent = continent_map.get(country_code, 'Unknown')
                    result += f"🌎 Continent: {continent}\n"
                    
                    if country_code:
                        result += f"🔤 Country Code: {country_code.upper()}\n"
                    
                    # Rate limiting for Nominatim (1 request per second)
                    time.sleep(1.1)
                    
                    return result
                    
                except ValueError:
                    return f" Invalid coordinates format: {coordinates}. Use 'lat,lon' format."
                except requests.RequestException as e:
                    return f" Error accessing Nominatim API: {str(e)}"
                    
            elif len(parts) == 4:
                # Bounding box: south_lat, west_lon, north_lat, east_lon
                try:
                    south_lat, west_lon, north_lat, east_lon = map(float, parts)
                    
                    # Calculate center point for geocoding
                    center_lat = (south_lat + north_lat) / 2
                    center_lon = (west_lon + east_lon) / 2
                    
                    # Use Nominatim for center point
                    url = "https://nominatim.openstreetmap.org/reverse"
                    params = {
                        'lat': center_lat,
                        'lon': center_lon,
                        'format': 'json',
                        'addressdetails': 1,
                        'accept-language': 'en'
                    }
                    headers = {'User-Agent': 'Climate-KG-Agent/1.0'}
                    
                    response = requests.get(url, params=params, headers=headers, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'error' in data:
                        return f" Could not geocode bounding box: {coordinates}"
                    
                    address = data.get('address', {})
                    
                    result = f"📦 BOUNDING BOX INFO\n"
                    result += "=" * 40 + "\n"
                    result += f"📐 Coordinates: {south_lat}, {west_lon}, {north_lat}, {east_lon}\n"
                    result += f" Center: {center_lat:.4f}, {center_lon:.4f}\n"
                    
                    # Calculate area and classify scope
                    area = abs(north_lat - south_lat) * abs(east_lon - west_lon)
                    result += f"📏 Area: {area:.4f} degrees²\n"
                    
                    if area > 100:
                        scope = "Global"
                    elif area > 10:
                        scope = "Continental"
                    elif area > 1:
                        scope = "Country/Regional"
                    else:
                        scope = "Local/City"
                    
                    result += f" Scope: {scope}\n"
                    
                    # Add place names
                    place_names = []
                    for key in ['city', 'town', 'village', 'county', 'state', 'country']:
                        if key in address and address[key]:
                            place_names.append(address[key])
                    
                    result += f" Place Names: {', '.join(place_names) if place_names else 'Unknown'}\n"
                    
                    # Rate limiting for Nominatim
                    time.sleep(1.1)
                    
                    return result
                    
                except ValueError:
                    return f" Invalid bounding box format: {coordinates}. Use 'south_lat west_lon north_lat east_lon' format."
                except requests.RequestException as e:
                    return f" Error accessing Nominatim API: {str(e)}"
            else:
                return f" Invalid input format: {coordinates}. Use 'lat,lon' for point or 'south_lat west_lon north_lat east_lon' for bounding box."
                
        except Exception as e:
            return f" Error during geocoding: {str(e)}"


# --- Create LangChain Agent (EXACTLY like original) ---

class AskFollowUpQuestionTool(BaseTool):
    """Ask follow-up questions to gather more specific information from the user - USE FREELY THROUGHOUT WORKFLOW"""
    name: str = "ask_follow_up_question"
    description: str = "Ask the user follow-up questions WHENEVER you need clarification - at the beginning, during search, or after finding results. Use this tool liberally to get details about temporal extent, spatial coverage, variables, data types, research objectives, or any other information needed for effective dataset discovery. Don't hesitate to ask multiple times!"
    
    def _run(self, question_context: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Ask follow-up questions based on missing information context
        
        Args:
            question_context: Description of what information is needed (e.g., "temporal_extent", "location", "variables", "data_resolution")
        """
        
        # Define context-specific follow-up questions
        follow_up_templates = {
            "temporal_extent": {
                "title": "🕒 Temporal Coverage Clarification",
                "questions": [
                    "What time period are you interested in? (e.g., 2000-2020, after:2015-01-01, year:2023)",
                    "Do you need data from specific years, decades, or ongoing datasets?",
                    "Are you looking for specific date ranges or particular years of data?"
                ]
            },
            "location": {
                "title": "🌍 Geographic Coverage Clarification", 
                "questions": [
                    "What geographic region are you focusing on? (e.g., Arctic, North America, global, specific cities/countries)",
                    "Do you need local-scale data (specific locations) or regional/global coverage?",
                    "Are there specific coordinates or place names I should search for?"
                ]
            },
            "variables": {
                "title": "📊 Data Variables & Measurements",
                "questions": [
                    "What specific climate variables or measurements are you interested in? (e.g., temperature, precipitation, sea ice, atmospheric CO2)",
                    "Are you looking for observational data, model outputs, or both?",
                    "Do you need specific measurement units or processing levels?"
                ]
            },
            "data_resolution": {
                "title": "📏 Data Resolution Requirements",
                "questions": [
                    "What temporal resolution do you need? (e.g., daily, monthly, annual)",
                    "What spatial resolution is required? (e.g., high-resolution gridded data, station data, regional averages)",
                    "Are there specific data quality or processing level requirements?"
                ]
            },
            "data_source": {
                "title": "🏢 Data Source & Organization",
                "questions": [
                    "Do you have preferences for specific data providers? (e.g., NASA, NOAA, CESM models)",
                    "Are you looking for satellite data, in-situ observations, or model simulations?",
                    "Do you need data from specific instruments or missions?"
                ]
            },
            "research_purpose": {
                "title": "🎯 Research Context & Purpose",
                "questions": [
                    "What is the main purpose of your research? (e.g., climate change analysis, weather forecasting, impact assessment)",
                    "Are you comparing different time periods, locations, or datasets?",
                    "Do you need datasets that are suitable for specific types of analysis (e.g., trend analysis, extreme events, correlations)?"
                ]
            },
            "data_format": {
                "title": "💾 Data Format & Access Requirements",
                "questions": [
                    "Do you have preferences for data formats? (e.g., NetCDF, CSV, HDF5)",
                    "Do you need cloud-accessible data (S3) or are you working with downloadable files?",
                    "Are there any file size or processing constraints I should consider?"
                ]
            },
            "general": {
                "title": "❓ General Information Needed",
                "questions": [
                    "Could you provide more specific details about your research requirements?",
                    "What aspects of climate data are most important for your analysis?",
                    "Are there any constraints or preferences I should know about for the data search?"
                ]
            }
        }
        
        # Parse the context to determine what type of questions to ask
        context_lower = question_context.lower()
        
        # Map context keywords to question categories
        if any(word in context_lower for word in ['time', 'temporal', 'date', 'period', 'year']):
            question_type = "temporal_extent"
        elif any(word in context_lower for word in ['location', 'geographic', 'spatial', 'region', 'place']):
            question_type = "location"
        elif any(word in context_lower for word in ['variable', 'measurement', 'parameter', 'data_type']):
            question_type = "variables"
        elif any(word in context_lower for word in ['resolution', 'frequency', 'grid', 'scale']):
            question_type = "data_resolution"
        elif any(word in context_lower for word in ['source', 'organization', 'provider', 'instrument']):
            question_type = "data_source"
        elif any(word in context_lower for word in ['purpose', 'research', 'goal', 'objective']):
            question_type = "research_purpose"
        elif any(word in context_lower for word in ['format', 'access', 'download', 'file']):
            question_type = "data_format"
        else:
            question_type = "general"
        
        # Generate the follow-up question response
        template = follow_up_templates[question_type]
        
        output = f"🤔 **{template['title']}**\n\n"
        output += f"To help you find the most relevant climate datasets, I need some additional information:\n\n"
        
        for i, question in enumerate(template['questions'], 1):
            output += f"{i}. {question}\n"
        
        output += f"\n💡 **Context:** {question_context}\n\n"
        
        # Actually pause execution and wait for user input
        print(output)
        print("🔴 **WAITING FOR USER INPUT** 🔴")
        print("Please provide any of the above details that are relevant to your research:")
        
        user_response = input("\n>>> Your response: ")
        
        return f"User provided the following clarification: {user_response}\n\nNow I can proceed with searching for datasets based on this information."

def create_knowledge_graph_agent():
    """Create the LangChain agent with all tools - EXACTLY like original"""
    
    # Define all available tools
    tools = [
        SearchByVariableTool(),
        SearchByKeywordTool(), 
        SearchByDataCategoryTool(),
        SearchByTemporalResolutionTool(),
        SearchBySpatialResolutionTool(),
        SearchByLocationTool(),
        SearchByTemporalExtentTool(),
        MultiCriteriaDatasetSearchTool(),
        SearchAnyNodeTypeTool(),
        ConditionalRelationshipSearchTool(),
        InspectGraphNodeTool(),
        ExploreGraphStructureTool(),
        StoreDatasetRelationshipsTool(),
        QueryDatasetByIdTool(),
        SearchDatasetLinksTool(),
        GeocodingTool(),
        AskFollowUpQuestionTool()
    ]
    
    # Create the structured climate research prompt
    template = """You are a Climate Research Data Discovery Assistant with access to the ClimaGraph database on AWS Neptune.

CRITICAL: ASK FOLLOW-UP QUESTIONS WHENEVER YOU NEED MORE DETAILS
Use 'ask_follow_up_question' FREELY AND FREQUENTLY whenever you need clarification:
- At the BEGINNING if the initial request is vague
- DURING search when you find too many/too few results
- AFTER finding datasets when you need to refine the search
- WHEN you're unsure about user requirements
- ANYTIME you need more specific details about:
  * Temporal extent (start/end dates or time periods)
  * Geographic coordinates or detailed location info
  * Variable names or measurement types
  * Data resolution requirements (temporal/spatial)
  * Research objectives or analysis goals

REMEMBER: It's ALWAYS better to ask for clarification than to guess what the user wants. Use 'ask_follow_up_question' liberally throughout your workflow!

IMPORTANT INSPECTION LIMITS:
- NEVER inspect ALL nodes of any category (DataCategory, Dataset, etc.)
- LIMIT inspections to maximum 10 most relevant nodes
- If more than 5 datasets are found, ask user to specify criteria to narrow the search
- Always prioritize quality over quantity in node inspections

STRUCTURED WORKFLOW - Follow these steps in order:

0. CLARIFICATION CHECK: Use 'ask_follow_up_question' tool WHENEVER you need more details - at the start, during search, or after finding results. Don't hesitate to ask for clarification multiple times throughout the workflow!

1. DATACATEGORY SEARCH (PRIMARY FOR DATASETS): 🥇 DataCategory is the BEST way to find datasets! Start by using 'search_by_data_category' to find relevant data categories, then inspect the DATASET NODES directly (not the DataCategory). Dataset nodes contain all the main relationships (variables, locations, organizations, formats, etc.) that you need for comprehensive analysis.

2. MULTI-CRITERIA SEARCH (SECONDARY): For searches with multiple requirements (time + location, location + variable, etc.), use 'multi_criteria_dataset_search' with DataCategory as one of the criteria when possible.

3. SINGLE-CRITERIA SEARCH (TERTIARY): Only use individual search tools when you have just ONE specific search criterion.

4. RELATIONSHIP ANALYSIS: Inspect dataset relationships (variables, formats, locations, etc.)
5. MANDATORY STORAGE: 🚨 ALWAYS use 'store_dataset_relationships' for EVERY relevant dataset found - this is REQUIRED!
6. COMPREHENSIVE SUMMARY: Provide detailed summary with confirmation of stored datasets

TOOL SELECTION PRIORITY:
🥇 PRIMARY: 'search_by_data_category' - BEST for finding datasets! DataCategory provides comprehensive summaries and is the most effective starting point
🥈 SECONDARY: 'multi_criteria_dataset_search' - Use for searches with 2+ criteria, include DataCategory when possible
🥉 TERTIARY: Individual search tools - Only for single-criterion searches or when exploring specific node types
🏅 QUATERNARY: 'search_any_node_type' - For schema exploration or unknown node types

You have access to these tools:
{tools}

WHEN TO ASK FOLLOW-UP QUESTIONS:
- Vague requests like "climate data" or "weather information"
- Missing temporal information (no time period specified)
- Missing geographic scope (no location or region mentioned)
- Unclear variables or data types needed
- No mention of data resolution or format preferences

WHEN TO USE MULTI-CRITERIA SEARCH:
✅ Use 'multi_criteria_dataset_search' when you have ANY combination of:
- Time period + Location (e.g., "Arctic data from 2000-2020")
- Location + Variable (e.g., "Temperature data in Pacific Ocean")
- Organization + Time (e.g., "NASA datasets after 2015")
- Variable + Resolution (e.g., "Daily precipitation data")
- ANY request with 2+ search criteria

❌ DON'T use multiple individual tools when one multi-criteria search can do it all!

LOCATION SEARCH STRATEGY:
🌍 When searching for specific locations, ALWAYS include broader geographic coverage:
- Searching for "California"? → Search for "California", "USA", "United States", "North America"
- Searching for "Texas"? → Search for "Texas", "USA", "United States", "North America"  
- Searching for "London"? → Search for "London", "UK", "United Kingdom", "Europe"
- Searching for "Tokyo"? → Search for "Tokyo", "Japan", "Asia"

This ensures you find datasets with broader geographic coverage that include the specific area!

EXAMPLE WORKFLOWS:

VAGUE REQUEST: "I need climate data"
→ ask_follow_up_question: "The request is too general - need clarification on temporal extent, location, and specific variables"

DATASET DISCOVERY REQUEST: "I need sea ice data for research"
1. ✅ Use search_by_data_category: "sea ice" (PRIMARY - best for finding datasets!)
2. inspect_graph_node: [data category ID to see connected datasets]
3. inspect_graph_node: [DATASET IDs directly - these contain main relationships: variables, locations, organizations, formats]
4. 🚨 store_dataset_relationships: for EVERY dataset found (dataset_id_1, dataset_id_2, dataset_id_3, etc.)
5. Final Answer with confirmation of ALL stored datasets

MULTI-CRITERIA REQUEST: "Arctic temperature data from 2000-2020"
1. ✅ Use multi_criteria_dataset_search: "DataCategory: temperature, Location: Arctic, TemporalExtent: between:2000-01-01:2020-12-31"
2. inspect_graph_node: [DATASET IDs from results - these contain main relationships: variables, locations, organizations, formats]
3. 🚨 store_dataset_relationships: for EVERY dataset found (dataset_id_1, dataset_id_2, etc.)
4. Final Answer with confirmation of ALL stored datasets

SPECIFIC REQUEST: "Analyze Arctic sea ice temperature trends from 2000-2020"
1. Enrichment: "sea ice temperature measurements Arctic regions cryospheric data 2000-2020"
2. search_by_data_category: "sea ice temperature" 
3. inspect_graph_node: [found data category ID to see connected datasets]
4. inspect_graph_node: [DATASET IDs directly - these contain main relationships: variables, locations, organizations, formats] [LIMIT TO TOP 10 MOST RELEVANT - DO NOT inspect all datasets]
5. 🚨 store_dataset_relationships: for EVERY dataset found (dataset_id_1, dataset_id_2, etc.)
6. Final Answer with confirmation of ALL stored datasets

COMPLETION CRITERIA: You MUST provide a Final Answer only after:
- Having sufficient details from the user (FREELY use 'ask_follow_up_question' whenever you need clarification!)
- Finding relevant datasets with their relationships
- 🚨 MANDATORY: Using 'store_dataset_relationships' for EVERY relevant dataset found (not just one!)
- Confirming ALL datasets have been successfully stored in the database
- Having comprehensive information about variables, formats, locations, etc.
- NEVER inspecting more than 10  nodes total per query

REMEMBER: If you're EVER unsure about what the user wants, don't guess - just ask! Use 'ask_follow_up_question' liberally throughout the entire workflow.

Use the following format:
Question: the input question you must answer
Thought: I should follow the structured workflow starting with enrichment
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (continue through all workflow steps)
Thought: I have stored the key datasets and have complete information
Final Answer: the final comprehensive answer with all dataset details and storage confirmation

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
        max_iterations=50,  # Higher safety net, but agent should stop naturally
        early_stopping_method="generate"  # Stop when agent generates final answer
    )
    
    return agent_executor

# Orchestrator integration functions
def get_knowledge_graph_tools():
    """Get Knowledge Graph tools for orchestrator integration"""
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
        print(f" Error loading Knowledge Graph tools: {e}")
        return []

def get_knowledge_graph_agent():
    """Get Knowledge Graph agent for orchestrator coordination"""
    try:
        # Return agent creation function if available
        if 'create_knowledge_graph_agent' in globals():
            return create_knowledge_graph_agent()
        else:
            return None
    except Exception as e:
        print(f" Error creating Knowledge Graph agent: {e}")
        return None

# Test and example usage
if __name__ == "__main__":
    print(" KnowledgeGraphAgent - PROPER Bedrock + LangChain Implementation")
    print("=" * 80)
    print("\n Using AWS Bedrock Claude Sonnet for reasoning")
    print(" Using AWS Neptune Analytics for graph queries")  
    print("🧠 Using sentence-transformers for embeddings")
    print(" Using LangChain for agent framework")
    
    print("\n" + "="*80)
    print(" TESTING KnowledgeGraphAgent with Bedrock")
    print("="*80)
    
    try:
        # Create the agent
        print("\n Initializing LangChain agent with Bedrock...")
        agent = create_knowledge_graph_agent()
        print(" Agent initialized successfully!")
        
        # Test with a research question
        research_question = "Find me datasets in NYC for rainfall and flooding"
        print(f"Research Question: {research_question}")
        
        print("Running agent...")
        response = agent.invoke({"input": research_question})
        
        print(response.get('output', 'No output'))
        
    except Exception as e:
        print(f"TEST FAILED: {str(e)}")
        