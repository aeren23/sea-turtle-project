# SeaTurtle Photo-ID: Project State & History

**Last Updated:** 2026-05-05

This document tracks the high-level progress, completed milestones, and current active phase of the SeaTurtle Photo-ID project. It is intended to provide immediate context to any AI Agent joining the workspace.

## 🟢 Current Phase: Phase 2.6 - Production Inference Pipeline
**Status:** In Progress

Building a fully autonomous inference pipeline that takes a raw turtle photograph and returns an identification result without any manual parameters (no `--bbox`, no `--side`).
*   **Focus:** Automatic head detection + orientation classification via YOLOv8n, end-to-end inference orchestration.
*   **Architecture:** Single YOLOv8-Nano model with 3 classes (`head_left`, `head_right`, `head_top`) performs both head detection and orientation classification in one forward pass.
*   **Completed Tasks:**
    *   `prepare_yolo_dataset.py`: Converts COCO annotations.json → YOLO format with 3 classes, using existing orientation→side mapping and metadata_splits.csv for train/val split.
    *   `train_yolo_detector.py`: YOLOv8n training script with configurable epochs/batch, auto-copies best weights to `checkpoints/yolo_head_detector.pt`.
    *   `HeadDetector` (`src/inference/head_detector.py`): YOLO model wrapper — detects head bbox + biological side + confidence from raw image.
    *   `TurtleInferencePipeline` (`src/inference/inference_pipeline.py`): Orchestrates full flow: YOLO → preprocessing → embedding → FAISS search → `IdentificationResult`.
    *   `infer_turtle.py`: CLI script — `python scripts/infer_turtle.py --image foto.jpg` (zero manual params).
    *   Config updated: `YOLO_CHECKPOINT_PATH`, `YOLO_DATASET_DIR`, `YOLO_CLASS_NAMES`, `YOLO_CLASS_TO_SIDE`, `YOLO_CONFIDENCE_THRESHOLD`, `YOLO_IMAGE_SIZE` added to `data_config.py`.
    *   `ultralytics>=8.0.0` added to `requirements.txt`.
    *   **10 unit tests** covering: HeadDetection DTO, detector init/edge cases, full pipeline orchestration (known/unknown/error/empty-index scenarios).
*   **Pending:** YOLO model training execution (requires `prepare_yolo_dataset.py` → `train_yolo_detector.py` run).

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
