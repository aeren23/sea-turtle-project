"""
Turtle Identifier module for SeaTurtle Photo-ID.

This module provides the high-level identification service that takes
a new turtle image, extracts its embedding, and searches the FAISS
gallery for the most similar known individuals.  A configurable
similarity threshold determines whether the query turtle is a known
individual or a new / unknown one.
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import torch

from src.config.data_config import (
    FAISS_INDEX_DIR,
    IDENTIFICATION_THRESHOLD,
    TOP_K_RESULTS,
)
from src.data.augmentation import get_val_transforms
from src.identification.embedding_extractor import EmbeddingExtractor
from src.identification.vector_store import TurtleVectorStore
from src.preprocessing.pipeline import TurtlePreprocessingPipeline


@dataclass
class IdentificationResult:
    """Encapsulates the outcome of a single identification query."""

    is_known: bool
    best_match_id: str | None
    best_match_score: float
    top_k_matches: list[tuple[float, dict]]
    biological_side: str


class TurtleIdentifier:
    """
    Identifies a turtle from a query image by searching the FAISS gallery.

    The caller **must** supply the ``biological_side`` parameter so that
    only the correct FAISS index is queried.  In the future this can be
    automated with an orientation classifier model.
    """

    def __init__(
        self,
        extractor: EmbeddingExtractor | None = None,
        vector_store: TurtleVectorStore | None = None,
        pipeline: TurtlePreprocessingPipeline | None = None,
        gallery_dir: str | Path | None = None,
        threshold: float = IDENTIFICATION_THRESHOLD,
        top_k: int = TOP_K_RESULTS,
    ):
        """
        Initializes the identifier and loads the gallery from disk.

        Args:
            extractor: Pre-configured EmbeddingExtractor instance.
            vector_store: Pre-configured TurtleVectorStore instance.
            pipeline: Preprocessing pipeline instance.
            gallery_dir: Path to the saved gallery directory.
            threshold: Cosine similarity threshold for "known" classification.
            top_k: Number of nearest neighbours to retrieve.
        """
        self.extractor = extractor or EmbeddingExtractor()
        self.vector_store = vector_store or TurtleVectorStore()
        self.pipeline = pipeline or TurtlePreprocessingPipeline()
        self.val_transforms = get_val_transforms()
        self.threshold = threshold
        self.top_k = top_k

        resolved_dir = str(gallery_dir or FAISS_INDEX_DIR)
        self.vector_store.load(resolved_dir)

    def identify(
        self,
        image_path: str,
        biological_side: str,
        bbox: list[float] | None = None,
    ) -> IdentificationResult:
        """
        Identifies a turtle from a single query image.

        Args:
            image_path: Absolute path to the query image file.
            biological_side: Which profile side the image shows
                             (``"left"``, ``"right"``, or ``"top"``).
            bbox: Optional bounding box ``[x, y, w, h]`` for head cropping.
                  If None the full image is used.

        Returns:
            An ``IdentificationResult`` with the best match, score, and
            whether the individual is classified as known or unknown.

        Raises:
            IOError: If the image cannot be read.
            ValueError: If the biological side is invalid.
        """
        embedding = self._image_to_embedding(image_path, bbox)

        matches = self.vector_store.search(
            query_embedding=embedding,
            biological_side=biological_side,
            top_k=self.top_k,
        )

        if not matches:
            return IdentificationResult(
                is_known=False,
                best_match_id=None,
                best_match_score=0.0,
                top_k_matches=[],
                biological_side=biological_side,
            )

        best_score, best_meta = matches[0]
        is_known = best_score >= self.threshold

        return IdentificationResult(
            is_known=is_known,
            best_match_id=best_meta["turtle_id"] if is_known else None,
            best_match_score=best_score,
            top_k_matches=matches,
            biological_side=biological_side,
        )

    def _image_to_embedding(
        self, image_path: str, bbox: list[float] | None
    ) -> np.ndarray:
        """
        Loads, preprocesses, and extracts an embedding from an image file.

        Args:
            image_path: Path to the image file.
            bbox: Optional bounding box for head cropping.

        Returns:
            A 1-D float32 numpy array of shape (embedding_dim,).

        Raises:
            IOError: If the image cannot be loaded.
        """
        raw_image = cv2.imdecode(
            np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if raw_image is None:
            raise IOError(f"Could not read image: {image_path}")

        processed_bgr = self.pipeline.process(raw_image, bbox=bbox)
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

        augmented = self.val_transforms(image=processed_rgb)
        image_tensor: torch.Tensor = augmented["image"]

        return self.extractor.extract_single(image_tensor)
