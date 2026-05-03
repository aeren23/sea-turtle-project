"""
Image preprocessing filters for underwater sea turtle photographs.

This module provides pure functions for individual image processing steps
such as CLAHE, underwater color correction, and bounding box cropping.
It adheres to the Single Responsibility Principle by keeping each filter
focused on a single transformation task.
"""

import cv2
import numpy as np


def apply_clahe(image: np.ndarray, clip_limit: float = 2.0, tile_grid_size: tuple[int, int] = (8, 8)) -> np.ndarray:
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) to the L channel
    of the image in LAB color space to equalize underwater lighting variations.

    Args:
        image (np.ndarray): The input BGR image.
        clip_limit (float): Threshold for contrast limiting.
        tile_grid_size (tuple): Size of grid for histogram equalization.

    Returns:
        np.ndarray: The CLAHE-enhanced BGR image.
        
    Raises:
        ValueError: If the input image is empty or invalid.
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid input image provided to apply_clahe.")

    # Convert to LAB color space
    lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab_image)

    # Apply CLAHE to L-channel
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    cl = clahe.apply(l_channel)

    # Merge channels and convert back to BGR
    merged_lab = cv2.merge((cl, a_channel, b_channel))
    final_image = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
    
    return final_image


def correct_underwater_color(image: np.ndarray, saturation_factor: float = 1.2) -> np.ndarray:
    """
    Compensates for the blue/green color cast typical of underwater environments
    by adjusting the saturation channel in HSV color space.

    Args:
        image (np.ndarray): The input BGR image.
        saturation_factor (float): Multiplier for the saturation channel.

    Returns:
        np.ndarray: The color-corrected BGR image.
        
    Raises:
        ValueError: If the input image is empty or invalid.
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid input image provided to correct_underwater_color.")

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    
    # Adjust saturation channel
    hsv_image[:, :, 1] = hsv_image[:, :, 1] * saturation_factor
    hsv_image[:, :, 1] = np.clip(hsv_image[:, :, 1], 0, 255)
    
    hsv_image = hsv_image.astype(np.uint8)
    corrected_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    
    return corrected_image


def crop_image_by_bbox(image: np.ndarray, bbox: list[float]) -> np.ndarray:
    """
    Crops the image according to the provided COCO-format bounding box.
    COCO bbox format is [x_min, y_min, width, height].

    Args:
        image (np.ndarray): The input BGR image.
        bbox (list[float]): Bounding box coordinates [x, y, w, h].

    Returns:
        np.ndarray: The cropped region of the image.
        
    Raises:
        ValueError: If the bounding box is invalid or out of bounds.
    """
    if image is None or image.size == 0:
        raise ValueError("Invalid input image provided to crop_image_by_bbox.")
    
    if len(bbox) != 4:
        raise ValueError(f"Invalid bounding box format. Expected 4 elements, got {len(bbox)}.")

    x, y, w, h = [int(v) for v in bbox]
    img_h, img_w = image.shape[:2]

    # Validate boundaries
    x = max(0, x)
    y = max(0, y)
    w = min(w, img_w - x)
    h = min(h, img_h - y)

    if w <= 0 or h <= 0:
        raise ValueError("Bounding box dimensions must be positive and within image bounds.")

    cropped = image[y:y+h, x:x+w]
    return cropped
