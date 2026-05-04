"""
Gallery Builder module for SeaTurtle Photo-ID.

This module orchestrates the construction of the FAISS embedding gallery
by iterating over all known turtle images, running them through the
preprocessing pipeline and embedding extractor, and inserting the
resulting vectors into the correct per-side FAISS index.
"""

import cv2
import numpy as np
import torch
from tqdm import tqdm

from src.config.data_config import FAISS_INDEX_DIR
from src.data.dataset_parser import SeaTurtleDatasetParser, TurtleImageDTO
from src.data.augmentation import get_val_transforms
from src.identification.embedding_extractor import EmbeddingExtractor
from src.identification.vector_store import (
    EmbeddingMetadata,
    TurtleVectorStore,
)
from src.preprocessing.pipeline import TurtlePreprocessingPipeline


class GalleryBuilder:
    """
    Builds the FAISS embedding gallery from the full turtle dataset.

    For every annotated turtle head image the builder:
    1. Loads the raw image from disk.
    2. Applies the OpenCV preprocessing pipeline (crop, CLAHE, color correct, resize).
    3. Converts to a normalized tensor via validation transforms.
    4. Extracts a 512-d L2-normalized embedding.
    5. Inserts the embedding into the correct biological-side FAISS index.
    """

    def __init__(
        self,
        extractor: EmbeddingExtractor | None = None,
        vector_store: TurtleVectorStore | None = None,
        parser: SeaTurtleDatasetParser | None = None,
        pipeline: TurtlePreprocessingPipeline | None = None,
    ):
        """
        Initializes the gallery builder with injectable dependencies.

        Args:
            extractor: Pre-configured EmbeddingExtractor instance.
            vector_store: Pre-configured TurtleVectorStore instance.
            parser: Dataset parser. Defaults to a new instance.
            pipeline: Preprocessing pipeline. Defaults to a new instance.
        """
        self.extractor = extractor or EmbeddingExtractor()
        self.vector_store = vector_store or TurtleVectorStore()
        self.parser = parser or SeaTurtleDatasetParser()
        self.pipeline = pipeline or TurtlePreprocessingPipeline()
        self.val_transforms = get_val_transforms()

    def build(self, save_directory: str | None = None) -> dict[str, int]:
        """
        Processes the full dataset and builds the gallery indexes.

        Args:
            save_directory: Where to persist the FAISS files.
                            Defaults to ``FAISS_INDEX_DIR`` from config.

        Returns:
            A stats dictionary mapping each biological side to its
            vector count, e.g. ``{"left": 245, "right": 230, "top": 125}``.
        """
        all_dtos = self.parser.parse()
        skipped_count = 0

        print(f"Gallery Builder: Processing {len(all_dtos)} annotated images...")

        for dto in tqdm(all_dtos, desc="Building gallery"):
            try:
                embedding, side = self._process_single_dto(dto)
            except (IOError, ValueError) as exc:
                skipped_count += 1
                tqdm.write(f"  Skipped {dto.file_path}: {exc}")
                continue

            # Extract the base turtle identity (without the side suffix)
            base_identity = self._extract_base_identity(dto.identity)

            metadata = EmbeddingMetadata(
                turtle_id=base_identity,
                image_path=str(dto.file_path),
                orientation=dto.orientation or "unknown",
                biological_side=side,
            )

            self.vector_store.add_embedding(embedding, side, metadata)

        # Persist to disk
        target_dir = save_directory or str(FAISS_INDEX_DIR)
        self.vector_store.save(target_dir)

        stats = self.vector_store.get_stats()
        total = sum(stats.values())
        print(f"\nGallery built successfully!")
        print(f"  Total embeddings: {total}  |  Skipped: {skipped_count}")
        for side, count in stats.items():
            print(f"  {side.capitalize():>5}: {count} embeddings")

        return stats

    def _process_single_dto(
        self, dto: TurtleImageDTO
    ) -> tuple[np.ndarray, str]:
        """
        Loads, preprocesses, and extracts an embedding from a single DTO.

        Args:
            dto: Data transfer object with image metadata and bbox.

        Returns:
            A tuple of (embedding_array, biological_side).

        Raises:
            IOError: If the image cannot be read.
            ValueError: If preprocessing fails.
        """
        # 1. Load raw image (Unicode-safe for Windows paths)
        image_path_str = str(dto.file_path)
        raw_image = cv2.imdecode(
            np.fromfile(image_path_str, dtype=np.uint8), cv2.IMREAD_COLOR
        )
        if raw_image is None:
            raise IOError(f"Could not read image: {image_path_str}")

        # 2. OpenCV preprocessing (crop → resize → CLAHE → color correct)
        processed_bgr = self.pipeline.process(raw_image, bbox=dto.head_bbox)

        # 3. BGR → RGB
        processed_rgb = cv2.cvtColor(processed_bgr, cv2.COLOR_BGR2RGB)

        # 4. Albumentations validation transforms (Normalize + ToTensor)
        augmented = self.val_transforms(image=processed_rgb)
        image_tensor: torch.Tensor = augmented["image"]

        # 5. Extract embedding
        embedding = self.extractor.extract_single(image_tensor)

        # 6. Determine biological side from the virtual identity suffix
        side = self._extract_side_from_identity(dto.identity)

        return embedding, side

    @staticmethod
    def _extract_base_identity(virtual_identity: str) -> str:
        """
        Strips the biological side suffix from a virtual identity string.

        ``"t001_left"`` → ``"t001"``

        Args:
            virtual_identity: Identity string in ``{id}_{side}`` format.

        Returns:
            The base turtle identity without the side suffix.
        """
        parts = virtual_identity.rsplit("_", 1)
        return parts[0] if len(parts) == 2 else virtual_identity

    @staticmethod
    def _extract_side_from_identity(virtual_identity: str) -> str:
        """
        Extracts the biological side from a virtual identity string.

        ``"t001_left"`` → ``"left"``

        Args:
            virtual_identity: Identity string in ``{id}_{side}`` format.

        Returns:
            The biological side string.  Defaults to ``"top"`` if
            the format is unexpected.
        """
        parts = virtual_identity.rsplit("_", 1)
        if len(parts) == 2 and parts[1] in ("left", "right", "top"):
            return parts[1]
        return "top"
