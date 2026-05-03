# OpenCV-Based Image Preprocessing Pipeline for Underwater Sea Turtle Photographs

## Introduction
This document outlines a comprehensive image preprocessing pipeline designed specifically for underwater sea turtle photographs. The aim is to standardize input images for the SeaTurtle Photo-ID system, ensuring consistent model inputs through effective preprocessing techniques.

## Pipeline Steps
### 1. Face Detection & Cropping
- **Technique:** Haar Cascade Classifier for Object Detection
- **OpenCV Function:** `cv2.CascadeClassifier()` combined with `detectMultiScale()`  
- **Parameters:**  
  - `scaleFactor`: 1.1 (for image scaling)  
  - `minNeighbors`: 5 (for detecting reliable faces)  
  - `minSize`: (30, 30) (minimum size of the detected face)  
- **Justification:** 
 This method effectively isolates the turtle's head by eliminating unnecessary body parts and background clutter, thus improving the focus on identification features. 

### 2. Angle/Perspective Correction
- **Technique:** Affine Transformations for Geometric Correction
- **OpenCV Function:** `cv2.getAffineTransform()` and `cv2.warpAffine()`  
- **Parameters:**  
  - Source points: landmarks (e.g., turtle eyes) to compute affine transformation  
  - Destination points: standard positions for desired orientation  
- **Justification:** 
 Affine transformations allow for a straightforward alignment of the turtle's face profile to a standardized horizontal orientation, ensuring that the scaling patterns are consistently positioned for further analysis. 

### 3. Light & Contrast Optimization
- **Technique:** Contrast Limited Adaptive Histogram Equalization (CLAHE)
- **OpenCV Function:** `cv2.createCLAHE()`, `apply()`  
- **Parameters:**  
  - `clipLimit`: 2.0 (to limit contrast amplification)  
  - `tileGridSize`: (8, 8) (size of the grid for contrast enhancement)  
- **Justification:** 
 CLAHE effectively addresses non-uniform lighting conditions typical in underwater images by enhancing contrast locally without introducing excessive noise, making turtle scale patterns more discernible. 

### 4. Underwater Color Correction
- **Technique:** Color Space Conversion and Channel Adjustments
- **OpenCV Functions:**  
  - `cv2.cvtColor()` (to convert BGR to LAB or HSV)  
  - `cv2.split()` and `cv2.merge()` (to adjust individual channels)  
- **Parameters:**  
  - Convert BGR to LAB for lightness adjustment or to HSV for color shifts  
  - Adjust V channel in HSV or L channel in LAB to reduce blue/green casts.  
- **Justification:** 
 Converting color spaces allows for better manipulation of color information, compensating for the distinctive blue/green hue often seen in underwater photographs, leading to more natural and true-to-life images. 

### 5. Output Standardization
- **Technique:** Resizing and Normalization 
- **OpenCV Function:** `cv2.resize()`  
- **Parameters:**  
  - `dsize`: (224, 224)  
  - `interpolation`: `cv2.INTER_LINEAR` (for resizing)  
- **Justification:** 
 Resizing to a fixed dimension of 224x224 RGB images makes them suitable for input into convolutional neural networks (CNNs), ensuring uniformity across the dataset in terms of image dimensions and color format, which is vital for model training and prediction.

## Conclusion
This preprocessing pipeline will standardize the preprocessing of underwater sea turtle photographs, enhancing the efficacy of subsequent image analysis and machine learning tasks. Each step is carefully selected to address specific challenges associated with underwater imagery.