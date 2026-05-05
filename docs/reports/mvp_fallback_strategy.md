# MVP Fallback Strategy: YOLO Orientation Confidence Handling

**Date:** 2026-05-05
**Status:** ✅ Implemented (Option C — Search All 3 Indexes)
**Related:** Phase 2.6 YOLO Head Detection (`docs/reports/phase2_6_yolo_head_detection.md`)

---

## Problem

YOLO head detection is strong (mAP50 = 0.761, 94–98% detection rate), but left/right orientation classification has 31–42% cross-confusion due to annotation inconsistency in the source `annotations.json`.

When YOLO misclassifies orientation, the system searches the wrong FAISS index and may fail to identify a known turtle.

---

## Proposed Strategies

### Option A: Confidence Threshold Fallback

```
IF YOLO confidence ≥ 0.7:
    Search only the predicted FAISS index (fast)
ELSE:
    Search all 3 FAISS indexes, return best overall match
```

- **Pro:** Fast for high-confidence predictions
- **Con:** Most predictions fall below 0.7 (val shows 0.3–0.5 typical), so fallback triggers too often

### Option B: Merge Left + Right, Separate Top

```
IF YOLO predicts head_left OR head_right:
    Search both faiss_left AND faiss_right, return best match
IF YOLO predicts head_top:
    Search only faiss_top
```

- **Pro:** Directly targets the confused class pair
- **Pro:** head_top is 74% accurate, can be trusted independently
- **Con:** Minor cross-side false match risk (mitigated by embedding quality)

### Option C: Always Search All 3 Indexes (Recommended for MVP)

```
Regardless of YOLO class prediction:
    Search faiss_left + faiss_right + faiss_top
    Return the match with highest similarity score
```

- **Pro:** Simplest implementation, most robust, zero orientation dependency
- **Pro:** FAISS search is ~5ms total for 8,526 vectors — negligible vs YOLO (~100ms) and embedding extraction (~50ms)
- **Pro:** YOLO orientation is still returned as metadata (informational, not decisional)
- **Pro:** Easily reverted to single-index search when annotations are cleaned
- **Con:** Ignores orientation classification entirely for identification decisions

---

## Recommendation

**Option C** for MVP. YOLO's primary value is **head bbox detection** (crop area), not orientation. The orientation prediction can be logged as metadata for future analysis but should not gate the FAISS search until annotation quality improves.

---

## Implementation Notes

Changes needed in `src/inference/inference_pipeline.py`:

```python
# Current: single-index search
result = self.vector_store.search(embedding, side=detection.biological_side, top_k=k)

# Proposed: multi-index search
best_result = None
for side in ("left", "right", "top"):
    result = self.vector_store.search(embedding, side=side, top_k=k)
    if best_result is None or result.score > best_result.score:
        best_result = result
```

Estimated effort: ~15 lines of code change.

---

## When to Revisit

- After annotation cleanup / relabeling effort
- After retraining YOLO with cleaned data (expected left/right accuracy > 85%)
- When per-class confusion matrix shows acceptable separation
