**Architectural Roadmap for Autonomous Sea Turtle Biometric ID Preprocessing Pipeline**

### 1. **Dependency & Ordering**
- **Priority**: Develop **Module A (Head Detection)** first. Accurate head cropping is a prerequisite for orientation classification in Module B. Without reliable head detection, orientation classification becomes infeasible.

---

### 2. **Algorithm Selection**
#### **Module A (Head Detection)**: 
   - Use **YOLOv5 Nano** or **YOLOv8 Nano** due to their lightweight architecture and strong detection performance in constrained environments. These models are ideal for detecting turtle heads efficiently within underwater photos.
   - Assumes training on a dataset with bounding box annotations around sea turtle heads.

#### **Module B (Orientation Classifier)**:
   - Implement **MobileNet-V3 Small** for classification. It provides high accuracy with a low computational footprint, making it suitable for production pipelines. Train on cropped turtle faces labeled as “left,” “right,” or “top.”

---

### 3. **Preprocessing Pipeline**
#### **Module A Preprocessing**:
- Normalize input image dimensions: Resize to 640x640 for YOLOv5/YOLOv8 detection, retaining aspect ratio.
- Perform underwater-specific preprocessing:
  - **CLAHE**: Improve visibility and balance contrast distorted by underwater lighting.
  - **Color correction**: Convert from BGR→LAB or HSV to mitigate blue/green casts.
  - **Filtering**: Bilateral filter to suppress noise while preserving edges.
- Data Augmentation:
  - Vertical flips, ±25° rotation, elastic distortions (water refraction mimicry).

#### **Module B Preprocessing**:
- Cropped image normalization: Resize to 224x224.
- Enhance post-ocular scale clarity:
  - **Contrast Stretching/CLAHE**: Focus visibility on the eye region and scale patterns.
  - **Masking**: Highlight only relevant areas (e.g., removing background elements).
- Augmentations: ±15° rotation, color shifting for underwater realism.

---

### 4. **Integration Strategy**
- **Pipeline Flow**:
  - Input raw photo → Standardized preprocessing (Module A pipeline) → Head detection with bounding box cropping → Cropped image preprocessing (Module B pipeline) → Orientation classification.
- Integrate both modules as callable services within `identifier.py`, replacing manual bbox input and `--side` flags.
- Use SOLID principles: Abstract YOLO head detection into a Detection class and orientation classification into a Classifier class. These classes can be instantiated and tested independently.
- Add error-handling mechanisms for head detection failures, ensuring graceful degradation and error reporting.

---

### 5. **Next Steps**
- Review datasets such as SeaTurtle ID and iNaturalist. If annotated datasets are missing, allocate resources for manual data annotation.
- Train YOLO-based head detection model using augmented dataset.
- Obtain cropped images from Module A output and train MobileNet-V3 for orientation classification.
- Test pipeline end-to-end using a diverse test set to ensure seamless operation and sufficient accuracy before deploying APIs.

--- 

Consistency across preprocessing steps and augmentation methods will ensure compatibility, accurate inference, and quicker deployment in production systems.