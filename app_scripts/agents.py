from typing import Callable, Dict
from Agents.nasa_cmr_data_acquisition_agent import create_nasa_cmr_agent
from Agents.knowledge_graph_agent_bedrock import create_knowledge_graph_agent
from Agents.cesm_lens_langchain_agent import create_cesm_lens_agent
from Agents.climate_research_orchestrator import create_climate_research_orchestrator

# Registry of agent factories. Add/remove here for easier management.
AGENTS: Dict[str, Callable[[], object]] = {
    "NASA CMR": create_nasa_cmr_agent,
    "Knowledge Graph": create_knowledge_graph_agent,
    "CESM Lens": create_cesm_lens_agent,
    "Orchestrator": create_climate_research_orchestrator,
}

CURRENT_AGENT_KEY = "Knowledge Graph"
AGENT = None

def get_agent():
    """Return a singleton agent instance of CURRENT_AGENT_KEY."""
    global AGENT
    if AGENT is None:
        AGENT = AGENTS[CURRENT_AGENT_KEY]()
    return AGENT

def switch_agent(new_key: str):
    """Switch the active agent by name. Instance will be recreated on next get."""
    global CURRENT_AGENT_KEY, AGENT
    CURRENT_AGENT_KEY = new_key
    AGENT = None

def restart_agent():
    """Drop current agent instance."""
    global AGENT
    AGENT = None
    return True
