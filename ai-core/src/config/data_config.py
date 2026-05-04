"""
Configuration module for data processing, PyTorch Dataset setup, and
identification pipeline parameters.

This module stores all constants, paths, and hyperparameters related to image
preprocessing and turtle identification to ensure no magic numbers exist
in the main codebase.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_ROOT = PROJECT_ROOT / "archiveu" / "turtles-data" / "data"

# File Paths
ANNOTATIONS_FILE = DATA_ROOT / "annotations.json"
METADATA_SPLITS_FILE = DATA_ROOT / "metadata_splits.csv"
IMAGES_DIR = DATA_ROOT / "images"

# Preprocessing Constants
TARGET_IMAGE_SIZE = (224, 224)

# CLAHE (Contrast Limited Adaptive Histogram Equalization) Parameters
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Categories and Attributes
TARGET_CATEGORY_NAME = "head"

# ---------------------------------------------------------------------------
# Identification & FAISS Configuration
# ---------------------------------------------------------------------------

# Model Embedding Dimension (must match TurtleResNet output)
EMBEDDING_DIM = 512

# Best trained model checkpoint path
CHECKPOINT_PATH = PROJECT_ROOT / "checkpoints" / "best_turtle_resnet_orientation.pth"

# FAISS index directory — stores separate indexes per biological side
FAISS_INDEX_DIR = PROJECT_ROOT / "gallery_index"

# The three biological side groups derived from orientation mapping
BIOLOGICAL_SIDES = ("left", "right", "top")

# Cosine similarity threshold below which a match is considered "Unknown Individual"
IDENTIFICATION_THRESHOLD = 0.6

# Number of top-K results returned during identification search
TOP_K_RESULTS = 5

# ---------------------------------------------------------------------------
# YOLO Head Detector Configuration
# ---------------------------------------------------------------------------

# YOLO class names — maps class index to biological side
YOLO_CLASS_NAMES = {0: "head_left", 1: "head_right", 2: "head_top"}

# Reverse mapping: YOLO class name → biological side for FAISS index routing
YOLO_CLASS_TO_SIDE = {"head_left": "left", "head_right": "right", "head_top": "top"}

# Trained YOLO checkpoint path
YOLO_CHECKPOINT_PATH = PROJECT_ROOT / "checkpoints" / "yolo_head_detector.pt"

# YOLO dataset directory (prepared from annotations.json)
YOLO_DATASET_DIR = PROJECT_ROOT / "datasets" / "yolo_head"

# YOLO inference confidence threshold
YOLO_CONFIDENCE_THRESHOLD = 0.25

# YOLO input image size (square)
YOLO_IMAGE_SIZE = 640
