# 🔬 SeaTurtle Photo-ID: Preprocessing Pipeline Analysis Report

**Date:** 2026-05-03  
**Status:** ✅ Verified & Logged  
**Project:** DEKAMER Sea Turtle Recognition System  

---

## 🌊 Overview
Sea turtle underwater photography presents unique challenges: light refraction, scattering, color aberrations, and orientation variances. This report documents the verified preprocessing pipeline used to standardize the dataset of ~600 images before deep learning ingestion.

## 🛠️ The Pipeline Stages

### 1. ROI Localization (Original + BBox)
The system identifies the "post-ocular" area. This is critical because sea turtle identification relies on the unique scale patterns located behind the eye.
*   **Purpose:** Isolate the biometric identifier.
*   **Result:** Reduced noise from body segments and background water.

### 2. Geometric Standardization (Cropped Head)
By cropping to the bounding box, we eliminate background clutter such as corals, sand, or other marine life.
*   **Technique:** Bounding box coordinate extraction.
*   **Outcome:** Improved signal-to-noise ratio for the CNN.

### 3. Illumination Balancing (CLAHE)
Underwater light is rarely uniform. Contrast Limited Adaptive Histogram Equalization (CLAHE) is applied to neutralize shadows and glares.
*   **Mechanism:** Localized histogram equalization with clipping to prevent noise amplification.
*   **Benefit:** Brings out the subtle textures of the scale edges.

### 4. Chromatic Correction (Color Correction)
Water acts as a cyan filter. We neutralize this shift to restore the natural contrast of the scales.
*   **Outcome:** "Post-ocular" patterns become distinct, aiding the model in feature extraction.

### 5. Neural Input Standardization (Final Resized)
Images are resized to **224x224 RGB**, matching the architecture requirements of the ResNet-50 backbone.
*   **Interpolation:** Linear (Bi-linear) to preserve edge sharpess.

---

## 🧠 Strategic Decision: The Asymmetry Rule
> [!IMPORTANT]
> **Biological Constraint:** Sea turtle scale patterns are asymmetrical. The pattern on the left side of a turtle's face is different from the pattern on the right side.
> 
> **Decision:** Horizontal Flipping has been **EXCLUDED** from the data augmentation strategy. 
> *   **Reason:** Mirrored images would create "ghost" individuals that do not exist, leading to false identification in real-world scenarios.
> *   **Alternative:** We rely on Rotation, Color Jitter, and Elastic Deformations to augment the dataset safely.

---

## 📊 Verification Result
![Preprocessing Results Verification](file:///c:/Users/alihe/OneDrive/Masaüstü/sea-turtle-project/preprocessing_results.png)
*Figure 1: Step-by-step transformation from raw underwater capture to standardized neural input.*
