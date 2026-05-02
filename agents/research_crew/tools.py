"""
Tool definitions for the SeaTurtle Photo-ID Research Crew.

Provides the FileWriteTool (from crewai_tools) and a DuckDuckGo search
wrapper compatible with CrewAI's tool interface. No API key required
for DuckDuckGo — this makes the setup zero-cost for internet research.
"""

from crewai.tools import tool
from crewai_tools import FileWriterTool
from langchain_community.tools import DuckDuckGoSearchRun

# ---------------------------------------------------------------------------
# File Writer Tool — used by all agents to save research outputs
# ---------------------------------------------------------------------------
file_write_tool = FileWriterTool()

# ---------------------------------------------------------------------------
# DuckDuckGo Search Tool — wrapped for CrewAI compatibility
# ---------------------------------------------------------------------------
_duckduckgo_engine = DuckDuckGoSearchRun()


@tool("DuckDuckGo Search")
def duckduckgo_search_tool(query: str) -> str:
    """Searches the internet using DuckDuckGo and returns relevant results.

    Use this tool to find current information about sea turtle datasets,
    computer vision techniques, deep learning architectures, or any other
    research topic relevant to the Photo-ID project.

    Args:
        query: The search query string describing what to look for.

    Returns:
        str: A summary of search results from DuckDuckGo.
    """
    return _duckduckgo_engine.run(query)


# ---------------------------------------------------------------------------
# Tool Lists — assigned to agents based on their role
# ---------------------------------------------------------------------------
RESEARCHER_TOOLS = [file_write_tool, duckduckgo_search_tool]
MANAGER_TOOLS = [file_write_tool]
