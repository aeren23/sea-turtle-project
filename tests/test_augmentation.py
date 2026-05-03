"""
Tests for the Data Augmentation pipeline.
"""

import os
import sys
import unittest
from pathlib import Path

import numpy as np
import torch

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.augmentation import get_train_transforms, get_val_transforms

class TestDataAugmentation(unittest.TestCase):
    def setUp(self):
        # Create a dummy image (H, W, C)
        self.dummy_image = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
        self.train_transform = get_train_transforms()
        self.val_transform = get_val_transforms()

    def test_train_transforms_output_shape_and_type(self):
        augmented = self.train_transform(image=self.dummy_image)
        tensor = augmented["image"]
        
        self.assertTrue(isinstance(tensor, torch.Tensor))
        # After ToTensorV2, image is (C, H, W)
        self.assertEqual(tensor.shape, (3, 224, 224))
        
        # Check if values are normalized (should roughly be in [-3, 3] range instead of [0, 255])
        self.assertTrue(tensor.min() < 0)
        self.assertTrue(tensor.max() > 0)

    def test_val_transforms_output_shape_and_type(self):
        augmented = self.val_transform(image=self.dummy_image)
        tensor = augmented["image"]
        
        self.assertTrue(isinstance(tensor, torch.Tensor))
        self.assertEqual(tensor.shape, (3, 224, 224))

if __name__ == "__main__":
    unittest.main()
