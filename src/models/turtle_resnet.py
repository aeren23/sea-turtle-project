"""
Deep Learning Model module for SeaTurtle Photo-ID.

This module defines the ResNet-50 based architecture for turtle identification.
It uses Metric Learning (generating an embedding) rather than Softmax classification,
making it suitable for open-set identification where new turtles can be added
without retraining the entire network.
"""

import torch
import torch.nn as nn
import torchvision.models as models

class TurtleResNet(nn.Module):
    """
    ResNet-50 based feature extractor for Sea Turtle Identification.
    
    Instead of outputting class probabilities, this model outputs a 
    high-dimensional embedding vector (e.g., 512-d). These embeddings 
    can be compared using distances (e.g., Cosine Similarity or L2 distance)
    to match turtles or discover new individuals.
    """

    def __init__(self, embedding_dim: int = 512, pretrained: bool = True):
        """
        Initializes the TurtleResNet model.

        Args:
            embedding_dim (int): The size of the output embedding vector.
            pretrained (bool): Whether to use ImageNet pre-trained weights.
        """
        super(TurtleResNet, self).__init__()
        
        # Load the base ResNet-50 model
        weights = models.ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
        self.backbone = models.resnet50(weights=weights)
        
        # Extract the number of features entering the original Fully Connected (FC) layer
        num_features = self.backbone.fc.in_features
        
        # Replace the original classification head with our embedding head
        self.backbone.fc = nn.Sequential(
            nn.Linear(num_features, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(1024, embedding_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the model.

        Args:
            x (torch.Tensor): Input image tensor of shape (B, 3, 224, 224).

        Returns:
            torch.Tensor: L2-normalized embedding tensor of shape (B, embedding_dim).
        """
        # Get raw embeddings from the modified ResNet
        embeddings = self.backbone(x)
        
        # L2 Normalize the embeddings (crucial for metric learning like Triplet Loss/Cosine Similarity)
        # This projects the embeddings onto a unit hypersphere
        normalized_embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        return normalized_embeddings
