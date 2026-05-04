"""
Autonomous Turtle Identification CLI.

Takes a raw turtle photograph and returns the identification result
without requiring any manual bbox or side parameters.

Usage:
    python scripts/infer_turtle.py --image path/to/photo.jpg
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.inference.inference_pipeline import TurtleInferencePipeline


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Identify a sea turtle from a raw photograph (fully autonomous)."
    )
    parser.add_argument(
        "--image", type=str, required=True,
        help="Path to the raw turtle photograph.",
    )
    return parser.parse_args()


def main() -> None:
    """Runs the autonomous inference pipeline on a single image."""
    args = parse_args()
    image_path = str(Path(args.image).resolve())

    print("=" * 60)
    print("SeaTurtle Photo-ID — Autonomous Inference")
    print("=" * 60)
    print(f"Image: {image_path}\n")

    print("Loading pipeline (YOLO + ResNet + FAISS)...")
    pipeline = TurtleInferencePipeline()

    print("Running inference...\n")
    result = pipeline.run(image_path)

    if result.error:
        print(f"ERROR: {result.error}")
        return

    det = result.detection
    ident = result.identification

    print(f"--- Head Detection ---")
    print(f"  BBox (COCO):       {det.bbox}")
    print(f"  Biological Side:   {det.biological_side}")
    print(f"  YOLO Confidence:   {det.confidence:.4f}")

    print(f"\n--- Identification ---")
    if ident.is_known:
        print(f"  Status:            KNOWN INDIVIDUAL")
        print(f"  Turtle ID:         {ident.best_match_id}")
    else:
        print(f"  Status:            UNKNOWN INDIVIDUAL")

    print(f"  Best Match Score:  {ident.best_match_score:.4f}")
    print(f"  Side Searched:     {ident.biological_side}")

    if ident.top_k_matches:
        print(f"\n--- Top-K Matches ---")
        for rank, (score, meta) in enumerate(ident.top_k_matches, 1):
            print(f"  {rank}. {meta['turtle_id']} — score: {score:.4f}")

    print("\nDone.")


if __name__ == "__main__":
    main()
