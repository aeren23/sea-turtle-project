"""
Photo storage service for the SeaTurtle AI Service.

Manages persistent photo storage in the dataset directory structure,
ensuring all uploaded images follow the existing convention:
    images/tXXX/filename.ext

Also provides a staging area for photos of unidentified turtles
that are awaiting user confirmation before registration.
"""

import logging
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("ai-service.photo_storage")


class PhotoStorageService:
    """
    Manages turtle photo persistence in the dataset directory.

    Responsibilities:
        - Save photos for known turtles to images/tXXX/
        - Stage photos for unknown turtles to images/_staging/
        - Move staged photos to permanent turtle directories on registration
        - Clean up expired staging files
    """

    def __init__(self, images_dir: Path) -> None:
        """
        Initializes the photo storage service.

        Args:
            images_dir: Base directory for turtle images
                        (e.g. ai-core/archiveu/turtles-data/data/images/).
        """
        self.images_dir = Path(images_dir)
        self.staging_dir = self.images_dir / "_staging"
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        logger.info("PhotoStorageService initialized — images_dir=%s", self.images_dir)

    def save_to_turtle(
        self,
        photo_bytes: bytes,
        turtle_id: str,
        original_filename: str,
    ) -> Path:
        """
        Saves a photo permanently to the turtle's directory.

        Creates the turtle directory if it doesn't exist.
        Generates a unique filename to prevent collisions.

        Args:
            photo_bytes: Raw image file content.
            turtle_id: Target turtle ID (e.g. "t042").
            original_filename: Original upload filename for extension detection.

        Returns:
            Absolute path to the saved file.
        """
        turtle_dir = self.images_dir / turtle_id
        turtle_dir.mkdir(parents=True, exist_ok=True)

        new_filename = self._generate_filename(original_filename)
        file_path = turtle_dir / new_filename
        file_path.write_bytes(photo_bytes)

        logger.info(
            "Saved photo for %s → %s (%d bytes)",
            turtle_id,
            file_path.name,
            len(photo_bytes),
        )
        return file_path

    def save_to_staging(
        self,
        photo_bytes: bytes,
        original_filename: str,
    ) -> Path:
        """
        Saves a photo to the staging area for unidentified turtles.

        Staged photos are temporary and will be cleaned up if the
        associated session expires without registration.

        Args:
            photo_bytes: Raw image file content.
            original_filename: Original upload filename for extension detection.

        Returns:
            Absolute path to the staged file.
        """
        staged_filename = self._generate_filename(original_filename)
        file_path = self.staging_dir / staged_filename
        file_path.write_bytes(photo_bytes)

        logger.info(
            "Staged photo → %s (%d bytes)",
            file_path.name,
            len(photo_bytes),
        )
        return file_path

    def move_from_staging(
        self,
        staged_photo_path: str,
        turtle_id: str,
    ) -> Path:
        """
        Moves a staged photo to its permanent turtle directory.

        Called during registration of a previously unknown turtle.

        Args:
            staged_photo_path: Path to the staged photo file.
            turtle_id: Newly assigned turtle ID (e.g. "t611").

        Returns:
            Absolute path to the photo in its final location.

        Raises:
            FileNotFoundError: If the staged photo no longer exists.
        """
        staged_path = Path(staged_photo_path)
        if not staged_path.exists():
            raise FileNotFoundError(
                f"Staged photo not found: {staged_path}. "
                "Session may have expired and file was cleaned up."
            )

        turtle_dir = self.images_dir / turtle_id
        turtle_dir.mkdir(parents=True, exist_ok=True)

        new_filename = self._generate_filename(staged_path.name)
        final_path = turtle_dir / new_filename
        shutil.move(str(staged_path), str(final_path))

        logger.info(
            "Moved staged photo → %s/%s",
            turtle_id,
            final_path.name,
        )
        return final_path

    def cleanup_expired_staging(self, max_age_seconds: int = 600) -> int:
        """
        Removes staged photos older than the specified age.

        Args:
            max_age_seconds: Maximum age in seconds before a staged
                             file is considered expired.

        Returns:
            Number of files removed.
        """
        if not self.staging_dir.exists():
            return 0

        now = time.time()
        removed_count = 0

        for file_path in self.staging_dir.iterdir():
            if not file_path.is_file():
                continue
            age = now - file_path.stat().st_mtime
            if age > max_age_seconds:
                file_path.unlink(missing_ok=True)
                removed_count += 1
                logger.debug("Cleaned expired staging file: %s", file_path.name)

        if removed_count > 0:
            logger.info("Cleaned %d expired staging file(s).", removed_count)

        return removed_count

    @staticmethod
    def _generate_filename(original_filename: str) -> str:
        """
        Generates a unique filename preserving the original extension.

        Format: {YYYYMMDD_HHMMSS}_{uuid_short}.{ext}

        Args:
            original_filename: Source filename for extension detection.

        Returns:
            A new unique filename string.
        """
        ext = Path(original_filename).suffix.lower() or ".jpg"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:6]
        return f"{timestamp}_{short_uuid}{ext}"
