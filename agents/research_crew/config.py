"""
Configuration module for the SeaTurtle Photo-ID Research Crew.

Centralizes all constants, file paths, and the LLM factory function.
No magic numbers or hardcoded strings should exist outside this module.
"""

import os
from pathlib import Path

from crewai import LLM

# ---------------------------------------------------------------------------
# LLM Configuration Constants
# ---------------------------------------------------------------------------
GITHUB_MODELS_BASE_URL = "https://models.inference.ai.azure.com"
DEFAULT_MODEL_NAME = "openai/gpt-4o"

# ---------------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------------
# Project root is two levels up from this file: research_crew/ -> agents/ -> project_root/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

LOG_FILE_PATH = PROJECT_ROOT / "docs" / "project_log.md"
RESEARCH_OUTPUTS_DIR = PROJECT_ROOT / "docs" / "research_outputs"

# Agent-specific output directories
DATA_RESEARCHER_OUTPUT_DIR = RESEARCH_OUTPUTS_DIR / "data_researcher"
CV_RESEARCHER_OUTPUT_DIR = RESEARCH_OUTPUTS_DIR / "cv_researcher"
DL_STRATEGIST_OUTPUT_DIR = RESEARCH_OUTPUTS_DIR / "dl_strategist"
BIOLOGIST_OUTPUT_DIR = RESEARCH_OUTPUTS_DIR / "biologist"
ORCHESTRATOR_OUTPUT_DIR = RESEARCH_OUTPUTS_DIR / "orchestrator"

ALL_OUTPUT_DIRS = [
    DATA_RESEARCHER_OUTPUT_DIR,
    CV_RESEARCHER_OUTPUT_DIR,
    DL_STRATEGIST_OUTPUT_DIR,
    BIOLOGIST_OUTPUT_DIR,
    ORCHESTRATOR_OUTPUT_DIR,
]


def ensure_output_directories() -> None:
    """Creates all agent output directories if they do not already exist.

    This must be called once before the crew runs to guarantee that
    FileWriteTool has valid target paths available.
    """
    for directory in ALL_OUTPUT_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


def create_llm() -> LLM:
    """Factory function that creates an LLM instance configured for GitHub Models.

    Uses the GITHUB_TOKEN environment variable for authentication.
    The token must be set before calling this function (typically via .env).

    Returns:
        LLM: A CrewAI LLM instance pointing to GitHub Models.

    Raises:
        ValueError: If GITHUB_TOKEN is not set in the environment.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError(
            "GITHUB_TOKEN environment variable is not set. "
            "Please add it to your .env file or export it in your shell."
        )

    return LLM(
        model=DEFAULT_MODEL_NAME,
        base_url=GITHUB_MODELS_BASE_URL,
        api_key=github_token,
    )
