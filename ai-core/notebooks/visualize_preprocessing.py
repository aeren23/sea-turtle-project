"""
Visualization script for SeaTurtle Photo-ID preprocessing pipeline.

This script randomly selects images from the dataset and visualizes the
step-by-step transformations applied during preprocessing, saving the result
to a PNG file for inspection.
"""

import os
import sys
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np

# Add project root to path for absolute imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.dataset_parser import SeaTurtleDatasetParser
from src.preprocessing.filters import apply_clahe, correct_underwater_color, crop_image_by_bbox
from src.config.data_config import TARGET_IMAGE_SIZE


def visualize_pipeline(num_samples: int = 4, output_path: str = "preprocessing_results.png"):
    """
    Visualizes the step-by-step preprocessing of random sea turtle images.
    
    Steps visualized:
    1. Original (with BBox)
    2. Cropped Head
    3. CLAHE Enhanced
    4. Color Corrected
    5. Final Resized (224x224)
    """
    parser = SeaTurtleDatasetParser()
    dtos = parser.parse()
    
    if not dtos:
        print("No valid annotations found!")
        return
        
    # Pick random samples
    indices = np.random.choice(len(dtos), size=num_samples, replace=False)
    selected_dtos = [dtos[i] for i in indices]
    
    fig, axes = plt.subplots(num_samples, 5, figsize=(20, 4 * num_samples))
    plt.suptitle("Sea Turtle Photo-ID: Preprocessing Pipeline Verification", fontsize=16)
    
    col_titles = ["1. Original + BBox", "2. Cropped Head", "3. CLAHE Enhanced", "4. Color Corrected", "5. Final Resized"]
    for i, title in enumerate(col_titles):
        axes[0, i].set_title(title, fontsize=14)
        
    for i, dto in enumerate(selected_dtos):
        image_path_str = str(dto.file_path)
        # Use imdecode to support unicode paths on Windows (like Masaüstü)
        image = cv2.imdecode(np.fromfile(image_path_str, dtype=np.uint8), cv2.IMREAD_COLOR)
        
        if image is None:
            print(f"Failed to load image: {image_path_str}")
            continue
            
        # Convert BGR to RGB for matplotlib
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 1. Original with BBox
        img_with_bbox = img_rgb.copy()
        if dto.head_bbox:
            x, y, w, h = [int(v) for v in dto.head_bbox]
            cv2.rectangle(img_with_bbox, (x, y), (x+w, y+h), (255, 0, 0), thickness=4)
        axes[i, 0].imshow(img_with_bbox)
        axes[i, 0].text(10, 30, f"ID: {dto.identity} | {dto.orientation}", color='white', 
                        bbox=dict(facecolor='red', alpha=0.7))
        axes[i, 0].axis('off')
        
        if not dto.head_bbox:
            for j in range(1, 5):
                axes[i, j].axis('off')
            continue
            
        # 2. Cropped
        cropped_bgr = crop_image_by_bbox(image, dto.head_bbox)
        axes[i, 1].imshow(cv2.cvtColor(cropped_bgr, cv2.COLOR_BGR2RGB))
        axes[i, 1].axis('off')
        
        # 3. CLAHE
        clahe_bgr = apply_clahe(cropped_bgr)
        axes[i, 2].imshow(cv2.cvtColor(clahe_bgr, cv2.COLOR_BGR2RGB))
        axes[i, 2].axis('off')
        
        # 4. Color Corrected
        color_bgr = correct_underwater_color(clahe_bgr)
        axes[i, 3].imshow(cv2.cvtColor(color_bgr, cv2.COLOR_BGR2RGB))
        axes[i, 3].axis('off')
        
        # 5. Final Resized
        final_bgr = cv2.resize(color_bgr, TARGET_IMAGE_SIZE, interpolation=cv2.INTER_LINEAR)
        axes[i, 4].imshow(cv2.cvtColor(final_bgr, cv2.COLOR_BGR2RGB))
        axes[i, 4].axis('off')
        
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Visualize Preprocessing Pipeline")
    parser.add_argument("--samples", type=int, default=4, help="Number of samples to visualize")
    parser.add_argument("--output", type=str, default="preprocessing_results.png", help="Output file path")
    args = parser.parse_args()
    
    visualize_pipeline(num_samples=args.samples, output_path=args.output)
