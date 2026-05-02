"""
Log Writer Utility for the SeaTurtle Photo-ID Research Crew.

Provides thread-safe append-only logging to docs/project_log.md
following the strict format defined in docs/rules/logging_standards.md.
Also provides timestamped filename generation for dynamic output files.
"""

import threading
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Thread lock to prevent concurrent write corruption
_log_lock = threading.Lock()

# Turkish timezone offset (UTC+3)
_TURKEY_TZ = timezone(timedelta(hours=3))

# Project root is three levels up from this file: utils/ -> research_crew/ -> agents/ -> project_root/
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_LOG_FILE_PATH = _PROJECT_ROOT / "docs" / "project_log.md"


def _get_current_timestamp() -> str:
    """Returns the current timestamp in 'YYYY-MM-DD HH:MM:SS' format (Turkey timezone).

    Returns:
        str: Formatted timestamp string.
    """
    now = datetime.now(tz=_TURKEY_TZ)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def _get_filename_timestamp() -> str:
    """Returns the current timestamp in 'YYYYMMDD_HHMMSS' format for file naming.

    Returns:
        str: Compact timestamp string suitable for filenames.
    """
    now = datetime.now(tz=_TURKEY_TZ)
    return now.strftime("%Y%m%d_%H%M%S")


def generate_output_filename(base_name: str, extension: str = ".md") -> str:
    """Generates a timestamped filename for agent output files.

    Combines a descriptive base name with a timestamp suffix to ensure
    each crew run produces uniquely named output files.

    Args:
        base_name: The descriptive prefix for the file (e.g., 'dataset_analysis').
        extension: The file extension including the dot (default: '.md').

    Returns:
        str: A filename like 'dataset_analysis_20260502_021200.md'.
    """
    timestamp = _get_filename_timestamp()
    return f"{base_name}_{timestamp}{extension}"


def append_log(
    author: str,
    content: str,
    files_affected: str = "None",
    issues: str = "None",
) -> None:
    """Appends a structured log entry to docs/project_log.md.

    This function is thread-safe and strictly follows the format
    defined in docs/rules/logging_standards.md. It NEVER overwrites
    the existing file content — only appends to the end.

    Args:
        author: The agent or tool name (e.g., 'Data Researcher', 'Orchestrator').
        content: A brief description of the action/task and key details/decisions.
        files_affected: Comma-separated list of affected files (default: 'None').
        issues: Description of any errors and resolutions (default: 'None').

    Raises:
        OSError: If the log file cannot be opened or written to.
    """
    timestamp = _get_current_timestamp()

    log_entry = (
        f"\n---\n"
        f"### [{timestamp}] — {author}\n"
        f"* **Action/Task:** {content}\n"
        f"* **Files Affected:** {files_affected}\n"
        f"* **Details/Decisions:** {content}\n"
        f"* **Issues & Resolutions:** {issues}\n"
    )

    with _log_lock:
        _LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_LOG_FILE_PATH, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
