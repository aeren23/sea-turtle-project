# 📐 SeaTurtle Photo-ID: Metric Learning Strategy Report

**Date:** 2026-05-03  
**Status:** ✅ Approved & Implemented  
**Project:** DEKAMER Sea Turtle Recognition System  

---

## 🎯 The Problem: Closed-Set vs. Open-Set Identification
In standard deep learning classification tasks (e.g., Cats vs. Dogs), the model uses a final "Softmax" layer to output a probability distribution over a **fixed number of classes**. This is known as a **Closed-Set** problem.

If we applied this to Sea Turtles, where every turtle ID (e.g., `Caretta-001`, `Caretta-002`) is a "class", we would face a catastrophic scaling issue:
1.  **The "New Individual" Problem:** If an unseen turtle is photographed (`Caretta-051`), the Softmax classifier will confidently (and incorrectly) classify it as one of the existing 50 turtles.
2.  **Retraining Bottleneck:** To add `Caretta-051` to the database, we would have to modify the final layer of the neural network from 50 to 51 outputs, and retrain the entire model from scratch.

## 🚀 The Solution: Metric Learning (Re-Identification)
To solve this, we are shifting the architecture from **Classification** to **Open-Set Identification** using **Metric Learning**.

Instead of predicting a "class probability", the ResNet-50 backbone is modified to output a **512-dimensional numerical vector (Embedding)**. Think of this embedding as a unique digital "fingerprint" for the turtle's face.

### How it Works
1.  **Feature Extraction:** The CNN processes the preprocessed image (CLAHE + Color Corrected) and generates the 512-d vector.
2.  **Vector Normalization:** We apply L2-Normalization to project these vectors onto a hypersphere, ensuring that only the *angle* (Cosine Similarity) between vectors matters, not their magnitude.
3.  **Database Matching (KNN):** The new vector is compared against a database of known turtle vectors.
    *   If the distance to the nearest known vector is below a certain threshold -> **Match Found** (e.g., It is `Caretta-001`).
    *   If the distance is above the threshold -> **New Individual Identified**. We simply save this new vector into the database. **Zero retraining required!**

---

## ⚖️ Training Strategy & Loss Functions
To teach the model how to produce these high-quality embeddings, we will use the `pytorch-metric-learning` library.

1.  **Triplet Margin Loss:** The model takes an Anchor (Turtle A), a Positive (another photo of Turtle A), and a Negative (Turtle B). It updates weights to pull the Anchor and Positive close together in the 512-d space, while pushing the Negative far away.
2.  **Hard Negative Mining:** To make the model highly discriminative, the algorithm will specifically seek out "Negatives" that look extremely similar to the "Anchor" but are actually different turtles, forcing the CNN to learn the micro-textures of the scales.

---

## 📈 Evaluation Metrics
We cannot use standard "Accuracy" for this model. Instead, we use industry-standard Re-Identification (Re-ID) metrics:

*   **Top-1 Accuracy:** Does the closest matching vector in the database belong to the correct turtle?
*   **Top-5 Accuracy:** Is the correct turtle within the top 5 closest matches? (Useful for presenting options to DEKAMER researchers).
*   **mAP (Mean Average Precision):** Evaluates whether *all* correct matches for a queried turtle appear at the top of the search results, penalizing the model if correct matches are buried under wrong ones.
