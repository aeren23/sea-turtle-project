"""
Embedding Extractor module for SeaTurtle Photo-ID.

This module is responsible for loading a trained TurtleResNet checkpoint
and extracting L2-normalized 512-d embedding vectors from preprocessed
turtle head images. It guarantees that every output vector lies on the
unit hypersphere, which is required for FAISS IndexFlatIP (Inner Product)
to behave as Cosine Similarity.
"""

import torch
import torch.nn.functional as F
import numpy as np

from src.models.turtle_resnet import TurtleResNet
from src.config.data_config import CHECKPOINT_PATH, EMBEDDING_DIM


class EmbeddingExtractor:
    """
    Loads a trained TurtleResNet and produces L2-normalized embeddings.

    This class enforces a defensive L2 normalization step on top of the
    model's own normalization to guarantee unit-length vectors before
    they enter the FAISS index.
    """

    def __init__(
        self,
        checkpoint_path: str | None = None,
        embedding_dim: int = EMBEDDING_DIM,
        device: torch.device | None = None,
    ):
        """
        Initializes the extractor by loading the model checkpoint.

        Args:
            checkpoint_path: Path to the .pth checkpoint file.
                             Defaults to the config constant.
            embedding_dim: Dimensionality of the embedding vector.
            device: Torch device (auto-detected if None).
        """
        self.device = device or torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.embedding_dim = embedding_dim

        resolved_path = str(checkpoint_path or CHECKPOINT_PATH)

        self.model = TurtleResNet(
            embedding_dim=embedding_dim, pretrained=False
        )
        self._load_checkpoint(resolved_path)
        self.model.to(self.device)
        self.model.eval()

    def _load_checkpoint(self, checkpoint_path: str) -> None:
        """
        Loads model weights from a checkpoint file.

        Args:
            checkpoint_path: Absolute path to the .pth file.

        Raises:
            FileNotFoundError: If the checkpoint file does not exist.
        """
        checkpoint = torch.load(
            checkpoint_path, map_location=self.device, weights_only=False
        )
        self.model.load_state_dict(checkpoint["model_state_dict"])

    def extract_single(self, image_tensor: torch.Tensor) -> np.ndarray:
        """
        Extracts a single L2-normalized embedding from a preprocessed image tensor.

        Args:
            image_tensor: A tensor of shape (C, H, W) — single image,
                          already preprocessed and normalized.

        Returns:
            A 1-D numpy array of shape (embedding_dim,) on the unit hypersphere.
        """
        if image_tensor.dim() == 3:
            image_tensor = image_tensor.unsqueeze(0)

        return self.extract_batch(image_tensor)[0]

    def extract_batch(self, image_batch: torch.Tensor) -> np.ndarray:
        """
        Extracts L2-normalized embeddings for a batch of preprocessed images.

        Args:
            image_batch: A tensor of shape (B, C, H, W).

        Returns:
            A numpy array of shape (B, embedding_dim) where every row
            has unit L2 norm.
        """
        image_batch = image_batch.to(self.device)

        with torch.no_grad():
            raw_embeddings = self.model(image_batch)

            # Defensive L2 normalization — guarantees unit vectors
            # even if the model's internal normalization is ever removed
            normalized = F.normalize(raw_embeddings, p=2, dim=1)

        return normalized.cpu().numpy()
