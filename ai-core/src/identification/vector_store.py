"""
FAISS-based Vector Store module for SeaTurtle Photo-ID.

This module manages a dictionary of FAISS indexes — one per biological
side (left, right, top).  Keeping the indexes separate prevents
cross-side noise during nearest-neighbour search and preserves the
biological asymmetry rule established in Phase 1.

Each index is paired with a JSON metadata file that stores per-vector
information (turtle identity, image path, orientation) since FAISS
itself only holds float32 vectors.
"""

import json
from dataclasses import dataclass, asdict
from pathlib import Path

import faiss
import numpy as np

from src.config.data_config import (
    BIOLOGICAL_SIDES,
    EMBEDDING_DIM,
    FAISS_INDEX_DIR,
    TOP_K_RESULTS,
)


@dataclass
class EmbeddingMetadata:
    """Metadata stored alongside each embedding vector in the gallery."""

    turtle_id: str
    image_path: str
    orientation: str
    biological_side: str


class TurtleVectorStore:
    """
    Manages per-side FAISS IndexFlatIP indexes and their metadata.

    Inner Product on L2-normalized vectors is equivalent to Cosine
    Similarity, so higher scores mean better matches (range 0 → 1).
    """

    def __init__(
        self,
        index_dir: str | Path | None = None,
        embedding_dim: int = EMBEDDING_DIM,
        biological_sides: tuple[str, ...] = BIOLOGICAL_SIDES,
    ):
        """
        Initializes empty FAISS indexes for each biological side.

        Args:
            index_dir: Directory where indexes and metadata are persisted.
            embedding_dim: Dimensionality of the embedding vectors.
            biological_sides: Tuple of side names that each get their own index.
        """
        self.index_dir = Path(index_dir or FAISS_INDEX_DIR)
        self.embedding_dim = embedding_dim
        self.biological_sides = biological_sides

        self._indexes: dict[str, faiss.IndexFlatIP] = {}
        self._metadata: dict[str, list[dict]] = {}

        for side in self.biological_sides:
            self._indexes[side] = faiss.IndexFlatIP(self.embedding_dim)
            self._metadata[side] = []

    # ------------------------------------------------------------------
    # Write Operations
    # ------------------------------------------------------------------

    def add_embedding(
        self,
        embedding: np.ndarray,
        biological_side: str,
        metadata: EmbeddingMetadata,
    ) -> None:
        """
        Adds a single embedding vector to the index for the given side.

        Args:
            embedding: A 1-D float32 array of shape (embedding_dim,).
            biological_side: One of the configured biological sides.
            metadata: Associated metadata for this vector.

        Raises:
            ValueError: If the biological side is not recognized.
        """
        self._validate_side(biological_side)

        vector = embedding.astype(np.float32).reshape(1, -1)
        self._indexes[biological_side].add(vector)
        self._metadata[biological_side].append(asdict(metadata))

    def add_embeddings_batch(
        self,
        embeddings: np.ndarray,
        biological_side: str,
        metadata_list: list[EmbeddingMetadata],
    ) -> None:
        """
        Adds a batch of embedding vectors to the index for the given side.

        Args:
            embeddings: A 2-D float32 array of shape (N, embedding_dim).
            biological_side: One of the configured biological sides.
            metadata_list: List of metadata objects matching each vector row.

        Raises:
            ValueError: If batch size does not match metadata list length.
        """
        self._validate_side(biological_side)

        if len(embeddings) != len(metadata_list):
            raise ValueError(
                f"Batch size mismatch: {len(embeddings)} embeddings "
                f"vs {len(metadata_list)} metadata entries."
            )

        vectors = embeddings.astype(np.float32)
        self._indexes[biological_side].add(vectors)
        self._metadata[biological_side].extend(
            [asdict(m) for m in metadata_list]
        )

    # ------------------------------------------------------------------
    # Read Operations
    # ------------------------------------------------------------------

    def search(
        self,
        query_embedding: np.ndarray,
        biological_side: str,
        top_k: int = TOP_K_RESULTS,
    ) -> list[tuple[float, dict]]:
        """
        Searches the index for the given side and returns top-K matches.

        Args:
            query_embedding: A 1-D float32 array of shape (embedding_dim,).
            biological_side: Which side's index to search.
            top_k: Number of nearest neighbours to return.

        Returns:
            A list of (score, metadata_dict) tuples sorted by descending
            similarity score.  An empty list is returned when the index
            has no vectors.

        Raises:
            ValueError: If the biological side is not recognized.
        """
        self._validate_side(biological_side)

        index = self._indexes[biological_side]
        if index.ntotal == 0:
            return []

        effective_k = min(top_k, index.ntotal)
        query = query_embedding.astype(np.float32).reshape(1, -1)
        scores, indices = index.search(query, effective_k)

        results: list[tuple[float, dict]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((float(score), self._metadata[biological_side][idx]))

        return results

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, directory: str | Path | None = None) -> None:
        """
        Persists all indexes and metadata to disk.

        Creates files like ``faiss_left.bin`` / ``meta_left.json`` for
        each biological side inside the target directory.

        Args:
            directory: Target directory.  Defaults to ``self.index_dir``.
        """
        target = Path(directory or self.index_dir)
        target.mkdir(parents=True, exist_ok=True)

        for side in self.biological_sides:
            index_path = target / f"faiss_{side}.bin"
            meta_path = target / f"meta_{side}.json"

            # Use serialize_index so Python handles file I/O.
            # faiss.write_index() internally calls C++ fopen() which
            # fails on Windows paths containing non-ASCII characters.
            index_bytes = faiss.serialize_index(self._indexes[side])
            with open(index_path, "wb") as fh:
                fh.write(index_bytes.tobytes())

            with open(meta_path, "w", encoding="utf-8") as fh:
                json.dump(self._metadata[side], fh, ensure_ascii=False, indent=2)

    def load(self, directory: str | Path | None = None) -> None:
        """
        Loads all indexes and metadata from disk.

        Args:
            directory: Source directory.  Defaults to ``self.index_dir``.

        Raises:
            FileNotFoundError: If any expected index or metadata file is missing.
        """
        source = Path(directory or self.index_dir)

        for side in self.biological_sides:
            index_path = source / f"faiss_{side}.bin"
            meta_path = source / f"meta_{side}.json"

            if not index_path.exists():
                raise FileNotFoundError(
                    f"FAISS index file not found: {index_path}"
                )
            if not meta_path.exists():
                raise FileNotFoundError(
                    f"Metadata file not found: {meta_path}"
                )

            # Mirror of save(): Python opens the file, FAISS deserializes
            # from bytes — avoids C++ fopen() Unicode path failure on Windows.
            with open(index_path, "rb") as fh:
                index_bytes = np.frombuffer(fh.read(), dtype=np.uint8)
            self._indexes[side] = faiss.deserialize_index(index_bytes)

            with open(meta_path, "r", encoding="utf-8") as fh:
                self._metadata[side] = json.load(fh)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, int]:
        """
        Returns the number of vectors stored in each side index.

        Returns:
            A dictionary mapping side name to vector count,
            e.g. ``{"left": 245, "right": 230, "top": 125}``.
        """
        return {
            side: self._indexes[side].ntotal
            for side in self.biological_sides
        }

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _validate_side(self, biological_side: str) -> None:
        """
        Raises ValueError if the given side is not in the configured set.

        Args:
            biological_side: Side string to validate.
        """
        if biological_side not in self.biological_sides:
            raise ValueError(
                f"Unknown biological side '{biological_side}'. "
                f"Expected one of {self.biological_sides}."
            )
