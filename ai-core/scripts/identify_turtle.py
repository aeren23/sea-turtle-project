"""
CLI entry point to identify a turtle from a single query image.

Usage:
    python scripts/identify_turtle.py --image path/to/photo.jpg --side left
    python scripts/identify_turtle.py --image photo.jpg --side right --bbox "100,200,300,400"
    python scripts/identify_turtle.py --image photo.jpg --side top --top-k 10
"""

import argparse
import sys
import os

# Ensure ai-core root is on the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.config.data_config import BIOLOGICAL_SIDES, IDENTIFICATION_THRESHOLD, TOP_K_RESULTS
from src.identification.identifier import TurtleIdentifier


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for the identifier."""
    parser = argparse.ArgumentParser(
        description="Identify a sea turtle from a query image using the FAISS gallery."
    )
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Path to the query image file.",
    )
    parser.add_argument(
        "--side",
        type=str,
        required=True,
        choices=list(BIOLOGICAL_SIDES),
        help="Biological side of the turtle profile in the image (left, right, top).",
    )
    parser.add_argument(
        "--bbox",
        type=str,
        default=None,
        help='Optional bounding box "x,y,w,h" for head cropping.',
    )
    parser.add_argument(
        "--gallery",
        type=str,
        default=None,
        help="Path to the gallery index directory. Defaults to config value.",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Path to model checkpoint (.pth). Defaults to config value.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=IDENTIFICATION_THRESHOLD,
        help=f"Cosine similarity threshold for known/unknown decision (default: {IDENTIFICATION_THRESHOLD}).",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=TOP_K_RESULTS,
        help=f"Number of top matches to display (default: {TOP_K_RESULTS}).",
    )
    return parser.parse_args()


def parse_bbox_string(bbox_str: str | None) -> list[float] | None:
    """
    Converts a comma-separated bbox string to a list of floats.

    Args:
        bbox_str: String in ``"x,y,w,h"`` format, or None.

    Returns:
        A list of four floats, or None if input is None.

    Raises:
        ValueError: If the string is malformed.
    """
    if bbox_str is None:
        return None

    parts = bbox_str.split(",")
    if len(parts) != 4:
        raise ValueError(
            f"Bounding box must have 4 comma-separated values, got: '{bbox_str}'"
        )
    return [float(p.strip()) for p in parts]


def main() -> None:
    """Runs turtle identification on a single query image."""
    args = parse_arguments()

    bbox = parse_bbox_string(args.bbox)

    print("=" * 60)
    print("  SeaTurtle Photo-ID — Identification Query")
    print("=" * 60)
    print(f"  Image : {args.image}")
    print(f"  Side  : {args.side}")
    print(f"  BBox  : {bbox or 'None (full image)'}")
    print("=" * 60)

    identifier = TurtleIdentifier(
        gallery_dir=args.gallery,
        threshold=args.threshold,
        top_k=args.top_k,
    )

    result = identifier.identify(
        image_path=args.image,
        biological_side=args.side,
        bbox=bbox,
    )

    print()
    if result.is_known:
        print(f"  MATCH FOUND: {result.best_match_id}")
        print(f"  Confidence : {result.best_match_score:.4f}")
    else:
        print("  UNKNOWN INDIVIDUAL — No match above threshold.")
        if result.best_match_score > 0:
            print(f"  Closest candidate score: {result.best_match_score:.4f}")

    if result.top_k_matches:
        print(f"\n  Top-{len(result.top_k_matches)} Matches:")
        print(f"  {'Rank':<6} {'Score':<10} {'Turtle ID':<15} {'Side':<8} {'Image'}")
        print(f"  {'-'*6} {'-'*10} {'-'*15} {'-'*8} {'-'*30}")
        for rank, (score, meta) in enumerate(result.top_k_matches, start=1):
            marker = " <--" if rank == 1 and result.is_known else ""
            print(
                f"  {rank:<6} {score:<10.4f} {meta['turtle_id']:<15} "
                f"{meta['biological_side']:<8} {meta['image_path']}{marker}"
            )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
