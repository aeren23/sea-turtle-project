"""
Preprocessing pipeline module for the SeaTurtle Photo-ID project.

This module defines the main pipeline class that orchestrates the execution
of various image filters in a specific, scientifically-backed order.
"""

import cv2
import numpy as np

from src.preprocessing.filters import (
    apply_clahe,
    correct_underwater_color,
    crop_image_by_bbox,
)
from src.config.data_config import (
    TARGET_IMAGE_SIZE,
    CLAHE_CLIP_LIMIT,
    CLAHE_TILE_GRID_SIZE,
)


class TurtlePreprocessingPipeline:
    """
    Orchestrates the sequence of image processing steps applied to raw sea turtle photos.
    
    The pipeline executes the following steps in order:
    1. Cropping the region of interest (Head) using bounding boxes.
    2. Applying CLAHE for local contrast and lighting optimization.
    3. Applying underwater color correction.
    4. Resizing to the standard target dimension for CNN input.
    """

    def __init__(
        self,
        target_size: tuple[int, int] = TARGET_IMAGE_SIZE,
        clahe_clip: float = CLAHE_CLIP_LIMIT,
        clahe_tile: tuple[int, int] = CLAHE_TILE_GRID_SIZE,
    ):
        """
        Initializes the preprocessing pipeline with required hyperparameters.

        Args:
            target_size (tuple[int, int]): The desired output dimensions (width, height).
            clahe_clip (float): Clip limit for CLAHE filter.
            clahe_tile (tuple[int, int]): Grid size for CLAHE filter.
        """
        self.target_size = target_size
        self.clahe_clip = clahe_clip
        self.clahe_tile = clahe_tile

    def process(self, image: np.ndarray, bbox: list[float] | None = None) -> np.ndarray:
        """
        Executes the full preprocessing pipeline on a single image.

        Args:
            image (np.ndarray): The raw BGR input image.
            bbox (list[float] | None): Bounding box coordinates [x, y, w, h] to crop.
                                       If None, skips the cropping step.

        Returns:
            np.ndarray: The preprocessed BGR image ready for CNN ingestion.
            
        Raises:
            ValueError: If the input image is invalid.
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid input image provided to the preprocessing pipeline.")

        current_image = image

        # 1. Crop
        if bbox is not None:
            current_image = crop_image_by_bbox(current_image, bbox)

        # 2. Light & Contrast Optimization (CLAHE)
        current_image = apply_clahe(
            current_image, 
            clip_limit=self.clahe_clip, 
            tile_grid_size=self.clahe_tile
        )

        # 3. Underwater Color Correction
        current_image = correct_underwater_color(current_image)

        # 4. Standardization (Resize)
        # Using INTER_LINEAR as recommended by CV Researcher for up/down scaling consistency
        current_image = cv2.resize(current_image, self.target_size, interpolation=cv2.INTER_LINEAR)

        return current_image
