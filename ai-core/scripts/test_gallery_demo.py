"""
Gallery Demo Tests for SeaTurtle Photo-ID.

Test 1 — Known Turtle:
    Picks a random LEFT-side image already in the gallery and queries it
    using the SAME bounding box that was used during gallery build.
    Expected: cosine similarity near 1.0, correct turtle_id at rank 1.

    IMPORTANT: The gallery stores embeddings of CROPPED turtle heads.
    Querying without the same bbox produces a completely different
    embedding (full image vs. cropped head) → low similarity even for
    the exact same file.  The DTO bbox is therefore retrieved from the
    dataset parser and passed to the identifier.

Test 2 — Unknown Individual:
    Feeds Gaussian noise through the pipeline (simulates a completely
    unrelated / out-of-distribution image).
    Expected: best score well below IDENTIFICATION_THRESHOLD → "Unknown".
"""

import json
import os
import random
import sys
import tempfile

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config.data_config import FAISS_INDEX_DIR, IDENTIFICATION_THRESHOLD
from src.data.dataset_parser import SeaTurtleDatasetParser
from src.identification.identifier import TurtleIdentifier


SEPARATOR = "=" * 62


def build_path_to_dto_map() -> dict:
    """
    Parses the full dataset and returns a dict mapping
    image_path (str) → TurtleImageDTO for fast bbox lookup.
    """
    parser = SeaTurtleDatasetParser()
    dtos = parser.parse()
    return {str(dto.file_path): dto for dto in dtos}


def load_random_left_entry() -> dict:
    """Reads meta_left.json and returns one random entry."""
    meta_path = FAISS_INDEX_DIR / "meta_left.json"
    with open(meta_path, "r", encoding="utf-8") as fh:
        entries = json.load(fh)
    return random.choice(entries)


def create_noise_image_path() -> str:
    """
    Saves a random Gaussian noise image to a temp file and returns its path.
    Simulates a completely out-of-distribution query (unknown individual).
    """
    noise = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    cv2.imwrite(tmp.name, noise)
    return tmp.name


def run_test_1(identifier: TurtleIdentifier, path_to_dto: dict) -> None:
    """Known Turtle Test — gallery image queried with its original bbox."""
    print(f"\n{SEPARATOR}")
    print("  TEST 1 — Known Turtle (Left Side, Gallery Image + Correct BBox)")
    print(SEPARATOR)

    entry = load_random_left_entry()
    image_path = entry["image_path"]
    expected_id = entry["turtle_id"]

    # Retrieve the original bounding box used during gallery build
    dto = path_to_dto.get(image_path)
    bbox = dto.head_bbox if dto else None

    print(f"  Query image  : {os.path.basename(image_path)}")
    print(f"  Expected ID  : {expected_id}")
    print(f"  BBox used    : {bbox}")
    print(f"  Threshold    : {IDENTIFICATION_THRESHOLD}")
    print()

    result = identifier.identify(
        image_path=image_path,
        biological_side="left",
        bbox=bbox,
    )

    status = "MATCH FOUND" if result.is_known else "UNKNOWN (below threshold)"
    print(f"  Result       : {status}")
    print(f"  Best Match ID: {result.best_match_id or 'N/A'}")
    print(f"  Best Score   : {result.best_match_score:.6f}")
    correct = result.best_match_id == expected_id
    print(f"  Correct?     : {'YES ✓' if correct else 'NO ✗'}")

    print(f"\n  Top-{len(result.top_k_matches)} Matches:")
    print(f"  {'Rank':<5} {'Score':<12} {'Turtle ID'}")
    print(f"  {'-'*5} {'-'*12} {'-'*15}")
    for rank, (score, meta) in enumerate(result.top_k_matches, 1):
        marker = " <-- expected" if meta["turtle_id"] == expected_id else ""
        print(f"  {rank:<5} {score:<12.6f} {meta['turtle_id']}{marker}")


def run_test_2(identifier: TurtleIdentifier) -> None:
    """Unknown Individual Test — Gaussian noise image."""
    print(f"\n{SEPARATOR}")
    print("  TEST 2 — Unknown Individual (Gaussian Noise Image)")
    print(SEPARATOR)
    print("  Query image  : [synthetic Gaussian noise — 224x224 RGB]")
    print(f"  Threshold    : {IDENTIFICATION_THRESHOLD}")
    print()

    noise_path = create_noise_image_path()
    try:
        result = identifier.identify(
            image_path=noise_path,
            biological_side="left",
            bbox=None,
        )
    finally:
        os.unlink(noise_path)

    status = "MATCH FOUND (unexpected!)" if result.is_known else "UNKNOWN INDIVIDUAL ✓ (correct — below threshold)"
    print(f"  Result       : {status}")
    print(f"  Best Score   : {result.best_match_score:.6f}")
    print(f"  All scores below {IDENTIFICATION_THRESHOLD}? : {'YES ✓' if not result.is_known else 'NO ✗'}")

    if result.top_k_matches:
        print(f"\n  Top-{len(result.top_k_matches)} Closest (all should be low):")
        print(f"  {'Rank':<5} {'Score':<12} {'Turtle ID'}")
        print(f"  {'-'*5} {'-'*12} {'-'*15}")
        for rank, (score, meta) in enumerate(result.top_k_matches, 1):
            print(f"  {rank:<5} {score:<12.6f} {meta['turtle_id']}")


def main() -> None:
    print(SEPARATOR)
    print("  SeaTurtle Photo-ID — Gallery Demo Tests")
    print(SEPARATOR)
    print("  Loading gallery indexes and model...")

    identifier = TurtleIdentifier()

    stats = identifier.vector_store.get_stats()
    print(f"  Gallery loaded: Left={stats['left']} | Right={stats['right']} | Top={stats['top']}")

    print("  Building image-path → DTO map for bbox lookup...")
    path_to_dto = build_path_to_dto_map()

    run_test_1(identifier, path_to_dto)
    run_test_2(identifier)

    print(f"\n{SEPARATOR}\n")


if __name__ == "__main__":
    main()
