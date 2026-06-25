#!/usr/bin/env python3
"""
FloodNet Data Acquisition Agent
================================

Searches and downloads NYC FloodNet street flood sensor data via the
NYC Open Data SODA API (dataset aq7i-eu5q).

Source: NYC Department of Environmental Protection
API:    https://data.cityofnewyork.us/resource/aq7i-eu5q.json
"""

import os
import json
import logging
import requests
import sqlite3
import pandas as pd
from typing import Optional, List, Any
from pathlib import Path
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
import boto3

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SODA_API_URL    = "https://data.cityofnewyork.us/resource/aq7i-eu5q.json"
DOWNLOAD_DIR    = "floodnet_downloads"
DB_PATH         = "climate_knowledge_graph.db"
BEDROCK_REGION  = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


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
        return "bedrock_claude"

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        if not self.bedrock:
            return "Bedrock not available."
        stop_sequences = stop or ["\nObservation:"]
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "stop_sequences": stop_sequences,
        })
        response = self.bedrock.invoke_model(modelId=self.model_id, body=body)
        return json.loads(response["body"].read())["content"][0]["text"].strip()


class SearchFloodNetKGTool(BaseTool):
    """Search the local knowledge graph for FloodNet datasets."""
    name: str = "search_floodnet_kg"
    description: str = (
        "Search the knowledge graph for FloodNet NYC flood sensor datasets. "
        "Input: a search term such as a borough (Brooklyn, Queens), sensor name, "
        "date (2021-09), or 'all' to list available sensors."
    )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            if query.strip().lower() == "all":
                sql = "SELECT dataset_id, title, short_name FROM stored_datasets WHERE short_name LIKE 'FLOODNET%' LIMIT 30"
                rows = conn.execute(sql).fetchall()
            else:
                sql = """SELECT dataset_id, title, short_name, dataset_properties
                         FROM stored_datasets
                         WHERE short_name LIKE 'FLOODNET%'
                         AND (title LIKE ? OR dataset_properties LIKE ?)
                         LIMIT 20"""
                term = f"%{query}%"
                rows = conn.execute(sql, (term, term)).fetchall()
            conn.close()

            if not rows:
                return f"No FloodNet datasets found matching '{query}'."

            out = f"Found {len(rows)} FloodNet dataset(s) matching '{query}':\n"
            for row in rows:
                props = json.loads(row[3]) if len(row) > 3 else {}
                depth = props.get("max_depth_inches", "")
                start = props.get("time_start", "")
                out += f"  - {row[2]} | {row[1]}"
                if start:
                    out += f" | start={start[:10]}"
                if depth:
                    out += f" | max_depth={depth} in"
                out += "\n"
            return out
        except Exception as e:
            return f"Error searching knowledge graph: {e}"


class DownloadFloodNetTool(BaseTool):
    """Download FloodNet flood event records to a local CSV file."""
    name: str = "download_floodnet_data"
    description: str = (
        "Download FloodNet flood sensor records from NYC Open Data to a CSV file. "
        "Input: JSON with optional filters, e.g. "
        "{\"sensor_name\": \"Brooklyn\", \"limit\": 500, \"start\": \"2021-08-01\", \"end\": \"2021-09-01\"}. "
        "Leave empty or pass '{}' to download all available records."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params_in = json.loads(tool_input) if tool_input.strip().startswith("{") else {}
        except Exception:
            params_in = {}

        limit       = params_in.get("limit", 2000)
        sensor_name = params_in.get("sensor_name", "")
        start_dt    = params_in.get("start", "")
        end_dt      = params_in.get("end", "")

        api_params: dict = {"$limit": limit, "$order": "flood_start_time DESC"}

        where_clauses = []
        if sensor_name:
            where_clauses.append(f"sensor_name like '%{sensor_name}%'")
        if start_dt:
            where_clauses.append(f"flood_start_time >= '{start_dt}'")
        if end_dt:
            where_clauses.append(f"flood_start_time <= '{end_dt}'")
        if where_clauses:
            api_params["$where"] = " AND ".join(where_clauses)

        try:
            response = requests.get(SODA_API_URL, params=api_params, timeout=30)
            response.raise_for_status()
            records = response.json()
        except Exception as e:
            return f"Error calling FloodNet API: {e}"

        if not records:
            return "No records returned from FloodNet API with given filters."

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"floodnet_{sensor_name or 'all'}_{ts}.csv"
        output_path = Path(DOWNLOAD_DIR) / filename

        df = pd.DataFrame(records)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        return (
            f"Downloaded {len(df)} FloodNet flood event records to {output_path.resolve()}.\n"
            f"Columns: {', '.join(df.columns.tolist())}\n"
            f"Date range: {df['flood_start_time'].min()} to {df['flood_start_time'].max()}"
        )


FLOODNET_PROMPT = PromptTemplate.from_template("""You are the FloodNet Data Acquisition Agent.
You help users find and download NYC street flood sensor data from the FloodNet network.

IMPORTANT date handling rules:
- If the user mentions a year (e.g. "2024"), set start="YYYY-01-01" and end="YYYY-12-31".
- If the user mentions a month (e.g. "August 2021"), set start="2021-08-01" and end="2021-08-31".
- Always pass sensor_name and date filters together in the JSON input to download_floodnet_data.
- Example for "Brooklyn 2024": {{"sensor_name": "Brooklyn", "start": "2024-01-01", "end": "2024-12-31", "limit": 2000}}

Tools available: {tools}
Tool names: {tool_names}

Format:
Thought: <reasoning>
Action: <tool_name>
Action Input: <input>
Observation: <result>
...
Thought: I now know the final answer.
Final Answer: <answer>

MANDATORY: always include COMPLETE absolute file path in Final Answer for any saved file.

Question: {input}
Thought:{agent_scratchpad}""")


def get_floodnet_agent() -> AgentExecutor:
    llm = BedrockClaudeLLM()
    tools = [SearchFloodNetKGTool(), DownloadFloodNetTool()]
    agent = create_react_agent(llm=llm, tools=tools, prompt=FLOODNET_PROMPT)
    return AgentExecutor(
        agent=agent, tools=tools,
        verbose=True, max_iterations=8, handle_parsing_errors=True,
    )


if __name__ == "__main__":
    executor = get_floodnet_agent()
    result = executor.invoke({"input": "Find FloodNet sensor data from Brooklyn and download it."})
    print(result.get("output"))
