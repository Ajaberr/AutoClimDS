#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scholar Data Acquisition Agent

An intelligent agent for searching academic literature via the Semantic Scholar
API. Returns paper metadata, abstracts, TL;DR summaries, and citation counts.

Features:
- Query Semantic Scholar for climate research papers
- Filter by year range, minimum citations, and open-access availability
- Three summary modes: Quick (TL;DR only), Standard (LLM 3-sentence),
  Detailed (LLM 100-word paragraph)
- Environment-driven controls for UI integration:
  SCHOLAR_TOP_K, SCHOLAR_YEAR_FROM, SCHOLAR_YEAR_TO,
  SCHOLAR_SUMMARY_DEPTH, SCHOLAR_MIN_CITATIONS, SCHOLAR_SORT_BY,
  SCHOLAR_OPEN_ACCESS_ONLY, SCHOLAR_INCLUDE_ABSTRACT

API: https://api.semanticscholar.org/graph/v1
"""

import os
import json
import logging
import requests
import pandas as pd
from typing import Optional, List, Any
from pathlib import Path
from datetime import datetime

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import BaseTool
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

SEMANTIC_SCHOLAR_BASE = "https://api.semanticscholar.org/graph/v1"
SCHOLAR_API_KEY       = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
DOWNLOAD_DIR          = "scholar_downloads"
BEDROCK_REGION        = os.getenv("BEDROCK_REGION", "us-east-2")
BEDROCK_MODEL_ID      = os.getenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-20250514-v1:0")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

FIELDS = "title,authors,year,abstract,tldr,citationCount,externalIds,openAccessPdf,venue"

# User-facing default controls (overridable via env vars set by the UI)
DEFAULTS = {
    "top_k":            5,
    "year_from":        2020,
    "year_to":          None,       # None → current year
    "summary_depth":    "standard", # quick / standard / detailed
    "min_citations":    0,
    "sort_by":          "relevance",# relevance / year / citations
    "open_access_only": False,
    "include_abstract": False,
}

VALID_DEPTHS   = {"quick", "standard", "detailed"}
VALID_SORT_BYS = {"relevance", "year", "citations"}


def _ss_headers() -> dict:
    h = {"Content-Type": "application/json"}
    if SCHOLAR_API_KEY:
        h["x-api-key"] = SCHOLAR_API_KEY
    return h


def _read_env_controls() -> dict:
    """Merge env-var overrides with DEFAULTS. Env vars are set by the Streamlit sidebar."""
    def _env(key, cast=str, default=None):
        v = os.getenv(key)
        if v is None or v == "":
            return default
        try:
            if cast is bool:
                return v.lower() in ("1", "true", "yes", "on")
            return cast(v)
        except Exception:
            return default

    ctrl = dict(DEFAULTS)
    ctrl["top_k"]            = _env("SCHOLAR_TOP_K",            int,  ctrl["top_k"])
    ctrl["year_from"]        = _env("SCHOLAR_YEAR_FROM",        int,  ctrl["year_from"])
    ctrl["year_to"]          = _env("SCHOLAR_YEAR_TO",          int,  ctrl["year_to"])
    ctrl["summary_depth"]    = _env("SCHOLAR_SUMMARY_DEPTH",    str,  ctrl["summary_depth"])
    ctrl["min_citations"]    = _env("SCHOLAR_MIN_CITATIONS",    int,  ctrl["min_citations"])
    ctrl["sort_by"]          = _env("SCHOLAR_SORT_BY",          str,  ctrl["sort_by"])
    ctrl["open_access_only"] = _env("SCHOLAR_OPEN_ACCESS_ONLY", bool, ctrl["open_access_only"])
    ctrl["include_abstract"] = _env("SCHOLAR_INCLUDE_ABSTRACT", bool, ctrl["include_abstract"])

    # Normalize / bound
    if ctrl["summary_depth"] not in VALID_DEPTHS:
        ctrl["summary_depth"] = DEFAULTS["summary_depth"]
    if ctrl["sort_by"] not in VALID_SORT_BYS:
        ctrl["sort_by"] = DEFAULTS["sort_by"]
    ctrl["top_k"]         = max(1, min(int(ctrl["top_k"]), 100))
    ctrl["min_citations"] = max(0, int(ctrl["min_citations"]))
    return ctrl


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


# Shared LLM instance for summarization (kept lazy so import-time is cheap)
_SUMMARY_LLM: Optional[BedrockClaudeLLM] = None

def _get_summary_llm() -> BedrockClaudeLLM:
    global _SUMMARY_LLM
    if _SUMMARY_LLM is None:
        _SUMMARY_LLM = BedrockClaudeLLM()
    return _SUMMARY_LLM


def _summarize(paper: dict, depth: str) -> str:
    """Produce a per-paper summary at the requested depth."""
    tldr = paper.get("tldr") or {}
    tldr_text = tldr.get("text", "") if isinstance(tldr, dict) else ""
    abstract = paper.get("abstract") or ""

    if depth == "quick":
        # Zero-cost path: use API's TL;DR verbatim; fall back to first abstract sentence.
        if tldr_text:
            return tldr_text
        return abstract.split(". ")[0] + ("." if abstract else "")

    if not abstract and not tldr_text:
        return "(no abstract available)"

    source = abstract or tldr_text
    if depth == "standard":
        prompt = (
            "Summarize this paper abstract in exactly 3 sentences. "
            "Keep it concrete and technical.\n\n"
            f"Abstract:\n{source}"
        )
    else:  # detailed
        prompt = (
            "Summarize this paper abstract in one paragraph (~100 words). "
            "Cover method, findings, and significance.\n\n"
            f"Abstract:\n{source}"
        )

    try:
        return _get_summary_llm()._call(prompt).strip()
    except Exception as e:
        logger.warning(f"Summary LLM failed, falling back to TL;DR: {e}")
        return tldr_text or (source[:200] + "...")


def _apply_filters(papers: List[dict], ctrl: dict) -> List[dict]:
    out = []
    for p in papers:
        if int(p.get("citationCount") or 0) < ctrl["min_citations"]:
            continue
        if ctrl["open_access_only"]:
            pdf = p.get("openAccessPdf") or {}
            if not (isinstance(pdf, dict) and pdf.get("url")):
                continue
        out.append(p)
    return out


def _sort_papers(papers: List[dict], sort_by: str) -> List[dict]:
    if sort_by == "year":
        return sorted(papers, key=lambda p: int(p.get("year") or 0), reverse=True)
    if sort_by == "citations":
        return sorted(papers, key=lambda p: int(p.get("citationCount") or 0), reverse=True)
    # relevance = API's natural order
    return papers


class SearchScholarTool(BaseTool):
    """Search academic papers via Semantic Scholar."""
    name: str = "search_scholar_papers"
    description: str = (
        "Search academic literature using Semantic Scholar. "
        "Input: JSON with 'query' (required). All other parameters (top_k, year range, "
        "summary depth, min citations, sort order, open-access filter) come from the "
        "user's sidebar controls; do NOT set them in tool input unless the user "
        "explicitly requests a different value in the query. "
        "Example: {\"query\": \"urban flood 311 reporting bias\"} "
        "Returns: ranked list with title, authors, year, citations, summary, venue, PDF link."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params_in = json.loads(tool_input) if tool_input.strip().startswith("{") else {"query": tool_input}
        except Exception:
            params_in = {"query": tool_input}

        query = params_in.get("query", "").strip()
        if not query:
            return "Error: 'query' is required."

        ctrl = _read_env_controls()

        # Per-query overrides (rarely used; mostly the sidebar drives things)
        for key in ("top_k", "year_from", "year_to", "summary_depth",
                    "min_citations", "sort_by", "open_access_only", "include_abstract"):
            if key in params_in and params_in[key] is not None:
                ctrl[key] = params_in[key]

        year_to = ctrl["year_to"] or datetime.now().year

        # Ask API for a larger candidate pool so post-filter still returns top_k
        candidate_limit = min(max(ctrl["top_k"] * 4, 20), 100)
        api_params: dict = {
            "query":  query,
            "limit":  candidate_limit,
            "fields": FIELDS,
            "year":   f"{ctrl['year_from']}-{year_to}",
        }

        try:
            resp = requests.get(
                f"{SEMANTIC_SCHOLAR_BASE}/paper/search",
                params=api_params,
                headers=_ss_headers(),
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            return f"Error calling Semantic Scholar API: {e}"

        papers = data.get("data", [])
        if not papers:
            return f"No papers found for query: '{query}'"

        filtered = _apply_filters(papers, ctrl)
        if not filtered:
            return (
                f"Found {len(papers)} candidate paper(s) for '{query}', "
                f"but none passed filters (min_citations={ctrl['min_citations']}, "
                f"open_access_only={ctrl['open_access_only']}). "
                "Try loosening the sidebar controls."
            )

        ranked = _sort_papers(filtered, ctrl["sort_by"])[: ctrl["top_k"]]

        header = (
            f"Top {len(ranked)} paper(s) for '{query}' "
            f"(year {ctrl['year_from']}-{year_to}, sort={ctrl['sort_by']}, "
            f"depth={ctrl['summary_depth']}):\n"
        )
        lines = [header]

        for i, p in enumerate(ranked, 1):
            authors_list = p.get("authors", []) or []
            authors = ", ".join(a.get("name", "") for a in authors_list[:3])
            if len(authors_list) > 3:
                authors += " et al."
            pdf = p.get("openAccessPdf") or {}
            pdf_url = pdf.get("url", "") if isinstance(pdf, dict) else ""

            lines.append(f"[{i}] {p.get('title', 'No title')}")
            lines.append(
                f"    Authors: {authors}  |  Year: {p.get('year', '?')}  "
                f"|  Citations: {p.get('citationCount', 0)}"
            )
            if p.get("venue"):
                lines.append(f"    Venue: {p['venue']}")

            summary = _summarize(p, ctrl["summary_depth"])
            if summary:
                lines.append(f"    Summary: {summary}")

            if ctrl["include_abstract"] and p.get("abstract"):
                lines.append(f"    Abstract: {p['abstract']}")

            if pdf_url:
                lines.append(f"    PDF: {pdf_url}")
            lines.append("")

        return "\n".join(lines)


class GetPaperDetailsTool(BaseTool):
    """Get full details for a specific paper by Semantic Scholar paper ID or DOI."""
    name: str = "get_paper_details"
    description: str = (
        "Get full details (abstract, references, citations) for a specific paper. "
        "Input: a Semantic Scholar paper ID (e.g. '649def34f8be52c8b66281af98ae884c09aef38d') "
        "or a DOI (e.g. '10.1145/3292500.3330749'). "
        "Use this after search_scholar_papers to get the full abstract of a paper."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        paper_id = tool_input.strip().strip('"').strip("'")

        if paper_id.startswith("10."):
            paper_id = f"DOI:{paper_id}"

        try:
            resp = requests.get(
                f"{SEMANTIC_SCHOLAR_BASE}/paper/{paper_id}",
                params={"fields": FIELDS + ",references"},
                headers=_ss_headers(),
                timeout=20,
            )
            resp.raise_for_status()
            p = resp.json()
        except Exception as e:
            return f"Error fetching paper details: {e}"

        authors = ", ".join(a.get("name", "") for a in p.get("authors", []))
        tldr = p.get("tldr") or {}
        tldr_text = tldr.get("text", "") if isinstance(tldr, dict) else ""
        pdf = p.get("openAccessPdf") or {}
        pdf_url = pdf.get("url", "") if isinstance(pdf, dict) else ""

        out = [
            f"Title: {p.get('title', '')}",
            f"Authors: {authors}",
            f"Year: {p.get('year', '?')}  |  Citations: {p.get('citationCount', 0)}",
            f"Venue: {p.get('venue', '')}",
        ]
        if tldr_text:
            out.append(f"TL;DR: {tldr_text}")
        if p.get("abstract"):
            out.append(f"\nAbstract:\n{p['abstract']}")
        if pdf_url:
            out.append(f"\nPDF: {pdf_url}")

        refs = p.get("references", [])
        if refs:
            out.append(f"\nKey references ({len(refs)} total):")
            for r in refs[:5]:
                out.append(f"  - {r.get('title', '')} ({r.get('year', '?')})")

        return "\n".join(out)


class SaveScholarResultsTool(BaseTool):
    """Save search results to a CSV file."""
    name: str = "save_scholar_results"
    description: str = (
        "Save the current search results to a CSV file for further analysis. "
        "Input: JSON with 'query' (the search term) and 'limit' (number of results). "
        "Example: {\"query\": \"flood crowdsourcing bias\", \"limit\": 50} "
        "Returns the file path of the saved CSV."
    )

    def _run(self, tool_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            params_in = json.loads(tool_input) if tool_input.strip().startswith("{") else {"query": tool_input}
        except Exception:
            params_in = {"query": tool_input}

        query = params_in.get("query", "").strip()
        limit = min(int(params_in.get("limit", 50)), 100)

        if not query:
            return "Error: 'query' is required."

        try:
            resp = requests.get(
                f"{SEMANTIC_SCHOLAR_BASE}/paper/search",
                params={"query": query, "limit": limit, "fields": FIELDS},
                headers=_ss_headers(),
                timeout=20,
            )
            resp.raise_for_status()
            papers = resp.json().get("data", [])
        except Exception as e:
            return f"Error calling Semantic Scholar API: {e}"

        if not papers:
            return f"No papers found for '{query}'"

        rows = []
        for p in papers:
            tldr = p.get("tldr") or {}
            tldr_text = tldr.get("text", "") if isinstance(tldr, dict) else ""
            pdf = p.get("openAccessPdf") or {}
            pdf_url = pdf.get("url", "") if isinstance(pdf, dict) else ""
            rows.append({
                "title":         p.get("title", ""),
                "authors":       ", ".join(a.get("name", "") for a in p.get("authors", [])),
                "year":          p.get("year", ""),
                "venue":         p.get("venue", ""),
                "citations":     p.get("citationCount", 0),
                "tldr":          tldr_text,
                "abstract":      p.get("abstract", ""),
                "pdf_url":       pdf_url,
                "doi":           (p.get("externalIds") or {}).get("DOI", ""),
            })

        df = pd.DataFrame(rows)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c if c.isalnum() else "_" for c in query)[:40]
        filename = f"scholar_{safe_query}_{ts}.csv"
        output_path = Path(DOWNLOAD_DIR) / filename
        df.to_csv(output_path, index=False)

        return (
            f"Saved {len(df)} papers to {output_path.resolve()}\n"
            f"Columns: {', '.join(df.columns.tolist())}"
        )


SCHOLAR_PROMPT = PromptTemplate.from_template("""You are the Scholar Data Acquisition Agent for AutoClimDS.
You search academic literature using Semantic Scholar to find relevant papers on climate science,
data analysis methods, agentic AI, flood research, and related topics.

WORKFLOW:
1. Use search_scholar_papers to find papers matching the user's topic.
2. Use get_paper_details to retrieve the full abstract of a specific paper if needed.
3. Use save_scholar_results to export results to CSV when the user wants to save them.

GUIDELINES:
- search_scholar_papers reads the user's sidebar controls (top_k, year range, summary depth,
  min citations, sort order, open-access filter). Just pass the query; do not override
  those controls unless the user explicitly asks in their message.
- If the user asks for papers on a climate topic, add relevant keywords (e.g. "urban flooding machine learning").
- For saving results, use save_scholar_results with the same query.

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

Question: {input}
Thought:{agent_scratchpad}""")


def get_scholar_agent() -> AgentExecutor:
    llm = BedrockClaudeLLM()
    tools = [SearchScholarTool(), GetPaperDetailsTool(), SaveScholarResultsTool()]
    agent = create_react_agent(llm=llm, tools=tools, prompt=SCHOLAR_PROMPT)
    return AgentExecutor(
        agent=agent, tools=tools,
        verbose=True, max_iterations=8, handle_parsing_errors=True,
    )


if __name__ == "__main__":
    executor = get_scholar_agent()
    result = executor.invoke({"input": "Find recent papers on urban flood reporting bias and crowdsourcing."})
    print(result.get("output"))
