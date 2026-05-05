"""
YOLO Dataset Preparation Script for SeaTurtle Head Detection.

Converts COCO-format annotations.json into YOLO-format label files
with 3 classes (head_left, head_right, head_top). Uses the existing
orientation-to-side mapping and metadata_splits.csv for train/val splitting.

NO images are copied. Original images stay in archiveu/.
Only label .txt files and train.txt/val.txt index files are written.
YOLO finds labels by replacing the /images/ segment with /labels/ in each path.

Output structure (datasets/yolo_head/):
    labels/train/<turtle_id>/<stem>.txt
    labels/val/<turtle_id>/<stem>.txt
    train.txt  — absolute paths to original train images
    val.txt    — absolute paths to original val images
    dataset.yaml

Usage:
    python scripts/prepare_yolo_dataset.py
"""

import csv
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config.data_config import (
    ANNOTATIONS_FILE,
    IMAGES_DIR,
    METADATA_SPLITS_FILE,
    TARGET_CATEGORY_NAME,
    YOLO_DATASET_DIR,
)

LEFT_ORIENTATIONS = {"left", "topleft"}
RIGHT_ORIENTATIONS = {"right", "topright"}

# Labels root mirrors IMAGES_DIR but under "labels/" instead of "images/"
LABELS_DIR = IMAGES_DIR.parent / "labels"


def orientation_to_class_id(orientation: str | None) -> int:
    """Maps raw orientation to YOLO class index: 0=left, 1=right, 2=top."""
    if orientation in LEFT_ORIENTATIONS:
        return 0
    elif orientation in RIGHT_ORIENTATIONS:
        return 1
    return 2


def coco_bbox_to_yolo(
    bbox: list[float], img_w: int, img_h: int
) -> tuple[float, float, float, float]:
    """Converts COCO bbox [x,y,w,h] to YOLO normalized [cx,cy,w,h]."""
    x, y, w, h = bbox
    cx = max(0.0, min(1.0, (x + w / 2.0) / img_w))
    cy = max(0.0, min(1.0, (y + h / 2.0) / img_h))
    nw = max(0.0, min(1.0, w / img_w))
    nh = max(0.0, min(1.0, h / img_h))
    return cx, cy, nw, nh


def load_splits(metadata_path: Path) -> dict[str, str]:
    """Reads metadata_splits.csv → {file_name: split}."""
    splits = {}
    with open(metadata_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            splits[row["file_name"]] = row["split_closed"]
    return splits


def resolve_image_rel_path(file_name: str) -> str:
    """
    Strips the leading 'images/' prefix from an annotation file_name
    to get the path relative to IMAGES_DIR.

    e.g. 'images/t001/foo.JPG' → 't001/foo.JPG'
    """
    if file_name.startswith("images/"):
        return file_name[len("images/"):]
    return file_name


def prepare_yolo_dataset() -> None:
    """
    Converts COCO annotations to YOLO format with train/val split.
    Images are NOT copied — only label files and index txt files are written.
    """
    print("=" * 60)
    print("YOLO Dataset Preparation — SeaTurtle Head Detection")
    print("(No image copying — labels written alongside originals)")
    print("=" * 60)

    with open(ANNOTATIONS_FILE, "r", encoding="utf-8") as f:
        coco = json.load(f)

    split_map = load_splits(METADATA_SPLITS_FILE)

    head_cat_id = None
    for cat in coco.get("categories", []):
        if cat["name"] == TARGET_CATEGORY_NAME:
            head_cat_id = cat["id"]
            break
    if head_cat_id is None:
        raise ValueError(f"Category '{TARGET_CATEGORY_NAME}' not found.")

    img_lookup = {}
    for img in coco.get("images", []):
        img_lookup[img["id"]] = {
            "file_name": img["file_name"],
            "width": img["width"],
            "height": img["height"],
        }

    # Clean and recreate only the YOLO index directory (no images subdir)
    if YOLO_DATASET_DIR.exists():
        shutil.rmtree(YOLO_DATASET_DIR)
    YOLO_DATASET_DIR.mkdir(parents=True)

    # Group annotations by image_id
    ann_by_image: dict[int, list[dict]] = {}
    for ann in coco.get("annotations", []):
        if ann["category_id"] != head_cat_id:
            continue
        ann_by_image.setdefault(ann["image_id"], []).append(ann)

    stats = {"train": 0, "val": 0, "skipped": 0}
    class_counts = {0: 0, 1: 0, 2: 0}
    index_lines: dict[str, list[str]] = {"train": [], "val": []}

    for image_id, anns in ann_by_image.items():
        img_info = img_lookup.get(image_id)
        if not img_info:
            stats["skipped"] += 1
            continue

        file_name = img_info["file_name"]
        if file_name not in split_map:
            stats["skipped"] += 1
            continue

        raw_split = split_map[file_name]
        # "test" fold → treat as val (no separate test set for YOLO training)
        if raw_split in ("train", "val"):
            subset = raw_split
        else:
            subset = "val"

        rel_path = resolve_image_rel_path(file_name)
        src_image = IMAGES_DIR / rel_path

        if not src_image.exists():
            stats["skipped"] += 1
            continue

        # --- Write YOLO label file ---
        # YOLO derives label path from image path by replacing /images/ → /labels/
        # so label must live at LABELS_DIR / rel_path (with .txt extension)
        label_path = LABELS_DIR / Path(rel_path).parent / (Path(rel_path).stem + ".txt")
        label_path.parent.mkdir(parents=True, exist_ok=True)

        lines = []
        for ann in anns:
            bbox = ann.get("bbox")
            if not bbox or len(bbox) != 4:
                continue

            orientation = None
            if "attributes" in ann and "orientation" in ann["attributes"]:
                orientation = ann["attributes"]["orientation"]

            cls_id = orientation_to_class_id(orientation)
            cx, cy, nw, nh = coco_bbox_to_yolo(
                bbox, img_info["width"], img_info["height"]
            )
            lines.append(f"{cls_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
            class_counts[cls_id] += 1

        with open(label_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        # Record absolute image path for the index file
        index_lines[subset].append(str(src_image.resolve()))
        stats[subset] += 1

    # Write train.txt and val.txt index files
    for subset in ("train", "val"):
        index_path = YOLO_DATASET_DIR / f"{subset}.txt"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(index_lines[subset]))

    # Write dataset.yaml — uses txt index files, no 'path' prefix needed
    yaml_content = (
        f"train: {(YOLO_DATASET_DIR / 'train.txt').as_posix()}\n"
        f"val: {(YOLO_DATASET_DIR / 'val.txt').as_posix()}\n"
        f"\n"
        f"names:\n"
        f"  0: head_left\n"
        f"  1: head_right\n"
        f"  2: head_top\n"
    )
    yaml_path = YOLO_DATASET_DIR / "dataset.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(yaml_content)

    print(f"\nLabels written to:    {LABELS_DIR}")
    print(f"Index files at:       {YOLO_DATASET_DIR}")
    print(f"  Train images: {stats['train']}")
    print(f"  Val images:   {stats['val']}")
    print(f"  Skipped:      {stats['skipped']}")
    print(f"\nClass distribution:")
    print(f"  head_left:  {class_counts[0]}")
    print(f"  head_right: {class_counts[1]}")
    print(f"  head_top:   {class_counts[2]}")
    print(f"\ndataset.yaml written to: {yaml_path}")
    print("\nNO images were copied. Originals remain in archiveu/.")


if __name__ == "__main__":
    prepare_yolo_dataset()
