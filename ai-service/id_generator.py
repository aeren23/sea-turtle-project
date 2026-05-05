"""
Automatic turtle ID generator for new registrations.

Scans existing FAISS gallery metadata to find the highest ``tNNN`` ID,
then returns ``t(NNN+1)`` for the next registration.
"""

import re
import sys
from pathlib import Path

AI_CORE_DIR = Path(__file__).resolve().parent.parent / "ai-core"
sys.path.insert(0, str(AI_CORE_DIR))

from src.identification.vector_store import TurtleVectorStore  # noqa: E402

_TURTLE_ID_PATTERN = re.compile(r"^t(\d+)")


def generate_next_turtle_id(vector_store: TurtleVectorStore) -> str:
    """
    Scans all metadata entries across all FAISS indexes to find the
    maximum numeric turtle ID, then returns the next one.

    Examples:
        - Gallery has t001..t400 → returns "t401"
        - Empty gallery → returns "t001"

    Args:
        vector_store: The loaded TurtleVectorStore instance.

    Returns:
        A new turtle ID string in ``tNNN`` format.
    """
    max_num = 0

    for side in vector_store.biological_sides:
        metadata_list = vector_store._metadata.get(side, [])
        for meta in metadata_list:
            turtle_id = meta.get("turtle_id", "")
            match = _TURTLE_ID_PATTERN.match(turtle_id)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num

    next_num = max_num + 1
    return f"t{next_num:03d}"
