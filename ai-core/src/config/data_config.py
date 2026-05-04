"""
Configuration module for data processing and PyTorch Dataset setup.

This module stores all constants, paths, and hyperparameters related to image
preprocessing to ensure no magic numbers exist in the main codebase.
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
