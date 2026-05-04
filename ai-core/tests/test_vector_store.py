"""
Unit tests for the TurtleVectorStore module.

Validates per-side FAISS index operations: add, search, save/load,
stats, and side validation.
"""

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from src.config.data_config import EMBEDDING_DIM, BIOLOGICAL_SIDES
from src.identification.vector_store import (
    EmbeddingMetadata,
    TurtleVectorStore,
)


def _random_unit_vector(dim: int = EMBEDDING_DIM) -> np.ndarray:
    """Generates a random L2-normalized vector."""
    vec = np.random.randn(dim).astype(np.float32)
    return vec / np.linalg.norm(vec)


def _sample_metadata(turtle_id: str, side: str) -> EmbeddingMetadata:
    """Creates a sample metadata object."""
    return EmbeddingMetadata(
        turtle_id=turtle_id,
        image_path=f"/images/{turtle_id}_{side}.jpg",
        orientation=side,
        biological_side=side,
    )


class TestTurtleVectorStoreAdd:
    """Tests for add_embedding and add_embeddings_batch."""

    def test_add_single_embedding_updates_count(self):
        store = TurtleVectorStore()
        emb = _random_unit_vector()
        meta = _sample_metadata("t001", "left")

        store.add_embedding(emb, "left", meta)

        assert store.get_stats()["left"] == 1
        assert store.get_stats()["right"] == 0
        assert store.get_stats()["top"] == 0

    def test_add_batch_embeddings(self):
        store = TurtleVectorStore()
        batch_size = 5
        embeddings = np.stack([_random_unit_vector() for _ in range(batch_size)])
        metadata_list = [_sample_metadata(f"t{i:03d}", "right") for i in range(batch_size)]

        store.add_embeddings_batch(embeddings, "right", metadata_list)

        assert store.get_stats()["right"] == batch_size

    def test_add_batch_size_mismatch_raises(self):
        store = TurtleVectorStore()
        embeddings = np.stack([_random_unit_vector() for _ in range(3)])
        metadata_list = [_sample_metadata("t001", "left")]

        with pytest.raises(ValueError, match="Batch size mismatch"):
            store.add_embeddings_batch(embeddings, "left", metadata_list)

    def test_add_invalid_side_raises(self):
        store = TurtleVectorStore()
        emb = _random_unit_vector()
        meta = _sample_metadata("t001", "bottom")

        with pytest.raises(ValueError, match="Unknown biological side"):
            store.add_embedding(emb, "bottom", meta)


class TestTurtleVectorStoreSearch:
    """Tests for the search operation."""

    def test_search_returns_correct_match(self):
        store = TurtleVectorStore()

        target = _random_unit_vector()
        store.add_embedding(target, "left", _sample_metadata("t001", "left"))

        for i in range(5):
            store.add_embedding(
                _random_unit_vector(), "left", _sample_metadata(f"noise_{i}", "left")
            )

        results = store.search(target, "left", top_k=1)

        assert len(results) == 1
        assert results[0][1]["turtle_id"] == "t001"
        assert results[0][0] > 0.99  # Self-match should be near 1.0

    def test_search_empty_index_returns_empty(self):
        store = TurtleVectorStore()
        query = _random_unit_vector()

        results = store.search(query, "left", top_k=5)

        assert results == []

    def test_search_only_queries_correct_side(self):
        store = TurtleVectorStore()

        target = _random_unit_vector()
        store.add_embedding(target, "left", _sample_metadata("t001", "left"))
        store.add_embedding(
            _random_unit_vector(), "right", _sample_metadata("t002", "right")
        )

        results = store.search(target, "left", top_k=5)

        assert len(results) == 1
        assert results[0][1]["biological_side"] == "left"

    def test_search_top_k_capped_at_index_size(self):
        store = TurtleVectorStore()
        store.add_embedding(
            _random_unit_vector(), "top", _sample_metadata("t001", "top")
        )

        results = store.search(_random_unit_vector(), "top", top_k=100)

        assert len(results) <= 1


class TestTurtleVectorStorePersistence:
    """Tests for save and load operations."""

    def test_save_and_load_preserves_data(self):
        store = TurtleVectorStore()

        left_emb = _random_unit_vector()
        right_emb = _random_unit_vector()
        store.add_embedding(left_emb, "left", _sample_metadata("t001", "left"))
        store.add_embedding(right_emb, "right", _sample_metadata("t002", "right"))

        with tempfile.TemporaryDirectory() as tmpdir:
            store.save(tmpdir)

            # Verify files exist
            for side in BIOLOGICAL_SIDES:
                assert (Path(tmpdir) / f"faiss_{side}.bin").exists()
                assert (Path(tmpdir) / f"meta_{side}.json").exists()

            # Load into a new store
            loaded_store = TurtleVectorStore()
            loaded_store.load(tmpdir)

            assert loaded_store.get_stats() == store.get_stats()

            # Verify search still works
            results = loaded_store.search(left_emb, "left", top_k=1)
            assert results[0][1]["turtle_id"] == "t001"

    def test_load_missing_file_raises(self):
        store = TurtleVectorStore()

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                store.load(tmpdir)


class TestTurtleVectorStoreStats:
    """Tests for the get_stats diagnostic method."""

    def test_stats_reflects_all_sides(self):
        store = TurtleVectorStore()

        for i in range(3):
            store.add_embedding(
                _random_unit_vector(), "left", _sample_metadata(f"t{i}", "left")
            )
        store.add_embedding(
            _random_unit_vector(), "right", _sample_metadata("t10", "right")
        )

        stats = store.get_stats()

        assert stats["left"] == 3
        assert stats["right"] == 1
        assert stats["top"] == 0
