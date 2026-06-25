#!/usr/bin/env python3
"""
MRMS Data Acquisition Agent
============================

Searches and downloads MRMS (Multi-Radar/Multi-Sensor System) operational
radar and precipitation products from the NOAA/NCEP data server.

Products: QPE, reflectivity, rotation, hail, lightning (GRIB2 format)
Server:   https://mrms.ncep.noaa.gov/data/
Coverage: CONUS, ~1 km / 2-minute resolution
"""

import os
import json
import logging
import requests
import sqlite3
from typing import Optional, List, Any
from pathlib import Path
from datetime import datetime, timedelta

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

MRMS_SERVER      = "https://mrms.ncep.noaa.gov/data/2D"
DOWNLOAD_DIR     = "mrms_downloads"
DB_PATH          = "climate_knowledge_graph.db"
BEDROCK_REGION   = os.getenv("BEDROCK_REGION", "us-east-2")
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


class SearchMRMSKGTool(BaseTool):
    """Search the knowledge graph for MRMS products."""
    name: str = "search_mrms_kg"
    description: str = (
        "Search the knowledge graph for MRMS radar/precipitation products. "
        "Input: a category (Precipitation, Reflectivity, Severe Weather, Hail, Lightning, Quality), "
        "a product name (e.g. MultiSensor_QPE_01H_Pass2), or 'all' to list all products."
    )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            conn = sqlite3.connect(DB_PATH)
            if query.strip().lower() == "all":
                sql = """SELECT short_name, title FROM stored_datasets
                         WHERE short_name LIKE 'MRMS_%' LIMIT 50"""
                rows = conn.execute(sql).fetchall()
            else:
                sql = """SELECT short_name, title, dataset_properties
                         FROM stored_datasets
                         WHERE short_name LIKE 'MRMS_%'
                         AND (title LIKE ? OR dataset_properties LIKE ? OR short_name LIKE ?)
                         LIMIT 20"""
                term = f"%{query}%"
                rows = conn.execute(sql, (term, term, term)).fetchall()
            conn.close()

            if not rows:
                return f"No MRMS products found matching '{query}'."

            out = f"Found {len(rows)} MRMS product(s) matching '{query}':\n"
            for row in rows:
                props = json.loads(row[2]) if len(row) > 2 else {}
                interval = props.get("mrms_update_interval_min", "")
                units    = props.get("mrms_units", "")
                category = props.get("mrms_category", "")
                out += f"  - {row[0]} | {row[1]}"
                if category:
                    out += f" | category={category}"
                if interval:
                    out += f" | update={interval}min"
                if units:
                    out += f" | units={units}"
                out += "\n"
            return out
        except Exception as e:
            return f"Error searching knowledge graph: {e}"


class ListMRMSProductsTool(BaseTool):
    """List MRMS products available on the NCEP live server."""
    name: str = "list_mrms_live_products"
    description: str = (
        "List MRMS product directories available on the NOAA NCEP live server. "
        "Input: 'all' or a category keyword like 'QPE', 'Reflectivity', 'Rotation'."
    )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            response = requests.get(MRMS_SERVER + "/", timeout=15)
            response.raise_for_status()
            # Parse directory listing (NCEP uses Apache directory listing)
            lines = response.text.split("\n")
            dirs = [
                l.split('href="')[1].split('"')[0].rstrip("/")
                for l in lines
                if 'href="' in l and not l.strip().startswith("<a href=\"../\"")
                and not l.strip().startswith("<a href=\"?")
            ]
            dirs = [d for d in dirs if d and not d.startswith("?")]

            if query.lower() != "all":
                dirs = [d for d in dirs if query.lower() in d.lower()]

            if not dirs:
                return f"No MRMS product directories found matching '{query}' on live server."

            out = f"Found {len(dirs)} MRMS product(s) on NCEP server:\n"
            for d in dirs[:30]:
                out += f"  - {d}  →  {MRMS_SERVER}/{d}/\n"
            return out
        except Exception as e:
            return f"Could not reach MRMS live server ({e}). Use search_mrms_kg to query the knowledge graph instead."


class DownloadMRMSTool(BaseTool):
    """Download the latest MRMS GRIB2 file for a given product."""
    name: str = "download_mrms_data"
    description: str = (
        "Download the latest available MRMS GRIB2 file for a product from the NCEP server. "
        "Input: JSON with 'product' name, e.g. "
        "{\"product\": \"MultiSensor_QPE_01H_Pass2\"}. "
        "The most recent file is downloaded automatically."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input.strip().startswith("{") else {}
        except Exception:
            return "Invalid input. Provide JSON like {\"product\": \"MultiSensor_QPE_01H_Pass2\"}."

        product = params.get("product", "").strip()
        if not product:
            return "Error: 'product' name is required."

        product_url = f"{MRMS_SERVER}/{product}/"
        try:
            resp = requests.get(product_url, timeout=15)
            resp.raise_for_status()
        except Exception as e:
            return (
                f"Could not reach product directory for '{product}': {e}\n"
                f"Tried: {product_url}\n"
                f"Use list_mrms_live_products to see exact product directory names."
            )

        # Find the most recent .grib2.gz file in the directory listing
        lines = resp.text.split("\n")
        files = [
            l.split('href="')[1].split('"')[0]
            for l in lines
            if 'href="' in l and ".grib2.gz" in l
        ]
        if not files:
            return f"No GRIB2 files found in {product_url}"

        latest_file = sorted(files)[-1]
        file_url    = product_url + latest_file

        out_dir  = Path(DOWNLOAD_DIR) / product
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / latest_file

        if out_path.exists():
            return f"File already downloaded: {out_path}"

        try:
            dl = requests.get(file_url, timeout=60, stream=True)
            dl.raise_for_status()
            with open(out_path, "wb") as f:
                for chunk in dl.iter_content(chunk_size=65536):
                    f.write(chunk)
            size_mb = out_path.stat().st_size / 1_000_000
            return (
                f"Downloaded MRMS product '{product}':\n"
                f"  File: {out_path}\n"
                f"  Size: {size_mb:.2f} MB\n"
                f"  Format: GRIB2 (compressed .gz) — use wgrib2 or cfgrib to read\n"
                f"  Source: {file_url}"
            )
        except Exception as e:
            return f"Download failed for {file_url}: {e}"


MRMS_PROMPT = PromptTemplate.from_template("""You are the MRMS Data Acquisition Agent.
You help users find and download MRMS (Multi-Radar/Multi-Sensor System) radar and
precipitation products covering the contiguous United States at ~1 km / 2-min resolution.

Product categories: Precipitation (QPE), Reflectivity, Severe Weather (Rotation/Shear),
                    Hail (MESH), Lightning, Quality Index
Format: GRIB2 (.grib2.gz) — decode with wgrib2, cfgrib, or pygrib

Tools: {tools}
Tool names: {tool_names}

Format:
Thought: <reasoning>
Action: <tool_name>
Action Input: <input>
Observation: <result>
...
Final Answer: <answer>

MANDATORY: always include COMPLETE absolute file path in Final Answer for any saved file.

Question: {input}
Thought:{agent_scratchpad}""")


def get_mrms_agent() -> AgentExecutor:
    llm = BedrockClaudeLLM()
    tools = [SearchMRMSKGTool(), ListMRMSProductsTool(), DownloadMRMSTool()]
    agent = create_react_agent(llm=llm, tools=tools, prompt=MRMS_PROMPT)
    return AgentExecutor(
        agent=agent, tools=tools,
        verbose=True, max_iterations=8, handle_parsing_errors=True,
    )


if __name__ == "__main__":
    executor = get_mrms_agent()
    result = executor.invoke({"input": "What MRMS QPE products are available and download the latest MultiSensor_QPE_01H_Pass2."})
    print(result.get("output"))
