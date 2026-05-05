# SeaTurtle Photo-ID: Project State & History

**Last Updated:** 2026-05-05

This document tracks the high-level progress, completed milestones, and current active phase of the SeaTurtle Photo-ID project. It is intended to provide immediate context to any AI Agent joining the workspace.

## 🟢 Current Phase: Phase 3.0 — AI Microservice (FastAPI)
**Status:** ✅ Completed

Exposed `TurtleInferencePipeline` as a standalone FastAPI microservice with REST endpoints for identification and registration.
*   **Focus:** REST API wrapper around the AI pipeline + 2-phase registration flow for unknown turtles.
*   **Architecture:** Standalone `ai-service/` module, imports `src.*` from `ai-core/` via `sys.path`. Pipeline loaded as singleton at startup.
*   **Endpoints:**
    *   `POST /api/v1/identify` — Upload photo → YOLO + ResNet + FAISS → identification result. Returns `session_id` for unknown turtles.
    *   `POST /api/v1/register` — Confirm registration of unknown turtle using `session_id`. Auto-generates `tNNN` ID, adds embedding to FAISS, saves to disk.
    *   `GET /health` — Service health check.
*   **Completed Tasks:**
    *   `ai-service/schemas.py`: Pydantic models — `DetectionResponse`, `IdentificationResponse`, `IdentifyResponse`, `RegisterRequest`, `RegisterResponse`, `HealthResponse`.
    *   `ai-service/main.py`: FastAPI app with `lifespan` startup, session management, file validation.
    *   `ai-service/session_store.py`: In-memory session cache with 10-min TTL for pending registrations.
    *   `ai-service/id_generator.py`: Auto turtle ID generator — scans FAISS metadata for max `tNNN`, returns `t(NNN+1)`.
    *   `ai-service/requirements.txt`: fastapi, uvicorn[standard], python-multipart.
    *   `ai-service/README.md`: Quick start, endpoint docs, registration flow, architecture diagram.
    *   `ai-core/src/inference/inference_pipeline.py`: Added `embedding` field to `InferenceResult` for registration caching.
*   **Test Results:**
    *   Health check: `{"status": "ok", "pipeline_loaded": true}`
    *   `POST /api/v1/identify` with t001 photo → `is_known: true`, `turtle_id: "t001"`, `best_score: 0.986`
    *   `POST /api/v1/register` with invalid session → correctly returns 404
    *   Swagger UI auto-generated at `/docs`
    *   8/8 ai-core unit tests still passing

---

## ✅ Phase 2.6 - Production Inference Pipeline (Completed)

Built a fully autonomous inference pipeline that takes a raw turtle photograph and returns an identification result without any manual parameters (no `--bbox`, no `--side`).

*   **Focus:** Automatic head detection + orientation classification via YOLOv8n, end-to-end inference orchestration.
*   **Architecture:** Single YOLOv8-Nano model with 3 classes (`head_left`, `head_right`, `head_top`) performs both head detection and orientation classification in one forward pass.
*   **Training Results (40 epochs, early stop):**
    *   **mAP50 = 0.761**, mAP50-95 = 0.595, Precision = 0.655, Recall = 0.783
    *   Head detection is strong (94–98% detection rate).
    *   `head_top` classification: 74% accurate.
    *   `head_left` ↔ `head_right` confusion: 31–42% cross-misclassification due to annotation inconsistency in source data.
    *   Full training report: `docs/reports/phase2_6_yolo_head_detection.md`
*   **Completed Tasks:**
    *   `prepare_yolo_dataset.py`: COCO → YOLO format, no image copying (labels written alongside originals).
    *   `train_yolo_detector.py`: YOLOv8n training, best weights saved to `runs/detect/turtle_head_detector/weights/best.pt`.
    *   `HeadDetector` (`src/inference/head_detector.py`): YOLO model wrapper — detects head bbox + biological side + confidence.
    *   `TurtleInferencePipeline` (`src/inference/inference_pipeline.py`): Orchestrates full flow: YOLO → preprocessing → embedding → FAISS search → `IdentificationResult`.
    *   `infer_turtle.py`: CLI script — `python scripts/infer_turtle.py --image foto.jpg` (zero manual params).
    *   Config: `YOLO_CHECKPOINT_PATH`, `YOLO_DATASET_DIR`, `YOLO_CLASS_NAMES`, `YOLO_CLASS_TO_SIDE` added to `data_config.py`.
    *   `ultralytics>=8.0.0` added to `requirements.txt`.
    *   **10 unit tests** covering HeadDetection DTO, detector init/edge cases, full pipeline orchestration.
*   **Completed Post-Training:**
    *   Fallback search strategy implemented (Option C — search all 3 FAISS indexes, return best overall match). Orientation classification noise fully absorbed.
    *   `best.pt` auto-copied to `checkpoints/yolo_head_detector.pt` by training script.
    *   End-to-end smoke test passed: t001 → 0.986 score, t042 → 0.979 score. Pipeline fully operational.
    *   8/8 unit tests passing (including new fallback cross-index test).

---

## ✅ Completed Phases

### Phase 2.5: Embedding Gallery & FAISS Vector Store
**Status:** Completed

Built the full identification pipeline that converts all preprocessed turtle images into 512-d embeddings and stores them in a FAISS-based vector database for nearest-neighbour identity matching.
*   **Focus:** Gallery construction, per-side FAISS indexing, identification service.
*   **Completed Tasks:**
    *   `EmbeddingExtractor` (`src/identification/embedding_extractor.py`): Loads trained checkpoint, extracts 512-d embeddings with defensive L2 normalization guarantee (`F.normalize`).
    *   `TurtleVectorStore` (`src/identification/vector_store.py`): Manages **3 separate FAISS `IndexFlatIP` indexes** (left, right, top) to prevent cross-side noise. Each index paired with a JSON metadata file.
    *   `GalleryBuilder` (`src/identification/gallery_builder.py`): Orchestrates full dataset → preprocess → embed → FAISS insertion pipeline with progress tracking.
    *   `TurtleIdentifier` (`src/identification/identifier.py`): Query service with configurable similarity threshold. Reports "Unknown Individual" for sub-threshold matches. Requires manual `biological_side` parameter (no auto-classifier yet).
    *   CLI scripts: `scripts/build_gallery.py` (builds 3 FAISS indexes) and `scripts/identify_turtle.py` (query with `--image` + `--side`).
    *   Config updated: `EMBEDDING_DIM`, `FAISS_INDEX_DIR`, `BIOLOGICAL_SIDES`, `IDENTIFICATION_THRESHOLD`, `TOP_K_RESULTS`, `CHECKPOINT_PATH` added to `data_config.py`.
    *   **18 unit/integration tests** all passing: vector store CRUD, L2 norm guarantee, cross-side isolation, persistence, identification pipeline.

### Phase 2: Deep Learning Implementation
**Status:** Completed

The PyTorch training pipeline for the CNN is fully built and recently refactored in **Phase A** to resolve embedding collapse and poor evaluation metrics (mAP ~2%).
*   **Focus:** Metric Learning (Open-Set Identification).
*   **Completed Tasks:**
    *   `pytorch-metric-learning` initially implemented with Triplet Margin Loss, later upgraded to **ArcFace Loss** to eliminate the need for complex hard-negative mining (like MPerClassSampler) and provide stronger decision boundaries.
    *   Virtual Identities refactored: Mapped 7 orientation types to **3 biological sides** (left, right, top) to preserve biological asymmetry while improving samples-per-class ratio.
    *   Learning Rate Scheduler (`CosineAnnealingWarmRestarts`) with linear warmup added to `train.py`.
    *   Advanced data augmentations (Scale variation, GridDistortion, GaussianBlur, CoarseDropout) implemented via Albumentations to simulate harsh underwater conditions.
    *   Full 20-Epoch training loop executed on GPU, best model saved to `checkpoints/best_turtle_resnet.pth`.
    *   OpenCV `cv::OutOfMemoryError` fixed during evaluation loop by moving Resize step earlier and optimizing memory allocations in `filters.py`.

### Phase 1: Architecture Planning & Data Pipeline
**Status:** Completed
*   **CrewAI Research:** Multi-agent system (Data Researcher, CV Researcher, DL Strategist) successfully analyzed the ~600 image dataset and recommended technical approaches.
*   **Biological Constraints Resolved:** Discovered that Sea Turtle post-ocular scales are asymmetrical. **Decision:** Banned "Horizontal Flip" from data augmentation to prevent "ghost turtle" creation.
*   **Preprocessing Pipeline:** OpenCV pipeline built (`src/preprocessing/pipeline.py`). Successfully crops BBox, applies CLAHE (illumination balance), color corrects the cyan underwater shift, and resizes to 224x224. Verified visually via `preprocessing_results.png`.
*   **Data Dataset & Parsers:** PyTorch Dataset (`src/data/turtle_dataset.py`) built. It lazily loads images, applies the OpenCV preprocessing, and converts to tensors.
*   **Data Augmentation:** Albumentations integrated (`src/data/augmentation.py`) using Rotation, Color Jitter, and Elastic Deformation.
*   **Model Backbone:** `src/models/turtle_resnet.py` built. Stripped the Softmax layer from ResNet-50 and replaced it with a 512-d L2-Normalized Embedding head for Metric Learning.

---

## ⏳ Upcoming Phases

### Phase 3: Web Platform & Backend Integration (Clean Architecture)
*   **Tech Stack:** .NET 8 RESTful API + FastAPI Python microservice.
*   **Goal:** Build the web service where users/researchers can upload photos, register new turtles, or query existing ones.
*   **Integration:** The TurtleInferencePipeline will be exposed via FastAPI as a standalone microservice that the .NET backend communicates with.

### Phase 4: Frontend Development
*   **Goal:** A visually stunning, dynamic UI for DEKAMER researchers to interact with the system.

---
**Note to AI Agents:** When undertaking new tasks, strictly adhere to the standards outlined in `docs/rules/coding_standards.md` and log your major decisions in `docs/project_log.md` using the Python `log_writer` utility.
