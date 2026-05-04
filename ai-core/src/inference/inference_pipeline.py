"""
Production Inference Pipeline for SeaTurtle Photo-ID.

Orchestrates the full end-to-end flow from a raw turtle photograph
to an identification result, requiring zero manual parameters.

Flow:
    Raw Photo → HeadDetector (YOLO) → Preprocessing → EmbeddingExtractor → FAISS Search → Result
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
from src.identification.identifier import IdentificationResult
from src.identification.vector_store import TurtleVectorStore
from src.inference.head_detector import HeadDetection, HeadDetector
from src.preprocessing.pipeline import TurtlePreprocessingPipeline


@dataclass
class InferenceResult:
    """Encapsulates the full output of the inference pipeline."""

    detection: HeadDetection | None
    identification: IdentificationResult | None
    error: str | None


class TurtleInferencePipeline:
    """
    Orchestrates the autonomous identification of a turtle from a raw photo.

    This class chains the HeadDetector, TurtlePreprocessingPipeline,
    EmbeddingExtractor, and TurtleVectorStore into a single ``run``
    method that accepts only an image path and returns the full result.
    """

    def __init__(
        self,
        head_detector: HeadDetector | None = None,
        extractor: EmbeddingExtractor | None = None,
        vector_store: TurtleVectorStore | None = None,
        pipeline: TurtlePreprocessingPipeline | None = None,
        gallery_dir: str | Path | None = None,
        threshold: float = IDENTIFICATION_THRESHOLD,
        top_k: int = TOP_K_RESULTS,
    ):
        """
        Initializes the inference pipeline with injectable dependencies.

        Args:
            head_detector: Pre-configured HeadDetector instance.
            extractor: Pre-configured EmbeddingExtractor instance.
            vector_store: Pre-configured TurtleVectorStore instance.
            pipeline: Preprocessing pipeline instance.
            gallery_dir: Path to the saved FAISS gallery directory.
            threshold: Cosine similarity threshold for known/unknown decision.
            top_k: Number of top-K nearest neighbours to retrieve.
        """
        self.head_detector = head_detector or HeadDetector()
        self.extractor = extractor or EmbeddingExtractor()
        self.vector_store = vector_store or TurtleVectorStore()
        self.pipeline = pipeline or TurtlePreprocessingPipeline()
        self.val_transforms = get_val_transforms()
        self.threshold = threshold
        self.top_k = top_k

        resolved_dir = str(gallery_dir or FAISS_INDEX_DIR)
        self.vector_store.load(resolved_dir)

    def run(self, image_path: str) -> InferenceResult:
        """
        Runs the full inference pipeline on a single image.

        Args:
            image_path: Absolute path to the raw turtle photograph.

        Returns:
            An ``InferenceResult`` containing detection info, identification
            result, or an error message if any stage fails.
        """
        # 1. Load raw image
        raw_image = cv2.imdecode(
            np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if raw_image is None:
            return InferenceResult(
                detection=None,
                identification=None,
                error=f"Could not read image: {image_path}",
            )

        # 2. Detect head + orientation
        detection = self.head_detector.detect(raw_image)
        if detection is None:
            return InferenceResult(
                detection=None,
                identification=None,
                error="No turtle head detected in the image.",
            )

        # 3. Preprocess (crop → resize → CLAHE → color correct)
        try:
            processed_bgr = self.pipeline.process(
                raw_image, bbox=detection.bbox
            )
        except ValueError as exc:
            return InferenceResult(
                detection=detection,
                identification=None,
                error=f"Preprocessing failed: {exc}",
            )

        # 4. BGR → RGB → tensor
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)
        augmented = self.val_transforms(image=processed_rgb)
        image_tensor: torch.Tensor = augmented["image"]

        # 5. Extract embedding
        embedding = self.extractor.extract_single(image_tensor)

        # 6. Search the correct FAISS index
        matches = self.vector_store.search(
            query_embedding=embedding,
            biological_side=detection.biological_side,
            top_k=self.top_k,
        )

        # 7. Build identification result
        if not matches:
            identification = IdentificationResult(
                is_known=False,
                best_match_id=None,
                best_match_score=0.0,
                top_k_matches=[],
                biological_side=detection.biological_side,
            )
        else:
            best_score, best_meta = matches[0]
            is_known = best_score >= self.threshold
            identification = IdentificationResult(
                is_known=is_known,
                best_match_id=best_meta["turtle_id"] if is_known else None,
                best_match_score=best_score,
                top_k_matches=matches,
                biological_side=detection.biological_side,
            )

        return InferenceResult(
            detection=detection,
            identification=identification,
            error=None,
        )
