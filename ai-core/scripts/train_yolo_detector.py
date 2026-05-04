"""
YOLOv8-Nano Training Script for SeaTurtle Head Detection.

Trains a YOLOv8n model on the prepared YOLO dataset with 3 classes
(head_left, head_right, head_top) for simultaneous head detection
and orientation classification.

Usage:
    python scripts/train_yolo_detector.py
    python scripts/train_yolo_detector.py --epochs 50 --batch 16
"""

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ultralytics import YOLO

from src.config.data_config import (
    YOLO_CHECKPOINT_PATH,
    YOLO_DATASET_DIR,
    YOLO_IMAGE_SIZE,
)

DEFAULT_EPOCHS = 50
DEFAULT_BATCH_SIZE = 16


def parse_args() -> argparse.Namespace:
    """Parses command-line arguments for YOLO training."""
    parser = argparse.ArgumentParser(
        description="Train YOLOv8n for sea turtle head detection."
    )
    parser.add_argument(
        "--epochs", type=int, default=DEFAULT_EPOCHS,
        help=f"Number of training epochs (default: {DEFAULT_EPOCHS}).",
    )
    parser.add_argument(
        "--batch", type=int, default=DEFAULT_BATCH_SIZE,
        help=f"Batch size (default: {DEFAULT_BATCH_SIZE}).",
    )
    parser.add_argument(
        "--resume", action="store_true",
        help="Resume training from last checkpoint.",
    )
    return parser.parse_args()


def train_yolo_detector(epochs: int, batch_size: int, resume: bool) -> None:
    """
    Trains a YOLOv8n model on the turtle head detection dataset.

    Args:
        epochs: Number of training epochs.
        batch_size: Training batch size.
        resume: Whether to resume from the last checkpoint.
    """
    dataset_yaml = YOLO_DATASET_DIR / "dataset.yaml"
    if not dataset_yaml.exists():
        raise FileNotFoundError(
            f"Dataset config not found: {dataset_yaml}\n"
            f"Run 'python scripts/prepare_yolo_dataset.py' first."
        )

    print("=" * 60)
    print("YOLOv8n Training — SeaTurtle Head Detection (3 classes)")
    print("=" * 60)
    print(f"  Dataset:    {dataset_yaml}")
    print(f"  Epochs:     {epochs}")
    print(f"  Batch size: {batch_size}")
    print(f"  Image size: {YOLO_IMAGE_SIZE}")

    model = YOLO("yolov8n.pt")

    results = model.train(
        data=str(dataset_yaml),
        epochs=epochs,
        imgsz=YOLO_IMAGE_SIZE,
        batch=batch_size,
        name="turtle_head_detector",
        project=str(YOLO_DATASET_DIR.parent.parent / "runs" / "detect"),
        exist_ok=True,
        resume=resume,
        patience=10,
        save=True,
        verbose=True,
    )

    # Copy best weights to the canonical checkpoint path
    best_weights = Path(results.save_dir) / "weights" / "best.pt"
    if best_weights.exists():
        YOLO_CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(best_weights, YOLO_CHECKPOINT_PATH)
        print(f"\nBest weights copied to: {YOLO_CHECKPOINT_PATH}")
    else:
        print("\nWARNING: best.pt not found — check training output.")

    print("Training complete.")


if __name__ == "__main__":
    args = parse_args()
    train_yolo_detector(
        epochs=args.epochs,
        batch_size=args.batch,
        resume=args.resume,
    )
