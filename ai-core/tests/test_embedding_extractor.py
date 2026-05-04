"""
Unit tests for the EmbeddingExtractor module.

Validates that the extractor produces L2-normalized embeddings with
the correct shape and unit-length guarantee.
"""

import numpy as np
import pytest
import torch

from src.config.data_config import EMBEDDING_DIM


class TestEmbeddingExtractorContract:
    """
    Tests the EmbeddingExtractor output contract using a mock model.

    These tests do NOT require a real checkpoint — they validate the
    normalization and shape guarantees independently.
    """

    def test_single_embedding_shape(self):
        """Output of extract_single must be a 1-D array of EMBEDDING_DIM."""
        from src.identification.embedding_extractor import EmbeddingExtractor

        # Create a dummy checkpoint to test with
        from src.models.turtle_resnet import TurtleResNet
        import tempfile
        import os

        model = TurtleResNet(embedding_dim=EMBEDDING_DIM, pretrained=False)
        tmpdir = tempfile.mkdtemp()
        checkpoint_path = os.path.join(tmpdir, "dummy.pth")
        torch.save({"model_state_dict": model.state_dict()}, checkpoint_path)

        extractor = EmbeddingExtractor(
            checkpoint_path=checkpoint_path,
            embedding_dim=EMBEDDING_DIM,
        )

        dummy_input = torch.randn(3, 224, 224)
        embedding = extractor.extract_single(dummy_input)

        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (EMBEDDING_DIM,)

    def test_batch_embedding_shape(self):
        """Output of extract_batch must be (B, EMBEDDING_DIM)."""
        from src.identification.embedding_extractor import EmbeddingExtractor
        from src.models.turtle_resnet import TurtleResNet
        import tempfile
        import os

        model = TurtleResNet(embedding_dim=EMBEDDING_DIM, pretrained=False)
        tmpdir = tempfile.mkdtemp()
        checkpoint_path = os.path.join(tmpdir, "dummy.pth")
        torch.save({"model_state_dict": model.state_dict()}, checkpoint_path)

        extractor = EmbeddingExtractor(
            checkpoint_path=checkpoint_path,
            embedding_dim=EMBEDDING_DIM,
        )

        batch_size = 4
        dummy_batch = torch.randn(batch_size, 3, 224, 224)
        embeddings = extractor.extract_batch(dummy_batch)

        assert embeddings.shape == (batch_size, EMBEDDING_DIM)

    def test_l2_normalization_guarantee(self):
        """Every embedding vector must have L2 norm approximately equal to 1.0."""
        from src.identification.embedding_extractor import EmbeddingExtractor
        from src.models.turtle_resnet import TurtleResNet
        import tempfile
        import os

        model = TurtleResNet(embedding_dim=EMBEDDING_DIM, pretrained=False)
        tmpdir = tempfile.mkdtemp()
        checkpoint_path = os.path.join(tmpdir, "dummy.pth")
        torch.save({"model_state_dict": model.state_dict()}, checkpoint_path)

        extractor = EmbeddingExtractor(
            checkpoint_path=checkpoint_path,
            embedding_dim=EMBEDDING_DIM,
        )

        batch_size = 8
        dummy_batch = torch.randn(batch_size, 3, 224, 224)
        embeddings = extractor.extract_batch(dummy_batch)

        norms = np.linalg.norm(embeddings, axis=1)
        np.testing.assert_allclose(
            norms,
            np.ones(batch_size),
            atol=1e-5,
            err_msg="L2 normalization guarantee violated: norms are not ~1.0",
        )
