"""
CLI entry point to build the FAISS embedding gallery from the full dataset.

Usage:
    python scripts/build_gallery.py
    python scripts/build_gallery.py --output gallery_index
    python scripts/build_gallery.py --checkpoint checkpoints/best_turtle_resnet_orientation.pth
"""

import argparse
import sys
import os

# Ensure ai-core root is on the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.identification.embedding_extractor import EmbeddingExtractor
from src.identification.gallery_builder import GalleryBuilder
from src.identification.vector_store import TurtleVectorStore


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments for the gallery builder."""
    parser = argparse.ArgumentParser(
        description="Build the FAISS embedding gallery for SeaTurtle Photo-ID."
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Path to model checkpoint (.pth). Defaults to config value.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory for FAISS index files. Defaults to config value.",
    )
    return parser.parse_args()


def main() -> None:
    """Builds the FAISS gallery from the complete turtle dataset."""
    args = parse_arguments()

    print("=" * 60)
    print("  SeaTurtle Photo-ID — Gallery Builder")
    print("=" * 60)

    extractor = EmbeddingExtractor(checkpoint_path=args.checkpoint)
    vector_store = TurtleVectorStore(index_dir=args.output)

    builder = GalleryBuilder(
        extractor=extractor,
        vector_store=vector_store,
    )

    stats = builder.build(save_directory=args.output)

    print("\n" + "=" * 60)
    print("  Gallery Build Complete")
    print("=" * 60)
    for side, count in stats.items():
        print(f"  {side.capitalize():>5} index: {count} vectors")
    print(f"  {'Total':>5}      : {sum(stats.values())} vectors")
    print("=" * 60)


if __name__ == "__main__":
    main()
