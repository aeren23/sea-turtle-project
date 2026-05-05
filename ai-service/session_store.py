"""
In-memory session store for pending turtle registrations.

When ``POST /api/v1/identify`` returns an unknown individual, the
embedding, detection metadata, and staged photo path are cached here
under a unique ``session_id``.  The client can later call
``POST /api/v1/register`` with that ``session_id`` to confirm.

Sessions expire after ``TTL_SECONDS`` (default 10 minutes) and are
cleaned up lazily on each access.  Expired staging photos are also
deleted during cleanup.
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger("ai-service.session_store")


@dataclass
class PendingRegistration:
    """Cached data for an unconfirmed turtle registration."""

    session_id: str
    embedding: np.ndarray
    biological_side: str
    bbox: list[float]
    yolo_confidence: float
    staged_photo_path: str
    original_filename: str
    created_at: float = field(default_factory=time.time)


class SessionStore:
    """
    Thread-safe in-memory store for pending registrations with TTL expiry.

    Notes:
        - Sessions are removed after successful registration or expiry.
        - A server restart clears all sessions (acceptable for MVP).
    """

    TTL_SECONDS: int = 600  # 10 minutes

    def __init__(self, ttl_seconds: int | None = None) -> None:
        self._store: dict[str, PendingRegistration] = {}
        if ttl_seconds is not None:
            self.TTL_SECONDS = ttl_seconds

    def create(
        self,
        embedding: np.ndarray,
        biological_side: str,
        bbox: list[float],
        yolo_confidence: float,
        staged_photo_path: str,
        original_filename: str,
    ) -> str:
        """
        Creates a new pending registration and returns its session_id.

        Args:
            embedding: 512-d L2-normalized embedding vector.
            biological_side: YOLO-predicted biological side.
            bbox: Head bounding box in COCO format [x, y, w, h].
            yolo_confidence: YOLO detection confidence score.
            staged_photo_path: Path to the staged photo file.
            original_filename: Original filename of the uploaded photo.

        Returns:
            A unique session_id string (UUID4).
        """
        self._cleanup_expired()

        session_id = uuid.uuid4().hex
        self._store[session_id] = PendingRegistration(
            session_id=session_id,
            embedding=embedding,
            biological_side=biological_side,
            bbox=bbox,
            yolo_confidence=yolo_confidence,
            staged_photo_path=staged_photo_path,
            original_filename=original_filename,
        )
        return session_id

    def get(self, session_id: str) -> PendingRegistration | None:
        """
        Retrieves a pending registration by session_id.

        Returns None if not found or expired.
        """
        self._cleanup_expired()
        return self._store.get(session_id)

    def remove(self, session_id: str) -> None:
        """Removes a session after successful registration."""
        self._store.pop(session_id, None)

    def _cleanup_expired(self) -> None:
        """Removes all expired sessions and their associated staging photos."""
        now = time.time()
        expired = [
            sid
            for sid, reg in self._store.items()
            if now - reg.created_at > self.TTL_SECONDS
        ]
        for sid in expired:
            reg = self._store[sid]
            if reg.staged_photo_path:
                staged = Path(reg.staged_photo_path)
                if staged.exists():
                    staged.unlink(missing_ok=True)
                    logger.debug("Cleaned expired staging photo: %s", staged.name)
            del self._store[sid]

        if expired:
            logger.info("Cleaned %d expired session(s).", len(expired))

    @property
    def pending_count(self) -> int:
        """Returns the number of active pending registrations."""
        self._cleanup_expired()
        return len(self._store)
