"""
Unit tests for the TurtleInferencePipeline module.

Tests cover the end-to-end orchestration flow with mocked components
to verify correct chaining of detection, preprocessing, embedding,
and FAISS search stages.
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from src.inference.head_detector import HeadDetection
from src.inference.inference_pipeline import InferenceResult, TurtleInferencePipeline


@pytest.fixture
def mock_pipeline():
    """Creates a TurtleInferencePipeline with all dependencies mocked."""
    with patch.object(TurtleInferencePipeline, "__init__", return_value=None):
        pipe = TurtleInferencePipeline.__new__(TurtleInferencePipeline)

    pipe.head_detector = MagicMock()
    pipe.extractor = MagicMock()
    pipe.vector_store = MagicMock()
    pipe.pipeline = MagicMock()
    pipe.val_transforms = MagicMock()
    pipe.threshold = 0.6
    pipe.top_k = 5

    return pipe


class TestInferenceResult:
    """Tests for the InferenceResult dataclass."""

    def test_error_result(self):
        """InferenceResult properly stores error state."""
        result = InferenceResult(detection=None, identification=None, error="test error")
        assert result.error == "test error"
        assert result.detection is None
        assert result.identification is None


class TestPipelineRun:
    """Tests for the run method with mocked components."""

    @patch("src.inference.inference_pipeline.cv2.imdecode", return_value=None)
    @patch("src.inference.inference_pipeline.np.fromfile")
    def test_unreadable_image_returns_error(self, mock_fromfile, mock_imdecode, mock_pipeline):
        """Error returned when image cannot be loaded."""
        result = mock_pipeline.run("fake/path.jpg")

        assert result.error is not None
        assert "Could not read" in result.error

    @patch("src.inference.inference_pipeline.cv2.imdecode")
    @patch("src.inference.inference_pipeline.np.fromfile")
    def test_no_detection_returns_error(self, mock_fromfile, mock_imdecode, mock_pipeline):
        """Error returned when no head is detected."""
        mock_imdecode.return_value = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_pipeline.head_detector.detect.return_value = None

        result = mock_pipeline.run("some/image.jpg")

        assert result.error == "No turtle head detected in the image."
        assert result.detection is None

    @patch("src.inference.inference_pipeline.cv2.cvtColor")
    @patch("src.inference.inference_pipeline.cv2.imdecode")
    @patch("src.inference.inference_pipeline.np.fromfile")
    def test_successful_known_identification(
        self, mock_fromfile, mock_imdecode, mock_cvtcolor, mock_pipeline
    ):
        """Full pipeline returns known identification for good match."""
        fake_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imdecode.return_value = fake_image
        mock_cvtcolor.return_value = fake_image

        detection = HeadDetection(
            bbox=[10.0, 20.0, 100.0, 80.0],
            biological_side="left",
            confidence=0.92,
        )
        mock_pipeline.head_detector.detect.return_value = detection
        mock_pipeline.pipeline.process.return_value = fake_image

        mock_pipeline.val_transforms.return_value = {"image": MagicMock()}
        mock_pipeline.extractor.extract_single.return_value = np.random.randn(512).astype(np.float32)

        mock_pipeline.vector_store.search.side_effect = [
            [(0.85, {"turtle_id": "t042", "biological_side": "left"})],
            [(0.42, {"turtle_id": "t015", "biological_side": "right"})],
            [],
        ]

        result = mock_pipeline.run("test/photo.jpg")

        assert result.error is None
        assert result.detection.biological_side == "left"
        assert result.identification.is_known is True
        assert result.identification.best_match_id == "t042"
        assert result.identification.best_match_score == 0.85

    @patch("src.inference.inference_pipeline.cv2.cvtColor")
    @patch("src.inference.inference_pipeline.cv2.imdecode")
    @patch("src.inference.inference_pipeline.np.fromfile")
    def test_unknown_individual_below_threshold(
        self, mock_fromfile, mock_imdecode, mock_cvtcolor, mock_pipeline
    ):
        """Pipeline returns unknown when best score is below threshold."""
        fake_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imdecode.return_value = fake_image
        mock_cvtcolor.return_value = fake_image

        detection = HeadDetection(
            bbox=[5.0, 10.0, 80.0, 60.0],
            biological_side="right",
            confidence=0.88,
        )
        mock_pipeline.head_detector.detect.return_value = detection
        mock_pipeline.pipeline.process.return_value = fake_image

        mock_pipeline.val_transforms.return_value = {"image": MagicMock()}
        mock_pipeline.extractor.extract_single.return_value = np.random.randn(512).astype(np.float32)

        mock_pipeline.vector_store.search.side_effect = [
            [],
            [(0.45, {"turtle_id": "t099", "biological_side": "right"})],
            [],
        ]

        result = mock_pipeline.run("test/unknown.jpg")

        assert result.error is None
        assert result.identification.is_known is False
        assert result.identification.best_match_id is None
        assert result.identification.best_match_score == 0.45

    @patch("src.inference.inference_pipeline.cv2.imdecode")
    @patch("src.inference.inference_pipeline.np.fromfile")
    def test_preprocessing_failure_returns_error(
        self, mock_fromfile, mock_imdecode, mock_pipeline
    ):
        """Error returned when preprocessing raises ValueError."""
        mock_imdecode.return_value = np.zeros((480, 640, 3), dtype=np.uint8)

        detection = HeadDetection(
            bbox=[0.0, 0.0, 0.0, 0.0],
            biological_side="top",
            confidence=0.7,
        )
        mock_pipeline.head_detector.detect.return_value = detection
        mock_pipeline.pipeline.process.side_effect = ValueError("Bad bbox")

        result = mock_pipeline.run("test/bad.jpg")

        assert result.error is not None
        assert "Preprocessing failed" in result.error
        assert result.detection is not None

    @patch("src.inference.inference_pipeline.cv2.cvtColor")
    @patch("src.inference.inference_pipeline.cv2.imdecode")
    @patch("src.inference.inference_pipeline.np.fromfile")
    def test_empty_faiss_index_returns_unknown(
        self, mock_fromfile, mock_imdecode, mock_cvtcolor, mock_pipeline
    ):
        """Unknown returned when FAISS index has no vectors for the side."""
        fake_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imdecode.return_value = fake_image
        mock_cvtcolor.return_value = fake_image

        detection = HeadDetection(
            bbox=[10.0, 10.0, 50.0, 50.0],
            biological_side="top",
            confidence=0.9,
        )
        mock_pipeline.head_detector.detect.return_value = detection
        mock_pipeline.pipeline.process.return_value = fake_image

        mock_pipeline.val_transforms.return_value = {"image": MagicMock()}
        mock_pipeline.extractor.extract_single.return_value = np.random.randn(512).astype(np.float32)

        mock_pipeline.vector_store.search.side_effect = [[], [], []]

        result = mock_pipeline.run("test/empty_index.jpg")

        assert result.error is None
        assert result.identification.is_known is False
        assert result.identification.best_match_id is None
        assert len(result.identification.top_k_matches) == 0

    @patch("src.inference.inference_pipeline.cv2.cvtColor")
    @patch("src.inference.inference_pipeline.cv2.imdecode")
    @patch("src.inference.inference_pipeline.np.fromfile")
    def test_fallback_finds_match_in_different_index(
        self, mock_fromfile, mock_imdecode, mock_cvtcolor, mock_pipeline
    ):
        """Fallback correctly finds match even when YOLO predicts wrong side."""
        fake_image = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_imdecode.return_value = fake_image
        mock_cvtcolor.return_value = fake_image

        detection = HeadDetection(
            bbox=[10.0, 20.0, 100.0, 80.0],
            biological_side="left",
            confidence=0.45,
        )
        mock_pipeline.head_detector.detect.return_value = detection
        mock_pipeline.pipeline.process.return_value = fake_image

        mock_pipeline.val_transforms.return_value = {"image": MagicMock()}
        mock_pipeline.extractor.extract_single.return_value = np.random.randn(512).astype(np.float32)

        # YOLO said "left" but best match is in "right" index
        mock_pipeline.vector_store.search.side_effect = [
            [(0.35, {"turtle_id": "t010", "biological_side": "left"})],
            [(0.91, {"turtle_id": "t042", "biological_side": "right"})],
            [],
        ]

        result = mock_pipeline.run("test/cross_index.jpg")

        assert result.error is None
        assert result.detection.biological_side == "left"
        assert result.identification.is_known is True
        assert result.identification.best_match_id == "t042"
        assert result.identification.best_match_score == 0.91
