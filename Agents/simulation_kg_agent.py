#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simulation Knowledge Graph Agent
================================

This module orchestrates metadata discovery, filtering, download planning, and link
validation for ERA5 and CMIP6 simulation datasets.

Goals:
    1. Reuse existing metadata assets (ERA5Data, CMIP6Data) to build a lightweight store.
    2. Provide a LangChain ReAct workflow backed by AWS Bedrock Claude for interactive search.
    3. Support multi-criteria search (keywords, variables, temporal/spatial coverage, DRS fields)
       and produce download plans with URL validation.
    4. Persist curated datasets into the local SQLite database (`climate_knowledge_graph.db`) to
       serve downstream agents.

Key components:
    - ERA5MetadataLoader / CMIP6MetadataLoader: load local metadata, build in-memory indexes,
      and execute filters.
    - SimulationGraphStore: handle SQLite persistence.
    - DownloadValidator: perform lightweight availability checks for ERA5 CDS endpoints and CMIP6 ESGF URLs.
    - LangChain toolset: expose search, inspection, validation, and storage capabilities to the agent.
    - create_simulation_agent(): assemble the LangChain AgentExecutor.
"""

from __future__ import annotations

import json
import os
import sys
import sqlite3
import logging
import inspect
import hashlib
import pathlib
import importlib
import re
import requests
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple, Iterable, TYPE_CHECKING
from datetime import datetime

try:  # pragma: no cover - boto3 may be unavailable in some environments
    import boto3  # type: ignore
except ImportError:  # pragma: no cover
    boto3 = None  # type: ignore

LANGCHAIN_AVAILABLE = False
try:
    _agents_mod = importlib.import_module("langchain.agents")
    _tools_mod = importlib.import_module("langchain.tools")
    _memory_mod = importlib.import_module("langchain.memory")
    _prompts_mod = importlib.import_module("langchain.prompts")
    _llm_mod = importlib.import_module("langchain.llms.base")
    _callback_mod = importlib.import_module("langchain.callbacks.manager")
    _core_callback_mod = importlib.import_module("langchain_core.callbacks")

    AgentExecutor = getattr(_agents_mod, "AgentExecutor")
    create_react_agent = getattr(_agents_mod, "create_react_agent")
    BaseTool = getattr(_tools_mod, "BaseTool")
    ConversationBufferWindowMemory = getattr(_memory_mod, "ConversationBufferWindowMemory")
    PromptTemplate = getattr(_prompts_mod, "PromptTemplate")
    LLM = getattr(_llm_mod, "LLM")
    CallbackManagerForLLMRun = getattr(_callback_mod, "CallbackManagerForLLMRun")
    CallbackManagerForToolRun = getattr(_core_callback_mod, "CallbackManagerForToolRun")
    LANGCHAIN_AVAILABLE = True
except Exception:  # pragma: no cover
    LANGCHAIN_AVAILABLE = False

if not LANGCHAIN_AVAILABLE:  # pragma: no cover - stub definitions
    class BaseTool:  # type: ignore
        name: str = "unavailable_tool"
        description: str = "LangChain is not installed."

        def _run(self, tool_input: str, run_manager: Optional[Any] = None) -> str:
            raise ImportError("LangChain is required to use this tool.")

    def create_react_agent(*args: Any, **kwargs: Any) -> Any:  # type: ignore
        raise ImportError("LangChain is not installed.")

    class AgentExecutor:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("LangChain is not installed.")

    class ConversationBufferWindowMemory:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("LangChain is not installed.")

    class PromptTemplate:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("LangChain is not installed.")

    class LLM:  # type: ignore
        pass

    class CallbackManagerForLLMRun:  # type: ignore
        pass

    class CallbackManagerForToolRun:  # type: ignore
        pass

# ---------- Basic Configuration ----------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT_DIR = pathlib.Path(__file__).resolve().parents[1]
# Use current directory (Agents/) for database and metadata
CURRENT_DIR = pathlib.Path(__file__).resolve().parent
ERA5_META_DIR = ROOT_DIR / "ERA5Data" / "ERA5Meta"
CMIP6_DIR = ROOT_DIR / "CMIP6Data"
CMIP6_META_PATH = CMIP6_DIR / "CMIP6Meta" / "220514_CMIP6_metaData_restartedInd-24949000.json"
CMIP6_CV_DIR = CMIP6_DIR / "CMIP6Meta"

# Database in current directory (Agents/)
DB_PATH = CURRENT_DIR / "climate_knowledge_graph.db"

# Make ERA5/CMIP6 helper modules importable
ERA5_MODULE_DIR = (ROOT_DIR / "ERA5Data").resolve()
CMIP6_MODULE_DIR = (ROOT_DIR / "CMIP6Data").resolve()
for module_dir in [ERA5_MODULE_DIR, CMIP6_MODULE_DIR]:
    module_path = str(module_dir)
    if module_path not in sys.path:
        sys.path.append(module_path)

# Lazy import era5_scraper to avoid creating directories at import time
# Only import functions when actually needed
extract_download_form_from_metadata = None
extract_available_variables_from_form = None

def _lazy_import_era5_helpers():
    """Lazy import era5_scraper helpers only when needed"""
    global extract_download_form_from_metadata, extract_available_variables_from_form
    if extract_download_form_from_metadata is None:
        try:
            era5_module = importlib.import_module("era5_scraper")
            extract_download_form_from_metadata = getattr(era5_module, "extract_download_form_from_metadata", None)
            extract_available_variables_from_form = getattr(era5_module, "extract_available_variables_from_form", None)
        except Exception as exc:
            logger.warning("Failed to import era5_scraper helpers: %s", exc)
            extract_download_form_from_metadata = None
            extract_available_variables_from_form = None

try:
    cmip6_module = importlib.import_module("cmip6_meta_resolver")
    iter_cmip6_records = getattr(cmip6_module, "iter_records", None)
    rec_to_esgf_query = getattr(cmip6_module, "rec_to_esgf_query", None)
    pick_first_file_url = getattr(cmip6_module, "pick_first_file_url", None)
    esgf_search = getattr(cmip6_module, "esgf_search", None)
except Exception as exc:
    logger.warning("Failed to import cmip6_meta_resolver helpers: %s", exc)
    iter_cmip6_records = None
    rec_to_esgf_query = None
    pick_first_file_url = None
    esgf_search = None


# ---------- AWS Bedrock Claude / LangChain wrapper ----------

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")


class BedrockClaudeLLM(LLM):
    """LangChain LLM wrapper for AWS Bedrock Claude (aligned with other agents)."""

    bedrock: Any = None
    model_id: str = BEDROCK_MODEL_ID

    def __init__(self):
        super().__init__()
        if boto3 is None:  # pragma: no cover - gracefully degrade without AWS SDK
            logger.warning("boto3 is not installed; Bedrock calls are disabled.")
            self.bedrock = None
            return
        try:  # pragma: no cover - requires cloud environment
            self.bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)
            logger.info("Bedrock Claude LLM initialized successfully.")
        except Exception as exc:  # pragma: no cover - requires cloud environment
            logger.warning("Bedrock client init failed: %s", exc)
            self.bedrock = None

    @property
    def _llm_type(self) -> str:
        return "bedrock_claude_sonnet"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if not self.bedrock:
            return f"[BEDROCK DISABLED] Prompt echo:\n{prompt}"
        stop_sequences = stop or ["\nObservation:"]
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "top_p": 0.9,
                "stop_sequences": stop_sequences,
            }
        )
        response = self.bedrock.invoke_model(modelId=self.model_id, body=body)
        payload = json.loads(response["body"].read())
        return payload["content"][0]["text"].strip()


# ---------- Data Structures ----------


@dataclass
class DownloadLink:
    url: str
    protocol: str
    description: str = ""
    size_bytes: Optional[int] = None
    last_checked: Optional[str] = None
    status: Optional[str] = None


@dataclass
class SimulationDataset:
    dataset_id: str
    family: str  # "ERA5" or "CMIP6"
    title: str
    description: str
    keywords: List[str] = field(default_factory=list)
    variables: List[str] = field(default_factory=list)
    spatial_coverage: str = ""
    temporal_coverage: str = ""
    frequency: Optional[str] = None
    provider: Optional[str] = None
    native_format: Optional[str] = None
    api_endpoint: Optional[str] = None
    search_handles: Dict[str, Any] = field(default_factory=dict)
    download_links: List[DownloadLink] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_flat_dict(self) -> Dict[str, Any]:
        """Return a flatten JSON-like dictionary for persistence."""
        return {
            "dataset_id": self.dataset_id,
            "family": self.family,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "variables": self.variables,
            "spatial_coverage": self.spatial_coverage,
            "temporal_coverage": self.temporal_coverage,
            "frequency": self.frequency,
            "provider": self.provider,
            "native_format": self.native_format,
            "api_endpoint": self.api_endpoint,
            "search_handles": self.search_handles,
            "download_links": [link.__dict__ for link in self.download_links],
            "extra": self.extra,
        }


# ---------- ERA5 Metadata Loader ----------


class ERA5MetadataLoader:
    """Load, index, and search ERA5 metadata from the ERA5Meta directory."""

    def __init__(self, meta_dir: pathlib.Path = ERA5_META_DIR):
        self.meta_dir = meta_dir
        self.datasets: Dict[str, SimulationDataset] = {}
        if not self.meta_dir.exists():
            logger.warning("ERA5 metadata directory missing: %s", self.meta_dir)
        else:
            self._load_all()

    def _load_all(self) -> None:
        for json_file in sorted(self.meta_dir.glob("dataset_*.json")):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as exc:
                logger.warning("Failed to load %s: %s", json_file.name, exc)
                continue

            dataset_id = data.get("id") or json_file.stem.replace("dataset_", "")
            title = data.get("title", dataset_id)
            description = data.get("description", "")
            keywords = data.get("keywords", [])
            provider = None
            for kw in keywords:
                if kw.lower().startswith("provider:"):
                    provider = kw.split(":", 1)[-1].strip()
                    break

            # Spatial & temporal coverage
            extent = data.get("extent", {})
            spatial_bbox = extent.get("spatial", {}).get("bbox", [])
            spatial_coverage = "Global"
            if spatial_bbox:
                bb = spatial_bbox[0]
                spatial_coverage = f"bbox(lat:{bb[1]}~{bb[3]}, lon:{bb[0]}~{bb[2]})"
            temporal = extent.get("temporal", {}).get("interval", [])
            temporal_coverage = ""
            if temporal and temporal[0]:
                start, end = temporal[0]
                temporal_coverage = f"{start} → {end or 'present'}"

            # Download endpoints & variables
            api_endpoint = None
            native_format = None
            download_links: List[DownloadLink] = []
            for link in data.get("links", []):
                rel = link.get("rel", "")
                href = link.get("href")
                if not href:
                    continue
                if rel == "retrieve":
                    api_endpoint = href
                elif rel == "constraints":
                    download_links.append(
                        DownloadLink(
                            url=href,
                            protocol="HTTPS",
                            description="Download constraints spec",
                        )
                    )
                elif rel == "layout":
                    download_links.append(
                        DownloadLink(
                            url=href,
                            protocol="HTTPS",
                            description="Landing page layout JSON",
                        )
                    )

            # Parse download form to discover variables and formats
            variables: List[str] = []
            retrieve_payload = {}
            # Lazy import era5 helpers to avoid creating directories at import time
            _lazy_import_era5_helpers()
            if extract_download_form_from_metadata:
                form = extract_download_form_from_metadata(self.meta_dir / json_file.name)
                if form and extract_available_variables_from_form:
                    variables = sorted(extract_available_variables_from_form(form))
                if isinstance(form, dict):
                    # Capture optional field defaults/types for payload generation
                    retrieve_payload = {
                        key: value
                        for key, value in form.get("fields", {}).items()
                        if isinstance(value, dict)
                    }
                    # Infer default data format
                    fmt_field = form.get("fields", {}).get("format")
                    if fmt_field:
                        native_format = fmt_field.get("default") or fmt_field.get("value")

            dataset = SimulationDataset(
                dataset_id=f"ERA5::{dataset_id}",
                family="ERA5",
                title=title,
                description=description,
                keywords=keywords,
                variables=variables,
                spatial_coverage=spatial_coverage,
                temporal_coverage=temporal_coverage,
                provider=provider or "Copernicus C3S",
                native_format=native_format or "NetCDF/GRIB",
                api_endpoint=api_endpoint,
                search_handles={
                    "slug": dataset_id,
                    "retrieve_payload_schema": retrieve_payload,
                },
                download_links=download_links,
                extra={
                    "published": data.get("published"),
                    "updated": data.get("updated"),
                    "sci:doi": data.get("sci:doi"),
                },
            )
            self.datasets[dataset.dataset_id] = dataset

    # ---- Query helpers ----

    def list_datasets(self) -> List[str]:
        return sorted(self.datasets.keys())

    def search(
        self,
        query: str = "",
        variable: Optional[str] = None,
        temporal_hint: Optional[str] = None,
        spatial_hint: Optional[str] = None,
        limit: int = 10,
    ) -> List[SimulationDataset]:
        query_lower = query.lower()
        results: List[Tuple[float, SimulationDataset]] = []
        for dataset in self.datasets.values():
            score = 0.0
            if query_lower:
                haystack = " ".join(
                    [
                        dataset.title.lower(),
                        dataset.description.lower(),
                        " ".join(kw.lower() for kw in dataset.keywords),
                    ]
                )
                if query_lower in haystack:
                    score += 1.0
            if variable and dataset.variables:
                if variable.lower() in {v.lower() for v in dataset.variables}:
                    score += 1.0
            if temporal_hint and dataset.temporal_coverage:
                if any(token in dataset.temporal_coverage.lower() for token in temporal_hint.lower().split()):
                    score += 0.5
            if spatial_hint and dataset.spatial_coverage:
                if any(token in dataset.spatial_coverage.lower() for token in spatial_hint.lower().split()):
                    score += 0.5
            if score > 0:
                results.append((score, dataset))
        results.sort(key=lambda x: x[0], reverse=True)
        return [ds for _, ds in results[:limit]]

    def get(self, dataset_id: str) -> Optional[SimulationDataset]:
        return self.datasets.get(dataset_id)


# ---------- CMIP6 Metadata Loader ----------


class CMIP6MetadataLoader:
    """Load CMIP6 metadata and provide search capabilities using local JSON and CV files."""

    def __init__(
        self,
        meta_path: pathlib.Path = CMIP6_META_PATH,
        cv_dir: pathlib.Path = CMIP6_CV_DIR,
    ):
        self.meta_path = meta_path
        self.cv_dir = cv_dir
        self._cv_cache: Dict[str, Dict[str, Any]] = {}
        self.load_controlled_vocabularies()

    def load_controlled_vocabularies(self) -> None:
        if not self.cv_dir.exists():
            logger.warning("CMIP6 CV directory missing: %s", self.cv_dir)
            return
        for cv_file in self.cv_dir.glob("CMIP6_*_id.json"):
            try:
                with open(cv_file, "r", encoding="utf-8") as f:
                    cv_data = json.load(f)
                key = cv_file.stem.replace("CMIP6_", "")
                self._cv_cache[key] = cv_data
            except Exception as exc:
                logger.warning("Failed to load CV %s: %s", cv_file.name, exc)

    def _enrich_record(self, rec: Dict[str, Any]) -> SimulationDataset:
        dataset_id = rec.get("instance_id") or self._compose_instance_id(rec)
        experiment_id = rec.get("experiment_id", "")
        source_id = rec.get("source_id", "")
        variable_id = rec.get("variable_id", "")
        activity_id = rec.get("activity_id", "")
        grid_label = rec.get("grid_label", "")
        table_id = rec.get("table_id", "")

        experiment_desc = self._lookup_cv("experiment_id", experiment_id, "experiment") or experiment_id
        source_desc = self._lookup_cv("source_id", source_id, "label") or source_id
        activity_desc = activity_id
        variable_desc = self._lookup_cv("variable_id", variable_id, "long_name") or variable_id
        frequency = rec.get("frequency") or self._lookup_cv("frequency", rec.get("frequency"), "frequency")
        nominal_resolution = self._lookup_cv("nominal_resolution", rec.get("nominal_resolution"), "value")

        description = (
            f"Experiment: {experiment_desc}\n"
            f"Model: {source_desc}\n"
            f"Variable: {variable_desc}\n"
            f"Activity: {activity_desc}"
        )

        dataset = SimulationDataset(
            dataset_id=f"CMIP6::{dataset_id}",
            family="CMIP6",
            title=f"{variable_id} {experiment_id} ({source_id})",
            description=description,
            keywords=[
                experiment_id,
                source_id,
                variable_id,
                activity_id,
                grid_label,
                table_id,
            ],
            variables=[variable_id],
            spatial_coverage=f"Grid label: {grid_label}",
            temporal_coverage=f"Table: {table_id}",
            frequency=frequency,
            provider=rec.get("institution_id"),
            native_format="NetCDF",
            search_handles={
                "drs": {
                    "activity_id": activity_id,
                    "institution_id": rec.get("institution_id"),
                    "source_id": source_id,
                    "experiment_id": experiment_id,
                    "variant_label": rec.get("variant_label"),
                    "table_id": table_id,
                    "variable_id": variable_id,
                    "grid_label": grid_label,
                    "version": rec.get("version"),
                }
            },
            extra={
                "nominal_resolution": nominal_resolution,
                "member_id": rec.get("variant_label"),
                "mip_era": rec.get("mip_era"),
            },
        )
        return dataset

    def _lookup_cv(self, cv_key: str, entry_id: Optional[str], field: str) -> Optional[str]:
        if not entry_id:
            return None
        cv = self._cv_cache.get(cv_key)
        if not cv:
            return None
        entries = cv.get(cv_key) or cv.get(f"{cv_key}_id")
        if not entries:
            return None
        entry = entries.get(entry_id)
        if entry is None:
            return None
        if isinstance(entry, dict):
            return entry.get(field) or entry.get(field.replace("_", " "))
        if isinstance(entry, (str, int, float)):
            return str(entry)
        return None

    def _compose_instance_id(self, rec: Dict[str, Any]) -> str:
        parts = [
            rec.get("mip_era", "CMIP6"),
            rec.get("activity_id"),
            rec.get("institution_id"),
            rec.get("source_id"),
            rec.get("experiment_id"),
            rec.get("variant_label"),
            rec.get("table_id"),
            rec.get("variable_id"),
            rec.get("grid_label"),
            rec.get("version"),
        ]
        return ".".join([str(p) for p in parts if p])

    def search(
        self,
        filters: Dict[str, str],
        limit: int = 10,
        minimal: bool = True,
        latest: bool = True,
    ) -> List[SimulationDataset]:
        """
        filters example:
            {
                "activity_id": "ScenarioMIP",
                "experiment_id": "ssp585",
                "variable_id": "tas",
                "table_id": "Amon",
                "grid_label": "gn",
            }
        """
        if iter_cmip6_records is None:
            logger.error("CMIP6 metadata iterator unavailable.")
            return []

        results: List[SimulationDataset] = []
        scanned = 0
        for rec in iter_cmip6_records(str(self.meta_path)):
            scanned += 1
            if not isinstance(rec, dict):
                continue
            if self._record_matches(rec, filters):
                dataset = self._enrich_record(rec)
                results.append(dataset)
                if len(results) >= limit:
                    break
        logger.info("CMIP6 search scanned %s entries, hits=%s", scanned, len(results))
        return results

    def _record_matches(self, rec: Dict[str, Any], filters: Dict[str, str]) -> bool:
        for key, value in filters.items():
            if not value:
                continue
            if str(rec.get(key, "")).lower() != value.lower():
                return False
        return True

    def fetch_download_links(
        self, dataset: SimulationDataset, limit: int = 5
    ) -> List[DownloadLink]:
        """Retrieve download URLs by querying the ESGF API."""
        if esgf_search is None or rec_to_esgf_query is None:
            logger.error("CMIP6 ESGF helpers unavailable.")
            return []
        query = rec_to_esgf_query(
            dataset.search_handles["drs"],
            target="File",
            minimal=True,
            latest=True,
        )
        node, docs = esgf_search(query)
        links: List[DownloadLink] = []
        for doc in docs[:limit]:
            if not isinstance(doc, dict):
                continue
            url = pick_first_file_url(doc) if pick_first_file_url else None
            if not url:
                continue
            protocol = "HTTPServer"
            if "thredds" in url.lower():
                protocol = "THREDDS"
            size_bytes = doc.get("size") or doc.get("size_bytes")
            description = doc.get("title") or doc.get("id") or ""
            links.append(
                DownloadLink(
                    url=url,
                    protocol=protocol,
                    description=f"{description} (ESGF node: {node})",
                    size_bytes=size_bytes,
                )
            )
        return links


# ---------- SQLite Storage ----------


class SimulationGraphStore:
    """Persist simulation dataset metadata and link checks to the local SQLite database."""

    def __init__(self, db_path: pathlib.Path = DB_PATH):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_datasets (
                    dataset_id TEXT PRIMARY KEY,
                    family TEXT,
                    title TEXT,
                    description TEXT,
                    keywords TEXT,
                    variables TEXT,
                    spatial_coverage TEXT,
                    temporal_coverage TEXT,
                    frequency TEXT,
                    provider TEXT,
                    native_format TEXT,
                    api_endpoint TEXT,
                    search_handles TEXT,
                    download_links TEXT,
                    extra TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_download_checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id TEXT,
                    url TEXT,
                    protocol TEXT,
                    status TEXT,
                    checked_at TEXT,
                    details TEXT,
                    UNIQUE(dataset_id, url)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_dataset_relationships (
                    dataset_id TEXT,
                    relation_type TEXT,
                    relation_value TEXT,
                    relation_extra TEXT,
                    PRIMARY KEY (dataset_id, relation_type, relation_value)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_dataset_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id TEXT,
                    event_type TEXT,
                    payload TEXT,
                    created_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS simulation_quality_assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id TEXT,
                    quality_grade TEXT,
                    overall_score REAL,
                    metadata_completeness REAL,
                    temporal_coverage_quality REAL,
                    download_readiness REAL,
                    drs_completeness REAL,
                    issues TEXT,
                    recommendations TEXT,
                    assessed_at TEXT,
                    UNIQUE(dataset_id)
                )
                """
            )
            conn.commit()

    def upsert_dataset(self, dataset: SimulationDataset) -> None:
        payload = dataset.to_flat_dict()
        now = datetime.utcnow().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO simulation_datasets (
                    dataset_id, family, title, description, keywords, variables,
                    spatial_coverage, temporal_coverage, frequency, provider,
                    native_format, api_endpoint, search_handles, download_links,
                    extra, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(dataset_id) DO UPDATE SET
                    family=excluded.family,
                    title=excluded.title,
                    description=excluded.description,
                    keywords=excluded.keywords,
                    variables=excluded.variables,
                    spatial_coverage=excluded.spatial_coverage,
                    temporal_coverage=excluded.temporal_coverage,
                    frequency=excluded.frequency,
                    provider=excluded.provider,
                    native_format=excluded.native_format,
                    api_endpoint=excluded.api_endpoint,
                    search_handles=excluded.search_handles,
                    download_links=excluded.download_links,
                    extra=excluded.extra,
                    updated_at=excluded.updated_at
                """,
                (
                    dataset.dataset_id,
                    dataset.family,
                    dataset.title,
                    dataset.description,
                    json.dumps(payload["keywords"]),
                    json.dumps(payload["variables"]),
                    dataset.spatial_coverage,
                    dataset.temporal_coverage,
                    dataset.frequency,
                    dataset.provider,
                    dataset.native_format,
                    dataset.api_endpoint,
                    json.dumps(payload["search_handles"]),
                    json.dumps(payload["download_links"]),
                    json.dumps(payload["extra"]),
                    now,
                    now,
                ),
            )

    def record_download_check(
        self,
        dataset_id: str,
        link: DownloadLink,
        status: str,
        details: Dict[str, Any],
    ) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO simulation_download_checks (
                    dataset_id, url, protocol, status, checked_at, details
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(dataset_id, url) DO UPDATE SET
                    status=excluded.status,
                    checked_at=excluded.checked_at,
                    details=excluded.details
                """,
                (
                    dataset_id,
                    link.url,
                    link.protocol,
                    status,
                    datetime.utcnow().isoformat(),
                    json.dumps(details),
                ),
            )

    # -- Relationship helpers -------------------------------------------------

    def replace_relationships(self, dataset: SimulationDataset) -> None:
        relationships: List[Tuple[str, str, Dict[str, Any]]] = []

        def add_relation(rel_type: str, value: Optional[str], extra: Optional[Dict[str, Any]] = None) -> None:
            if value:
                relationships.append((rel_type, str(value), extra or {}))

        for keyword in dataset.keywords:
            add_relation("keyword", keyword)
        for variable in dataset.variables:
            add_relation("variable", variable)

        add_relation("family", dataset.family)
        add_relation("spatial_coverage", dataset.spatial_coverage)
        add_relation("temporal_coverage", dataset.temporal_coverage)
        add_relation("native_format", dataset.native_format)
        add_relation("provider", dataset.provider)

        # Encode search handles
        if dataset.search_handles:
            for key, value in dataset.search_handles.items():
                if isinstance(value, dict):
                    for sub_key, sub_val in value.items():
                        add_relation(f"{key}.{sub_key}", sub_val)
                elif isinstance(value, (list, tuple, set)):
                    for item in value:
                        add_relation(f"{key}", item)
                else:
                    add_relation(key, value)

        # Extra metadata
        for key, value in dataset.extra.items():
            if isinstance(value, (list, tuple, set)):
                for item in value:
                    add_relation(f"extra.{key}", item)
            else:
                add_relation(f"extra.{key}", value)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM simulation_dataset_relationships WHERE dataset_id = ?",
                (dataset.dataset_id,),
            )
            if relationships:
                conn.executemany(
                    """
                    INSERT OR REPLACE INTO simulation_dataset_relationships (
                        dataset_id, relation_type, relation_value, relation_extra
                    ) VALUES (?, ?, ?, ?)
                    """,
                    [
                        (
                            dataset.dataset_id,
                            rel_type,
                            rel_value,
                            json.dumps(extra, ensure_ascii=False),
                        )
                        for rel_type, rel_value, extra in relationships
                    ],
                )

    def log_event(self, dataset_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO simulation_dataset_events (
                    dataset_id, event_type, payload, created_at
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    dataset_id,
                    event_type,
                    json.dumps(payload, ensure_ascii=False),
                    datetime.utcnow().isoformat(),
                ),
            )
    
    def store_quality_assessment(self, assessment: Dict[str, Any]) -> None:
        """Store quality assessment results."""
        scores = assessment.get("scores", {})
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO simulation_quality_assessments (
                    dataset_id, quality_grade, overall_score,
                    metadata_completeness, temporal_coverage_quality,
                    download_readiness, drs_completeness,
                    issues, recommendations, assessed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(dataset_id) DO UPDATE SET
                    quality_grade=excluded.quality_grade,
                    overall_score=excluded.overall_score,
                    metadata_completeness=excluded.metadata_completeness,
                    temporal_coverage_quality=excluded.temporal_coverage_quality,
                    download_readiness=excluded.download_readiness,
                    drs_completeness=excluded.drs_completeness,
                    issues=excluded.issues,
                    recommendations=excluded.recommendations,
                    assessed_at=excluded.assessed_at
                """,
                (
                    assessment["dataset_id"],
                    scores.get("quality_grade", "N/A"),
                    scores.get("overall_quality", 0.0),
                    scores.get("metadata_completeness", 0.0),
                    scores.get("temporal_coverage_quality", 0.0),
                    scores.get("download_readiness", 0.0),
                    scores.get("drs_completeness", 0.0),
                    json.dumps(assessment.get("issues", []), ensure_ascii=False),
                    json.dumps(assessment.get("recommendations", []), ensure_ascii=False),
                    assessment.get("assessed_at", datetime.utcnow().isoformat()),
                ),
            )

    def list_stored_datasets(self, family: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT dataset_id, family, title, updated_at FROM simulation_datasets"
        params: Tuple[Any, ...] = ()
        if family:
            query += " WHERE family = ?"
            params = (family,)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params = params + (limit,)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
        return [
            {
                "dataset_id": row[0],
                "family": row[1],
                "title": row[2],
                "updated_at": row[3],
            }
            for row in rows
        ]

    def fetch_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM simulation_datasets WHERE dataset_id = ?",
                (dataset_id,),
            )
            dataset_row = cursor.fetchone()
            if not dataset_row:
                return None
            columns = [col[0] for col in cursor.description]
            dataset_data = dict(zip(columns, dataset_row))

            rel_cursor = conn.execute(
                """
                SELECT relation_type, relation_value, relation_extra
                FROM simulation_dataset_relationships
                WHERE dataset_id = ?
                ORDER BY relation_type, relation_value
                """,
                (dataset_id,),
            )
            relationships = [
                {
                    "relation_type": rel_type,
                    "relation_value": rel_value,
                    "relation_extra": json.loads(extra) if extra else {},
                }
                for rel_type, rel_value, extra in rel_cursor.fetchall()
            ]

            checks_cursor = conn.execute(
                """
                SELECT url, protocol, status, checked_at, details
                FROM simulation_download_checks
                WHERE dataset_id = ?
                ORDER BY checked_at DESC
                """,
                (dataset_id,),
            )
            download_checks = [
                {
                    "url": url,
                    "protocol": protocol,
                    "status": status,
                    "checked_at": checked_at,
                    "details": json.loads(details) if details else {},
                }
                for url, protocol, status, checked_at, details in checks_cursor.fetchall()
            ]

        dataset_data["relationships"] = relationships
        dataset_data["download_checks"] = download_checks
        return dataset_data

# ---------- Download Link Validation ----------


class DownloadValidator:
    """Perform lightweight reachability checks for download URLs and API endpoints."""

    DEFAULT_TIMEOUT = 15

    @staticmethod
    def check_head(url: str, timeout: int = DEFAULT_TIMEOUT) -> Tuple[str, Dict[str, Any]]:
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            status = f"{response.status_code} {response.reason}"
            ok = response.status_code < 400
            details = {
                "final_url": response.url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }
            return ("OK" if ok else "ERROR"), {**details, "message": status}
        except Exception as exc:
            return "ERROR", {"message": str(exc), "url": url}

    @staticmethod
    def check_get(url: str, timeout: int = DEFAULT_TIMEOUT) -> Tuple[str, Dict[str, Any]]:
        try:
            response = requests.get(url, timeout=timeout, allow_redirects=True)
            status = f"{response.status_code} {response.reason}"
            ok = response.status_code < 400
            details = {
                "final_url": response.url,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content_preview": response.text[:500],
            }
            return ("OK" if ok else "ERROR"), {**details, "message": status}
        except Exception as exc:
            return "ERROR", {"message": str(exc), "url": url}

    def validate_era5_endpoint(self, dataset: SimulationDataset) -> Tuple[str, Dict[str, Any]]:
        """
        Validate ERA5 API endpoint (NOT a direct download link).
        
        ERA5 uses an asynchronous API workflow:
        1. This endpoint returns API metadata (available variables, parameters, etc.)
        2. Actual data download requires:
           - Using cdsapi library to submit a request to /execution endpoint
           - Waiting for async job completion
           - Downloading the generated data files
        
        This validation only checks that the API endpoint is accessible and returns metadata.
        Actual data file download will be handled by simulation_data_acquisition_agent.
        """
        if not dataset.api_endpoint:
            return "ERROR", {"message": "Dataset missing ERA5 retrieve endpoint"}
        
        status, details = self.check_get(dataset.api_endpoint)
        
        # Enhance details to clarify this is an API endpoint, not a direct download link
        if status == "OK":
            details["note"] = (
                "This is an API metadata endpoint, not a direct download link. "
                "Actual data download requires using cdsapi library to submit a request "
                "to the /execution endpoint with specific parameters (variables, time range, etc.). "
                "The simulation_data_acquisition_agent will handle the actual data download."
            )
            details["api_type"] = "CDS API metadata endpoint"
            details["requires"] = "cdsapi library + authentication + parameter specification"
        
        return status, details

    def validate_cmip6_links(self, links: List[DownloadLink]) -> List[Tuple[DownloadLink, str, Dict[str, Any]]]:
        results = []
        for link in links:
            status, details = self.check_head(link.url)
            method_used = "HEAD"

            # Fallback to GET when HEAD is not supported
            status_code = details.get("status_code")
            if status == "ERROR" or status_code in {400, 401, 403, 405, 500, 501}:
                try:
                    response = requests.get(link.url, timeout=self.DEFAULT_TIMEOUT, allow_redirects=True, stream=True)
                    method_used = "GET"
                    status_message = f"{response.status_code} {response.reason}"
                    response.close()
                    details = {
                        "final_url": response.url,
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "message": status_message,
                    }
                    status = "OK" if response.status_code < 400 else "ERROR"
                except Exception as exc:
                    status = "ERROR"
                    details = {"message": str(exc), "url": link.url}

            details["method_used"] = method_used
            results.append((link, status, details))
        return results


# ---------- Data Quality Assessment ----------


class DataQualityAssessor:
    """Assess data quality metrics for simulation datasets."""
    
    @staticmethod
    def assess_dataset_quality(dataset: SimulationDataset) -> Dict[str, Any]:
        """Comprehensive quality assessment for a dataset."""
        scores = {}
        issues = []
        recommendations = []
        
        # Metadata completeness (0-1 score)
        metadata_fields = [
            "title", "description", "variables", "temporal_coverage",
            "spatial_coverage", "provider", "api_endpoint" if dataset.family == "ERA5" else None,
        ]
        metadata_fields = [f for f in metadata_fields if f]
        filled_fields = sum(1 for field in metadata_fields if getattr(dataset, field, None))
        metadata_score = filled_fields / len(metadata_fields)
        scores["metadata_completeness"] = metadata_score
        
        if metadata_score < 0.7:
            issues.append("Incomplete metadata")
            recommendations.append("Enrich dataset metadata with missing fields")
        
        # Variable availability
        if dataset.variables:
            scores["variable_count"] = len(dataset.variables)
            if len(dataset.variables) < 1:
                issues.append("No variables listed")
        else:
            scores["variable_count"] = 0
            issues.append("Missing variable information")
        
        # Temporal coverage validity
        temporal_score = 1.0
        if dataset.temporal_coverage:
            if "→" in dataset.temporal_coverage or "to" in dataset.temporal_coverage.lower():
                temporal_score = 1.0
            elif dataset.temporal_coverage.lower() in ["historical", "present", "ongoing"]:
                temporal_score = 0.8
            else:
                temporal_score = 0.6
        else:
            temporal_score = 0.0
            issues.append("Missing temporal coverage")
        scores["temporal_coverage_quality"] = temporal_score
        
        # Download link availability and validation
        download_score = 0.0
        if dataset.family == "ERA5":
            if dataset.api_endpoint:
                download_score = 0.8
            else:
                issues.append("Missing ERA5 API endpoint")
        elif dataset.family == "CMIP6":
            if dataset.download_links:
                verified_count = sum(1 for link in dataset.download_links if link.status == "OK")
                download_score = min(0.9, 0.5 + (verified_count / len(dataset.download_links)) * 0.4)
            else:
                issues.append("No CMIP6 download links found")
                recommendations.append("Fetch download links via ESGF API")
        scores["download_readiness"] = download_score
        
        # DRS completeness for CMIP6
        if dataset.family == "CMIP6":
            drs = dataset.search_handles.get("drs", {})
            required_drs = ["activity_id", "experiment_id", "variable_id", "source_id"]
            drs_completeness = sum(1 for field in required_drs if drs.get(field)) / len(required_drs)
            scores["drs_completeness"] = drs_completeness
            if drs_completeness < 1.0:
                issues.append(f"DRS incomplete: missing {[f for f in required_drs if not drs.get(f)]}")
        
        # Overall quality score (weighted average)
        weights = {
            "metadata_completeness": 0.3,
            "temporal_coverage_quality": 0.2,
            "download_readiness": 0.4,
            "drs_completeness": 0.1 if dataset.family == "CMIP6" else 0.0,
        }
        overall_score = sum(scores.get(k, 0) * weights.get(k, 0) for k in weights.keys())
        scores["overall_quality"] = overall_score
        
        # Quality grade
        if overall_score >= 0.9:
            grade = "A"
        elif overall_score >= 0.75:
            grade = "B"
        elif overall_score >= 0.6:
            grade = "C"
        else:
            grade = "D"
        scores["quality_grade"] = grade
        
        return {
            "dataset_id": dataset.dataset_id,
            "family": dataset.family,
            "scores": scores,
            "issues": issues,
            "recommendations": recommendations,
            "assessed_at": datetime.utcnow().isoformat(),
        }


# ---------- Evaluation Metrics Framework ----------


class AgentEvaluationMetrics:
    """Framework for evaluating agent performance."""
    
    def __init__(self):
        self.metrics = {
            "total_queries": 0,
            "successful_searches": 0,
            "datasets_found": 0,
            "datasets_stored": 0,
            "average_response_time": 0.0,
            "query_types": {},
            "error_count": 0,
        }
        self.query_times: List[float] = []
    
    def record_query(self, query_type: str, success: bool, datasets_found: int = 0, response_time: float = 0.0):
        """Record a query execution."""
        self.metrics["total_queries"] += 1
        if success:
            self.metrics["successful_searches"] += 1
            self.metrics["datasets_found"] += datasets_found
        else:
            self.metrics["error_count"] += 1
        
        self.query_times.append(response_time)
        if self.query_times:
            self.metrics["average_response_time"] = sum(self.query_times) / len(self.query_times)
        
        if query_type not in self.metrics["query_types"]:
            self.metrics["query_types"][query_type] = 0
        self.metrics["query_types"][query_type] += 1
    
    def record_storage(self, count: int = 1):
        """Record dataset storage."""
        self.metrics["datasets_stored"] += count
    
    def compute_recall(self, relevant_found: int, total_relevant: int) -> float:
        """Compute recall metric."""
        if total_relevant == 0:
            return 1.0
        return relevant_found / total_relevant
    
    def compute_precision(self, relevant_found: int, total_found: int) -> float:
        """Compute precision metric."""
        if total_found == 0:
            return 0.0
        return relevant_found / total_found
    
    def get_summary(self) -> Dict[str, Any]:
        """Get evaluation summary."""
        success_rate = (
            self.metrics["successful_searches"] / self.metrics["total_queries"]
            if self.metrics["total_queries"] > 0
            else 0.0
        )
        return {
            **self.metrics,
            "success_rate": success_rate,
            "average_datasets_per_query": (
                self.metrics["datasets_found"] / self.metrics["total_queries"]
                if self.metrics["total_queries"] > 0
                else 0.0
            ),
        }


# Global evaluation metrics instance
EVALUATION_METRICS = AgentEvaluationMetrics()


# ---------- LangChain Tools ----------


# Initialize loaders (ERA5MetadataLoader will use lazy import for era5_scraper)
# This prevents era5_downloads and ERA5Meta folders from being created at import time
ERA5_LOADER = ERA5MetadataLoader()
CMIP6_LOADER = CMIP6MetadataLoader()
GRAPH_STORE = SimulationGraphStore()
VALIDATOR = DownloadValidator()
LLM_INSTANCE = BedrockClaudeLLM()

CMIP6_FILTER_ALIASES: Dict[str, str] = {
    "activity": "activity_id",
    "activity_id": "activity_id",
    "experiment": "experiment_id",
    "experiment_id": "experiment_id",
    "experiment_label": "experiment_id",
    "model": "source_id",
    "source": "source_id",
    "source_id": "source_id",
    "institution": "institution_id",
    "institution_id": "institution_id",
    "variable": "variable_id",
    "variable_id": "variable_id",
    "table": "table_id",
    "table_id": "table_id",
    "grid": "grid_label",
    "grid_label": "grid_label",
    "variant": "variant_label",
    "variant_label": "variant_label",
    "member": "variant_label",
    "version": "version",
    "frequency": "frequency",
}

VARIABLE_SYNONYMS: List[Dict[str, Any]] = [
    {
        "aliases": [
            "2m temperature",
            "2 meter temperature",
            "near surface air temperature",
            "surface air temperature",
            "t2m",
            "tas",
        ],
        "era5": "2m_temperature",
        "cmip6": "tas",
        "keywords": ["temperature", "surface"],
    },
    {
        "aliases": [
            "total precipitation",
            "precipitation",
            "rainfall",
            "pr",
            "precip",
        ],
        "era5": "total_precipitation",
        "cmip6": "pr",
        "keywords": ["precipitation"],
    },
    {
        "aliases": [
            "surface pressure",
            "sp",
            "mean sea level pressure",
            "msl",
        ],
        "era5": "surface_pressure",
        "cmip6": "psl",
        "keywords": ["pressure"],
    },
    {
        "aliases": [
            "wind speed",
            "u10",
            "v10",
            "10m wind",
        ],
        "era5": "10m_u_component_of_wind",
        "cmip6": "uas",
        "keywords": ["wind"],
    },
]

EXPERIMENT_SYNONYMS: Dict[str, str] = {
    "historical": "historical",
    "hist": "historical",
    "ssp585": "ssp585",
    "ssp 585": "ssp585",
    "ssp245": "ssp245",
    "ssp 245": "ssp245",
    "ssp126": "ssp126",
    "ssp 126": "ssp126",
    "ssp370": "ssp370",
    "ssp 370": "ssp370",
    "amip": "amip",
    "pi control": "piControl",
    "picontrol": "piControl",
    "preindustrial control": "piControl",
    "rcp85": "ssp585",
    "rcp8.5": "ssp585",
    "future high emissions": "ssp585",
}

# CMIP6 DRS auto-completion mappings
CMIP6_VARIANT_PATTERNS: Dict[str, List[str]] = {
    "r1i1p1f1": ["r1i1p1f1", "r1", "first realization", "default", "standard"],
    "r1i1p1f2": ["r1i1p1f2", "f2"],
    "r2i1p1f1": ["r2i1p1f1", "r2", "second realization"],
}

CMIP6_GRID_PATTERNS: Dict[str, List[str]] = {
    "gn": ["gn", "native", "native grid", "original grid"],
    "gr": ["gr", "regridded", "regular grid"],
    "gr1": ["gr1", "1 degree", "1deg", "1°"],
}

CMIP6_TABLE_PATTERNS: Dict[str, List[str]] = {
    "Amon": ["amon", "monthly", "atmospheric monthly", "monthly mean"],
    "Aday": ["aday", "daily", "atmospheric daily"],
    "A6hr": ["a6hr", "6 hourly", "6-hourly"],
    "Omon": ["omon", "ocean monthly"],
    "Lmon": ["lmon", "land monthly"],
}

LOCATION_SYNONYMS: Dict[str, List[str]] = {
    "New York": ["new york", "nyc", "new york city", "ny state"],
    "Arctic": ["arctic", "north pole", "high latitudes"],
    "Global": ["global", "worldwide", "entire globe"],
    "Europe": ["europe", "eu"],
    "Asia": ["asia"],
    "North America": ["north america", "usa", "united states", "canada"],
}


def resolve_variable_synonyms(candidate: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    token = candidate.strip().lower()
    for entry in VARIABLE_SYNONYMS:
        aliases = [alias.lower() for alias in entry.get("aliases", [])]
        era5 = entry.get("era5")
        cmip6 = entry.get("cmip6")
        if token in aliases or (era5 and token == era5.lower()) or (cmip6 and token == cmip6.lower()):
            return era5, cmip6, entry.get("keywords", [])
    return None, None, []


def resolve_experiment_synonym(value: str) -> Optional[str]:
    token = value.strip().lower()
    if token in EXPERIMENT_SYNONYMS:
        return EXPERIMENT_SYNONYMS[token]
    for alias, canonical in EXPERIMENT_SYNONYMS.items():
        if alias in token:
            return canonical
    return None


def resolve_location_synonym(value: str) -> Optional[str]:
    token = value.strip().lower()
    for canonical, aliases in LOCATION_SYNONYMS.items():
        if token == canonical.lower() or token in aliases:
            return canonical
        if any(alias in token for alias in aliases):
            return canonical
    return None


def auto_complete_cmip6_drs(filters: Dict[str, str], text_hint: Optional[str] = None) -> Dict[str, str]:
    """Auto-complete CMIP6 DRS fields using patterns and hints."""
    completed = filters.copy()
    text_lower = (text_hint or "").lower()
    
    # Auto-complete variant_label
    if not completed.get("variant_label"):
        for variant, patterns in CMIP6_VARIANT_PATTERNS.items():
            if any(pattern in text_lower for pattern in patterns):
                completed["variant_label"] = variant
                break
        if not completed.get("variant_label"):
            completed["variant_label"] = "r1i1p1f1"  # Default
    
    # Auto-complete grid_label
    if not completed.get("grid_label"):
        for grid, patterns in CMIP6_GRID_PATTERNS.items():
            if any(pattern in text_lower for pattern in patterns):
                completed["grid_label"] = grid
                break
        if not completed.get("grid_label"):
            completed["grid_label"] = "gn"  # Default native grid
    
    # Auto-complete table_id
    if not completed.get("table_id"):
        for table, patterns in CMIP6_TABLE_PATTERNS.items():
            if any(pattern in text_lower for pattern in patterns):
                completed["table_id"] = table
                break
    
    return completed


def parse_temporal_hints(text: str) -> Tuple[Optional[str], List[str]]:
    text_lower = text.lower()
    years = sorted(set(re.findall(r"(?:19|20)\d{2}", text_lower)))

    range_match = re.search(r"((?:19|20)\d{2})\s*(?:-|to|–|—)\s*((?:19|20)\d{2})", text_lower)
    if range_match:
        start_year, end_year = range_match.group(1), range_match.group(2)
        years.extend([start_year, end_year])
        years = sorted(set(years))
        return f"between:{years[0]}-01-01:{years[-1]}-12-31", years

    if len(years) >= 2:
        return f"between:{years[0]}-01-01:{years[-1]}-12-31", years
    if len(years) == 1:
        return f"year:{years[0]}", years

    if "recent" in text_lower and "decade" in text_lower:
        current_year = datetime.utcnow().year
        return f"between:{current_year - 10}-01-01:{current_year}-12-31", [str(current_year - 10), str(current_year)]

    if "historical" in text_lower:
        return "historical", []

    return None, []

class SearchERA5DatasetsTool(BaseTool):
    name: str = "search_era5_datasets"
    description: str = (
        "Search ERA5 datasets by keywords, variables, temporal or spatial hints. "
        "Input must be a JSON string, for example "
        '{"query": "temperature", "variable": "2m_temperature", "temporal_hint": "2020", "spatial_hint": "Arctic", "limit": 5}. '
        "SPATIAL HINTS: When user mentions a location (city/country), include it in spatial_hint. "
        "The data acquisition agent will automatically convert location names to coordinates for spatial filtering."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input else {}
        except json.JSONDecodeError:
            params = {"query": tool_input}
        results = ERA5_LOADER.search(
            query=params.get("query", ""),
            variable=params.get("variable"),
            temporal_hint=params.get("temporal_hint"),
            spatial_hint=params.get("spatial_hint"),
            limit=int(params.get("limit", 5)),
        )
        if not results:
            return "No matching ERA5 dataset found."
        formatted = []
        for ds in results:
            formatted.append(
                {
                    "dataset_id": ds.dataset_id,
                    "title": ds.title,
                    "variables_sample": ds.variables[:10],
                    "temporal_coverage": ds.temporal_coverage,
                    "spatial_coverage": ds.spatial_coverage,
                    "api_endpoint": ds.api_endpoint,
                }
            )
        return json.dumps(formatted, ensure_ascii=False, indent=2)


class SearchCMIP6DatasetsTool(BaseTool):
    name: str = "search_cmip6_datasets"
    description: str = (
        "Filter CMIP6 datasets using DRS fields. "
        "Input must be a JSON string, for example "
        '{"filters": {"activity_id": "ScenarioMIP", "experiment_id": "ssp585", "variable_id": "tas", "table_id": "Amon", "grid_label": "gn"}, "limit": 5}'
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input else {}
        except json.JSONDecodeError:
            return "Input must be a JSON string."
        filters = params.get("filters", {})
        limit = int(params.get("limit", 5))
        results = CMIP6_LOADER.search(filters=filters, limit=limit)
        if not results:
            return "No matching CMIP6 dataset found."
        formatted = []
        for ds in results:
            formatted.append(
                {
                    "dataset_id": ds.dataset_id,
                    "title": ds.title,
                    "keywords": ds.keywords,
                    "provider": ds.provider,
                    "frequency": ds.frequency,
                    "nominal_resolution": ds.extra.get("nominal_resolution"),
                }
            )
        return json.dumps(formatted, ensure_ascii=False, indent=2)


class InspectSimulationDatasetTool(BaseTool):
    name: str = "inspect_simulation_dataset"
    description: str = (
        "Inspect a simulation dataset by dataset_id and return metadata plus download information. "
        "Input can be a plain dataset_id such as 'ERA5::reanalysis-era5-single-levels' or a JSON object "
        "containing {'dataset_id': '...'}."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        dataset_id = tool_input.strip()
        if dataset_id.startswith("{"):
            try:
                params = json.loads(tool_input)
                dataset_id = params.get("dataset_id", dataset_id)
            except json.JSONDecodeError:
                pass
        dataset = ERA5_LOADER.get(dataset_id) or None
        if dataset is None and dataset_id.startswith("CMIP6::"):
            # Reconstruct DRS filters for a refined lookup
            drs_part = dataset_id.replace("CMIP6::", "")
            parts = drs_part.split(".")
            if len(parts) >= 9:
                filters = {
                    "activity_id": parts[1],
                    "institution_id": parts[2],
                    "source_id": parts[3],
                    "experiment_id": parts[4],
                    "variant_label": parts[5],
                    "table_id": parts[6],
                    "variable_id": parts[7],
                    "grid_label": parts[8],
                }
                res = CMIP6_LOADER.search(filters=filters, limit=1)
                if res:
                    dataset = res[0]
                    dataset.download_links = CMIP6_LOADER.fetch_download_links(dataset, limit=5)
        if dataset is None:
            return f"Dataset not found: {dataset_id}"
        return json.dumps(dataset.to_flat_dict(), ensure_ascii=False, indent=2)


class StoreSimulationDatasetTool(BaseTool):
    name: str = "store_simulation_dataset"
    description: str = (
        "Persist a dataset into SQLite. Accepts a dataset JSON payload or a dataset_id "
        "(the loader will retrieve metadata automatically before storing)."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        if tool_input.strip().startswith("{"):
            try:
                payload = json.loads(tool_input)
                dataset = SimulationDataset(
                    dataset_id=payload["dataset_id"],
                    family=payload["family"],
                    title=payload["title"],
                    description=payload.get("description", ""),
                    keywords=payload.get("keywords", []),
                    variables=payload.get("variables", []),
                    spatial_coverage=payload.get("spatial_coverage", ""),
                    temporal_coverage=payload.get("temporal_coverage", ""),
                    frequency=payload.get("frequency"),
                    provider=payload.get("provider"),
                    native_format=payload.get("native_format"),
                    api_endpoint=payload.get("api_endpoint"),
                    search_handles=payload.get("search_handles", {}),
                    download_links=[
                        DownloadLink(**link) for link in payload.get("download_links", [])
                    ],
                    extra=payload.get("extra", {}),
                )
            except Exception as exc:
                return f"Failed to parse input: {exc}"
        else:
            dataset_id = tool_input.strip()
            dataset = ERA5_LOADER.get(dataset_id)
            if dataset is None and dataset_id.startswith("CMIP6::"):
                filters = {"variable_id": dataset_id.split(".")[7]}
                res = CMIP6_LOADER.search(filters=filters, limit=1)
                if res:
                    dataset = res[0]
            if dataset is None:
                return f"Dataset not found: {dataset_id}"
        GRAPH_STORE.upsert_dataset(dataset)
        GRAPH_STORE.replace_relationships(dataset)
        
        # Auto-assess quality
        quality_assessment = DataQualityAssessor.assess_dataset_quality(dataset)
        GRAPH_STORE.store_quality_assessment(quality_assessment)
        GRAPH_STORE.log_event(
            dataset.dataset_id,
            "store_dataset",
            {
                "family": dataset.family,
                "title": dataset.title,
                "quality_grade": quality_assessment["scores"].get("quality_grade", "N/A"),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        EVALUATION_METRICS.record_storage(1)
        
        return f"Stored dataset in SQLite: {dataset.dataset_id} (Quality: {quality_assessment['scores'].get('quality_grade', 'N/A')})"


class InterpretSimulationQueryTool(BaseTool):
    name: str = "interpret_simulation_query"
    description: str = (
        "Interpret a natural-language request for ERA5/CMIP6 simulation data and output "
        "structured criteria for downstream tools. "
        "Input should be free-form text describing variables, locations, time ranges, experiments, etc."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        text = tool_input.strip()
        if not text:
            return json.dumps(
                {
                    "error": "Empty request.",
                    "suggestion": "Provide a sentence describing the desired simulation dataset.",
                },
                ensure_ascii=False,
                indent=2,
            )

        text_lower = text.lower()
        families: List[str] = []
        if "era5" in text_lower:
            families.append("ERA5")
        if "cmip6" in text_lower or "esgf" in text_lower:
            families.append("CMIP6")
        if not families:
            families = ["ERA5", "CMIP6"]

        keywords: List[str] = []
        variables: List[str] = []
        variable_synonyms_found: List[str] = []
        for entry in VARIABLE_SYNONYMS:
            for alias in entry["aliases"]:
                if alias.lower() in text_lower:
                    if entry["era5"]:
                        variables.append(entry["era5"])
                    if entry["cmip6"]:
                        variables.append(entry["cmip6"])
                    variable_synonyms_found.extend(entry.get("keywords", []))
                    break

        experiment = resolve_experiment_synonym(text_lower)
        cmip6_filters: Dict[str, str] = {}
        if experiment:
            cmip6_filters["experiment_id"] = experiment

        variant_match = re.search(r"r\d+i\d+p\d+f\d+", text_lower)
        if variant_match:
            cmip6_filters["variant_label"] = variant_match.group(0)

        grid_match = re.search(r"\b(g|gr|gr1|gn|gr[0-9])\b", text_lower)
        if grid_match:
            candidate = grid_match.group(0)
            if candidate in {"gn", "gr", "gr1"}:
                cmip6_filters["grid_label"] = candidate

        # Table hints (Amon, Omon etc.)
        table_match = re.search(r"\b([a-z]mon|day|6hr)\b", text_lower)
        if table_match:
            cmip6_filters["table_id"] = table_match.group(0)

        location: Optional[str] = None
        for canonical, aliases in LOCATION_SYNONYMS.items():
            if any(alias in text_lower for alias in aliases):
                location = canonical
                break

        temporal_hint, years = parse_temporal_hints(text)

        if not keywords:
            keywords = []
        keywords.extend(variable_synonyms_found)
        if location:
            keywords.append(location)
        if experiment:
            keywords.append(experiment)

        keywords = sorted({kw for kw in keywords if kw})

        missing: List[str] = []
        if not temporal_hint:
            missing.append("temporal_range")
        if not location:
            missing.append("location")
        if "CMIP6" in families and not cmip6_filters.get("experiment_id"):
            missing.append("cmip6_experiment_id")
        if "CMIP6" in families and not cmip6_filters.get("variable_id") and not variables:
            missing.append("cmip6_variable_id")

        recommendations: List[str] = []
        if "cmip6_experiment_id" in missing:
            recommendations.append("Specify CMIP6 experiment (e.g., historical, ssp585).")
        if "cmip6_variable_id" in missing:
            recommendations.append("Provide CMIP6 variable (e.g., tas, pr).")
        if "temporal_range" in missing:
            recommendations.append("Add explicit years or a time span.")
        if "location" in missing:
            recommendations.append("Mention a region or let ERA5 default to global.")

        result = {
            "families": families,
            "keywords": keywords,
            "variables": variables,
            "temporal": temporal_hint,
            "spatial": location,
            "cmip6_filters": cmip6_filters,
            "years_detected": years,
            "missing": missing,
            "recommendations": recommendations,
            "original_request": text,
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


class RequestClarificationTool(BaseTool):
    name: str = "request_clarification"
    description: str = (
        "Request additional information from the user. "
        "This tool will ACTUALLY pause execution and wait for user input using input(). "
        "After receiving the user's response, the agent will continue with the workflow. "
        "Input can be plain text (a direct question) or JSON with keys "
        "like {'missing': ['temporal_range', 'location'], 'context': 'Need time range for ERA5'}."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        # Instead of calling input(), we return a instruction that the LLM should parse as a Final Answer request.
        # This prevents blocking the Streamlit UI.
        question = tool_input
        try:
             # Try parsing if JSON
             payload = json.loads(tool_input)
             question = payload.get("question", tool_input)
        except:
             pass
             
        return f"STOP_EXECUTION_AND_ASK_USER: {question}. (Please output this question as your Final Answer now)"


class MultiCriteriaSimulationSearchTool(BaseTool):
    name: str = "search_simulation_by_criteria"
    description: str = (
        "Advanced search across ERA5 and CMIP6 using multiple criteria. "
        "Input JSON example: {\n"
        '  "families": ["ERA5", "CMIP6"],\n'
        '  "keywords": ["temperature", "New York"],\n'
        '  "variables": ["2m_temperature", "tas"],\n'
        '  "temporal": "year:2020",\n'
        '  "spatial": "New York",\n'
        '  "cmip6_filters": {"experiment": "historical", "table": "Amon"},\n'
        '  "limit": 5\n'
        "}"
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        import time
        start_time = time.time()
        
        try:
            params = json.loads(tool_input) if tool_input else {}
        except json.JSONDecodeError:
            return "Input must be a JSON string."

        families_raw = params.get("families") or params.get("family") or ["ERA5", "CMIP6"]
        if isinstance(families_raw, str):
            families = [families_raw.upper()]
        else:
            families = [str(f).upper() for f in families_raw]
        families = [fam for fam in families if fam in {"ERA5", "CMIP6"}]
        if not families:
            families = ["ERA5", "CMIP6"]

        keywords = params.get("keywords") or []
        if isinstance(keywords, str):
            keywords = [keywords]
        variables = params.get("variables") or []
        if isinstance(variables, str):
            variables = [variables]
        resolved_extra_keywords: List[str] = []
        resolved_variables: List[str] = []
        for var in list(variables):
            era5_var, cmip6_var, extra_keywords = resolve_variable_synonyms(var)
            if era5_var:
                resolved_variables.append(era5_var)
            if cmip6_var:
                resolved_variables.append(cmip6_var)
            resolved_extra_keywords.extend(extra_keywords)
        if resolved_variables:
            variables.extend(resolved_variables)
        if resolved_extra_keywords:
            keywords.extend(resolved_extra_keywords)
        temporal_hint = params.get("temporal") or ""
        spatial_hint = params.get("spatial") or ""
        if spatial_hint:
            canonical_location = resolve_location_synonym(spatial_hint)
            if canonical_location:
                spatial_hint = canonical_location
                keywords.append(canonical_location)
        keywords = [kw for kw in keywords if kw]
        keywords = list(dict.fromkeys(keywords))

        limit = int(params.get("limit", 5))
        limit = max(1, min(limit, 20))

        results: List[Dict[str, Any]] = []
        diagnostics: List[str] = []
        missing_guidance: List[str] = []

        if "ERA5" in families:
            query_text = " ".join(keywords) if keywords else ""
            variable_hint = None
            for variable in variables:
                if variable.lower().startswith("2m") or variable.lower() in {v.lower() for v in variables}:
                    variable_hint = variable
                    break
            era5_hits = ERA5_LOADER.search(
                query=query_text,
                variable=variable_hint,
                temporal_hint=temporal_hint if temporal_hint else None,
                spatial_hint=spatial_hint if spatial_hint else None,
                limit=limit,
            )
            if era5_hits:
                for ds in era5_hits:
                    justification = []
                    if query_text:
                        justification.append(f"keyword match on '{query_text}'")
                    if variable_hint:
                        justification.append(f"variable match '{variable_hint}'")
                    if temporal_hint:
                        justification.append(f"temporal hint '{temporal_hint}'")
                    if spatial_hint:
                        justification.append(f"spatial hint '{spatial_hint}'")
                    results.append(
                        {
                            "dataset_id": ds.dataset_id,
                            "family": ds.family,
                            "title": ds.title,
                            "temporal_coverage": ds.temporal_coverage,
                            "spatial_coverage": ds.spatial_coverage,
                            "variables": ds.variables[:10],
                            "api_endpoint": ds.api_endpoint,
                            "justification": justification,
                        }
                    )
            else:
                diagnostics.append("ERA5 search returned no results; consider refining keywords, variables, or temporal range.")

        if "CMIP6" in families:
            cmip6_filters_input = params.get("cmip6_filters") or {}
            if isinstance(cmip6_filters_input, str):
                try:
                    cmip6_filters_input = json.loads(cmip6_filters_input)
                except json.JSONDecodeError:
                    cmip6_filters_input = {}
            cmip6_filters: Dict[str, str] = {}
            for key, value in cmip6_filters_input.items():
                alias = CMIP6_FILTER_ALIASES.get(key.lower())
                if alias and value:
                    cmip6_filters[alias] = str(value)
                elif key in CMIP6_FILTER_ALIASES.values() and value:
                    cmip6_filters[key] = str(value)

            # Allow shorthand from variables list or keywords
            if not cmip6_filters.get("variable_id") and variables:
                cmip6_filters["variable_id"] = variables[0]
            if not cmip6_filters.get("experiment_id"):
                for kw in keywords:
                    experiment_candidate = resolve_experiment_synonym(kw)
                    if experiment_candidate:
                        cmip6_filters["experiment_id"] = experiment_candidate
                        break
            if temporal_hint and not cmip6_filters.get("experiment_id"):
                if "historical" in temporal_hint.lower() or "before" in temporal_hint.lower():
                    cmip6_filters["experiment_id"] = "historical"

            if cmip6_filters:
                # Auto-complete missing DRS fields
                cmip6_filters = auto_complete_cmip6_drs(cmip6_filters, text_hint=params.get("original_query", ""))
                cmip6_hits = CMIP6_LOADER.search(filters=cmip6_filters, limit=limit)
                if cmip6_hits:
                    for ds in cmip6_hits:
                        drs_info = ds.search_handles.get("drs", {})
                        results.append(
                            {
                                "dataset_id": ds.dataset_id,
                                "family": ds.family,
                                "title": ds.title,
                                "keywords": ds.keywords,
                                "provider": ds.provider,
                                "frequency": ds.frequency,
                                "drs": drs_info,
                                "justification": [f"DRS filter {cmip6_filters}"],
                            }
                        )
                else:
                    diagnostics.append(
                        f"CMIP6 search with filters {cmip6_filters} returned no results. "
                        "You may need to provide variant_label or grid_label."
                    )
            else:
                missing_guidance.append(
                    "Provide CMIP6 DRS fields such as experiment_id, source_id, variable_id, table_id, grid_label."
                )

        payload = {
            "results": results,
            "diagnostics": diagnostics,
            "missing": missing_guidance,
        }
        
        # Record evaluation metrics
        EVALUATION_METRICS.record_query(
            query_type="multi_criteria_search",
            success=len(results) > 0,
            datasets_found=len(results),
            response_time=time.time() - start_time,
        )
        
        return json.dumps(payload, ensure_ascii=False, indent=2)


class ListStoredSimulationDatasetsTool(BaseTool):
    name: str = "list_stored_simulation_datasets"
    description: str = (
        "List datasets already stored in the local SQLite database. "
        "Input optional JSON: {'family': 'ERA5', 'limit': 20}."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        family = None
        limit = 20
        if tool_input.strip():
            try:
                params = json.loads(tool_input)
                family = params.get("family")
                limit = int(params.get("limit", limit))
            except json.JSONDecodeError:
                family = tool_input.strip()
        limit = max(1, min(limit, 100))
        entries = GRAPH_STORE.list_stored_datasets(family=family, limit=limit)
        if not entries:
            return "No datasets stored yet."
        return json.dumps(entries, ensure_ascii=False, indent=2)


class LoadStoredSimulationDatasetTool(BaseTool):
    name: str = "load_stored_simulation_dataset"
    description: str = (
        "Load a stored simulation dataset with relationships and download checks. "
        "Input JSON: {'dataset_id': 'ERA5::...'} or a plain dataset_id."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        dataset_id = tool_input.strip()
        if dataset_id.startswith("{"):
            try:
                params = json.loads(tool_input)
                dataset_id = params.get("dataset_id", dataset_id)
            except json.JSONDecodeError:
                pass
        if not dataset_id:
            return "dataset_id is required."
        data = GRAPH_STORE.fetch_dataset(dataset_id)
        if not data:
            return f"Dataset not found in SQLite: {dataset_id}"
        return json.dumps(data, ensure_ascii=False, indent=2)


class AssessDatasetQualityTool(BaseTool):
    name: str = "assess_dataset_quality"
    description: str = (
        "Assess data quality metrics for a simulation dataset. "
        "Input JSON: {'dataset_id': '...'} or a plain dataset_id. "
        "Returns quality scores, issues, and recommendations."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        dataset_id = tool_input.strip()
        if dataset_id.startswith("{"):
            try:
                params = json.loads(tool_input)
                dataset_id = params.get("dataset_id", dataset_id)
            except json.JSONDecodeError:
                pass
        
        dataset = ERA5_LOADER.get(dataset_id)
        if dataset is None and dataset_id.startswith("CMIP6::"):
            drs_part = dataset_id.replace("CMIP6::", "")
            parts = drs_part.split(".")
            if len(parts) >= 9:
                filters = {
                    "activity_id": parts[1],
                    "institution_id": parts[2],
                    "source_id": parts[3],
                    "experiment_id": parts[4],
                    "variant_label": parts[5],
                    "table_id": parts[6],
                    "variable_id": parts[7],
                    "grid_label": parts[8],
                }
                res = CMIP6_LOADER.search(filters=filters, limit=1)
                if res:
                    dataset = res[0]
                    dataset.download_links = CMIP6_LOADER.fetch_download_links(dataset, limit=5)
        
        if dataset is None:
            return f"Dataset not found: {dataset_id}"
        
        assessment = DataQualityAssessor.assess_dataset_quality(dataset)
        GRAPH_STORE.store_quality_assessment(assessment)
        GRAPH_STORE.log_event(
            dataset_id,
            "quality_assessment",
            assessment,
        )
        return json.dumps(assessment, ensure_ascii=False, indent=2)


class GetEvaluationMetricsTool(BaseTool):
    name: str = "get_evaluation_metrics"
    description: str = (
        "Get agent performance evaluation metrics including success rate, "
        "average response time, recall, precision, etc. "
        "Input: empty string or JSON with optional filters."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        summary = EVALUATION_METRICS.get_summary()
        return json.dumps(summary, ensure_ascii=False, indent=2)


class EnhancedEntityExtractionTool(BaseTool):
    name: str = "extract_entities_from_query"
    description: str = (
        "Enhanced entity extraction from natural language queries. "
        "Extracts variables, experiments, locations, temporal ranges, and CMIP6 DRS fields. "
        "Input: free-form text query."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Extract structured entities from natural language."""
        text = tool_input.strip()
        if not text:
            return json.dumps({"error": "Empty query"}, ensure_ascii=False, indent=2)
        
        text_lower = text.lower()
        entities = {
            "variables": [],
            "experiments": [],
            "locations": [],
            "temporal": None,
            "cmip6_drs": {},
            "families": [],
        }
        
        # Extract variables
        for entry in VARIABLE_SYNONYMS:
            for alias in entry.get("aliases", []):
                if alias.lower() in text_lower:
                    if entry.get("era5"):
                        entities["variables"].append({"era5": entry["era5"], "source": "synonym"})
                    if entry.get("cmip6"):
                        entities["variables"].append({"cmip6": entry["cmip6"], "source": "synonym"})
                    break
        
        # Extract experiments
        experiment = resolve_experiment_synonym(text_lower)
        if experiment:
            entities["experiments"].append(experiment)
            entities["cmip6_drs"]["experiment_id"] = experiment
        
        # Extract locations
        location = resolve_location_synonym(text_lower)
        if location:
            entities["locations"].append(location)
        
        # Extract temporal
        temporal_hint, years = parse_temporal_hints(text)
        if temporal_hint:
            entities["temporal"] = temporal_hint
        
        # Extract CMIP6 DRS patterns
        variant_match = re.search(r"r\d+i\d+p\d+f\d+", text_lower)
        if variant_match:
            entities["cmip6_drs"]["variant_label"] = variant_match.group(0)
        
        grid_match = re.search(r"\b(g|gr|gr1|gn|gr[0-9])\b", text_lower)
        if grid_match:
            candidate = grid_match.group(0)
            if candidate in {"gn", "gr", "gr1"}:
                entities["cmip6_drs"]["grid_label"] = candidate
        
        table_match = re.search(r"\b([a-z]mon|day|6hr)\b", text_lower)
        if table_match:
            entities["cmip6_drs"]["table_id"] = table_match.group(0)
        
        # Auto-complete CMIP6 DRS
        if entities["cmip6_drs"]:
            entities["cmip6_drs"] = auto_complete_cmip6_drs(entities["cmip6_drs"], text_hint=text)
        
        # Detect families
        if "era5" in text_lower:
            entities["families"].append("ERA5")
        if "cmip6" in text_lower or "esgf" in text_lower:
            entities["families"].append("CMIP6")
        if not entities["families"]:
            entities["families"] = ["ERA5", "CMIP6"]
        
        return json.dumps(entities, ensure_ascii=False, indent=2)


class VerifyDownloadLinksTool(BaseTool):
    name: str = "verify_download_links"
    description: str = (
        "Validate download URLs or ERA5 API endpoints. "
        "IMPORTANT: For ERA5, this validates the API metadata endpoint (not a direct download link). "
        "ERA5 requires using cdsapi library to submit requests and download data asynchronously. "
        "For CMIP6, this validates actual HTTP download links. "
        "Input JSON: {'dataset_id': '...', 'links': ['url1', ...]}."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input else {}
        except json.JSONDecodeError:
            return "Input must be a JSON string."

        dataset_id = params.get("dataset_id", "")
        dataset = ERA5_LOADER.get(dataset_id)
        if dataset is None and dataset_id.startswith("CMIP6::"):
            filters = params.get("filters") or {}
            if not filters and dataset_id.count(".") >= 8:
                parts = dataset_id.replace("CMIP6::", "").split(".")
                filters = {
                    "activity_id": parts[1],
                    "institution_id": parts[2],
                    "source_id": parts[3],
                    "experiment_id": parts[4],
                    "variant_label": parts[5],
                    "table_id": parts[6],
                    "variable_id": parts[7],
                    "grid_label": parts[8],
                }
            dataset = None
            if filters:
                res = CMIP6_LOADER.search(filters=filters, limit=1)
                if res:
                    dataset = res[0]
                    dataset.download_links = CMIP6_LOADER.fetch_download_links(dataset, limit=5)

        if dataset is None:
            return f"Dataset not found: {dataset_id}"

        report = {"dataset_id": dataset.dataset_id, "checks": []}
        # ERA5 endpoint (API metadata endpoint, NOT direct download link)
        if dataset.family == "ERA5" and dataset.api_endpoint:
            status, details = VALIDATOR.validate_era5_endpoint(dataset)
            GRAPH_STORE.record_download_check(dataset.dataset_id, DownloadLink(dataset.api_endpoint, "HTTPS"), status, details)
            report["checks"].append(
                {
                    "type": "ERA5 API endpoint (metadata, not direct download)",
                    "url": dataset.api_endpoint,
                    "status": status,
                    "details": details,
                    "note": "This is an API metadata endpoint. Actual data download requires cdsapi library and will be handled by simulation_data_acquisition_agent.",
                }
            )

        # CMIP6 URLs
        urls = params.get("links")
        links: List[DownloadLink] = []
        if urls:
            links = [DownloadLink(url=url, protocol="HTTPS") for url in urls]
        elif dataset.download_links:
            links = dataset.download_links

        if links:
            for link, status, details in VALIDATOR.validate_cmip6_links(links):
                GRAPH_STORE.record_download_check(dataset.dataset_id, link, status, details)
                report["checks"].append(
                    {
                        "type": "URL HEAD",
                        "url": link.url,
                        "protocol": link.protocol,
                        "status": status,
                        "details": details,
                    }
                )
        GRAPH_STORE.log_event(
            dataset.dataset_id,
            "verify_download_links",
            {
                "checks": report["checks"],
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        return json.dumps(report, ensure_ascii=False, indent=2)


class GenerateDownloadPlanTool(BaseTool):
    name: str = "generate_download_plan"
    description: str = (
        "Generate a download plan for a dataset. "
        "For ERA5: Generates Python code using cdsapi library (requires authentication via .cdsapirc). "
        "The API endpoint stored is a metadata endpoint; actual download requires submitting a request with parameters. "
        "For CMIP6: Generates ESGF query commands or HTTP download scripts. "
        "Input JSON: {'dataset_id': 'ERA5::...', 'parameters': {...}}. "
        "Returns shell/python snippets and parameter suggestions."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params = json.loads(tool_input) if tool_input else {}
        except json.JSONDecodeError:
            return "Input must be a JSON string."
        dataset_id = params.get("dataset_id", "")
        
        # Try finding in local loader
        dataset = ERA5_LOADER.get(dataset_id)
        
        # Fallback: Create "Virtual Dataset" if standard ID is recognized
        if not dataset:
            if dataset_id.startswith("ERA5::"):
                 real_id = dataset_id.replace("ERA5::", "")
                 dataset = SimulationDataset(
                     dataset_id=dataset_id,
                     family="ERA5",
                     title=f"Virtual Dataset: {real_id}",
                     description="Standard ERA5 dataset accessed directly via CDS API.",
                     variables=["(All CDS Variables Supported)"],
                     provider="Copernicus C3S",
                     api_endpoint="https://cds.climate.copernicus.eu/api/v2",
                     search_handles={"slug": real_id, "retrieve_payload_schema": {}} # Empty schema
                 )
            elif dataset_id.startswith("CMIP6::"):
                 pass # Will handle below in CMIP6 block

        if dataset:
            plan = self._build_era5_plan(dataset, params.get("parameters"))
            GRAPH_STORE.log_event(
                dataset.dataset_id,
                "generate_download_plan",
                {"family": dataset.family, "plan": plan, "timestamp": datetime.utcnow().isoformat()},
            )
            return json.dumps(plan, ensure_ascii=False, indent=2)

        if dataset_id.startswith("CMIP6::"):
            filters = params.get("filters") or {}
            res = CMIP6_LOADER.search(filters=filters, limit=1)
            # Create virtual CMIP6 if search yields nothing but ID looks real?
            # For now keep existing logic but allow fallback if filters provided
            if not res and not filters:
                 # Try inferring from ID string if complex
                 pass 
            
            if res:
                dataset = res[0]
                plan = self._build_cmip6_plan(dataset, params.get("limit", 3))
                GRAPH_STORE.log_event(
                    dataset.dataset_id,
                    "generate_download_plan",
                    {"family": dataset.family, "plan": plan, "timestamp": datetime.utcnow().isoformat()},
                )
                return json.dumps(plan, ensure_ascii=False, indent=2)
                
        return f"Unable to generate a download plan; dataset not recognized: {dataset_id}"

    def _build_era5_plan(self, dataset: SimulationDataset, override_params: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        schema = dataset.search_handles.get("retrieve_payload_schema", {})
        default_payload = {
            key: val.get("default") if isinstance(val, dict) else None
            for key, val in schema.items()
        }
        if override_params:
            default_payload.update(override_params)
        python_snippet = [
            "import cdsapi",
            "",
            "c = cdsapi.Client()",
            f"c.retrieve('{dataset.search_handles.get('slug')}',",
            "            payload,",
            "            'output.nc')",
        ]
        return {
            "dataset_id": dataset.dataset_id,
            "family": "ERA5",
            "recommended_payload": default_payload,
            "python_example": "\n".join(python_snippet).replace("payload", json.dumps(default_payload, indent=12, ensure_ascii=False)),
            "notes": "Ensure ~/.cdsapirc is configured. Adjust payload fields (time, area, variables, etc.) as needed.",
        }

    def _build_cmip6_plan(self, dataset: SimulationDataset, limit: int) -> Dict[str, Any]:
        if not dataset.download_links:
            dataset.download_links = CMIP6_LOADER.fetch_download_links(dataset, limit=limit)
        curl_commands = [
            f"curl -L -O '{link.url}'  # {link.description}"
            for link in dataset.download_links[:limit]
        ]
        return {
            "dataset_id": dataset.dataset_id,
            "family": "CMIP6",
            "esgf_query": dataset.search_handles.get("drs"),
            "curl_examples": curl_commands,
            "notes": "For batch downloads consider esgf-pyclient or synda. Configure ESGF OpenID/tokens if URLs require credentials.",
        }


# ---------- Agent Prompt ----------

SIMULATION_TEMPLATE = """You are a senior simulation data assistant responsible for locating ERA5 and CMIP6 datasets.

Follow these steps rigorously:
1. Run interpret_simulation_query on the user's request to extract families, keywords, variables, temporal hints, and CMIP6 filters.
2. If interpret_simulation_query reports missing information, call request_clarification with a focused question. 
   IMPORTANT: The request_clarification tool will ACTUALLY pause execution and wait for user input. After the user responds, the tool will return their input and you should continue with the workflow using that information.
3. Start broad with search_simulation_by_criteria. Include all interpreted clues (keywords, variables, temporal hints, CMIP6 filters). Review diagnostics; if the tool indicates missing information, loop back to clarification.
4. Use search_era5_datasets or search_cmip6_datasets for targeted follow-ups (single family, direct field matching) when additional refinement is needed.
5. Call inspect_simulation_dataset for shortlisted datasets to gather full metadata.
6. Use verify_download_links to confirm accessibility and generate_download_plan to produce actionable scripts or ESGF commands.
7. Optionally use assess_dataset_quality to evaluate data quality metrics (metadata completeness, download readiness, DRS completeness) before storing.
8. Persist confirmed datasets via store_simulation_dataset (auto-assesses quality and logs extended relationships for downstream agents). Optionally review what is stored using list_stored_simulation_datasets or load_stored_simulation_dataset.
9. Summarize results with datasets found (separated by ERA5/CMIP6), download recommendations, validation outcomes, quality grades, and stored dataset_ids.

SPATIAL FILTERING FOR ERA5:
- When user mentions a location (city, country, region), extract the location name from the query
- The location information will be passed to the data acquisition agent, which will automatically convert it to coordinates
- For ERA5 downloads, spatial filtering via 'area' parameter [north, west, south, east] significantly reduces download size
- Always include location information in search results when detected, even if coordinates are not yet resolved
- The data acquisition agent will handle coordinate resolution automatically using geocoding libraries

Available tools:
{tools}

When calling tools, follow this format:
Thought: reasoning about the next action
Action: tool name
Action Input: tool input
Observation: tool result

CRITICAL RULES:
- The request_clarification tool will ACTUALLY pause execution and wait for user input. After receiving the user's response, continue with the workflow using that information.
- Every Thought MUST be followed immediately by either an Action/Action Input/Observation sequence or by the Final Answer.
- Never output a Thought without an Action. If you have enough information to answer, skip the Thought and go straight to the Final Answer.
- When you are ready to provide the final response, use EXACTLY this format: "Final Answer: [your response]"
- Do NOT use "## Final Answer" or any other format. Use ONLY "Final Answer:"
- After outputting "Final Answer:", you MUST STOP immediately. Do NOT add any more text, thoughts, or actions.
- Do NOT repeat the Final Answer. Output it once and stop.
- The Final Answer is the LAST thing you output. Nothing comes after it.

The Final Answer must include:
    - Recommended datasets (clearly separate ERA5 vs CMIP6)
    - Download plan highlights
    - URL/endpoint validation outcomes
    - Quality grades for stored datasets (A/B/C/D)
    - Stored dataset_ids in SQLite and how to reload them (if applicable)
    - Location information extracted (if any) for spatial filtering

Now begin.

Question: {input}
Thought:{agent_scratchpad}"""


def create_simulation_agent() -> AgentExecutor:
    if not LANGCHAIN_AVAILABLE:
        raise RuntimeError("LangChain is not installed; simulation_kg_agent cannot be created.")
    tools = [
        InterpretSimulationQueryTool(),
        EnhancedEntityExtractionTool(),
        RequestClarificationTool(),
        MultiCriteriaSimulationSearchTool(),
        SearchERA5DatasetsTool(),
        SearchCMIP6DatasetsTool(),
        InspectSimulationDatasetTool(),
        VerifyDownloadLinksTool(),
        GenerateDownloadPlanTool(),
        StoreSimulationDatasetTool(),
        ListStoredSimulationDatasetsTool(),
        LoadStoredSimulationDatasetTool(),
        AssessDatasetQualityTool(),
        GetEvaluationMetricsTool(),
    ]
    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        template=SIMULATION_TEMPLATE,
    )
    tools_str = "\n".join(f"{tool.name}: {tool.description}" for tool in tools)
    tool_names_str = ", ".join([tool.name for tool in tools])
    prompt = prompt.partial(tools=tools_str, tool_names=tool_names_str)
    agent = create_react_agent(LLM_INSTANCE, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=40,
        return_intermediate_steps=False,
    )
    return executor


def get_simulation_agent() -> Optional[AgentExecutor]:
    try:
        return create_simulation_agent()
    except Exception as exc:
        logger.error("Failed to create simulation agent: %s", exc)
        return None


if __name__ == "__main__":
    print("Simulation KG Agent Self-Test")
    print("=" * 80)

    # 1. Summarize ERA5 metadata availability
    try:
        era5_total = len(ERA5_LOADER.list_datasets())
        print(f"[ERA5] Loaded dataset count: {era5_total}")
    except Exception as exc:  # pragma: no cover - manual self-test
        print(f"[ERA5] Failed to load metadata: {exc}")

    # 2. Display a representative ERA5 dataset and generate a download plan
    try:
        sample_era5_id = "ERA5::reanalysis-era5-single-levels"
        era5_dataset = ERA5_LOADER.get(sample_era5_id)
        if era5_dataset:
            print("\n[ERA5] Sample dataset:")
            print(f"  ID: {era5_dataset.dataset_id}")
            print(f"  Title: {era5_dataset.title}")
            print(f"  Temporal coverage: {era5_dataset.temporal_coverage}")
            print(f"  Variable count: {len(era5_dataset.variables)}")
            print(f"  API Endpoint: {era5_dataset.api_endpoint}")

            plan_tool = GenerateDownloadPlanTool()
            plan = plan_tool._run(
                json.dumps(
                    {
                        "dataset_id": sample_era5_id,
                        "parameters": {
                            "product_type": "reanalysis",
                            "variable": ["2m_temperature"],
                            "year": ["2020"],
                            "month": ["07"],
                            "day": ["01"],
                            "time": ["12:00"],
                            "format": "netcdf",
                        },
                    }
                )
            )
            print("\n[ERA5] Download plan sample:")
            print(plan)
        else:
            print("\n[ERA5] Sample dataset not found; verify the ERA5Meta directory.")
    except Exception as exc:  # pragma: no cover
        print(f"[ERA5] Failed to build download plan: {exc}")

    # 3. Run a sample CMIP6 search if local metadata is available
    try:
        cmip6_filters = {
            "activity_id": "CMIP",
            "experiment_id": "historical",
            "variable_id": "tas",
            "table_id": "Amon",
        }
        cmip6_results = CMIP6_LOADER.search(filters=cmip6_filters, limit=1)
        if cmip6_results:
            sample_cmip6 = cmip6_results[0]
            print("\n[CMIP6] Search sample:")
            print(f"  ID: {sample_cmip6.dataset_id}")
            print(f"  Title: {sample_cmip6.title}")
            print(f"  Keywords: {', '.join(sample_cmip6.keywords[:6])}")
            print(f"  Provider: {sample_cmip6.provider}")
        else:
            print("\n[CMIP6] No dataset matched the filters; ensure local CMIP6 metadata is available.")
    except Exception as exc:  # pragma: no cover
        print(f"[CMIP6] Search failed: {exc}")

    # 4. Initialize the agent to confirm the workflow can be created
    agent = get_simulation_agent()
    if agent:
        print("\n[Agent] AgentExecutor initialized successfully.")

        sample_query = '''
        # Please find and store the following datasets:

        1. **ERA5 historical data (1948-2023)**:
        - Temperature data for calculating warm season average (Tavg)
        - Hourly precipitation data for annual maximum warm season rainfall (R)

        2. **CMIP6 future projections (2020-2100)**:
        - Near-surface air temperature (tas) from three models: GFDL-ESM4, MPI-ESM1-2-HR, and CESM2
        - Two scenarios for each model: SSP126 and SSP370

        Once you've found and stored all datasets, provide a summary with dataset IDs ready for download.

        '''
        try:
            response = agent.invoke({"input": sample_query})
            agent_output = response.get("output", "No output")
            print(f"\n Agent response: {agent_output}")
        except Exception as exc:  # pragma: no cover
            print(f"\n[Agent] Invocation failed: {exc}")

        print("\n[Agent] Stored dataset snapshot (top 5):")
        overview_tool = ListStoredSimulationDatasetsTool()
        print(overview_tool._run(json.dumps({"limit": 5})))
    else:
        print("\n[Agent] AgentExecutor initialization failed; verify Bedrock/LangChain configuration.")
