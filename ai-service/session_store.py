"""
In-memory session store for pending turtle registrations.

When ``POST /api/v1/identify`` returns an unknown individual, the
embedding and detection metadata are cached here under a unique
``session_id``.  The client can later call ``POST /api/v1/register``
with that ``session_id`` to confirm registration.

Sessions expire after ``TTL_SECONDS`` (default 10 minutes) and are
cleaned up lazily on each access.
"""

import time
import uuid
from dataclasses import dataclass, field

import numpy as np


@dataclass
class PendingRegistration:
    """Cached data for an unconfirmed turtle registration."""

    session_id: str
    embedding: np.ndarray
    biological_side: str
    bbox: list[float]
    yolo_confidence: float
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
    ) -> str:
        """
        Creates a new pending registration and returns its session_id.

        Args:
            embedding: 512-d L2-normalized embedding vector.
            biological_side: YOLO-predicted biological side.
            bbox: Head bounding box in COCO format [x, y, w, h].
            yolo_confidence: YOLO detection confidence score.

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
        """Removes all sessions older than TTL_SECONDS."""
        now = time.time()
        expired = [
            sid
            for sid, reg in self._store.items()
            if now - reg.created_at > self.TTL_SECONDS
        ]
        for sid in expired:
            del self._store[sid]

    @property
    def pending_count(self) -> int:
        """Returns the number of active pending registrations."""
        self._cleanup_expired()
        return len(self._store)
