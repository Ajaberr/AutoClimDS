#!/usr/bin/env python3
"""
FloodSimBench Data Acquisition Agent
=====================================

Searches and downloads FloodSimBench flood simulation benchmark data
from Hugging Face (chrimerss/FloodSimBench).

Dataset: https://huggingface.co/datasets/chrimerss/FloodSimBench
Format:  GeoTIFF — DEM, water depth time series, flood severity maps
Cities:  10 US cities, 4 rainfall return periods (10/25/50/100-year)
"""

import os
import json
import logging
import requests
import sqlite3
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

HF_DATASET_ID    = "chrimerss/FloodSimBench"
HF_RESOLVE_BASE  = f"https://huggingface.co/datasets/{HF_DATASET_ID}/resolve/main"
HF_API_BASE      = f"https://huggingface.co/api/datasets/{HF_DATASET_ID}/tree/main"
HF_RAINFALL_JSON = f"https://huggingface.co/datasets/{HF_DATASET_ID}/resolve/main/cities_rainfall.json"

# Cache rainfall lookup so we only fetch once per session
_RAINFALL_CACHE: dict = {}
DOWNLOAD_DIR     = "floodsimbench_downloads"
DB_PATH          = "climate_knowledge_graph.db"
BEDROCK_REGION   = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")

# Actual region prefixes from the dataset (each city has multiple sub-regions)
CITY_MAP = {
    "houston":       ["HOU001", "HOU002", "HOU003", "HOU004", "HOU005", "HOU006", "HOU007"],
    "atlanta":       ["ATL001", "ATL002"],
    "austin":        ["AUS001", "AUS002"],
    "dallas":        ["DAL001", "DAL002"],
    "los angeles":   ["LA001",  "LA002"],
    "miami":         ["MIA001", "MIA002"],
    "new york":      ["NYC001", "NYC002"],
    "oklahoma city": ["OKC001", "OKC002"],
    "orlando":       ["ORL001", "ORL002"],
    "san francisco": ["SF001",  "SF002"],
}
RETURN_PERIODS = [10, 25, 50, 100]

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _get_rainfall_mm(region: str, return_period: int) -> Optional[int]:
    """Return the correct rainfall amount (mm) for a region and return period."""
    global _RAINFALL_CACHE
    if not _RAINFALL_CACHE:
        def _parse_mm(val):
            try:
                return int(str(val).replace("mm", "").replace(" ", "").strip())
            except Exception:
                return None

        try:
            resp = requests.get(HF_RAINFALL_JSON, timeout=15)
            resp.raise_for_status()
            for entry in resp.json():
                city_id = entry.get("City ID", "")
                _RAINFALL_CACHE[city_id] = {
                    10:  _parse_mm(entry.get("10-yr", 0)),
                    25:  _parse_mm(entry.get("25-yr", 0)),
                    50:  _parse_mm(entry.get("50-yr", 0)),
                    100: _parse_mm(entry.get("100-yr", 0)),
                }
        except Exception as e:
            logger.warning("Could not fetch cities_rainfall.json: %s", e)
            return None
    entry = _RAINFALL_CACHE.get(region)
    return entry.get(return_period) if entry else None


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


class SearchFloodSimBenchKGTool(BaseTool):
    """Search the knowledge graph for FloodSimBench datasets."""
    name: str = "search_floodsimbench_kg"
    description: str = (
        "Search the knowledge graph for FloodSimBench flood simulation datasets. "
        "Input: a city name (Houston, Miami, Nashville, etc.), return period (10, 25, 50, 100), "
        "or 'all' to list all available entries."
    )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        q = query.strip().lower()
        if q == "all" or "list" in q or "available" in q or "cities" in q:
            out = f"FloodSimBench contains {len(CITY_MAP)} US cities:\n"
            for city, regions in CITY_MAP.items():
                out += f"  - {city.title()}: {len(regions)} region(s) ({', '.join(regions)})\n"
            out += f"\nReturn periods available: {RETURN_PERIODS} years\n"
            out += "Data hosted on HuggingFace: chrimerss/FloodSimBench"
            return out

        matches = {city: regions for city, regions in CITY_MAP.items() if q in city}
        if matches:
            out = f"Found {len(matches)} matching city/cities:\n"
            for city, regions in matches.items():
                out += f"  - {city.title()}: regions {', '.join(regions)}, return periods {RETURN_PERIODS} years\n"
            return out

        return f"No FloodSimBench city found matching '{query}'. Available cities: {', '.join(c.title() for c in CITY_MAP)}"


class ListFloodSimBenchFilesTool(BaseTool):
    """List actual files available in a FloodSimBench region folder."""
    name: str = "list_floodsimbench_files"
    description: str = (
        "List the actual GeoTIFF files available for a FloodSimBench region on Hugging Face. "
        "Input: a region ID such as 'HOU001' or a city name like 'Houston' "
        "(returns first region for that city)."
    )

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        query_lower = query.strip().lower()

        # Resolve city name to first region ID
        region = query.strip().upper()
        for city, regions in CITY_MAP.items():
            if query_lower in city or city in query_lower:
                region = regions[0]
                break

        try:
            url = f"{HF_API_BASE}/{region}"
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            entries = resp.json()
            files = [e["path"].split("/")[-1] for e in entries if e.get("type") == "file"]
            if not files:
                return f"No files found in region '{region}'."
            out = f"Files in FloodSimBench/{region} ({len(files)} total):\n"
            for f in files[:20]:
                out += f"  {f}\n"
            if len(files) > 20:
                out += f"  ...and {len(files)-20} more.\n"
            return out
        except Exception as e:
            return f"Could not list files for region '{region}': {e}"


class DownloadFloodSimBenchTool(BaseTool):
    """Download FloodSimBench GeoTIFF files from Hugging Face."""
    name: str = "download_floodsimbench_data"
    description: str = (
        "Download FloodSimBench flood simulation GeoTIFF files from Hugging Face. "
        "Input: JSON with 'city' and 'return_period', e.g. "
        "{\"city\": \"Houston\", \"return_period\": 100}. "
        "Downloads the MaxDepth summary file (fastest) and the DEM by default. "
        "Set 'file_type': 'waterdepth' to get time-series frames (all frames by default). "
        "Set 'max_frames' to limit number of frames, e.g. {\"max_frames\": 5}."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input.strip().startswith("{") else {}
        except Exception:
            return "Invalid input. Provide JSON like {\"city\": \"Houston\", \"return_period\": 100}."

        city_name  = params.get("city", "").lower().strip()
        rp         = int(params.get("return_period", 100))
        region_in  = params.get("region", "").upper().strip()
        file_type  = params.get("file_type", "maxdepth").lower()
        max_frames = params.get("max_frames", None)  # None = download all frames

        if rp not in RETURN_PERIODS:
            return f"Return period {rp} not valid. Choose from: {RETURN_PERIODS}"

        # Resolve region
        if region_in:
            region = region_in
        else:
            regions = None
            for city, rs in CITY_MAP.items():
                if city_name in city or city in city_name:
                    regions = rs
                    break
            if not regions:
                available = ", ".join(k.title() for k in CITY_MAP)
                return f"City '{city_name}' not found. Available: {available}"
            region = regions[0]

        # Resolve correct rainfall mm for this region + return period
        rainfall_mm = _get_rainfall_mm(region, rp)
        mm_str = f"{rainfall_mm}mm" if rainfall_mm else f"{rp}mm"
        logger.info("Region %s, %d-yr return period → %s rainfall", region, rp, mm_str)

        # List files to find correct filenames
        try:
            list_url = f"{HF_API_BASE}/{region}"
            resp = requests.get(list_url, timeout=15)
            resp.raise_for_status()
            entries = resp.json()
            all_paths = [e["path"] for e in entries if e.get("type") == "file"]
        except Exception as e:
            return f"Could not list files for region '{region}': {e}"

        # Pick target files based on file_type
        if file_type == "waterdepth":
            targets = [
                p for p in all_paths
                if f"_{mm_str}_WaterDepth_" in p and p.endswith(".tif")
            ]
            if max_frames is not None:
                targets = targets[:int(max_frames)]
        else:
            # MaxDepth + DEM — small summary files, fast to download
            targets = [
                p for p in all_paths
                if (f"_{mm_str}_MaxDepth" in p or "_DEM" in p) and p.endswith(".tif")
            ]

        if not targets:
            available_names = [p.split("/")[-1] for p in all_paths[:10]]
            return (
                f"No files matching '{file_type}' for {rp}mm in region '{region}'.\n"
                f"Available files: {', '.join(available_names)}"
            )

        out_dir = Path(DOWNLOAD_DIR) / f"{region}_{rp}yr"
        out_dir.mkdir(parents=True, exist_ok=True)

        downloaded, failed = [], []
        for rel_path in targets:
            filename   = rel_path.split("/")[-1]
            url        = f"{HF_RESOLVE_BASE}/{rel_path}"
            local_path = out_dir / filename

            if local_path.exists():
                size_mb = local_path.stat().st_size / 1_000_000
                downloaded.append(f"{filename} ({size_mb:.1f} MB) [already exists]")
                continue
            try:
                dl = requests.get(url, timeout=180, stream=True)
                dl.raise_for_status()
                with open(local_path, "wb") as f:
                    for chunk in dl.iter_content(chunk_size=65536):
                        f.write(chunk)
                size_mb = local_path.stat().st_size / 1_000_000
                downloaded.append(f"{filename} ({size_mb:.1f} MB)")
            except Exception as e:
                failed.append(f"{filename}: {e}")

        result = (
            f"FloodSimBench — {city_name.title() or region}, "
            f"{rp}-year return period, region {region}:\n"
            f"  Downloaded: {len(downloaded)} file(s)\n"
        )
        if downloaded:
            result += f"  Saved to: {out_dir.resolve()}\n"
            for f in downloaded:
                result += f"    {f}\n"
        if failed:
            result += f"  Failed ({len(failed)}): {'; '.join(failed)}\n"
        return result


FLOODSIMBENCH_PROMPT = PromptTemplate.from_template("""You are the FloodSimBench Data Acquisition Agent.
You help users find and download flood simulation benchmark data for 10 US cities.

Available cities: Houston (HOU001-HOU007), Atlanta (ATL001-ATL002), Austin (AUS001-AUS002),
                  Dallas (DAL001-DAL002), Los Angeles (LA001-LA002), Miami (MIA001-MIA002),
                  New York (NYC001-NYC002), Oklahoma City (OKC001-OKC002),
                  Orlando (ORL001-ORL002), San Francisco (SF001-SF002)
Return periods: 10, 25, 50, 100 years
Data: 1-m DEM, water depth time series, flood severity maps (GeoTIFF)

WORKFLOW: First use list_floodsimbench_files to see available files, then download_floodsimbench_data.

Tools: {tools}
Tool names: {tool_names}

Format:
Thought: <reasoning>
Action: <tool_name>
Action Input: <input>
Observation: <result>
...
Final Answer: <answer>

Question: {input}
Thought:{agent_scratchpad}""")


def get_floodsimbench_agent() -> AgentExecutor:
    llm = BedrockClaudeLLM()
    tools = [SearchFloodSimBenchKGTool(), ListFloodSimBenchFilesTool(), DownloadFloodSimBenchTool()]
    memory = ConversationBufferWindowMemory(k=5, memory_key="chat_history", return_messages=True)
    agent = create_react_agent(llm=llm, tools=tools, prompt=FLOODSIMBENCH_PROMPT)
    return AgentExecutor(
        agent=agent, tools=tools, memory=memory,
        verbose=True, max_iterations=12, handle_parsing_errors=True,
    )


if __name__ == "__main__":
    executor = get_floodsimbench_agent()
    result = executor.invoke({"input": "Find FloodSimBench data for Houston with 100-year return period and download frame 0."})
    print(result.get("output"))
