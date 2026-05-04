"""
Tests for the Training Components (Loss, Metrics).
"""

import os
import sys
import unittest
from pathlib import Path

import torch
import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.training.loss import get_triplet_loss_and_miner
from src.training.metrics import compute_top_k_accuracy, get_accuracy_calculator

class TestTrainingComponents(unittest.TestCase):
    
    def test_loss_and_miner(self):
        miner, loss_func = get_triplet_loss_and_miner(margin=0.2)
        
        # Simulate a batch of embeddings: 4 images, 512 dimensions each
        # Let's say labels are [0, 0, 1, 1] (2 classes, 2 images per class)
        embeddings = torch.randn(4, 512)
        labels = torch.tensor([0, 0, 1, 1])
        
        # Mine hard pairs
        hard_pairs = miner(embeddings, labels)
        
        # Compute loss
        loss = loss_func(embeddings, labels, hard_pairs)
        
        # Loss should be a valid scalar tensor
        self.assertTrue(isinstance(loss, torch.Tensor))
        self.assertFalse(torch.isnan(loss))
        self.assertEqual(loss.dim(), 0)

    def test_compute_top_k_accuracy(self):
        # Simulate distance matrix for 3 queries and 4 gallery images
        # Rows: Queries, Cols: Gallery
        distances = np.array([
            [0.1, 0.9, 0.8, 0.7],  # Query 0 closest to Gallery 0
            [0.9, 0.2, 0.8, 0.7],  # Query 1 closest to Gallery 1
            [0.9, 0.8, 0.7, 0.1],  # Query 2 closest to Gallery 3
        ])
        
        query_labels = np.array([0, 1, 2])
        gallery_labels = np.array([0, 1, 0, 2])
        
        # Top-1 Accuracy Check
        top1 = compute_top_k_accuracy(distances, query_labels, gallery_labels, k=1)
        # Query 0 -> Gallery 0 (Label 0 == 0) -> HIT
        # Query 1 -> Gallery 1 (Label 1 == 1) -> HIT
        # Query 2 -> Gallery 3 (Label 2 == 2) -> HIT
        self.assertEqual(top1, 1.0)
        
        # Let's make Query 0 miss in top 1, but hit in top 2
        distances[0] = [0.9, 0.1, 0.8, 0.7] # Closest is Gallery 1 (Label 1), second closest is Gallery 3 (Label 2)
        top1_miss = compute_top_k_accuracy(distances, query_labels, gallery_labels, k=1)
        self.assertEqual(top1_miss, 2/3) # Only Query 1 and 2 hit

if __name__ == "__main__":
    unittest.main()
