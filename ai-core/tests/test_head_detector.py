"""
Unit tests for the HeadDetector module.

Tests cover detection output format, confidence threshold filtering,
and edge cases such as invalid images and missing checkpoints.
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import asdict

from src.inference.head_detector import HeadDetection, HeadDetector


class TestHeadDetection:
    """Tests for the HeadDetection dataclass."""

    def test_head_detection_fields(self):
        """HeadDetection stores bbox, biological_side, and confidence."""
        det = HeadDetection(
            bbox=[10.0, 20.0, 100.0, 80.0],
            biological_side="left",
            confidence=0.95,
        )
        assert det.bbox == [10.0, 20.0, 100.0, 80.0]
        assert det.biological_side == "left"
        assert det.confidence == 0.95

    def test_head_detection_serializable(self):
        """HeadDetection is serializable via asdict."""
        det = HeadDetection(
            bbox=[0.0, 0.0, 50.0, 50.0],
            biological_side="top",
            confidence=0.5,
        )
        d = asdict(det)
        assert d["biological_side"] == "top"
        assert len(d["bbox"]) == 4


class TestHeadDetectorInit:
    """Tests for HeadDetector initialization."""

    def test_missing_checkpoint_raises(self):
        """FileNotFoundError raised when checkpoint does not exist."""
        with pytest.raises(FileNotFoundError, match="YOLO checkpoint not found"):
            HeadDetector(checkpoint_path="/nonexistent/model.pt")


class TestHeadDetectorDetect:
    """Tests for the detect method using a mocked YOLO model."""

    @pytest.fixture
    def mock_detector(self):
        """Creates a HeadDetector with a mocked YOLO model."""
        with patch("src.inference.head_detector.HeadDetector.__init__", return_value=None):
            detector = HeadDetector.__new__(HeadDetector)

        detector.confidence_threshold = 0.25
        detector.image_size = 640

        mock_model = MagicMock()
        mock_model.names = {0: "head_left", 1: "head_right", 2: "head_top"}
        detector.model = mock_model

        return detector

    def test_detect_returns_none_on_no_results(self, mock_detector):
        """Returns None when YOLO detects nothing."""
        mock_result = MagicMock()
        mock_result.boxes = MagicMock()
        mock_result.boxes.__len__ = lambda self: 0
        mock_detector.model.predict.return_value = [mock_result]

        image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = mock_detector.detect(image)

        assert result is None

    def test_detect_invalid_image_raises(self, mock_detector):
        """ValueError raised for empty images."""
        with pytest.raises(ValueError, match="Invalid input image"):
            mock_detector.detect(np.array([]))

    def test_detect_invalid_none_raises(self, mock_detector):
        """ValueError raised for None input."""
        with pytest.raises(ValueError, match="Invalid input image"):
            mock_detector.detect(None)
