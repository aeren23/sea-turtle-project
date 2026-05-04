"""
Tests for the Deep Learning Model Architecture.
"""

import os
import sys
import unittest
from pathlib import Path

import torch

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.turtle_resnet import TurtleResNet

class TestTurtleResNet(unittest.TestCase):
    def setUp(self):
        # We test with a batch of 2 dummy images of size 224x224 (C, H, W)
        self.dummy_input = torch.randn(2, 3, 224, 224)
        # Using pretrained=False to speed up tests locally
        self.model = TurtleResNet(embedding_dim=512, pretrained=False)
        self.model.eval()

    def test_forward_pass_output_shape(self):
        with torch.no_grad():
            output = self.model(self.dummy_input)
            
        self.assertTrue(isinstance(output, torch.Tensor))
        # Batch size is 2, embedding dim is 512
        self.assertEqual(output.shape, (2, 512))

    def test_embeddings_are_l2_normalized(self):
        with torch.no_grad():
            output = self.model(self.dummy_input)
            
        # The L2 norm of each embedding vector should be 1.0 (or very close to it)
        norms = torch.norm(output, p=2, dim=1)
        for norm in norms:
            self.assertAlmostEqual(norm.item(), 1.0, places=5)

if __name__ == "__main__":
    unittest.main()
