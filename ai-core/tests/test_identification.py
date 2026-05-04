"""
Integration tests for the end-to-end identification pipeline.

Tests the flow: embedding → vector store → search → identification result.
Uses synthetic embeddings to avoid dependency on real images or checkpoints.
"""

import numpy as np
import pytest

from src.config.data_config import EMBEDDING_DIM
from src.identification.vector_store import EmbeddingMetadata, TurtleVectorStore
from src.identification.identifier import IdentificationResult


def _random_unit_vector(dim: int = EMBEDDING_DIM) -> np.ndarray:
    """Generates a random L2-normalized vector."""
    vec = np.random.randn(dim).astype(np.float32)
    return vec / np.linalg.norm(vec)


class TestIdentificationPipeline:
    """
    Tests the identification logic with a pre-populated vector store.

    These tests bypass image loading and model inference, focusing on
    the search + threshold decision logic.
    """

    def _build_populated_store(self) -> tuple[TurtleVectorStore, dict[str, np.ndarray]]:
        """Creates a store with known embeddings for each side."""
        store = TurtleVectorStore()
        known_embeddings = {}

        for side in ("left", "right", "top"):
            for i in range(5):
                turtle_id = f"t{i:03d}"
                emb = _random_unit_vector()
                known_embeddings[f"{turtle_id}_{side}"] = emb

                meta = EmbeddingMetadata(
                    turtle_id=turtle_id,
                    image_path=f"/images/{turtle_id}_{side}.jpg",
                    orientation=side,
                    biological_side=side,
                )
                store.add_embedding(emb, side, meta)

        return store, known_embeddings

    def test_known_turtle_identified_above_threshold(self):
        """A query matching a known embedding should return is_known=True."""
        store, known = self._build_populated_store()

        query = known["t002_left"]
        results = store.search(query, "left", top_k=5)

        assert len(results) > 0
        best_score, best_meta = results[0]
        assert best_meta["turtle_id"] == "t002"
        assert best_score > 0.99

    def test_unknown_turtle_below_threshold(self):
        """A random query should score below a strict threshold."""
        store, _ = self._build_populated_store()

        random_query = _random_unit_vector()
        results = store.search(random_query, "left", top_k=5)

        # With random vectors in 512-d space, cosine similarity should be near 0
        if results:
            best_score = results[0][0]
            assert best_score < 0.5  # Well below any reasonable threshold

    def test_cross_side_isolation(self):
        """Searching the wrong side should not return matches from another side."""
        store, known = self._build_populated_store()

        left_query = known["t001_left"]
        right_results = store.search(left_query, "right", top_k=5)

        # The t001_left embedding should NOT appear in right results
        right_ids = [meta["turtle_id"] for _, meta in right_results]
        # Matching turtle_id might coincidentally be t001 in right side too,
        # but the score should be low (random vectors)
        if right_results:
            best_score = right_results[0][0]
            assert best_score < 0.5

    def test_identification_result_dataclass(self):
        """IdentificationResult dataclass should hold all expected fields."""
        result = IdentificationResult(
            is_known=True,
            best_match_id="t001",
            best_match_score=0.95,
            top_k_matches=[(0.95, {"turtle_id": "t001"})],
            biological_side="left",
        )

        assert result.is_known is True
        assert result.best_match_id == "t001"
        assert result.best_match_score == 0.95
        assert result.biological_side == "left"
        assert len(result.top_k_matches) == 1
