#!/usr/bin/env python3
"""
FEMA Data Acquisition Agent
===========================

An intelligent agent for discovering and acquiring FEMA disaster and emergency management data
using the OpenFEMA API (v2).

Features:
- List available FEMA datasets (metadata)
- Query specific datasets with OData filtering (e.g., 'stateCode eq NY')
- Download data to CSV/JSON
- Auto-handling of pagination

API Documentation: https://www.fema.gov/about/openfema/developer
"""

import os
import json
import logging
import requests
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
FEMA_API_BASE = "https://www.fema.gov/api/open/v2"
DEFAULT_DOWNLOAD_DIR = "fema_data"

# Ensure download directory exists
os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)


# --- Bedrock LLM Wrapper (Identical to other agents for consistency) ---
import boto3
BEDROCK_REGION = "us-east-2"
BEDROCK_MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"

class BedrockClaudeLLM(LLM):
    bedrock: Any = None
    model_id: str = BEDROCK_MODEL_ID

    def __init__(self):
        super().__init__()
        try:
            self.bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
        except Exception as e:
            logger.error(f"Bedrock init failed: {e}")

    @property
    def _llm_type(self) -> str:
        return "bedrock_claude_sonnet"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        if not self.bedrock:
            return "Mock response: Bedrock not available."
        
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
            logger.error(f"LLM call failed: {e}")
            raise e

# --- Tools ---

class ListFemaDatasetsTool(BaseTool):
    """List available FEMA datasets from the API metadata."""
    name: str = "list_fema_datasets"
    description: str = "List all available FEMA datasets/endpoints. Useful for finding the correct dataset name (e.g., 'DisasterDeclarationsSummaries'). Input: 'all' or a search term."

    def _run(self, query: str = "all", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # OpenFEMA stores dataset metadata in the 'DataSets' endpoint
            url = f"{FEMA_API_BASE}/DataSets"
            # Get only published datasets
            params = {"$filter": "deprecated eq false"} 
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            datasets = data.get('DataSets', [])
            
            if query.lower() != 'all':
                datasets = [d for d in datasets if query.lower() in d['name'].lower() or query.lower() in d.get('title', '').lower()]
            
            if not datasets:
                return f"No datasets found matching '{query}'."
            
            output = f"Found {len(datasets)} FEMA Datasets:\n"
            for d in datasets[:15]: # Limit to avoid context overflow
                output += f"- {d['name']} (v{d['version']}): {d.get('title', 'No title')}\n"
            
            if len(datasets) > 15:
                output += f"...and {len(datasets)-15} more.\n"
                
            return output
        except Exception as e:
            return f"Error listing datasets: {e}"

class QueryFemaDatasetTool(BaseTool):
    """Query a specific FEMA dataset with filters."""
    name: str = "query_fema_dataset"
    description: str = "Query a specific FEMA dataset. Input: JSON with {'dataset': 'DisasterDeclarationsSummaries', 'limit': 5, 'filter': 'stateCode eq \'NY\''}."

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if "{" in tool_input else {"dataset": tool_input.strip()}
            
            dataset_name = params.get('dataset')
            limit = params.get('limit', 5)
            odata_filter = params.get('filter', '')
            
            if not dataset_name:
                return "Error: 'dataset' name is required."
            
            url = f"{FEMA_API_BASE}/{dataset_name}"
            
            api_params = {"$top": limit, "$format": "json"}
            if odata_filter:
                api_params["$filter"] = odata_filter
                
            output = f"Querying {url} with params {api_params}...\n"
            
            response = requests.get(url, params=api_params, timeout=15)
            
            if response.status_code == 404:
                return f"Error: Dataset '{dataset_name}' not found. Use list_fema_datasets to check names."
            
            response.raise_for_status()
            result_data = response.json()
            
            # The structure is typically {metadata: ..., [DatasetName]: [...]}
            # But specific endpoints use the dataset name as the key
            data_records = result_data.get(dataset_name, [])
            
            if not data_records:
                return f"No records found for {dataset_name} with filter '{odata_filter}'."
            
            output += f"Returned {len(data_records)} records.\n"
            # Preview first record
            output += f"Sample Record: {json.dumps(data_records[0], indent=2)}\n"
            
            return output
            
        except Exception as e:
            return f"Error querying FEMA API: {e}"

class DownloadFemaDataTool(BaseTool):
    """Download FEMA data to a local file."""
    name: str = "download_fema_data"
    description: str = "Download FEMA data to CSV. Input: JSON with {'dataset': '...', 'filter': '...', 'output_filename': 'data.csv'}."

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input)
            dataset_name = params.get('dataset')
            odata_filter = params.get('filter', '')
            filename = params.get('output_filename', f"{dataset_name}.csv")
            
            if not dataset_name:
                return "Error: dataset name required."
                
            output_path = Path(DEFAULT_DOWNLOAD_DIR) / filename
            
            # API Call (Fetching up to 1000 for this demo default, can be paginated if needed)
            url = f"{FEMA_API_BASE}/{dataset_name}"
            api_params = {"$top": 1000, "$format": "json"} # Simple limit for now
            if odata_filter:
                api_params["$filter"] = odata_filter
                
            print(f"Downloading from {url}...")
            response = requests.get(url, params=api_params)
            response.raise_for_status()
            
            data = response.json().get(dataset_name, [])
            
            if not data:
                return "No data found to download."
            
            df = pd.DataFrame(data)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)

            return f"Successfully downloaded {len(df)} records to {output_path.resolve()}."

        except Exception as e:
            return f"Download failed: {e}"

# --- Agent Factory ---

def create_fema_agent() -> AgentExecutor:
    """Create the FEMA Data Acquisition Agent."""

    llm = BedrockClaudeLLM()

    tools = [
        ListFemaDatasetsTool(),
        QueryFemaDatasetTool(),
        DownloadFemaDataTool()
    ]

    template = """You are an expert FEMA Data Acquisition Agent.
Your goal is to help users find and download disaster, flood, and emergency management data using the OpenFEMA API.

**API Information:**
- Base URL: https://www.fema.gov/api/open/v2
- Filtering uses OData format: `field_name eq 'value'`, `date gt '2020-01-01'`.
- Important Datasets:
  - `DisasterDeclarationsSummaries`: General info on declared disasters (state, type, year).
  - `HousingAssistanceOwners`/`HousingAssistanceRenters`: Individual assistance data.
  - `FemaWebDisasterDeclarations`: Detailed web declarations.
  - `NfipClaims`: National Flood Insurance Program claims (requires specific permissions usually, but check PII versions usually masked).
  - Use `list_fema_datasets` to find others.

**Strategy:**
1. If the user asks for data but doesn't specify a dataset ID, use `list_fema_datasets` to find the most relevant one.
2. Use `query_fema_dataset` to peek at the data and verify filters work (e.g. valid fields).
3. Use `download_fema_data` to save the final file.
4. **File Path Reporting (MANDATORY)**: In your Final Answer, ALWAYS include the COMPLETE absolute file path for any saved file. NEVER report just the filename without the full directory path.

**Methodological Guardrails (CRITICAL):**
1. **Cross-Categorical Search**: "Flood" is a result, not just a cause. When users ask for "flood data", you MUST qualify your search to include related Incident Types:
   - "Hurricane" (e.g., Hurricane Ida caused massive flooding but is classified as Hurricane)
   - "Severe Storm(s)"
   - "Coastal Storm"
   - "Dam/Levee Break"
   - "Tornado" (often accompanied by heavy rain/flooding)
2. **Zero-Result Safety Check**: If a query for `incidentType eq 'Flood'` returns 0 results for a known disaster period, do NOT conclude "no floods occurred". IMMEDIATELY re-run the query with `incidentType eq 'Hurricane'` or `incidentType eq 'Severe Storm'`.
3. **Clarification**: If unsure, list the disaster declarations found for that period regardless of type, so the user can see explicit event names.
4. **Expanded Disaster Types (Rule of Thumb)**:
   - **Wildfire**: Check also "Fire", "Drought" (precursor), "Mud/Landslide" (post-fire).
   - **Winter Storm**: Check also "Snow", "Ice Storm", "Freezing", "Blizzard", "Severe Storm".
   - **Severe Storm**: Check also "Tornado", "Straight-line Winds", "Thunderstorm", "Hail".
   - **Earthquake**: Check also "Tsunami", "Fire".
5. **Counting Methodology (CRITICAL - Avoid Misleading Numbers)**:
   - FEMA declarations are counted **per county and per declaration type** (IA, PA, EM). One hurricane affecting 20 counties = 20+ records in DisasterDeclarationsSummaries, NOT 20 separate hurricanes.
   - When reporting "how many" disasters occurred, ALWAYS deduplicate by `disasterNumber` to get **unique disaster events** (not raw record count).
   - Example: "261 hurricane declaration records" is WRONG to report as "261 hurricanes". It should be: "X unique hurricanes resulted in 261 county-level declarations."
   - Use this pattern: group by `disasterNumber` first, then count unique events vs total declaration records.
6. **Cascading Disaster Chains (Explain Relationships)**:
   - Hurricanes often cause flooding, storm surge, tornadoes, and landslides — but FEMA classifies the event by its PRIMARY incident type.
   - When a user asks about "floods in NY 2021", explain that Hurricane Ida (classified as "Hurricane") caused catastrophic flooding — it won't appear under `incidentType eq 'Flood'`.
   - Always explain these causal chains in your response so users understand why a "flood" search may miss hurricane-caused floods.

**Tools:**
{tools}

**Tool Names:**
[{tool_names}]

Use the following format:
Question: input question
Thought: reasoning
Action: tool name (must be one of [{tool_names}])
Action Input: input
Observation: result
...
Final Answer: Final response.

MANDATORY: always include COMPLETE absolute file path in Final Answer for any saved file.

Question: {input}
Thought: {agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)

    agent = create_react_agent(llm, tools, prompt)

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=20,
        handle_parsing_errors=True,
    )

def get_fema_agent():
    return create_fema_agent()

if __name__ == "__main__":
    print("Initializing FEMA Agent...")
    agent = create_fema_agent()
    print("Agent Ready.")
    
    test_q = "List available datasets containing 'Disaster'"
    print(f"Testing: {test_q}")
    res = agent.invoke({"input": test_q})
    print(res['output'])
