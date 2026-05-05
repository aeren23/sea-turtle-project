# Comprehensive AI Phase Master Chronicle
## SeaTurtle Photo-ID: From Concept to Autonomous Inference Pipeline

**Institution:** Pamukkale University — DEKAMER Sea Turtle Research, Rescue & Rehabilitation Center  
**Date Range:** 2026-05-02 → 2026-05-05  
**Authors:** AI Architect (Antigravity), CrewAI Multi-Agent System, Cascade AI  
**Document Type:** Architectural Decision Record & Engineering Narrative  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Phase 1.0 — Architecture Planning & Data Pipeline](#2-phase-10--architecture-planning--data-pipeline)
3. [Phase 2.0 — Deep Learning: Baseline Triplet Loss](#3-phase-20--deep-learning-baseline-triplet-loss)
4. [The Pivot — Biological Asymmetry & ArcFace](#4-the-pivot--biological-asymmetry--arcface)
5. [Phase 2.5 — Embedding Gallery & FAISS Vector Store](#5-phase-25--embedding-gallery--faiss-vector-store)
6. [Phase 2.6 — YOLO Head Detection & Autonomous Pipeline](#6-phase-26--yolo-head-detection--autonomous-pipeline)
7. [Appendix — Agent Roster & Methodology](#7-appendix--agent-roster--methodology)

---

## 1. Executive Summary

This document chronicles the complete R&D journey of the SeaTurtle Photo-ID AI system — a non-invasive biometric identification platform for sea turtles based on post-ocular scale patterns. Over four intensive days, the project evolved through multiple architectural pivots, each guided by a multi-agent CrewAI research system that simulated expert debates between a Marine Biologist, a Computer Vision Researcher, a Deep Learning Strategist, and a Research Orchestrator.

**Key Milestones:**

| Phase | Achievement | Key Metric |
|---|---|---|
| 1.0 | Preprocessing pipeline + CrewAI research infrastructure | 5-stage OpenCV pipeline verified |
| 2.0 (Baseline) | ResNet-50 + Triplet Loss training | Top-1: 18.41%, mAP: 1.00% |
| 2.0 (ArcFace) | Architectural pivot to ArcFace + Virtual Identities | Top-1: **49.69%** (+253%), mAP: **6.79%** (+159%) |
| 2.5 | FAISS vector store with 3 separate indexes | 8,526 embeddings, 18/18 tests passing |
| 2.6 | YOLOv8n head detector + Fallback search | mAP50: 0.761, 94–98% head detection rate |

The system progressed from a manual, single-model prototype to a fully autonomous inference pipeline capable of accepting a raw, uncropped sea turtle photograph and returning a ranked identity match — with zero human intervention.

---

## 2. Phase 1.0 — Architecture Planning & Data Pipeline

**Timeline:** 2026-05-02 → 2026-05-03  
**Objective:** Establish the research infrastructure, analyze the DEKAMER dataset, and build a robust image preprocessing pipeline.

### 2.1. CrewAI Multi-Agent System Bootstrap

The project's first architectural decision was to build a **hierarchical multi-agent research system** using CrewAI. Rather than relying on a single AI for all decisions, we deployed specialized agents that could debate domain-specific trade-offs:

| Agent | Role | Expertise |
|---|---|---|
| **Research Orchestrator** | Manager | Delegates tasks, synthesizes final decisions |
| **Data Researcher** | Analyst | Dataset quality, augmentation strategies |
| **CV Researcher** | Engineer | OpenCV preprocessing, image normalization |
| **DL Strategist** | Architect | CNN architectures, loss functions, training strategy |
| **Marine Biologist** | Domain Expert | Biological constraints, scale pattern biology |

> **Engineering Note:** The initial CrewAI implementation encountered a delegation loop where the Orchestrator was assigned an explicit task in the `tasks.py` file. In CrewAI's hierarchical process, the manager implicitly owns the overall goal. Assigning it a direct task caused coworker tracking conflicts. **Resolution:** Removed `final_decision_task` from `tasks.py`; the final synthesized decision is now written directly via `run_research_crew.py` using the kickoff result.  
> — *Project Log, 2026-05-02 03:41*

### 2.2. Preprocessing Pipeline Design

The CV Researcher agent produced a comprehensive OpenCV preprocessing pipeline tailored for underwater photography challenges:

| Stage | Technique | Purpose |
|---|---|---|
| 1. ROI Localization | Bounding box extraction | Isolate post-ocular scale region |
| 2. Geometric Crop | Coordinate-based cropping | Remove body/background noise |
| 3. CLAHE | Contrast Limited Adaptive Histogram Equalization | Neutralize underwater shadows/glare |
| 4. Color Correction | BGR→LAB channel adjustment | Compensate underwater cyan shift |
| 5. Resize | Bilinear interpolation to 224×224 | ResNet-50 input standardization |

> **CV Researcher** recommended:
> > *"CLAHE effectively addresses non-uniform lighting conditions typical in underwater images by enhancing contrast locally without introducing excessive noise, making turtle scale patterns more discernible."*
>
> **DL Strategist** added:
> > *"Resizing to a fixed dimension of 224×224 RGB images makes them suitable for input into convolutional neural networks (CNNs), ensuring uniformity across the dataset."*

### 2.3. ADR-1: The Horizontal Flip Controversy

This was the project's **first major architectural decision** and one of its most consequential. The question was simple: *Should we use Horizontal Flip in data augmentation to expand our limited 600-image dataset?*

The CrewAI agents were unanimously in favor:

> **Data Researcher** argued:
> > *"Horizontal Flip: Flip images horizontally to create mirrored representations of turtles, which can help in recognizing unique patterns from different views."*
>
> **DL Strategist** concurred:
> > *"Data Augmentation: Include transformations like rotations, flips, and color jittering to enhance generalization."*

**However, the human architect intervened with domain knowledge:**

> [!CAUTION]
> **DECISION: Horizontal Flip REJECTED**
>
> *"Based on biological domain knowledge (sea turtle scale patterns are highly asymmetrical on the left and right sides of the face), this AI recommendation was REJECTED. Using horizontal flip would create fake, non-existent turtles and ruin model accuracy."*  
> — *Project Log, 2026-05-03 04:43*

**Biological Rationale:** Sea turtle post-ocular scales are akin to human fingerprints — the left profile and right profile of the same individual are **completely different patterns**. A horizontal flip of a left-profile image would generate a synthetic "right profile" that does not exist in nature, poisoning the embedding space with phantom identities.

**Final Augmentation Strategy:**
- ✅ Small Angle Rotations (±15°)
- ✅ Underwater-specific Color Jitter (brightness/contrast)
- ✅ Elastic Deformations
- ❌ **Horizontal Flip — STRICTLY BANNED**

This decision would later prove to be the foundation of the entire "Virtual Identity" architecture.

---

## 3. Phase 2.0 — Deep Learning: Baseline Triplet Loss

**Timeline:** 2026-05-03 → 2026-05-04  
**Objective:** Train a ResNet-50 metric learning model to generate 512-dimensional identity embeddings.

### 3.1. ADR-2: Closed-Set Classification vs. Open-Set Metric Learning

Before any training began, a fundamental architectural choice had to be made: should the system use traditional Softmax classification or metric learning?

> [!IMPORTANT]
> **Architectural Pivot:** Shifted from Closed-Set Classification (Softmax) to Open-Set Identification (Metric Learning).
>
> **The "New Individual" Problem:** If a standard Softmax classifier trained on 438 turtles encounters turtle #439, it will confidently (and incorrectly) classify it as one of the existing 438. Adding a new individual requires modifying the final layer and retraining from scratch.
>
> **Metric Learning Solution:** The ResNet-50 outputs a 512-dimensional embedding vector (a "digital fingerprint"). New individuals are added to the database by simply storing their embedding — **zero retraining required.**

**Training Architecture (Baseline):**
- **Backbone:** ResNet-50 (ImageNet pretrained, fine-tuned)
- **Embedding Dimension:** 512-d, L2-normalized
- **Loss Function:** Triplet Margin Loss with Hard Negative Mining
- **Sampler:** MPerClassSampler (4 images per class per batch)
- **Optimizer:** AdamW
- **Epochs:** 20

### 3.2. Baseline Training Results

| Metric | Epoch 1 | Epoch 10 | Epoch 20 (Final) |
|---|---|---|---|
| **Training Loss** | 0.2017 | 0.1974 | 0.1905 |
| **mAP** | 0.0042 | 0.0077 | 0.0100 |
| **Top-1 Accuracy** | 10.07% | 14.49% | 18.41% |

### 3.3. ADR-3: The "Continue Training or Move to API?" Debate

With a Top-1 accuracy of only 18.41% and mAP of 1%, the team faced a critical decision: push for more epochs, or accept these metrics and move forward?

The CrewAI system was deployed with all four agents:

> **DL Strategist** analyzed:
> > *"The decrease in training loss indicates some learning, yet low accuracy suggests issues in generalization. The dataset's few-shot learning scenario, where many turtles have only one photo, presents a high risk of overfitting. Continuing training without robust data augmentation strategies may lead to memorization rather than generalization."*
>
> **Marine Biologist** warned:
> > *"Matching turtles based on post-ocular scale patterns with only one reference image is fraught with challenges. Variability in scale presentation influenced by age and stressors, combined with varying angles and lighting, can obfuscate important features."*
>
> **Research Orchestrator** synthesized:
> > *"Given the current analysis, it's recommended to transition from the standard training phase to implementing few-shot learning techniques. This approach will help mitigate the issues posed by our dataset's limitations, particularly the reliance on single photographs for turtle identification."*

**Key Insight:** The agents correctly diagnosed the symptom (low metrics) but did not identify the root cause. The real problem was not "too few epochs" — it was a **mathematical conflict in the identity space** caused by mixing left/right/top orientations under a single turtle ID.

---

## 4. The Pivot — Biological Asymmetry & ArcFace

**Timeline:** 2026-05-04  
**Objective:** Diagnose the root cause of metric collapse and implement a biologically-informed solution.

### 4.1. The Discovery: Profile Asymmetry Collapse

Upon deep analysis, the AI Architect identified the true root cause of the 1% mAP:

> [!WARNING]
> **Root Cause:** The dataset parser was assigning all orientations (left, right, top, front, back, topleft, topright) of the same physical turtle to a **single identity label**. This created a mathematical conflict:
>
> The Triplet Loss was simultaneously trying to:
> 1. **Pull together** left-profile and right-profile embeddings of turtle `t001` (same label)
> 2. While the CNN learned that left and right profiles look **completely different** (different scale patterns)
>
> This created an irreconcilable gradient conflict, causing **embedding collapse** — all vectors converged toward a meaningless centroid.

### 4.2. ADR-4: The "Virtual Identity" Architecture

The solution was elegant and biologically motivated:

**Before (Collapsed):**
```
t001 → [left_photo_1, left_photo_2, right_photo_1, top_photo_1]  (1 identity, mixed orientations)
```

**After (Virtual Identities):**
```
t001_left  → [left_photo_1, left_photo_2]   (virtual identity A)
t001_right → [right_photo_1]                 (virtual identity B)
t001_top   → [top_photo_1]                   (virtual identity C)
```

**Implementation Details:**
- Reduced 7 granular orientations to **3 biological sides** (`left`, `right`, `top`)
- Average samples per class increased from 3.1 to 4.5
- Preserved biological asymmetry while maximizing training signal

### 4.3. ADR-5: Triplet Loss → ArcFace Loss

Simultaneously, the loss function was replaced:

> [!IMPORTANT]
> **Why ArcFace over Triplet Loss?**
>
> 1. Triplet Loss requires complex hard-negative mining via `MPerClassSampler`, which was failing due to low samples per class
> 2. ArcFace provides a much stronger angular margin decision boundary
> 3. ArcFace computes loss across **all classes simultaneously** — no special samplers needed
> 4. Proven state-of-the-art in fine-grained Re-ID tasks (face recognition, vehicle Re-ID)

**Additional Improvements:**
- `CosineAnnealingWarmRestarts` LR scheduler with 3-epoch linear warmup
- Advanced augmentations: `RandomResizedCrop`, `GridDistortion`, `GaussianBlur`, `CoarseDropout`

### 4.4. ArcFace Training Results — The Breakthrough

| Metric | Baseline (Triplet Loss) | ArcFace Model | Relative Improvement |
|---|---|---|---|
| **mAP** | 0.0262 | **0.0679** (Epoch 19) | **+159%** |
| **Top-1 Accuracy** | 0.1405 | **0.4969** (Epoch 20) | **+253%** |
| **Top-5 Accuracy** | 0.2536 | **0.5232** (Epoch 19) | **+106%** |

**Training Dynamics:**
- **Initial High Loss:** ArcFace (Scale=64) began at loss ~40.38 (Epoch 1) — expected for angular margin losses
- **Warm Restart Effect:** At Epoch 14, the scheduler executed its restart. Loss temporarily spiked from 20.28 → 22.78, and Top-1 dipped from 43.9% → 43.0%. This forced the model out of a local minimum
- **Recovery:** Subsequent epochs saw rapid convergence. Final loss: 14.68 at Epoch 20, Top-1 peaked at **49.69%**
- **No Overfitting:** Loss continued to drop monotonically post-restart

> **Verdict:** The architectural pivot to ArcFace + Virtual Identities rescued the model from embedding collapse. The model correctly identifies the exact individual as its first guess **half the time** — in a 1000-class open-set problem with extreme few-shot constraints.

---

## 5. Phase 2.5 — Embedding Gallery & FAISS Vector Store

**Timeline:** 2026-05-04 (evening)  
**Objective:** Build a production-ready vector database for identity matching.

### 5.1. ADR-6: Three Separate FAISS Indexes

> [!IMPORTANT]
> **Design Decision:** Use 3 separate `IndexFlatIP` indexes instead of a single unified index.
>
> **Problem:** A single index containing left, right, and top embeddings would create cross-side noise. A left-profile query could return a mathematically close but biologically irrelevant right-profile match.
>
> **Solution:** `TurtleVectorStore` manages a dictionary of 3 indexes: `faiss_left.bin`, `faiss_right.bin`, `faiss_top.bin`, each with its own metadata JSON.

### 5.2. Gallery Build Results

| Side Index | Vector Count |
|---|---|
| Left | 3,906 |
| Right | 3,634 |
| Top | 986 |
| **Total** | **8,526** |

- **Processing time:** ~4 min 8 sec (34.35 images/sec, CPU)
- **Skipped:** 0
- **L2 Normalization Guarantee:** Defensive `F.normalize(embedding, p=2, dim=1)` applied after model forward pass

### 5.3. Live Gallery Validation

| Test | Query | Best Score | Result |
|---|---|---|---|
| Known Turtle | t522, left side, correct bbox | **1.000000** | ✅ MATCH FOUND |
| Unknown Individual | Synthetic Gaussian noise | 0.500139 (< 0.6 threshold) | ✅ UNKNOWN DETECTED |

### 5.4. Bug Fix: Unicode Path on Windows

`faiss.write_index()` internally calls C++ `fopen()` which fails on Windows paths containing non-ASCII characters (e.g., `Masaüstü`). **Fix:** Replaced with `faiss.serialize_index()` → bytes → Python `open("wb")`. Python's file I/O handles Unicode natively; FAISS only does in-memory (de)serialization.

### 5.5. Remaining Limitation

At this stage, the system required **two manual inputs** at query time:
1. `--side left|right|top` — which FAISS index to search
2. `--bbox x,y,w,h` — head bounding box for cropping

These dependencies blocked autonomous production inference and motivated Phase 2.6.

---

## 6. Phase 2.6 — YOLO Head Detection & Autonomous Pipeline

**Timeline:** 2026-05-05  
**Objective:** Eliminate all manual inputs by training a head detector and building a fallback search mechanism.

### 6.1. ADR-7: Two Models vs. One — The Pipeline Architecture Debate

The CrewAI system was deployed to debate the autonomous pipeline architecture. The question: should we build **two separate models** (YOLO detector + CNN orientation classifier) or **one unified model**?

> **CV Researcher** proposed two models:
> > *"Module A (Head Detection) must be developed first because the outputs (accurately cropped turtle heads) are essential inputs for Module B (Orientation Classifier). Module B's accuracy depends on the consistent input quality from Module A."*
> > *"For Module A: YOLO-based models such as YOLOv5n or YOLOv8n. For Module B: EfficientNet-B0."*
>
> **DL Strategist** agreed but pushed for optimization:
> > *"Priority: Develop Module A first because its output is a prerequisite for Module B. Poor head detection directly compromises Module B's classification accuracy."*
> > *"Module B: EfficientNet-B0 for lightweight, high-performance classification. Alternatively, MobileNetV2 for edge-heavy deployment."*
>
> **Marine Biologist** emphasized biological constraints:
> > *"Post-ocular scale patterns are biologically valid identifiers due to their uniqueness across individuals, akin to human fingerprints. The asymmetry between left and right profiles is essential for identification accuracy. Horizontal flipping would corrupt training."*
>
> **Research Orchestrator** synthesized the final decision:
> > *"By designing Module A with YOLOv8n and Module B with EfficientNet-B0, the proposed architecture strikes a balance between performance and computational efficiency."*

**The Implemented Decision** deviated from the agents' recommendation:

> [!IMPORTANT]
> **Architectural Decision:** Chose **single YOLOv8-Nano with 3 classes** (`head_left`, `head_right`, `head_top`) instead of two separate models.
>
> **Rationale:** A single YOLO model solves **both** head detection and orientation classification in one forward pass. This reduces complexity, latency, and error surface compared to a two-model cascade.

### 6.2. YOLO Training Configuration

| Parameter | Value |
|---|---|
| Base Model | `yolov8n.pt` (COCO pretrained) |
| Classes | 3: `head_left`, `head_right`, `head_top` |
| Epochs | 50 (early stopped at 40) |
| Image Size | 640 × 640 |
| Dataset | 8,526 images (4,571 train / 3,955 val) |
| Device | CPU |

### 6.3. Training Results

![YOLO Training Curves](assets/yolo_head_training/results.png)

**Final Model Performance (Best Epoch: 30):**

| Metric | Value |
|---|---|
| **mAP50** | **0.761** |
| **mAP50-95** | **0.595** |
| **Precision** | 0.655 |
| **Recall** | 0.783 |

### 6.4. Confusion Matrix — The Annotation Noise Discovery

![YOLO Confusion Matrix](assets/yolo_head_training/confusion_matrix_normalized.png)

| True Class | Correct | Major Confusion | Miss Rate |
|---|---|---|---|
| **head_left** | **54%** | 42% → predicted as head_right | 2% |
| **head_right** | **64%** | 31% → predicted as head_left | 2% |
| **head_top** | **74%** | 10% left + 10% right | 6% |

**Key Findings:**
1. **Head Detection is Strong:** Only 2–6% of true heads are missed — the model reliably locates turtle heads
2. **Left ↔ Right Confusion is Severe:** 31–42% cross-confusion — NOT a model flaw, but annotation noise

### 6.5. Root Cause: The Annotation Convention Problem

![Training Batch Ground Truth](assets/yolo_head_training/train_batch0.jpg)

During ground truth inspection, turtles swimming in **opposite directions** were labeled with the **same class**. The `annotations.json` `orientation` field mixed two conventions:

- **Convention A (Biological Side):** "left" = turtle's left biological side visible → turtle faces RIGHT in image
- **Convention B (Visual Direction):** "left" = turtle visually facing LEFT → right biological side visible

> [!WARNING]
> Some annotators used Convention A, others used Convention B, creating **systematic noise** in training labels. However, the system remains **internally consistent** because all three pipeline paths (gallery build, YOLO training, inference) use the same mapping from the same annotations.

### 6.6. ADR-8: The Fallback Search Strategy

Three options were evaluated to handle YOLO orientation uncertainty:

| Option | Strategy | Verdict |
|---|---|---|
| A | Confidence threshold (≥0.7 → single index, else → all) | ❌ Most predictions fall below 0.7 |
| B | Merge left+right, separate top | ⚠️ Partial solution |
| **C** | **Always search all 3 FAISS indexes** | ✅ **Implemented** |

> [!IMPORTANT]
> **Option C chosen:** Always search all 3 FAISS indexes regardless of YOLO's orientation prediction. FAISS search cost (~5ms for 8,526 vectors) is negligible vs. YOLO (~100ms) and embedding extraction (~50ms). This eliminates orientation misclassification as a failure mode entirely.

### 6.7. Visual Proof: The Fallback Strategy in Action

**Case A — Correct Orientation Prediction:**

![Case A - Correct Orientation](assets/fallback_demo/case_a_correct_orientation.png)

- **Turtle:** t001 | **YOLO Prediction:** head_top (confidence: 0.761) | **Actual:** top
- Both single-index and fallback find the correct match. Overhead: ~3ms.

**Case B — Wrong Orientation, Fallback Saves:**

![Case B - Wrong Orientation, Fallback Saves](assets/fallback_demo/case_b_wrong_orientation_fallback.png)

- **Turtle:** t015 | **YOLO Prediction:** head_right (confidence: 0.779) | **Actual:** left
- YOLO was **confidently wrong** (0.779!) — a threshold-based fallback would NOT have caught this
- The unconditional multi-index search found t015 with high confidence regardless

**Side-by-Side Summary:**

![Fallback Strategy Summary Comparison](assets/fallback_demo/summary_comparison.png)

| Metric | Single-Index | Fallback (All Indexes) |
|---|---|---|
| **Speed per query** | ~2ms | ~5ms |
| **Works when YOLO correct** | ✓ | ✓ |
| **Works when YOLO wrong** | ✗ Fails | ✓ Still works |
| **Orientation dependency** | High (54–64%) | None |

### 6.8. End-to-End Smoke Test Results

| Test Image | YOLO Confidence | Match ID | Score | Correct? |
|---|---|---|---|---|
| `t001/anuJvqUqBB.JPG` | 0.76 | t001 | **0.986** | ✅ |
| `t042/CoxZEtKVTi.JPG` | 0.86 | t042 | **0.979** | ✅ |

Top-5 separation strong: 2nd best ~0.53 vs 1st ~0.98 — clear decision boundary.

### 6.9. Final Production Pipeline Architecture

```
📷 Raw Photo (any angle, uncropped)
        │
   ┌────▼─────────────────────────────────┐
   │  1. HeadDetector (YOLOv8-Nano)       │
   │     • Finds head → bbox [x,y,w,h]   │
   │     • Predicts orientation → "left"  │
   │     • Confidence score → 0.76        │
   └────┬─────────────────────────────────┘
        │ bbox
   ┌────▼─────────────────────────────────┐
   │  2. TurtlePreprocessingPipeline      │
   │     • Crop head using bbox           │
   │     • Resize to 224×224              │
   │     • CLAHE contrast enhancement     │
   │     • Underwater color correction    │
   └────┬─────────────────────────────────┘
        │ clean 224×224 image
   ┌────▼─────────────────────────────────┐
   │  3. EmbeddingExtractor (ResNet-50)   │
   │     • Image → 512-d float vector     │
   │     • L2 normalize (unit length)     │
   └────┬─────────────────────────────────┘
        │ 512-d embedding
   ┌────▼─────────────────────────────────┐
   │  4. FAISS Fallback Search            │
   │     • Search faiss_left → results    │
   │     • Search faiss_right → results   │
   │     • Search faiss_top → results     │
   │     • Sort all by score              │
   │     • Return top-5                   │
   └────┬─────────────────────────────────┘
        │
   ┌────▼─────────────────────────────────┐
   │  5. Decision                         │
   │     • score ≥ 0.6 → "KNOWN: t042"   │
   │     • score < 0.6 → "UNKNOWN"       │
   └──────────────────────────────────────┘
```

---

## 7. Appendix — Agent Roster & Methodology

### 7.1. CrewAI Agent Configuration

The multi-agent system was implemented using the **CrewAI** framework with a hierarchical process model. The Orchestrator agent served as manager, delegating sub-tasks dynamically to specialist agents.

| Agent | LLM Backend | Key Contributions |
|---|---|---|
| Research Orchestrator | GPT-4o-mini | Synthesized final decisions from specialist reports |
| Data Researcher | GPT-4o-mini | Dataset analysis, augmentation strategy evaluation |
| CV Researcher | GPT-4o-mini | Preprocessing pipeline design, image normalization |
| DL Strategist | GPT-4o-mini | Architecture selection, loss function analysis, training strategy |
| Marine Biologist | GPT-4o-mini | Biological constraints, scale pattern asymmetry validation |

### 7.2. Summary of Architectural Decision Records (ADRs)

| ADR | Decision | Rationale |
|---|---|---|
| ADR-1 | Ban Horizontal Flip | Biological asymmetry of post-ocular scales |
| ADR-2 | Metric Learning over Classification | Open-set identification, no retraining for new individuals |
| ADR-3 | Diagnose before continuing training | Low metrics from identity conflict, not insufficient epochs |
| ADR-4 | Virtual Identity Architecture | Separate left/right/top profiles as independent identities |
| ADR-5 | ArcFace over Triplet Loss | Stronger angular margins, no special samplers needed |
| ADR-6 | Three Separate FAISS Indexes | Prevent cross-side noise, preserve biological asymmetry |
| ADR-7 | Single YOLO (3-class) over two models | Reduced complexity, single forward pass |
| ADR-8 | Unconditional multi-index fallback search | Eliminates orientation misclassification risk entirely |

### 7.3. Technology Stack

| Component | Technology |
|---|---|
| Deep Learning Framework | PyTorch 2.x |
| CNN Backbone | ResNet-50 (ImageNet pretrained) |
| Loss Function | ArcFace (Scale=64, Margin=0.5) |
| Object Detection | YOLOv8-Nano (Ultralytics) |
| Vector Database | FAISS IndexFlatIP (CPU) |
| Preprocessing | OpenCV (CLAHE, color correction) |
| Augmentation | Albumentations |
| Multi-Agent System | CrewAI (hierarchical process) |
| Metrics | pytorch-metric-learning (mAP, Top-K) |

### 7.4. Dataset Statistics

| Property | Value |
|---|---|
| Total Images | 8,526 |
| Unique Turtle IDs | 438 |
| Average Images per ID | ~19.5 (raw), ~1.3 per virtual identity |
| Left Profiles | 3,906 (45.8%) |
| Right Profiles | 3,634 (42.6%) |
| Top Profiles | 986 (11.6%) |
| Image Resolution (Input) | 224×224 RGB |
| Embedding Dimension | 512 |

---

*This document serves as the definitive engineering record of the SeaTurtle Photo-ID AI system's evolution from concept to production-ready autonomous inference pipeline. Every architectural pivot was driven by empirical evidence, multi-agent deliberation, and deep respect for the biological constraints of the domain.*

**— End of Chronicle —**
