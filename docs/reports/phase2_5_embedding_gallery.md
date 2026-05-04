# Phase 2.5 Report: Embedding Gallery & FAISS Vector Store Pipeline

**Date:** 2026-05-04
**Author:** Cascade / AI Coding Assistant

---

## Summary

Built the complete identification pipeline that bridges the trained CNN model (Phase 2) with a production-ready identity matching system. All preprocessed turtle head images can now be converted to 512-d embeddings and stored in a FAISS-based vector database, enabling nearest-neighbour identity search for new query images.

---

## Architecture

```
ai-core/src/identification/
├── __init__.py
├── embedding_extractor.py   # Model inference + L2 norm guarantee
├── vector_store.py           # Per-side FAISS index dictionary
├── gallery_builder.py        # Dataset → FAISS orchestrator
└── identifier.py             # Query service (side param required)

ai-core/scripts/
├── build_gallery.py          # CLI: python scripts/build_gallery.py
└── identify_turtle.py        # CLI: python scripts/identify_turtle.py --image X --side left
```

---

## Key Design Decisions

### 1. Three Separate FAISS Indexes (Not One)
- **Problem:** A single FAISS index containing left, right, and top profile embeddings would create cross-side noise during search. A left profile query could return a mathematically close but biologically irrelevant right profile match.
- **Solution:** `TurtleVectorStore` manages a dictionary of 3 `IndexFlatIP` indexes: `faiss_left.bin`, `faiss_right.bin`, `faiss_top.bin`. Each has its own metadata JSON file.
- **Rationale:** Preserves the biological asymmetry rule established in Phase 1 (post-ocular scales are unique per side).

### 2. Defensive L2 Normalization
- **Problem:** FAISS `IndexFlatIP` (Inner Product) only behaves as Cosine Similarity when input vectors are unit-length. If the model's internal normalization is ever removed or altered, the entire system breaks silently.
- **Solution:** `EmbeddingExtractor` applies `F.normalize(embedding, p=2, dim=1)` **after** the model forward pass, regardless of the model's own normalization. Double normalization of an already-normalized vector is a no-op, so there is zero performance cost.
- **Test:** `test_l2_normalization_guarantee` verifies every output vector has norm ≈ 1.0.

### 3. Manual Biological Side Parameter
- **Problem:** At query time, the system needs to know which FAISS index to search. No automatic orientation classifier exists yet.
- **Solution:** `TurtleIdentifier.identify()` requires a `biological_side` parameter. The CLI enforces `--side left|right|top` as a required argument.
- **Future:** When an orientation classifier is built, this parameter becomes optional with auto-detection fallback.

### 4. Unknown Individual Detection
- **Mechanism:** If the best match score (cosine similarity) falls below `IDENTIFICATION_THRESHOLD` (default 0.6), the result is flagged as "Unknown Individual / New Turtle".
- **Threshold:** 0.6 is an initial conservative value. Should be tuned based on gallery statistics after the first full gallery build.

---

## Configuration Constants Added

| Constant | Value | Location |
|----------|-------|----------|
| `EMBEDDING_DIM` | 512 | `src/config/data_config.py` |
| `CHECKPOINT_PATH` | `checkpoints/best_turtle_resnet_orientation.pth` | `src/config/data_config.py` |
| `FAISS_INDEX_DIR` | `gallery_index/` | `src/config/data_config.py` |
| `BIOLOGICAL_SIDES` | `("left", "right", "top")` | `src/config/data_config.py` |
| `IDENTIFICATION_THRESHOLD` | 0.6 | `src/config/data_config.py` |
| `TOP_K_RESULTS` | 5 | `src/config/data_config.py` |

---

## Test Results

**18/18 tests passing.**

| Test File | Tests | Status |
|-----------|-------|--------|
| `test_vector_store.py` | 11 (add, search, persistence, stats, validation) | All Passed |
| `test_embedding_extractor.py` | 3 (shape, batch, L2 norm guarantee) | All Passed |
| `test_identification.py` | 4 (known match, unknown detection, cross-side isolation, dataclass) | All Passed |

---

## Files Created / Modified

### New Files (10)
- `src/identification/__init__.py`
- `src/identification/embedding_extractor.py`
- `src/identification/vector_store.py`
- `src/identification/gallery_builder.py`
- `src/identification/identifier.py`
- `scripts/build_gallery.py`
- `scripts/identify_turtle.py`
- `tests/test_vector_store.py`
- `tests/test_embedding_extractor.py`
- `tests/test_identification.py`

### Modified Files (3)
- `src/config/data_config.py` — Added identification constants
- `docs/specifications/state.md` — Updated to Phase 2.5
- `docs/project_log.md` — Appended log entry

---

## Gallery Build Results (Production Run)

| Side Index | Vector Count |
|------------|-------------|
| Left       | 3,906       |
| Right      | 3,634       |
| Top        | 986         |
| **Total**  | **8,526**   |

- **Processing time:** ~4 min 8 sec (34.35 images/sec, CPU)
- **Skipped:** 0
- **Files written:** `gallery_index/faiss_left.bin`, `faiss_right.bin`, `faiss_top.bin` + 3 JSON metadata files

---

## Bug Fix: Unicode Path (Windows)

`faiss.write_index()` internally calls C++ `fopen()` which fails on Windows paths containing non-ASCII characters (e.g. `Masaüstü`). Fixed by replacing with:
- **Save:** `faiss.serialize_index()` → bytes → Python `open("wb")`
- **Load:** Python `open("rb")` → `np.frombuffer()` → `faiss.deserialize_index()`

Python's file I/O handles Unicode paths natively; FAISS only does in-memory (de)serialization.

---

## Usage

### Build Gallery
```bash
cd ai-core
python scripts/build_gallery.py
```

### Identify a Turtle
```bash
python scripts/identify_turtle.py --image path/to/photo.jpg --side left
python scripts/identify_turtle.py --image photo.jpg --side right --bbox "100,200,300,400"
```

---

## Next Steps
- Run `build_gallery.py` on the full dataset to create the production FAISS indexes
- Tune `IDENTIFICATION_THRESHOLD` based on gallery similarity distribution
- Consider Phase B optimizations (GeM Pooling, BNNeck, longer training) to improve embedding quality
- Build automatic orientation classifier to remove manual `--side` requirement
