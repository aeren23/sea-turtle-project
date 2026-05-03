"""
Evaluation metrics module for SeaTurtle Photo-ID Metric Learning.
"""

import numpy as np
from pytorch_metric_learning.utils.accuracy_calculator import AccuracyCalculator


def get_accuracy_calculator() -> AccuracyCalculator:
    """
    Initializes and returns the AccuracyCalculator for Re-Identification.
    
    We configure it to compute:
    1. precision_at_1 (Top-1 Accuracy)
    2. mean_average_precision (mAP)
    
    These are the standard metrics for evaluating Open-Set identification 
    models like face recognition or animal photo-ID.
    """
    # Exclude metrics we don't care about to save compute time
    calc = AccuracyCalculator(
        include=(
            "precision_at_1",
            "mean_average_precision"
        ),
        k=1  # We care about Top-1 for precision_at_1
    )
    return calc


def compute_top_k_accuracy(distances: np.ndarray, query_labels: np.ndarray, gallery_labels: np.ndarray, k: int = 5) -> float:
    """
    Computes Top-K accuracy given a distance matrix.
    
    Args:
        distances (np.ndarray): Shape (num_queries, num_gallery). Pairwise distances.
        query_labels (np.ndarray): Shape (num_queries,). True labels of queries.
        gallery_labels (np.ndarray): Shape (num_gallery,). True labels of gallery.
        k (int): The 'K' in Top-K.
        
    Returns:
        float: Top-K accuracy percentage (0.0 to 1.0).
    """
    num_queries = distances.shape[0]
    correct = 0
    
    # For each query, sort the gallery items by distance (ascending)
    # The closest matches are at the beginning
    sorted_indices = np.argsort(distances, axis=1)
    
    for i in range(num_queries):
        top_k_indices = sorted_indices[i, :k]
        top_k_labels = gallery_labels[top_k_indices]
        
        # If the true label is anywhere within the top K predictions, it's a hit!
        if query_labels[i] in top_k_labels:
            correct += 1
            
    return correct / num_queries if num_queries > 0 else 0.0
