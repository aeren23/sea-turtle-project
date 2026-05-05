"""
SeaTurtle AI Service — FastAPI Microservice.

Exposes the TurtleInferencePipeline via REST endpoints:
    POST /api/v1/identify  — Upload a turtle photo, get identification result.
    POST /api/v1/register  — Confirm registration of an unknown turtle.

The inference pipeline (YOLO + ResNet + FAISS) is loaded once at startup
and shared across all requests as a singleton.

Usage:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

import logging
import sys
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Add ai-core to Python path so we can import src.* modules directly
# ---------------------------------------------------------------------------
AI_CORE_DIR = Path(__file__).resolve().parent.parent / "ai-core"
sys.path.insert(0, str(AI_CORE_DIR))

from src.identification.vector_store import EmbeddingMetadata  # noqa: E402
from src.inference.inference_pipeline import InferenceResult, TurtleInferencePipeline  # noqa: E402

from id_generator import generate_next_turtle_id  # noqa: E402
from schemas import (  # noqa: E402
    DetectionResponse,
    HealthResponse,
    IdentificationResponse,
    IdentifyResponse,
    MatchItem,
    RegisterRequest,
    RegisterResponse,
)
from session_store import SessionStore  # noqa: E402

logger = logging.getLogger("ai-service")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}
MAX_FILE_SIZE_MB = 20


# ---------------------------------------------------------------------------
# Lifespan — load pipeline once at startup
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Loads the inference pipeline on startup, cleans up on shutdown."""
    logger.info("Loading TurtleInferencePipeline (YOLO + ResNet + FAISS)...")
    app.state.pipeline = TurtleInferencePipeline()
    app.state.sessions = SessionStore()
    logger.info("Pipeline loaded successfully.")
    yield
    logger.info("Shutting down AI Service.")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SeaTurtle AI Service",
    description="Autonomous sea turtle identification from raw photographs.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _validate_upload(file: UploadFile) -> None:
    """Validates the uploaded file type and size."""
    if file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type '{ext}'. Allowed: {ALLOWED_EXTENSIONS}",
            )


def _map_result(result: InferenceResult) -> IdentifyResponse:
    """Maps the internal InferenceResult to the API response schema."""
    if result.error:
        return IdentifyResponse(
            success=False,
            detection=None,
            identification=None,
            error=result.error,
        )

    detection = None
    if result.detection:
        detection = DetectionResponse(
            bbox=result.detection.bbox,
            biological_side=result.detection.biological_side,
            confidence=result.detection.confidence,
        )

    identification = None
    if result.identification:
        top_k = [
            MatchItem(
                turtle_id=meta.get("turtle_id", "unknown"),
                score=round(score, 4),
            )
            for score, meta in result.identification.top_k_matches
        ]
        identification = IdentificationResponse(
            is_known=result.identification.is_known,
            turtle_id=result.identification.best_match_id,
            best_score=round(result.identification.best_match_score, 4),
            biological_side=result.identification.biological_side,
            top_k_matches=top_k,
        )

    return IdentifyResponse(
        success=True,
        detection=detection,
        identification=identification,
        error=None,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.post(
    "/api/v1/identify",
    response_model=IdentifyResponse,
    summary="Identify a sea turtle from a photograph",
    description=(
        "Upload a raw turtle photograph. The service automatically detects "
        "the head, extracts an embedding, and searches the FAISS gallery "
        "for the closest known individual."
    ),
)
async def identify_turtle(file: UploadFile = File(...)):
    """Handles turtle identification from an uploaded image file."""
    _validate_upload(file)

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE_MB} MB.",
        )

    # Save to temp file (pipeline.run expects a file path)
    suffix = Path(file.filename).suffix if file.filename else ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        pipeline: TurtleInferencePipeline = app.state.pipeline
        result = pipeline.run(tmp_path)
        response = _map_result(result)

        # If unknown, cache embedding for potential registration
        if (
            response.success
            and response.identification
            and not response.identification.is_known
            and result.detection
        ):
            sessions: SessionStore = app.state.sessions
            session_id = sessions.create(
                embedding=result.embedding,
                biological_side=result.detection.biological_side,
                bbox=result.detection.bbox,
                yolo_confidence=result.detection.confidence,
            )
            response.session_id = session_id
            logger.info("Unknown turtle — session %s created.", session_id[:8])

        return response
    except Exception as exc:
        logger.exception("Unexpected error during inference.")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.post(
    "/api/v1/register",
    response_model=RegisterResponse,
    summary="Register an unknown turtle",
    description=(
        "Confirm registration of a previously identified unknown turtle. "
        "Requires the session_id returned by a prior identify call."
    ),
)
async def register_turtle(request: RegisterRequest):
    """Registers an unknown turtle into the FAISS gallery."""
    sessions: SessionStore = app.state.sessions
    pending = sessions.get(request.session_id)

    if pending is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found or expired. Please re-identify the turtle.",
        )

    try:
        pipeline: TurtleInferencePipeline = app.state.pipeline
        vector_store = pipeline.vector_store

        new_id = generate_next_turtle_id(vector_store)

        metadata = EmbeddingMetadata(
            turtle_id=new_id,
            image_path="registered_via_api",
            orientation=pending.biological_side,
            biological_side=pending.biological_side,
        )

        vector_store.add_embedding(
            embedding=pending.embedding,
            biological_side=pending.biological_side,
            metadata=metadata,
        )
        vector_store.save()

        sessions.remove(request.session_id)

        logger.info(
            "Registered new turtle %s (side=%s).",
            new_id,
            pending.biological_side,
        )

        return RegisterResponse(
            success=True,
            turtle_id=new_id,
            biological_side=pending.biological_side,
            message=f"Turtle {new_id} registered successfully in faiss_{pending.biological_side} index.",
        )
    except Exception as exc:
        logger.exception("Registration failed.")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
)
async def health_check():
    """Returns the service status and whether the pipeline is loaded."""
    pipeline_loaded = hasattr(app.state, "pipeline") and app.state.pipeline is not None
    return HealthResponse(
        status="ok" if pipeline_loaded else "degraded",
        pipeline_loaded=pipeline_loaded,
    )
