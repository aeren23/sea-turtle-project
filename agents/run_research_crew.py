"""
Entry point for the SeaTurtle Photo-ID Research Crew.

Loads environment variables, ensures output directories exist,
builds the hierarchical crew, and kicks off execution with user input.

Usage:
    python run_research_crew.py
"""

import sys
from pathlib import Path

import os
from dotenv import load_dotenv

# Ensure the project root is in sys.path so that 'agents' package can be imported
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agents.research_crew.config import ensure_output_directories
from agents.research_crew.config import ensure_output_directories, ORCHESTRATOR_OUTPUT_DIR
from agents.research_crew.utils.log_writer import append_log, generate_output_filename

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_ENV_FILE_PATH = _PROJECT_ROOT / ".env"
_STARTUP_LOG_AUTHOR = "Antigravity / CLI Execution"


def main() -> None:
    """Main execution function for the research crew."""
    # Step 1: Load environment variables
    load_dotenv(dotenv_path=_ENV_FILE_PATH)

    # Step 2: Ensure directories exist
    ensure_output_directories()

    # Step 3: Check for API Key
    if not os.environ.get("GITHUB_TOKEN"):
        print("❌ Error: GITHUB_TOKEN environment variable is not set.")
        print("   Please create a .env file based on .env.example and add your token.")
        sys.exit(1)

    print("🐢 SeaTurtle Photo-ID Research Crew initializing...")

    # Step 4: Build the Crew
    try:
        from agents.research_crew.crew import build_crew

        crew = build_crew()
    except Exception as e:
        print(f"❌ Error building crew: {e}")
        sys.exit(1)

    # Step 5: Get user request
    print("\n📋 The Orchestrator will decide which agents to activate")
    print("   based on your request.\n")

    user_request = os.environ.get("MOCK_USER_REQUEST")
    if not user_request:
        user_request = input("🐢 Orchestrator'a görevinizi yazın: ").strip()

    if not user_request:
        print("❌ Empty request. Exiting.")
        sys.exit(1)

    # Step 6: Log the crew start
    append_log(
        author=_STARTUP_LOG_AUTHOR,
        content=f"Research crew started with user request: {user_request}",
        files_affected="agents/research_crew/",
    )

    # Step 7: Kick off the crew
    print("\n🚀 Starting crew execution...\n")
    print("=" * 60)

    result = crew.kickoff(inputs={"user_request": user_request})

    # Step 8: Save the final result to Orchestrator output dir
    final_filename = generate_output_filename("final_decision")
    final_filepath = ORCHESTRATOR_OUTPUT_DIR / final_filename
    
    with open(final_filepath, "w", encoding="utf-8") as f:
        f.write(result.raw)

    # Step 9: Display results
    print("\n" + "=" * 60)
    print("📋 FINAL RESULT")
    print("=" * 60)
    print(result)

    # Step 10: Log completion
    append_log(
        author=_STARTUP_LOG_AUTHOR,
        content=f"Research crew completed all tasks successfully. Final decision saved to {final_filename}",
        files_affected=str(final_filepath),
    )

    print("\n✅ All outputs saved to docs/research_outputs/")
    print("📝 Logs appended to docs/project_log.md")


if __name__ == "__main__":
    main()
