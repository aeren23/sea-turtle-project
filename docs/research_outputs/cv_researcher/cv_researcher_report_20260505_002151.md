# CV Preprocessing Considerations for Phase 3 Production Inference Pipeline

## Objective
To build a preprocessing pipeline using OpenCV that optimizes underwater sea turtle images for use in training the Module A (Head Detection) and Module B (Orientation Classifier). This involves handling underwater-specific distortions, ensuring consistent image alignment, lighting/contrast normalization, and preparing high-quality, standardized 224x224 RGB images as model input.

---

## **Pipeline Design Considerations**

### **1. Key Challenges in Underwater Imaging**
1. **Non-uniform Lighting**: Ambient underwater lighting causes bright spots and shadow regions in images, making it difficult to detect or classify turtle heads.
2. **Color Cast**: Blue/green wavelengths dominate underwater environments, leading to unnatural colors that can confuse both detection and classification models.
3. **Motion Blur**: Photographs often suffer from blur due to water refraction effects or camera motion in unstable environments.
4. **Camera Angle and Distortion**:
    - Angled shots introduce geometric artifacts that require perspective/affine correction.
    - Refraction at varying depths distorts the shape and size of turtle heads.
5. **Background Clutter**: Presence of sand, plants, or other marine organisms in the background creates occlusion and unwanted artifacts.

---

### **2. Preprocessing Steps**
A modular OpenCV-based preprocessing pipeline will transform raw underwater photographs into standardized 224x224 images optimized for Module A and Module B. 

#### **Step A: Light and Contrast Optimization**
Purpose: Counter underwater lighting issues and color cast.

1. **Color Space Conversion**:
    - Convert the image from BGR to LAB color space (`cv2.cvtColor(img, cv2.COLOR_BGR2LAB)`).
    - Perform CLAHE (Contrast Limited Adaptive Histogram Equalization) on the Lightness (L) channel to normalize brightness and contrast (`cv2.createCLAHE`).
    - Merge enhanced L-channel back into LAB space, then convert back to RGB for consistent color normalization.

2. **Color Cast Correction**:
    - Utilize a BGR to HSV conversion for hue adjustment (`cv2.cvtColor(img, cv2.COLOR_BGR2HSV)`).
    - Fine-tune saturation and value channels to reduce dominant blue-green tones (`cv2.addWeighted`).

#### **Step B: Gaussian and Bilateral Filtering for Noise Reduction**
Purpose: Reduce motion blur caused by water turbulence or camera instability.

1. **Gaussian Blur** (`cv2.GaussianBlur`):
    - Apply for moderate noise reduction without sacrificing edge information.
    - Experiment with kernel sizes (e.g., `3x3` or `5x5`) to balance smoothness vs. clarity.

2. **Bilateral Filtering** (`cv2.bilateralFilter`):
    - Use this for more aggressive denoising while preserving turtle head scale edge features.
    - Highly useful for preserving patterns necessary for ID.

#### **Step C: Geometric Correction**
Purpose: Normalize angled turtle heads to be upright for consistent detection and classification.

1. **Edge Detection for Head Boundary**:
    - Use Canny edge detection (`cv2.Canny`) to identify the rough contour of the turtle head.
    - Employ morphological transformations (`cv2.morphologyEx`) to clean edge noise.

2. **Keypoint Extraction**:
    - Find critical body landmarks (e.g., eyes, mouth, nostrils) that can serve as reference points for alignment.
    - Use feature detection algorithms like FAST/SIFT to automatically find robust keypoints.

3. **Affine Transformation**:
    - Use reference keypoints (e.g., ideally both eyes) to calculate rotation/shear matrices (`cv2.getAffineTransform`).
    - Warp the image (`cv2.warpAffine`) to make the turtle head upright and remove perspective distortions.

#### **Step D: Image Cropping**
Purpose: Output cropped turtle head for Module B.

1. **Bounding Box Identification**:
    - Use the bounding box output from Module A to crop the turtle head region (`cv2.boundingRect`).
    - Perform cropping with a margin to avoid cutting off critical features.

2. **Aspect Ratio and Standardization**:
    - Resize cropped images to a uniform 224x224 dimension (`cv2.resize`) to ensure compatibility with downstream models.

#### **Step E: Data Augmentation**
Purpose: Enhance dataset diversity for better generalization of models.

1. **Rotation and Scaling**:
    - Apply small rotation adjustments (e.g., ±[0–15 degrees]) around the center of the crop (`cv2.getRotationMatrix2D`).
    - Scale images to simulate proximity or distance to the turtle (`cv2.resize`).

2. **Color Variations**:
    - Perturb hue, saturation, and brightness values. Apply this selectively while ensuring visibility of scale features (`cv2.addWeighted` to tweak channels).

3. **Noise Simulation**:
    - Inject lightweight Gaussian noise to simulate underwater turbidity.
    - Use kernel-based blurring techniques (bilateral or median filters).

4. **Perspective Variations**:
    - Apply perspective transformations (`cv2.getPerspectiveTransform` and `cv2.warpPerspective`) to simulate different angles.

---

### **3. End-to-End Pipeline Flow**
1. Load raw image.
2. Apply light and contrast optimization (Step A).
3. Apply noise-reduction filtering (Step B).
4. Detect edges and keypoints for head boundary establishment.
5. Perform affine transformations to normalize head alignment (Step C).
6. Crop head using bounding box and resize to 224x224 (Step D).
7. Apply augmentations for dataset expansion (Step E).

---

## **Integration with Existing SOLID Codebase**

### **Module A: Head Detection**
- Pretrained lightweight YOLO model (e.g., YOLOv5s or YOLOv8n) for head detection.
- Train on preprocessed image dataset with bounding box annotations.
- Output: Bounding box coordinates of detected head.

### **Module B: Orientation Classifier**
- Lightweight CNN architecture (e.g., MobileNetV2 or EfficientNet-B0).
- Train on preprocessed cropped head dataset labeled with orientation.
- Input: 224x224 preprocessed head crops from Module A output.
- Output: Orientation class ("left," "right," "top").

### **Integration Strategy**
1. Integrate preprocessing pipeline into Module A as part of input normalization.
2. Enable Module A to call the preprocessing pipeline, detect turtle head, and pass cropped head images into Module B.
3. Modify existing `identifier.py` script to accept raw images as input, run Module A and Module B sequentially, and automatically query the correct FAISS Index based on orientation classification.

---

## Conclusion
A robust preprocessing pipeline is critical for addressing underwater imaging challenges and standardizing image quality for Module A and Module B. By employing OpenCV techniques such as CLAHE, affine transformations, and adaptive filtering, the pipeline ensures consistent and high-quality inputs for detection and classification models.