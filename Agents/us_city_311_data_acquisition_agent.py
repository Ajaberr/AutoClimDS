#!/usr/bin/env python3
"""
US City 311 Data Acquisition Agent
==================================
An intelligent agent for querying and acquiring 311 Service Requests data 
from major US cities using Socrata Open Data APIs.

Features:
- Support for multiple cities (NYC, Chicago, San Francisco, Austin, etc.)
- Inspect available fields in the 311 dataset for a specific city
- Query data using Socrata Query Language (SoQL)
- Download filtered results to CSV/JSON

Supported Cities (Socrata):
- New York City (NYC)
- Chicago
- San Francisco
- Austin
- (And customizable URL support)

API Documentation: https://dev.socrata.com/
"""

import os
import json
import logging
import requests
import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM

try:
    import kg_writer
except Exception:
    kg_writer = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
# Constants
# --- EFS PERSISTENCE ---
DATA_DIR_ROOT = os.getenv("SIMULATION_DATA_DIR", ".")
DEFAULT_DOWNLOAD_DIR = os.path.join(DATA_DIR_ROOT, "us_311_data")

# Known Socrata 311 Endpoints
# Format: City Key -> {Name, API_URL, Dataset_ID}
CITY_ENDPOINTS = {
    "nyc": {
        "name": "New York City",
        "domain": "data.cityofnewyork.us",
        "dataset_id": "erm2-nwe9",
        "doc_url": "https://data.cityofnewyork.us/resource/erm2-nwe9"
    },
    "chicago": {
        "name": "Chicago",
        "domain": "data.cityofchicago.org",
        "dataset_id": "v6vf-nfxy",
        "doc_url": "https://data.cityofchicago.org/resource/v6vf-nfxy"
    },
    "san_francisco": {
        "name": "San Francisco",
        "domain": "data.sfgov.org",
        "dataset_id": "vw6y-z8j6",
        "doc_url": "https://data.sfgov.org/resource/vw6y-z8j6"
    },
    "austin": {
        "name": "Austin",
        "domain": "data.austintexas.gov",
        "dataset_id": "xwdj-i9he",
        "doc_url": "https://data.austintexas.gov/resource/xwdj-i9he"
    }
}

# Ensure download directory exists
if not os.path.exists(DEFAULT_DOWNLOAD_DIR):
    try:
        os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create download directory {DEFAULT_DOWNLOAD_DIR}: {e}")

# --- Bedrock LLM Wrapper ---
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

# --- Helpers ---

def get_api_url(city_key: str) -> str:
    """Construct the API URL for a given city key."""
    city_key = city_key.lower().replace(" ", "_")
    if city_key not in CITY_ENDPOINTS:
        raise ValueError(f"Unknown city '{city_key}'. Supported: {list(CITY_ENDPOINTS.keys())}")
    
    meta = CITY_ENDPOINTS[city_key]
    return f"https://{meta['domain']}/resource/{meta['dataset_id']}.json"

def resolve_city_key(city_input: str) -> Optional[str]:
    """Fuzzy match city input to a known key. Returns None if not found."""
    city_input = city_input.lower().strip()
    if city_input in ["nyc", "new york", "new york city", "ny"]:
        return "nyc"
    if city_input in ["sf", "san francisco", "san fran"]:
        return "san_francisco"
    if city_input in ["chi", "chicago", "illinois"]:
        return "chicago"
    if city_input in ["austin", "tx", "texas"]:
        return "austin"
    
    # STRICT GUARDRAIL: Do not pass through unknown cities
    return None

# --- Tools ---

class ListSupportedCitiesTool(BaseTool):
    """List cities supported by this 311 agent."""
    name: str = "list_supported_cities"
    description: str = "List the cities that this agent currently knows how to query for 311 data. No input needed."

    def _run(self, tool_input: str = "", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        output = "Supported Cities for 311 Data:\n"
        for key, meta in CITY_ENDPOINTS.items():
            output += f"- {meta['name']} (Key: '{key}')\n  Source: {meta['domain']}\n"
        return output

class Get311FieldsTool(BaseTool):
    """Get a list of available fields/columns for a specific city."""
    name: str = "get_311_fields"
    description: str = "Returns a list of valid field names for a specific city's 311 dataset. Input: City name (e.g., 'nyc', 'chicago')."

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            city_key = resolve_city_key(tool_input)
            if not city_key:
                 return f"Error: City '{tool_input}' is not supported. Supported cities: {list(CITY_ENDPOINTS.keys())}"
            
            url = get_api_url(city_key)
            
            # We fetch 1 record to see the keys
            params = {"$limit": 1}
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return f"The dataset for {city_key} appears to be empty."
                
            fields = list(data[0].keys())
            return f"Available Fields for {city_key} ({len(fields)}): {', '.join(fields)}"
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            return f"Error fetching fields: {e}"

class Query311DataTool(BaseTool):
    """Query 311 data for a city using SoQL filters."""
    name: str = "query_311_data"
    description: str = "Query 311 data. Input: JSON string with 'city', 'where' (SoQL filter), 'limit'. Example: {'city': 'chicago', 'where': 'status=\"OPEN\"', 'limit': 5}"

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if "{" in tool_input else {}
            if not params:
                return "Error: Input must be a JSON string with 'city' and query parameters."

            city_input = params.get('city')
            if not city_input:
                return "Error: 'city' parameter is required."
                
            city_key = resolve_city_key(city_input)
            if not city_key:
                 return f"Error: City '{city_input}' is not supported. Supported cities: {list(CITY_ENDPOINTS.keys())}"

            url = get_api_url(city_key)
            
            # Socrata Query Parameters
            api_params = {}
            if "where" in params:
                api_params["$where"] = params["where"]
            if "limit" in params:
                api_params["$limit"] = params.get("limit", 5)
            else:
                api_params["$limit"] = 5
            if "select" in params:
                api_params["$select"] = params["select"]
            if "order" in params:
                api_params["$order"] = params["order"]

            output = f"Querying {CITY_ENDPOINTS.get(city_key, {}).get('name', city_key)} 311 API with params: {api_params}...\n"
            
            response = requests.get(url, params=api_params, timeout=120)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return f"No records found matching query: {api_params}"
            
            output += f"Returned {len(data)} records.\n"
            output += f"Sample Record: {json.dumps(data[0], indent=2)}\n"
            
            return output
            
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            return f"Error querying 311 API: {e}. Check your SoQL syntax."

class Analyze311CategoryCountsTool(BaseTool):
    """Analyze 311 data by counting records grouped by a specific column (e.g., complaint type)."""
    name: str = "analyze_311_counts"
    description: str = "Get aggregate counts of 311 requests grouped by a specific column (usually 'complaint_type', 'sr_type', or 'service_name'). Input: JSON with 'city', 'group_by', and optional 'where'. Example: {'city': 'nyc', 'group_by': 'complaint_type', 'where': 'created_date > \"2023-01-01\"'}"

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if "{" in tool_input else {}
            city_input = params.get('city')
            group_by_col = params.get('group_by')
            
            if not city_input or not group_by_col:
                return "Error: 'city' and 'group_by' parameters are required."

            city_key = resolve_city_key(city_input)
            if not city_key:
                 return f"Error: City '{city_input}' is not supported. Supported cities: {list(CITY_ENDPOINTS.keys())}"
            
            url = get_api_url(city_key)

            # Construct Aggregate Query
            # SoQL: $select=complaint_type, count(*)&$group=complaint_type&$order=count(*) desc
            api_params = {
                "$select": f"{group_by_col}, count(*) as total_count",
                "$group": group_by_col,
                "$order": "total_count DESC",
                "$limit": 50 # Top 50 categories
            }
            if "where" in params:
                api_params["$where"] = params["where"]

            output = f"Analyzing counts for {city_key} by '{group_by_col}'...\n"
            response = requests.get(url, params=api_params, timeout=300)
            response.raise_for_status()
            data = response.json()

            if not data:
                return "No data found."

            output += f"Top Results:\n"
            for row in data[:20]:
                output += f"- {row.get(group_by_col, 'Unknown')}: {row.get('total_count', 0)}\n"
            
            return output

        except Exception as e:
            return f"Error analyzing counts: {e}"

class Download311DataTool(BaseTool):
    """Download 311 data to a CSV file."""
    name: str = "download_311_data"
    description: str = "Download filtered 311 data to CSV. Input: JSON with 'city', 'where', 'limit', 'output_filename'. Example: {'city': 'sf', 'where': 'opened > \"2023-01-01\"', 'limit': 1000, 'output_filename': 'sf_311.csv'}"
    session_id: Optional[str] = None

    def __init__(self, session_id: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id


    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input)
            city_input = params.get('city')
            if not city_input:
                return "Error: 'city' parameter is required."

            city_key = resolve_city_key(city_input)
            if not city_key:
                 return f"Error: City '{city_input}' is not supported. Supported cities: {list(CITY_ENDPOINTS.keys())}"

            url = get_api_url(city_key)
            
            where_clause = params.get('where')
            # INCREASED DEFAULT LIMIT to avoid undercounting (User feedback: 10k vs 30k reality)
            limit = params.get('limit', 50000) 
            filename = params.get('output_filename', f"{city_key}_311_data.csv")
            
            # Apply Session ID prefix to strict isolation
            if self.session_id and not filename.startswith(f"{self.session_id}_"):
                 filename = f"{self.session_id}_{filename}"
            
            output_path = Path(DEFAULT_DOWNLOAD_DIR) / filename
            
            api_params = {
                "$limit": limit
            }
            if where_clause:
                api_params["$where"] = where_clause
            if "order" in params:
                api_params["$order"] = params["order"]
                
            print(f"Downloading data from {url} with params {api_params}...")
            response = requests.get(url, params=api_params, timeout=600)
            
            if response.status_code != 200:
                print(f"Error Response: {response.text}")
                
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                return "No data found to download."
            
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)

            kg_msg = ""
            if kg_writer is not None:
                try:
                    stats = kg_writer.write_311_complaints(data, city_key=city_key)
                    kg_msg = f" KG: {stats['written']} nodes (errors {len(stats['errors'])})."
                except Exception as e:
                    kg_msg = f" KG skipped ({e})."

            return f"Successfully downloaded {len(df)} records to {output_path}.{kg_msg}"
            
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            return f"Download failed: {e}"

# --- Agent Factory ---

def create_us_311_agent(session_id: Optional[str] = None) -> AgentExecutor:
    """Create the US City 311 Data Acquisition Agent."""
    
    llm = BedrockClaudeLLM()
    
    tools = [
        ListSupportedCitiesTool(),
        Get311FieldsTool(),
        Query311DataTool(),
        Analyze311CategoryCountsTool(),
        Download311DataTool(session_id=session_id)
    ]
    
    template = """You are an expert US City 311 Data Acquisition Agent.
Your goal is to help users find, filter, and download 311 Service Request data.

**SCOPE GUARDRAILS (CRITICAL):**
1. **Supported Cities Only**: You can ONLY query data for:
   - New York City (NYC)
   - Chicago
   - San Francisco (SF)
   - Austin
2. **Unsupported Cities**: If a user asks for a city NOT on this list (e.g., "Los Angeles", "Houston"), you MUST explicitly state: 
   "I currently only support NYC, Chicago, San Francisco, and Austin. I cannot access data for [City Name]."
   - **Do NOT** offer to search other cities.
   - **Do NOT** ask "Would you like to search [Supported City] instead?".
   - Just state the limitation and stop.
   Do NOT attempt to guess endpoints or hallucinate data.

**API Information:**
- All supported cities use the **Socrata Open Data API**.
- Query Language: SoQL (Similar to SQL).
  - `$where`: `status='Open'` or `created_date > '2023-01-01T00:00:00'`
  - `$limit`: Number of records.

**Strategy:**
1. **Identify the City**: Match user input to a supported city. If unsupported, stop and inform the user.
2. **Inspect Fields**: Field names vary by city! 
   - NYC: `complaint_type`, `borough`
   - Chicago: `sr_type`, `status`
   - SF: `service_request_id`, `service_name`
   - ALWAYS use `get_311_fields(city)` first to check the column names.
3. **Verify Counts**: Before downloading, use `analyze_311_counts` to see if your query captures the full picture.
   - Example: Group by `complaint_type` to see if "Street Flooding" is separate from "Sewer Backup".
   - If user asks for "Flooding", ensure you capture ALL relevant categories (e.g. `complaint_type IN ('Street Flooding', 'Sewer Backup', 'Catch Basin')`).
4. **Download**: Use `download_311_data`.
   - **CRITICAL**: The default limit is 50,000. For full-year analysis (like "2021 flooding"), ensure the limit is high enough (e.g. 100000) or check the counts first. Filters are your friend.
5. **File Path Reporting (MANDATORY)**: In your Final Answer, ALWAYS include the COMPLETE absolute file path for any saved file. Example: "File saved to `/mnt/efs/data/us_311_data/session_nyc_flood_2022.csv`". NEVER report just the filename without the directory path.

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

Question: {input}
Thought: {agent_scratchpad}"""

    prompt = PromptTemplate.from_template(template)
    
    agent = create_react_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=50,
        handle_parsing_errors=True,
    )

def get_311_agent(session_id: Optional[str] = None):
    return create_us_311_agent(session_id=session_id)

if __name__ == "__main__":
    print("Initializing US 311 Agent...")
    agent = create_us_311_agent()
    print("Agent Ready.")
    
    test_q = "Get the fields for Chicago 311 data"
    print(f"Testing: {test_q}")
    res = agent.invoke({"input": test_q})
    print(res['output'])
