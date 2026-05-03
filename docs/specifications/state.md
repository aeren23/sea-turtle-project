# SeaTurtle Photo-ID: Project State & History

**Last Updated:** 2026-05-03

This document tracks the high-level progress, completed milestones, and current active phase of the SeaTurtle Photo-ID project. It is intended to provide immediate context to any AI Agent joining the workspace.

## 🟢 Current Phase: Phase 2 - Deep Learning Implementation
**Status:** In Progress

We are currently building the PyTorch training pipeline for the CNN.
*   **Focus:** Metric Learning (Open-Set Identification).
*   **Active Tasks:**
    *   Implementing `pytorch-metric-learning` with Triplet Margin Loss.
    *   Building the `train.py` loop with Hard Negative Mining.
    *   Implementing Top-K Accuracy and mAP evaluation metrics.

---

## ✅ Completed Phases

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
*   **Tech Stack:** .NET 8 RESTful API.
*   **Goal:** Build the web service where users/researchers can upload photos, register new turtles, or query existing ones.
*   **Integration:** The PyTorch model will be integrated either via ONNX runtime within .NET, or as a standalone Python microservice (FastAPI/Flask) that the .NET backend communicates with.

### Phase 4: Frontend Development
*   **Goal:** A visually stunning, dynamic UI for DEKAMER researchers to interact with the system.

---
**Note to AI Agents:** When undertaking new tasks, strictly adhere to the standards outlined in `docs/rules/coding_standards.md` and log your major decisions in `docs/project_log.md` using the Python `log_writer` utility.
