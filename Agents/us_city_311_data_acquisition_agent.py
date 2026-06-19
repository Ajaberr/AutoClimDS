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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_DOWNLOAD_DIR = "us_311_data"
SOCRATA_APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN", "")

NYC_311_V3_URL = "https://data.cityofnewyork.us/api/v3/views/erm2-nwe9/query.json"

# Known Socrata 311 Endpoints
# Format: City Key -> {Name, API_URL, Dataset_ID}
CITY_ENDPOINTS = {
    "nyc": {
        "name": "New York City",
        "domain": "data.cityofnewyork.us",
        "dataset_id": "erm2-nwe9",
        "doc_url": "https://data.cityofnewyork.us/resource/erm2-nwe9",
        "v3_url": NYC_311_V3_URL,
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
os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)

# --- Bedrock LLM Wrapper ---
from dotenv import load_dotenv
load_dotenv()
import boto3
BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")

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

def get_socrata_headers() -> dict:
    """Return headers with app token if available."""
    headers = {}
    if SOCRATA_APP_TOKEN:
        headers["X-App-Token"] = SOCRATA_APP_TOKEN
    return headers

def resolve_city_key(city_input: str) -> str:
    """Fuzzy match city input to a known key, or return as is if it seems to be an ID."""
    city_input = city_input.lower().strip()
    if city_input in ["nyc", "new york", "new york city", "ny"]:
        return "nyc"
    if city_input in ["sf", "san francisco", "san fran"]:
        return "san_francisco"
    if city_input in ["chi", "chicago"]:
        return "chicago"
    if city_input in ["austin", "tx"]:
        return "austin"
    return city_input

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
            url = get_api_url(city_key)
            
            # We fetch 1 record to see the keys
            params = {"$limit": 1}
            response = requests.get(url, params=params, headers=get_socrata_headers(), timeout=10)
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
            
            response = requests.get(url, params=api_params, headers=get_socrata_headers(), timeout=15)
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
            response = requests.get(url, params=api_params, headers=get_socrata_headers(), timeout=20)
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

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input)
            city_input = params.get('city')
            if not city_input:
                return "Error: 'city' parameter is required."

            city_key = resolve_city_key(city_input)
            where_clause = params.get('where')
            limit = params.get('limit', 50000)
            filename = params.get('output_filename', f"{city_key}_311_data.csv")
            output_path = Path(DEFAULT_DOWNLOAD_DIR) / filename

            # Route NYC through the faster v3 API
            if city_key == "nyc":
                soql_parts = [f"SELECT * LIMIT {limit}"]
                if where_clause:
                    soql_parts.insert(0, f"SELECT * WHERE {where_clause} LIMIT {limit}")
                soql = soql_parts[0]
                print(f"Downloading NYC 311 data via v3 API...")
                resp = requests.get(NYC_311_V3_URL, params={"$query": soql},
                                    headers=get_socrata_headers(), timeout=120)
                resp.raise_for_status()
                raw = resp.json()
                if isinstance(raw, dict) and "data" in raw and "columns" in raw:
                    cols = [c.get("fieldName", c.get("name", f"col{i}"))
                            for i, c in enumerate(raw["columns"])]
                    data = [dict(zip(cols, row)) for row in raw["data"]]
                else:
                    data = raw if isinstance(raw, list) else []
            else:
                url = get_api_url(city_key)
                api_params = {"$limit": limit}
                if where_clause:
                    api_params["$where"] = where_clause
                if "order" in params:
                    api_params["$order"] = params["order"]
                print(f"Downloading data from {url} with params {api_params}...")
                response = requests.get(url, params=api_params,
                                        headers=get_socrata_headers(), timeout=120)
                if response.status_code != 200:
                    print(f"Error Response: {response.text}")
                response.raise_for_status()
                data = response.json()
            
            if not data:
                return "No data found to download."
            
            df = pd.DataFrame(data)
            df.to_csv(output_path, index=False)
            
            return f"Successfully downloaded {len(df)} records to {output_path}."
            
        except ValueError as ve:
            return str(ve)
        except Exception as e:
            return f"Download failed: {e}"

class QueryNYC311V3Tool(BaseTool):
    """Query NYC 311 data via the v3 API endpoint with full SoQL support."""
    name: str = "query_nyc311_v3"
    description: str = (
        "Query NYC 311 Service Requests using the v3 API endpoint. "
        "Supports SoQL: $where, $select, $order, $limit, $offset, or a full $query string. "
        "Input: JSON with any of: 'where', 'select', 'order', 'limit' (default 1000), 'offset', 'query' (full SoQL), 'download' (true/false), 'filename'. "
        "Example: {\"where\": \"complaint_type='Street Flooding' AND created_date>'2024-01-01'\", \"limit\": 500} "
        "Example: {\"query\": \"SELECT complaint_type, count(*) as n GROUP BY complaint_type ORDER BY n DESC LIMIT 20\"}"
    )

    def _parse_v3_response(self, data: Any) -> list:
        """Normalise v3 response to a list of dicts."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            # Format: {"data": [[...], ...], "columns": [...]}
            if "data" in data and "columns" in data:
                cols = [c.get("fieldName", c.get("name", f"col{i}"))
                        for i, c in enumerate(data["columns"])]
                rows = data["data"]
                if rows and isinstance(rows[0], list):
                    return [dict(zip(cols, row)) for row in rows]
                return rows
            # Format: {"data": [{...}, ...]}
            if "data" in data:
                return data["data"] if isinstance(data["data"], list) else [data["data"]]
        return []

    def _build_soql(self, params: dict) -> str:
        """Build a SoQL SELECT statement from individual params."""
        select  = params.get("select", "*")
        limit   = params.get("limit", 1000)
        offset  = params.get("offset", 0)
        parts   = [f"SELECT {select}"]
        if "where" in params:
            parts.append(f"WHERE {params['where']}")
        if "order" in params:
            parts.append(f"ORDER BY {params['order']}")
        parts.append(f"LIMIT {limit} OFFSET {offset}")
        return " ".join(parts)

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input.strip().startswith("{") else {}
        except Exception:
            return "Invalid input — provide a JSON object."

        soql = params.get("query") or self._build_soql(params)

        try:
            resp = requests.get(NYC_311_V3_URL, params={"$query": soql}, timeout=30)
            resp.raise_for_status()
            records = self._parse_v3_response(resp.json())
        except Exception as e:
            return f"NYC 311 v3 API error: {e}"

        if not records:
            return "No records returned."

        download = params.get("download", False)
        if download:
            filename = params.get("filename", "nyc_311_v3.csv")
            out_path = Path(DEFAULT_DOWNLOAD_DIR) / filename
            pd.DataFrame(records).to_csv(out_path, index=False)
            return (f"Downloaded {len(records)} records to {out_path}.\n"
                    f"Columns: {', '.join(records[0].keys()) if records else ''}")

        summary = f"Returned {len(records)} records.\n"
        summary += f"Columns: {', '.join(records[0].keys())}\n"
        summary += f"Sample record:\n{json.dumps(records[0], indent=2, default=str)}"
        return summary[:3000]


# --- Agent Factory ---

def create_us_311_agent() -> AgentExecutor:
    """Create the US City 311 Data Acquisition Agent."""
    
    llm = BedrockClaudeLLM()
    
    tools = [
        ListSupportedCitiesTool(),
        Get311FieldsTool(),
        QueryNYC311V3Tool(),
        Query311DataTool(),
        Analyze311CategoryCountsTool(),
        Download311DataTool()
    ]
    
    template = """You are an expert US City 311 Data Acquisition Agent.
Your goal is to help users find, filter, and download 311 Service Request data from multiple US cities.

**Supported Cities:**
- New York City (NYC) — has both v2 Socrata API and v3 API
- Chicago
- San Francisco
- Austin
- You can list them using `list_supported_cities`.

**API Information:**
- NYC has a **dedicated v3 API** at https://data.cityofnewyork.us/api/v3/views/erm2-nwe9/query.json — prefer `query_nyc311_v3` for all NYC queries.
- Other cities use the **Socrata v2 Open Data API** (SoQL syntax).
- Query Language: SoQL (Similar to SQL).
  - `$where`: `status='Open'` or `created_date > '2023-01-01T00:00:00'`
  - `$limit`: Number of records.

**Strategy:**
1. **For NYC queries**: Always use `query_nyc311_v3` first — it is faster and more reliable.
   - Pass `"download": true` and `"filename": "..."` to save results to CSV.
   - Pass `"query"` for full SoQL, or use individual `"where"`, `"select"`, `"order"`, `"limit"` keys.
2. **For other cities**: Use `get_311_fields` first to check column names, then `query_311_data` or `download_311_data`.
3. **Inspect Fields**: Field names vary by city!
   - NYC: `complaint_type`, `borough`, `created_date`, `incident_zip`
   - Chicago: `sr_type`, `status`
   - SF: `service_request_id`, `service_name`
4. **Verify Counts**: Before downloading, use `analyze_311_counts` to see if your query captures the full picture.
   - If user asks for "Flooding", capture ALL relevant categories (e.g. `complaint_type IN ('Street Flooding', 'Sewer Backup', 'Catch Basin')`).
5. **Download**: Use `download_311_data` for non-NYC cities, or `query_nyc311_v3` with `"download": true` for NYC.
   - **CRITICAL**: Default limit is 50,000. For full-year analysis, set limit higher or filter first.

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
        memory=ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)
    )

def get_311_agent():
    return create_us_311_agent()

if __name__ == "__main__":
    print("Initializing US 311 Agent...")
    agent = create_us_311_agent()
    print("Agent Ready.")
    
    test_q = "Get the fields for Chicago 311 data"
    print(f"Testing: {test_q}")
    res = agent.invoke({"input": test_q})
    print(res['output'])
