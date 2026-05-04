"""
Head Detector module for SeaTurtle Photo-ID.

Wraps a trained YOLOv8 model to detect turtle heads in raw photographs
and classify their biological side (left / right / top) in a single
forward pass. This eliminates the need for manual ``--bbox`` and
``--side`` parameters in the identification pipeline.
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from src.config.data_config import (
    YOLO_CHECKPOINT_PATH,
    YOLO_CLASS_TO_SIDE,
    YOLO_CONFIDENCE_THRESHOLD,
    YOLO_IMAGE_SIZE,
)


@dataclass
class HeadDetection:
    """Encapsulates a single detected turtle head."""

    bbox: list[float]
    biological_side: str
    confidence: float


class HeadDetector:
    """
    Detects turtle heads in raw images using a trained YOLOv8 model.

    Each detection provides a COCO-format bounding box, the predicted
    biological side, and a confidence score. Only the highest-confidence
    detection is returned by the primary ``detect`` method.
    """

    def __init__(
        self,
        checkpoint_path: str | Path | None = None,
        confidence_threshold: float = YOLO_CONFIDENCE_THRESHOLD,
        image_size: int = YOLO_IMAGE_SIZE,
    ):
        """
        Initializes the detector by loading the YOLO checkpoint.

        Args:
            checkpoint_path: Path to the trained YOLO .pt file.
            confidence_threshold: Minimum confidence to accept a detection.
            image_size: Input image size for YOLO inference.

        Raises:
            FileNotFoundError: If the checkpoint file does not exist.
        """
        from ultralytics import YOLO

        resolved_path = Path(checkpoint_path or YOLO_CHECKPOINT_PATH)
        if not resolved_path.exists():
            raise FileNotFoundError(
                f"YOLO checkpoint not found: {resolved_path}\n"
                f"Run 'python scripts/train_yolo_detector.py' first."
            )

        self.model = YOLO(str(resolved_path))
        self.confidence_threshold = confidence_threshold
        self.image_size = image_size

    def detect(self, image: np.ndarray) -> HeadDetection | None:
        """
        Detects the most confident turtle head in the given image.

        Args:
            image: Raw BGR image as a numpy array.

        Returns:
            A ``HeadDetection`` with bbox, biological_side, and confidence,
            or None if no head is detected above the confidence threshold.

        Raises:
            ValueError: If the input image is invalid.
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid input image provided to HeadDetector.")

        results = self.model.predict(
            source=image,
            imgsz=self.image_size,
            conf=self.confidence_threshold,
            verbose=False,
        )

        if not results or len(results[0].boxes) == 0:
            return None

        boxes = results[0].boxes
        best_idx = int(boxes.conf.argmax())

        return self._parse_detection(boxes, best_idx)

    def _parse_detection(self, boxes, index: int) -> HeadDetection:
        """
        Extracts a HeadDetection from YOLO result boxes at the given index.

        Args:
            boxes: YOLO Boxes object containing detection results.
            index: Index of the detection to parse.

        Returns:
            A ``HeadDetection`` instance.
        """
        xyxy = boxes.xyxy[index].cpu().numpy()
        x_min, y_min, x_max, y_max = xyxy
        bbox_coco = [
            float(x_min),
            float(y_min),
            float(x_max - x_min),
            float(y_max - y_min),
        ]

        cls_id = int(boxes.cls[index].item())
        cls_name = self.model.names.get(cls_id, "head_top")
        biological_side = YOLO_CLASS_TO_SIDE.get(cls_name, "top")

        confidence = float(boxes.conf[index].item())

        return HeadDetection(
            bbox=bbox_coco,
            biological_side=biological_side,
            confidence=confidence,
        )
