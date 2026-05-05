"""
Fallback Strategy Visualization Demo.

Generates comparative figures showing:
  Case A: YOLO correctly predicts orientation → single-index would work
  Case B: YOLO mispredicts orientation → fallback saves the identification

For each case, visualizes:
  1. Original image with YOLO bbox overlay
  2. Cropped head region
  3. Preprocessed image (CLAHE + color correction)
  4. Single-index vs Fallback search results

Output: docs/reports/assets/fallback_demo/

Usage:
    python scripts/visualize_fallback_demo.py
"""

import csv
import json
import sys
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config.data_config import (
    ANNOTATIONS_FILE,
    BIOLOGICAL_SIDES,
    FAISS_INDEX_DIR,
    IMAGES_DIR,
    METADATA_SPLITS_FILE,
    YOLO_CHECKPOINT_PATH,
)
from src.data.augmentation import get_val_transforms
from src.identification.embedding_extractor import EmbeddingExtractor
from src.identification.vector_store import TurtleVectorStore
from src.inference.head_detector import HeadDetector
from src.preprocessing.pipeline import TurtlePreprocessingPipeline

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "docs" / "reports" / "assets" / "fallback_demo"


def load_annotation_sides() -> dict[str, str]:
    """Loads file_name → annotated biological side from metadata + annotations."""
    splits = {}
    with open(METADATA_SPLITS_FILE, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            splits[row["file_name"]] = row

    with open(ANNOTATIONS_FILE, "r", encoding="utf-8") as f:
        coco = json.load(f)

    img_lookup = {img["id"]: img["file_name"] for img in coco["images"]}

    LEFT_ORIENTATIONS = {"left", "topleft"}
    RIGHT_ORIENTATIONS = {"right", "topright"}

    file_to_side: dict[str, str] = {}
    for ann in coco["annotations"]:
        file_name = img_lookup.get(ann["image_id"])
        if not file_name:
            continue
        orientation = None
        if "attributes" in ann and "orientation" in ann["attributes"]:
            orientation = ann["attributes"]["orientation"]
        if orientation in LEFT_ORIENTATIONS:
            side = "left"
        elif orientation in RIGHT_ORIENTATIONS:
            side = "right"
        else:
            side = "top"
        file_to_side[file_name] = side

    return file_to_side


def find_cases(detector: HeadDetector, file_to_side: dict) -> tuple[dict, dict]:
    """
    Scans validation images to find:
      - correct_case: YOLO side == annotation side, high confidence
      - wrong_case: YOLO side != annotation side, still identifiable via fallback
    """
    correct_case = None
    wrong_case = None

    # Iterate through images looking for both cases
    for file_name, true_side in file_to_side.items():
        if correct_case and wrong_case:
            break

        rel_path = file_name
        if rel_path.startswith("images/"):
            rel_path = rel_path[len("images/"):]

        img_path = IMAGES_DIR / rel_path
        if not img_path.exists():
            continue

        image = cv2.imdecode(
            np.fromfile(str(img_path), dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if image is None:
            continue

        detection = detector.detect(image)
        if detection is None:
            continue

        predicted_side = detection.biological_side

        # Extract turtle_id from path (e.g., t001/foo.JPG → t001)
        turtle_id = rel_path.split("/")[0] if "/" in rel_path else "unknown"

        case_info = {
            "file_name": file_name,
            "img_path": str(img_path),
            "true_side": true_side,
            "predicted_side": predicted_side,
            "confidence": detection.confidence,
            "bbox": detection.bbox,
            "turtle_id": turtle_id,
        }

        if not correct_case and predicted_side == true_side and detection.confidence > 0.5:
            correct_case = case_info
            print(f"  [Correct Case] {turtle_id} — predicted={predicted_side}, true={true_side}, conf={detection.confidence:.3f}")

        if not wrong_case and predicted_side != true_side and true_side != "top":
            wrong_case = case_info
            print(f"  [Wrong Case]   {turtle_id} — predicted={predicted_side}, true={true_side}, conf={detection.confidence:.3f}")

    return correct_case, wrong_case


def run_pipeline_steps(
    img_path: str,
    bbox: list[float],
    extractor: EmbeddingExtractor,
    vector_store: TurtleVectorStore,
    preprocess: TurtlePreprocessingPipeline,
    val_transforms,
) -> dict:
    """Runs full pipeline and returns intermediate results."""
    image = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)

    # Crop
    cropped = preprocess.process(image, bbox=bbox)

    # Convert for embedding
    processed_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
    augmented = val_transforms(image=processed_rgb)
    image_tensor: torch.Tensor = augmented["image"]
    embedding = extractor.extract_single(image_tensor)

    # Single-index search (predicted side only)
    # Multi-index search (all sides)
    results_per_side = {}
    for side in BIOLOGICAL_SIDES:
        matches = vector_store.search(
            query_embedding=embedding, biological_side=side, top_k=3
        )
        results_per_side[side] = matches

    return {
        "original_bgr": image,
        "cropped_bgr": cropped,
        "processed_rgb": processed_rgb,
        "embedding": embedding,
        "results_per_side": results_per_side,
    }


def draw_case_figure(
    case_info: dict,
    pipeline_results: dict,
    title: str,
    output_filename: str,
) -> None:
    """Draws a comprehensive figure for one case."""
    original = cv2.cvtColor(pipeline_results["original_bgr"], cv2.COLOR_BGR2RGB)
    cropped = cv2.cvtColor(pipeline_results["cropped_bgr"], cv2.COLOR_BGR2RGB)
    processed = pipeline_results["processed_rgb"]

    predicted_side = case_info["predicted_side"]
    true_side = case_info["true_side"]
    confidence = case_info["confidence"]
    bbox = case_info["bbox"]
    turtle_id = case_info["turtle_id"]

    results_per_side = pipeline_results["results_per_side"]

    # Single-index result
    single_matches = results_per_side.get(predicted_side, [])
    single_top = single_matches[0] if single_matches else None

    # Fallback result (best across all sides)
    all_matches = []
    for side_matches in results_per_side.values():
        all_matches.extend(side_matches)
    all_matches.sort(key=lambda x: x[0], reverse=True)
    fallback_top = all_matches[0] if all_matches else None

    # Create figure
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle(title, fontsize=14, fontweight="bold")

    # Row 1: Visual pipeline steps
    ax1 = fig.add_subplot(2, 3, 1)
    ax1.imshow(original)
    x, y, w, h = bbox
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, linewidth=2, edgecolor="lime", facecolor="none",
        boxstyle="round,pad=0"
    )
    ax1.add_patch(rect)
    ax1.set_title(f"1. Original + YOLO BBox\nConf: {confidence:.3f}")
    ax1.axis("off")

    ax2 = fig.add_subplot(2, 3, 2)
    ax2.imshow(cropped)
    ax2.set_title("2. Cropped Head")
    ax2.axis("off")

    ax3 = fig.add_subplot(2, 3, 3)
    ax3.imshow(processed)
    ax3.set_title("3. Preprocessed\n(CLAHE + Color Correction)")
    ax3.axis("off")

    # Row 2: Search results comparison
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.axis("off")
    info_text = (
        f"YOLO Prediction: head_{predicted_side} ({confidence:.2f})\n"
        f"Actual Side (annotation): {true_side}\n"
        f"Turtle ID: {turtle_id}\n"
        f"Match: {'✓ Correct' if predicted_side == true_side else '✗ Wrong orientation'}"
    )
    ax4.text(0.1, 0.5, info_text, fontsize=11, verticalalignment="center",
             fontfamily="monospace", transform=ax4.transAxes,
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    ax4.set_title("4. Detection Info")

    # Single-index result
    ax5 = fig.add_subplot(2, 3, 5)
    ax5.axis("off")
    if single_top:
        single_id = single_top[1].get("turtle_id", "?")
        single_score = single_top[0]
        single_correct = single_id.split("_")[0] == turtle_id
        single_color = "lightgreen" if single_correct else "lightcoral"
        single_text = (
            f"Search: faiss_{predicted_side} only\n\n"
            f"Top Match: {single_id}\n"
            f"Score: {single_score:.4f}\n"
            f"Result: {'✓ Correct' if single_correct else '✗ Wrong match'}"
        )
    else:
        single_color = "lightcoral"
        single_text = (
            f"Search: faiss_{predicted_side} only\n\n"
            f"Top Match: None\n"
            f"Score: —\n"
            f"Result: ✗ No match found"
        )
    ax5.text(0.1, 0.5, single_text, fontsize=11, verticalalignment="center",
             fontfamily="monospace", transform=ax5.transAxes,
             bbox=dict(boxstyle="round", facecolor=single_color, alpha=0.5))
    ax5.set_title("5. Single-Index Search")

    # Fallback result
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis("off")
    if fallback_top:
        fallback_id = fallback_top[1].get("turtle_id", "?")
        fallback_score = fallback_top[0]
        fallback_correct = fallback_id.split("_")[0] == turtle_id
        fallback_color = "lightgreen" if fallback_correct else "lightcoral"
        fallback_text = (
            f"Search: ALL 3 indexes\n\n"
            f"Top Match: {fallback_id}\n"
            f"Score: {fallback_score:.4f}\n"
            f"Result: {'✓ Correct' if fallback_correct else '✗ Wrong match'}"
        )
    else:
        fallback_color = "lightcoral"
        fallback_text = (
            f"Search: ALL 3 indexes\n\n"
            f"Top Match: None\n"
            f"Score: —\n"
            f"Result: ✗ No match found"
        )
    ax6.text(0.1, 0.5, fallback_text, fontsize=11, verticalalignment="center",
             fontfamily="monospace", transform=ax6.transAxes,
             bbox=dict(boxstyle="round", facecolor=fallback_color, alpha=0.5))
    ax6.set_title("6. Fallback Search (All Indexes)")

    plt.tight_layout()
    output_path = OUTPUT_DIR / output_filename
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


def main():
    print("=" * 60)
    print("Fallback Strategy — Visual Demo Generator")
    print("=" * 60)

    # Load components
    print("\n[1/5] Loading annotation sides...")
    file_to_side = load_annotation_sides()
    print(f"  Loaded {len(file_to_side)} annotations.")

    print("\n[2/5] Loading YOLO detector...")
    detector = HeadDetector(checkpoint_path=YOLO_CHECKPOINT_PATH)

    print("\n[3/5] Finding correct + wrong orientation cases...")
    correct_case, wrong_case = find_cases(detector, file_to_side)

    if not correct_case:
        print("ERROR: Could not find a correct case.")
        return
    if not wrong_case:
        print("ERROR: Could not find a wrong orientation case.")
        return

    print("\n[4/5] Loading embedding + FAISS components...")
    extractor = EmbeddingExtractor()
    vector_store = TurtleVectorStore()
    vector_store.load(str(FAISS_INDEX_DIR))
    preprocess = TurtlePreprocessingPipeline()
    val_transforms = get_val_transforms()

    print("\n[5/5] Generating visualizations...")

    # Case A: Correct prediction
    print("\n  --- Case A: Correct Orientation ---")
    results_a = run_pipeline_steps(
        correct_case["img_path"], correct_case["bbox"],
        extractor, vector_store, preprocess, val_transforms,
    )
    draw_case_figure(
        correct_case, results_a,
        title=f"Case A: Correct Orientation — YOLO predicts '{correct_case['predicted_side']}' (actual: '{correct_case['true_side']}')",
        output_filename="case_a_correct_orientation.png",
    )

    # Case B: Wrong prediction (fallback saves)
    print("\n  --- Case B: Wrong Orientation (Fallback) ---")
    results_b = run_pipeline_steps(
        wrong_case["img_path"], wrong_case["bbox"],
        extractor, vector_store, preprocess, val_transforms,
    )
    draw_case_figure(
        wrong_case, results_b,
        title=f"Case B: Wrong Orientation — YOLO predicts '{wrong_case['predicted_side']}' (actual: '{wrong_case['true_side']}')",
        output_filename="case_b_wrong_orientation_fallback.png",
    )

    # Summary comparison figure
    print("\n  --- Summary Comparison ---")
    draw_summary(correct_case, wrong_case, results_a, results_b)

    print("\n" + "=" * 60)
    print("Done! Figures saved to:")
    print(f"  {OUTPUT_DIR}")
    print("=" * 60)


def draw_summary(case_a: dict, case_b: dict, results_a: dict, results_b: dict):
    """Draws a side-by-side summary comparison."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Fallback Strategy: Single-Index vs Multi-Index Search", fontsize=13, fontweight="bold")

    # Case A
    orig_a = cv2.cvtColor(results_a["original_bgr"], cv2.COLOR_BGR2RGB)
    axes[0].imshow(orig_a)
    x, y, w, h = case_a["bbox"]
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, linewidth=2, edgecolor="lime", facecolor="none",
        boxstyle="round,pad=0"
    )
    axes[0].add_patch(rect)
    axes[0].set_title(
        f"Case A: ✓ Correct Prediction\n"
        f"YOLO: head_{case_a['predicted_side']} ({case_a['confidence']:.2f})\n"
        f"Actual: {case_a['true_side']} | ID: {case_a['turtle_id']}",
        fontsize=10
    )
    axes[0].axis("off")

    # Case B
    orig_b = cv2.cvtColor(results_b["original_bgr"], cv2.COLOR_BGR2RGB)
    axes[1].imshow(orig_b)
    x, y, w, h = case_b["bbox"]
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h, linewidth=2, edgecolor="red", facecolor="none",
        boxstyle="round,pad=0"
    )
    axes[1].add_patch(rect)

    # Get fallback result for case B
    all_matches_b = []
    for side_matches in results_b["results_per_side"].values():
        all_matches_b.extend(side_matches)
    all_matches_b.sort(key=lambda x: x[0], reverse=True)
    fb_top = all_matches_b[0] if all_matches_b else None
    fb_text = f"{fb_top[1].get('turtle_id', '?')} ({fb_top[0]:.3f})" if fb_top else "None"

    axes[1].set_title(
        f"Case B: ✗ Wrong Prediction → Fallback Saves\n"
        f"YOLO: head_{case_b['predicted_side']} ({case_b['confidence']:.2f})\n"
        f"Actual: {case_b['true_side']} | Fallback → {fb_text}",
        fontsize=10
    )
    axes[1].axis("off")

    plt.tight_layout()
    output_path = OUTPUT_DIR / "summary_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {output_path}")


if __name__ == "__main__":
    main()
