"""
Pydantic request/response models for the SeaTurtle AI Service.

Defines the API contract for the identification endpoint.
"""

from pydantic import BaseModel, Field


class DetectionResponse(BaseModel):
    """YOLO head detection output."""

    bbox: list[float] = Field(
        ..., description="Bounding box in COCO format [x, y, w, h]"
    )
    biological_side: str = Field(
        ..., description="Predicted biological side: left | right | top"
    )
    confidence: float = Field(
        ..., description="YOLO detection confidence score"
    )


class MatchItem(BaseModel):
    """A single match from the FAISS gallery."""

    turtle_id: str = Field(..., description="Matched turtle identity")
    score: float = Field(..., description="Cosine similarity score")


class IdentificationResponse(BaseModel):
    """Identification result from the FAISS gallery search."""

    is_known: bool = Field(
        ..., description="Whether the turtle is a known individual"
    )
    turtle_id: str | None = Field(
        None, description="Best match turtle ID (None if unknown)"
    )
    best_score: float = Field(
        ..., description="Highest cosine similarity score"
    )
    biological_side: str = Field(
        ..., description="Biological side used for search context"
    )
    top_k_matches: list[MatchItem] = Field(
        default_factory=list,
        description="Top-K nearest matches from the gallery",
    )


class IdentifyResponse(BaseModel):
    """Full response for POST /api/v1/identify."""

    success: bool = Field(..., description="Whether the request was processed")
    detection: DetectionResponse | None = Field(
        None, description="Head detection result (None on error)"
    )
    identification: IdentificationResponse | None = Field(
        None, description="Identification result (None on error)"
    )
    session_id: str | None = Field(
        None,
        description=(
            "Session ID for pending registration. "
            "Only returned when the turtle is UNKNOWN. "
            "Use this with POST /api/v1/register to confirm registration."
        ),
    )
    saved_photo_path: str | None = Field(
        None,
        description=(
            "Absolute path where the uploaded photo was permanently saved. "
            "Set for known turtles (images/tXXX/). None for unknown turtles "
            "until registration is confirmed."
        ),
    )
    gallery_updated: bool = Field(
        False,
        description=(
            "Whether the new photo's embedding was auto-added to the "
            "FAISS gallery. True only when a known turtle's confidence "
            "score exceeds the auto-add threshold (0.9)."
        ),
    )
    error: str | None = Field(
        None, description="Error message if any stage failed"
    )


class RegisterRequest(BaseModel):
    """Request body for POST /api/v1/register."""

    session_id: str = Field(
        ..., description="Session ID from a previous identify response"
    )


class RegisterResponse(BaseModel):
    """Response for POST /api/v1/register."""

    success: bool = Field(..., description="Whether registration succeeded")
    turtle_id: str = Field(..., description="Auto-generated turtle ID (e.g. t501)")
    biological_side: str = Field(
        ..., description="Biological side the embedding was registered under"
    )
    message: str = Field(..., description="Human-readable status message")


class HealthResponse(BaseModel):
    """Response for GET /health."""

    status: str = Field(..., description="Service status")
    pipeline_loaded: bool = Field(
        ..., description="Whether the inference pipeline is loaded"
    )
