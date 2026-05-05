# SeaTurtle Photo-ID: Agent Context Document

> **Purpose:** This document is the single source of truth for any AI agent or developer joining this project cold. Read this first, then `state.md` for current progress. No prior conversation history is required after reading both.

---

## 1. What This Project Does

An automated **non-invasive biometric identification system** for sea turtles. Each turtle has unique post-ocular (behind-the-eye) scale patterns — like fingerprints. The system:

1. Takes a photo of a turtle's head (left / right / top profile)
2. Crops the head region, preprocesses the image (CLAHE + underwater color correction)
3. Passes it through a trained CNN → outputs a 512-d L2-normalized embedding
4. Searches a FAISS vector database to find the closest known turtle
5. Returns the turtle's identity with a confidence score, or "Unknown Individual" if below threshold

**Institution:** Pamukkale University & DEKAMER  
**Species:** Chelonia mydas, Caretta caretta

---

## 2. Monorepo Structure

```
sea-turtle-project/
├── ai-core/                  # Python AI pipeline (THIS IS THE ACTIVE MODULE)
│   ├── src/
│   │   ├── config/
│   │   │   └── data_config.py        # All constants & paths (single source of truth)
│   │   ├── data/
│   │   │   ├── dataset_parser.py     # annotations.json + CSV → TurtleImageDTO list
│   │   │   ├── turtle_dataset.py     # PyTorch Dataset (train/valid/test splits)
│   │   │   └── augmentation.py       # Albumentations transforms
│   │   ├── preprocessing/
│   │   │   ├── pipeline.py           # Orchestrates: crop → resize → CLAHE → color fix
│   │   │   └── filters.py            # Pure functions: crop_image_by_bbox, apply_clahe, correct_underwater_color
│   │   ├── models/
│   │   │   └── turtle_resnet.py      # ResNet-50 backbone → 512-d L2-normalized embedding head
│   │   ├── training/
│   │   │   ├── trainer.py            # MetricLearningTrainer (train loop, eval, checkpoint save)
│   │   │   ├── loss.py               # ArcFace loss (margin=28.6, scale=64)
│   │   │   └── metrics.py            # mAP, Top-1, Top-5 accuracy calculators
│   │   ├── identification/           # Phase 2.5 — Identification pipeline
│   │   │   ├── embedding_extractor.py  # Loads checkpoint → extracts L2-normalized embeddings
│   │   │   ├── vector_store.py         # 3 separate FAISS IndexFlatIP (left/right/top)
│   │   │   ├── gallery_builder.py      # Dataset → FAISS gallery orchestrator
│   │   │   └── identifier.py           # Query service: image + side → match result
│   │   └── inference/                # Phase 2.6 — Production Inference Pipeline
│   │       ├── head_detector.py        # YOLOv8n wrapper → bbox + biological_side + confidence
│   │       └── inference_pipeline.py   # Orchestrator: raw photo → identification result
│   ├── scripts/
│   │   ├── build_gallery.py          # CLI: build all 3 FAISS indexes from dataset
│   │   ├── identify_turtle.py        # CLI: identify a single turtle image (manual bbox+side)
│   │   ├── infer_turtle.py           # CLI: autonomous inference (no manual params)
│   │   ├── prepare_yolo_dataset.py   # COCO → YOLO format dataset converter
│   │   ├── train_yolo_detector.py    # YOLOv8n training script
│   │   └── test_gallery_demo.py      # Demo: known + unknown turtle tests
│   ├── tests/
│   │   ├── test_vector_store.py      # 11 tests — FAISS CRUD, persistence, side isolation
│   │   ├── test_embedding_extractor.py  # 3 tests — shape, L2 norm guarantee
│   │   ├── test_identification.py    # 4 tests — end-to-end pipeline
│   │   ├── test_head_detector.py     # 5 tests — detection DTO, init, edge cases
│   │   └── test_inference_pipeline.py # 8 tests — full orchestration flow + fallback
│   ├── train.py                      # Main training entry point
│   ├── checkpoints/                  # .gitignored — best_turtle_resnet_orientation.pth + yolo_head_detector.pt
│   ├── gallery_index/                # .gitignored — faiss_*.bin + meta_*.json (6 files)
│   ├── datasets/yolo_head/           # .gitignored — YOLO format dataset (images + labels + dataset.yaml)
│   └── requirements.txt
├── backend/                  # .NET 8 REST API (Phase 3 — not started)
├── ai-service/               # FastAPI Python microservice (Phase 3 — scaffolded)
├── frontend/                 # React (Phase 4 — not started)
├── agents/research_crew/     # CrewAI multi-agent research (Phase 1 — completed)
└── docs/
    ├── specifications/
    │   ├── context.md        # THIS FILE — agent briefing
    │   ├── state.md          # Phase progress tracker
    │   └── spec.md           # Original project specification
    ├── reports/              # Per-phase technical reports
    ├── rules/                # coding_standards.md, git_standards.md, logging_standards.md
    └── project_log.md        # Mandatory log — every change must be recorded here
```

---

## 3. Data Flow (End-to-End)

### Gallery Build Flow (Phase 2.5 — batch, offline)

```
annotations.json (COCO format)        metadata_splits.csv
        │                                      │
        └──────── SeaTurtleDatasetParser ──────┘
                          │
                   TurtleImageDTO
                  ┌───────────────────────────────┐
                  │ image_id, file_path            │
                  │ identity   → "t042"            │
                  │ orientation → "left"           │
                  │ head_bbox  → [x, y, w, h]      │
                  │ split      → "train"           │
                  └───────────────────────────────┘
                          │
             TurtlePreprocessingPipeline
             (crop by bbox → resize 224×224
              → CLAHE → underwater color fix)
                          │
                  albumentations normalize
                  + ToTensorV2
                          │
                   TurtleResNet (ResNet-50)
                   512-d embedding output
                          │
               F.normalize(p=2, dim=1)   ← defensive L2 norm
                          │
            ┌─────────────┼─────────────┐
            │             │             │
      faiss_left     faiss_right    faiss_top
      meta_left      meta_right     meta_top
         (IndexFlatIP — cosine similarity on unit vectors)
```

### Production Inference Flow (Phase 2.6 — autonomous, no manual params)

```
Raw Photo (any angle)
        │
   HeadDetector (YOLOv8n — 3 classes)
   ├── bbox: [x, y, w, h]        (COCO format)
   ├── side: "left"|"right"|"top" (informational only)
   └── confidence: 0.76
        │
   TurtlePreprocessingPipeline
   (crop → resize 224×224 → CLAHE → color fix)
        │
   EmbeddingExtractor (ResNet-50)
   512-d L2-normalized embedding
        │
   ┌── Fallback Strategy (MVP) ──────────────────┐
   │  Search ALL 3 FAISS indexes:                 │
   │    faiss_left → top matches                  │
   │    faiss_right → top matches                 │
   │    faiss_top → top matches                   │
   │  Sort all by score ↓ , return top_k          │
   └──────────────────────────────────────────────┘
        │
   InferenceResult
   ├── detection: HeadDetection (side = informational)
   ├── identification: IdentificationResult
   └── error: None

---

## 4. Critical Design Rules (MUST NOT VIOLATE)

| Rule | Detail | Why |
|------|--------|-----|
| **No Horizontal Flip** | Banned from all augmentations | Post-ocular scales are asymmetrical — flipping creates "ghost turtles" |
| **3 Separate FAISS Indexes** | One per biological side (left/right/top) | Left profile embedding must NOT match against right profile gallery |
| **BBox Required at Query Time** | Identifier must receive the head bounding box | Gallery was built with cropped heads — querying without bbox gives mismatched embeddings |
| **Auto Detection via YOLO** | `TurtleInferencePipeline` auto-detects bbox + side via YOLOv8n | Replaces manual `--bbox` and `--side` — `HeadDetector` handles both in one pass |
| **Fallback Multi-Index Search** | Always search all 3 FAISS indexes, return best overall match | Left/right confusion (31–42%) makes single-index unreliable; fallback cost is ~5ms |
| **L2 Norm Guarantee** | Defensive `F.normalize()` in EmbeddingExtractor | FAISS IndexFlatIP = cosine similarity only when vectors are unit-length |
| **Virtual Identity Format** | `{turtle_id}_{side}` e.g. `t042_left` | Prevents cross-side confusion in classification labels |

---

## 5. Key Configuration (`ai-core/src/config/data_config.py`)

```python
PROJECT_ROOT       = ai-core/
DATA_ROOT          = ai-core/archiveu/turtles-data/data/
ANNOTATIONS_FILE   = DATA_ROOT / "annotations.json"
METADATA_SPLITS    = DATA_ROOT / "metadata_splits.csv"
IMAGES_DIR         = DATA_ROOT / "images/"
TARGET_IMAGE_SIZE  = (224, 224)
EMBEDDING_DIM      = 512
CHECKPOINT_PATH    = PROJECT_ROOT / "checkpoints/best_turtle_resnet_orientation.pth"
FAISS_INDEX_DIR    = PROJECT_ROOT / "gallery_index/"
BIOLOGICAL_SIDES   = ("left", "right", "top")
IDENTIFICATION_THRESHOLD = 0.6     # cosine similarity — tune after gallery analysis
TOP_K_RESULTS      = 5
```

---

## 6. Orientation → Biological Side Mapping

`SeaTurtleDatasetParser._map_orientation_to_side()`:

| Raw Orientation (annotations.json) | Biological Side |
|------------------------------------|-----------------|
| `"left"`, `"topleft"` | `left` |
| `"right"`, `"topright"` | `right` |
| `"top"`, `"front"`, `"back"`, others | `top` |

---

## 7. Model Details

- **Backbone:** ResNet-50 (ImageNet pretrained)
- **Head:** `Linear(2048→1024) → BN → ReLU → Dropout(0.3) → Linear(1024→512)`
- **Output:** 512-d L2-normalized embedding vector
- **Loss:** ArcFace (margin=28.6°, scale=64) via `pytorch-metric-learning`
- **Training:** 20 epochs, CosineAnnealingWarmRestarts LR scheduler + 3-epoch warmup
- **Results:** Top-1 Accuracy **49.69%**, mAP **0.0679** (baseline was 14.05% / 0.0262)
- **Checkpoint:** `checkpoints/best_turtle_resnet_orientation.pth`

---

## 8. Gallery Statistics (Production Build)

| Index | Vectors |
|-------|---------|
| Left  | 3,906   |
| Right | 3,634   |
| Top   | 986     |
| **Total** | **8,526** |

Built from 8,526 annotated images — 0 skipped.

---

## 9. Common Commands

```bash
cd ai-core

# Train the model
python train.py

# Build the FAISS gallery (creates gallery_index/ with 6 files)
python scripts/build_gallery.py

# Autonomous inference (no manual params) — RECOMMENDED
python scripts/infer_turtle.py --image path/to/photo.jpg

# Generate fallback strategy demo visuals
python scripts/visualize_fallback_demo.py

# Run demo tests (known + unknown turtle)
python scripts/test_gallery_demo.py

# Run all tests
python -m pytest tests/ -v
```

---

## 10. Known Limitations & Future Work

| Limitation | Impact | Planned Fix |
|------------|--------|-------------|
| ~~No orientation classifier~~ | ~~User must supply `--side` manually~~ | **Resolved (Phase 2.6):** YOLOv8n auto-detects side + fallback multi-index search |
| YOLO left/right confusion (31–42%) | Orientation prediction unreliable for left↔right | Fallback search all 3 indexes absorbs noise; future fix: annotation cleanup + retrain |
| `IDENTIFICATION_THRESHOLD = 0.6` not tuned | May have false positives/negatives | Analyze similarity distribution after gallery build |
| Model accuracy at 49.69% Top-1 | ~1 in 2 new-photo queries correct | GeM Pooling, BNNeck, longer training (see `docs/future_phases.md`) |
| FAISS IndexFlatIP (exact search) | O(n) per query — scales linearly | Switch to IndexIVFFlat for large galleries |
| No re-ID for new turtles | Unknown individuals not auto-registered | Build registration flow in backend (Phase 3) |

---

## 11. Coding Standards (Summary)

Full rules: `docs/rules/coding_standards.md` and `docs/rules/logging_standards.md`

- **SOLID principles** — every class has one responsibility
- **No magic numbers** — all constants in `data_config.py`
- **Every change** must be logged in `docs/project_log.md` with the mandatory template
- **state.md** must be updated after every completed phase
- **Git standards** in `docs/rules/git_standards.md`

---

## 12. YOLO Head Detector Details

- **Model:** YOLOv8-Nano (Ultralytics), pretrained on COCO, fine-tuned 40 epochs
- **Classes:** 3 — `head_left` (0), `head_right` (1), `head_top` (2)
- **Training Data:** 8,526 images converted from `annotations.json` COCO format → YOLO format (6,822 train / 1,704 val)
- **Orientation Mapping:** Same as `_map_orientation_to_side()` — left/topleft→0, right/topright→1, rest→2
- **Results:** mAP50 = 0.761, Precision = 0.655, Recall = 0.783
- **Known Issue:** Left↔Right confusion 31–42% due to annotation inconsistency (not a model bug)
- **Mitigation:** Fallback multi-index search (always search all 3 FAISS indexes)
- **Checkpoint:** `checkpoints/yolo_head_detector.pt`
- **Confidence Threshold:** 0.25 (configurable in `data_config.py`)
- **Reports:** `docs/reports/phase2_6_yolo_head_detection.md`, `docs/reports/fallback_demo_report.md`

---

## 13. YOLO Configuration (`data_config.py`)

```python
YOLO_CLASS_NAMES          = {0: "head_left", 1: "head_right", 2: "head_top"}
YOLO_CLASS_TO_SIDE        = {"head_left": "left", "head_right": "right", "head_top": "top"}
YOLO_CHECKPOINT_PATH      = PROJECT_ROOT / "checkpoints/yolo_head_detector.pt"
YOLO_DATASET_DIR          = PROJECT_ROOT / "datasets/yolo_head"
YOLO_CONFIDENCE_THRESHOLD = 0.25
YOLO_IMAGE_SIZE           = 640
```

---

*Last updated: 2026-05-05 | Maintained by: AI Coding Assistants & Project Team*
