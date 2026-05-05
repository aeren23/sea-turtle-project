# SeaTurtle AI Service

Lightweight FastAPI microservice that wraps `TurtleInferencePipeline` (YOLO + ResNet + FAISS) behind REST endpoints for identification and registration.

## Quick Start

```bash
# 1. Install ai-core dependencies first (if not already done)
cd ../ai-core
pip install -r requirements.txt

# 2. Install ai-service dependencies
cd ../ai-service
pip install -r requirements.txt

# 3. Run the service
uvicorn main:app --host 0.0.0.0 --port 8000
```

The pipeline (YOLO + ResNet + FAISS) loads at startup (~5-10 seconds). Subsequent requests are fast.

## Endpoints

### `POST /api/v1/identify`

Upload a turtle photograph to get identification result.

```bash
curl -X POST http://localhost:8000/api/v1/identify \
  -F "file=@path/to/turtle_photo.jpg"
```

**Response:**
```json
{
  "success": true,
  "detection": {
    "bbox": [1045.27, 611.89, 258.73, 228.92],
    "biological_side": "right",
    "confidence": 0.7566
  },
  "identification": {
    "is_known": true,
    "turtle_id": "t001",
    "best_score": 0.986,
    "biological_side": "right",
    "top_k_matches": [
      {"turtle_id": "t001", "score": 0.986},
      {"turtle_id": "t001", "score": 0.7934}
    ]
  },
  "error": null
}
```

### `POST /api/v1/register`

Register an unknown turtle into the FAISS gallery. Requires a `session_id` from a prior identify call where the turtle was unknown.

```bash
curl -X POST http://localhost:8000/api/v1/register \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc123..."}'
```

**Response:**
```json
{
  "success": true,
  "turtle_id": "t501",
  "biological_side": "right",
  "message": "Turtle t501 registered successfully in faiss_right index."
}
```

### Registration Flow

```
1. POST /api/v1/identify  (upload photo)
   → Result: UNKNOWN (is_known: false, session_id: "abc123...")

2. Client shows result to user, user confirms registration

3. POST /api/v1/register  ({session_id: "abc123..."})
   → Result: {turtle_id: "t501", success: true}

4. POST /api/v1/identify  (same photo)
   → Result: KNOWN (turtle_id: "t501")
```

**Session expiry:** 10 minutes. If expired, re-identify the turtle.

### `GET /health`

Health check endpoint.

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "ok",
  "pipeline_loaded": true
}
```

## API Documentation

FastAPI auto-generates interactive docs:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Architecture

```
Client (curl / .NET backend / frontend)
    │
    POST /api/v1/identify (multipart/form-data)
    │
    ▼
┌───────────────────────────────────────────┐
│  FastAPI (ai-service/)                      │
│  • Validates upload                          │
│  • Saves to temp file                        │
│  • Calls pipeline.run()                      │
│  • Maps result → JSON                        │
│  • If UNKNOWN → caches embedding + session_id │
│  • Cleans up temp file                       │
└──────┬────────────────────────────────────┘
       │
  ▼ (imports from ai-core/)
┌─────────────────────────────┐  POST /api/v1/register
│  TurtleInferencePipeline    │  {session_id}
│  1. YOLO → head detection   │        │
│  2. Preprocess → crop+CLAHE │        ▼
│  3. ResNet → 512-d embed    │  ┌───────────────────────┐
│  4. FAISS → gallery search  │  │  Registration Flow    │
│  5. Threshold → known/unkn  │  │  1. Get cached embed  │
└─────────────────────────────┘  │  2. Generate tNNN ID  │
                                 │  3. Add to FAISS      │
                                 │  4. Save to disk      │
                                 └───────────────────────┘
```

## Supported Image Formats

`.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.webp`

**Max file size:** 20 MB
