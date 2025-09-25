# ClimateAgent: Agents for Climate Research

This repo contains several research agents for climate research assistance.  
**Focus agents (as requested):** NasaCMR Data Acquisition, Cesm‑LENS (LangChain), Knowledge Graph Agent.  
**Supporting:** Verification Agent, Orchestrator.  
A Jupyter notebook demonstrates a full case study. The other folders under `agents/` (e.g., `case_study_1`, `npcc_fig*`, `sea_fig*`) are case‑study assets and can be ignored for a minimal run.

> We removed credentials from code. Put secrets in a local `.env` (see `env_example`) and do not commit it.

---
## Core Agents

### 🌍 NasaCMR Data Acquisition Agent  
This agent retrieves datasets from **NASA CMR**, **AWS Open Data**, and the **NOAA CDO API**, with built-in support for inline analysis. It streamlines the process of finding, accessing, and validating Earth science data.  

**Key capabilities**  
- **Dataset management**: list/query stored datasets and add new access paths.  
- **Multi-source access**: Earthdata (auth), AWS Open Data, and NOAA CDO, with automatic format detection.  
- **Inline code execution**: run Python code for computation, plotting, and validation directly after data retrieval.  

👉 **Use case**: complete a workflow of *discover → access → analyze* within a single agent for climate and statistical studies.  

---

### 🌡️ Cesm-LENS (LangChain) Agent  
This agent connects to the **CESM Large Ensemble (LENS)** and supports in-agent analysis of climate simulations. It can load data via the Intake catalog or AWS S3 `zarr`, handle CESM calendars, and produce both tabular and visual outputs.  

**Key capabilities**  
- **Flexible loading**: Intake catalog with S3 fallback, calendar decoding, and lazy loading.  
- **Ensemble analysis**: compute means, trends, and uncertainty bands, saving CSV/Parquet and figures.  
- **Integrated execution**: run analysis and visualization directly inside the agent.  

👉 **Use case**: calculate ensemble-based global temperature anomalies and export both figures and tables for downstream research.  

---

### 📚 Knowledge Graph Agent  
This agent leverages an AWS Neptune knowledge graph for **semantic dataset discovery** and structured retrieval, orchestrated by Bedrock-Claude. It enables researchers to search, filter, and persist dataset metadata for later use.  

**Key capabilities**  
- **Semantic & text search**: query datasets by variable, category, location, or resolution.  
- **Multi-criteria filtering**: combine temporal, spatial, and organizational metadata.  
- **Persistence**: save discovered datasets and metadata into SQLite for reproducible workflows.  

👉 **Use case**: locate Arctic surface temperature datasets (2000–2020, monthly resolution) and store metadata for integration into analysis workflows.  

---

### ✔️ Verification Agent  
This agent ensures the **quality and reliability** of CESM analyses and workflows. It validates datasets, checks methods, and reviews outputs for consistency.  

**Key capabilities**  
- **Data checks**: confirm CESM/observational datasets are accessible and correct.  
- **Workflow validation**: assess research steps and methodology.  
- **Output review**: verify comparison and statistical results.  

👉 **Use case**: confirm that CESM model runs and observational data are properly aligned before final analysis.  

---

### 🕹️ Orchestrator Agent  
The orchestrator acts as the **master coordinator** for climate research workflows. It interprets research questions, selects the right agents, and integrates their outputs into a coherent workflow. :contentReference[oaicite:0]{index=0}  

**Key capabilities**  
- **Agent coordination**: route tasks across NASA CMR, CESM LENS, Knowledge Graph, and Verification agents.  
- **Flexible workflows**: adapt steps dynamically based on the user’s research query.  
- **Integrated execution**: combine dataset discovery, loading, analysis, and validation in one flow.  

👉 **Use case**: handle a query like *“Validate CESM SST simulations against satellite data for 2020”* by coordinating all relevant agents automatically. :contentReference[oaicite:1]{index=1}  


---
## Quick start

### 1) Create env and install
Windows PowerShell
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Mac/Linux:
```bash
python3.10 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Secrets & config
Create .env file and fill tokens needed
```powershell
copy env_example .env   
```

### 3) Edit prompt & run

1) **Edit the prompt** at the agent file you want to run.  
2) **Run** the agent as a script:

```bash
# Observational data (NASA CMR / AWS Open Data / NOAA)
python nasa_cmr_data_acquisition_agent.py

# Climate simulations (CESM LENS)
python cesm_lens_langchain_agent.py

# Semantic discovery (Knowledge Graph / Neptune)
python knowledge_graph_agent_bedrock.py

# Verification (methodology, data & results checks)
python cesm_verification_agent.py

# End-to-end coordination (orchestrates the above)
python climate_research_orchestrator.py
```

> Notebook users: open the `.ipynb` and run top‑to‑bottom.


---

## Configuration via `.env`

| Key | Required | Notes |
| --- | --- | --- |
| `EARTHDATA_USERNAME` | ✅ | NASA Earthdata login |
| `EARTHDATA_PASSWORD` | ✅ | NASA Earthdata password |
| `NOAA_CDO_TOKEN` | ✅ | NOAA CDO API token |
| `NOAA_CDO_EMAIL` | ⛔️ optional | Email for NOAA CDO |
| `BEDROCK_REGION` | ⛔️ | Default `us-east-2` |
| `BEDROCK_MODEL_ID` | ⛔️ | e.g. `us.anthropic.claude-sonnet-4-20250514-v1:0` |
| `NEPTUNE_REGION` | ⛔️ | Default `us-east-2` |
| `GRAPH_ID` | ⛔️ | Neptune/graph id |


---
## Case Study
### Case Study: NPCC 2019 (Sea Level Rise)

We reproduced two key figures from the *New York City Panel on Climate Change 2019 Report (Chapter 3)* using our **NasaCMR Data Acquisition Agent**. (Top are reproduced ones and bottom are original ones)

<p align="center">
  <img src="/Agents/assets/figs/gmsl_reproduction.png" alt="Reproduced GMSL" width="45%"/>
  <img src="/Agents/assets/figs/battery_reproduction.png" alt="Reproduced Battery tide gauge" width="45%"/><br/>
  <img src="/Agents/assets/figs/gmsl_original.png" alt="NPCC 2019 Fig.3.1" width="45%"/>
  <img src="/Agents/assets/figs/battery_original.png" alt="NPCC 2019 Fig.3.2" width="45%"/>
</p>

- **Global Mean Sea Level (Fig. 3.1, 1993–2018):** Our reproduction matches the reported AVISO satellite altimetry trend (≈0.12 in/yr), capturing the long-term acceleration of global mean sea level during the satellite era.  
- **Relative Sea Level at The Battery, NYC (Fig. 3.2, 1856–2017):** Our reproduction replicates the historical tide gauge record and trend estimates (≈0.11 in/yr over the full record, ≈0.15 in/yr since 1993), consistent with NPCC’s findings of recent acceleration.

These results demonstrate that the agent can autonomously acquire observational datasets (satellite altimetry, NOAA tide gauges), process them into standardized formats, and generate publication-quality figures aligned with peer-reviewed references.


---

## Improvements, Problems, Limitations

- **Improvements**  
  - Extend coverage to more datasets (e.g., CMIP6, additional reanalyses).  
  - Refine data handling (units, calendars, spatial/temporal subsetting).  
  - Strengthen evaluation and reproducibility harness for consistent benchmarking.  
  - Incorporate machine learning based analysis methods to complement traditional statistical workflows.

- **Problems**  
  - External APIs (e.g., NOAA CDO) can be unstable or rate-limited, which sometimes interrupts pipelines.  
  - Current hand-off between Knowledge Graph and NasaCMR Agent is not fully seamless; metadata exchange can be improved.  
  - Large-scale data discovery still places heavy workload on NasaCMR, suggesting a need for more balanced task decomposition.  

- **Limitations**  
  - Case studies so far emphasize a few climate variables and scenarios; broader validation is still in progress.  
  - Knowledge Graph coverage is partial and expanding as new datasets are ingested.  
  - Prompt engineering remains important: different formulations can lead to different levels of data accessibility.  

---

## Project layout
```
ClimateAgent-main/agents/
├─ nasa_cmr_data_acquasition_agent.py
├─ cesm_lens_langchain_agent.py
├─ knowledge_graph_agent_bedrock.py
├─ cesm_verification_agent.py
├─ climate_research_orchestrator.py
├─ AgenticAIPipeline.ipynb
├─ case_studies/            
├─ requirements.txt
├─ env_example
└─ README.md
```
---
## Contributing
PRs welcome! Remove credentials from history and run formatters/tests before submitting.
