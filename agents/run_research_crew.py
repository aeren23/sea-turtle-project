"""
Entry point for the SeaTurtle Photo-ID Research Crew.

Loads environment variables, ensures output directories exist,
builds the hierarchical crew, and kicks off execution with user input.

Usage:
    python run_research_crew.py
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure the project root is in sys.path so that 'agents' package can be imported
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agents.research_crew.config import ensure_output_directories
from agents.research_crew.crew import build_crew
from agents.research_crew.utils.log_writer import append_log

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_ENV_FILE_PATH = _PROJECT_ROOT / ".env"
_STARTUP_LOG_AUTHOR = "Antigravity / CLI Execution"


def main() -> None:
    """Main execution flow for the research crew.

    1. Loads .env for GITHUB_TOKEN
    2. Creates output directories
    3. Prompts user for a research request
    4. Kicks off the hierarchical crew
    5. Displays the final result
    """
    # Step 1: Load environment variables
    load_dotenv(dotenv_path=_ENV_FILE_PATH)

    # Step 2: Ensure all output directories exist
    ensure_output_directories()

    # Step 3: Build the crew
    print("🐢 SeaTurtle Photo-ID Research Crew initializing...")
    print("=" * 60)

    try:
        crew = build_crew()
    except ValueError as error:
        print(f"\n❌ Configuration Error: {error}")
        sys.exit(1)

    # Step 4: Get user request
    print("\n📋 The Orchestrator will decide which agents to activate")
    print("   based on your request.\n")

    user_request = input("🐢 Orchestrator'a görevinizi yazın: ").strip()

    if not user_request:
        print("❌ Empty request. Exiting.")
        sys.exit(1)

    # Step 5: Log the crew start
    append_log(
        author=_STARTUP_LOG_AUTHOR,
        content=f"Research crew started with user request: {user_request}",
        files_affected="agents/research_crew/",
    )

    # Step 6: Kick off the crew
    print("\n🚀 Starting crew execution...\n")
    print("=" * 60)

    result = crew.kickoff(inputs={"user_request": user_request})

    # Step 7: Display results
    print("\n" + "=" * 60)
    print("📋 FINAL RESULT")
    print("=" * 60)
    print(result)

    # Step 8: Log completion
    append_log(
        author=_STARTUP_LOG_AUTHOR,
        content="Research crew completed all tasks successfully.",
        files_affected="docs/research_outputs/",
    )

    print("\n✅ All outputs saved to docs/research_outputs/")
    print("📝 Logs appended to docs/project_log.md")


if __name__ == "__main__":
    main()
