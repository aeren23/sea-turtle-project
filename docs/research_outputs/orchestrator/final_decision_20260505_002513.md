## Comprehensive Strategic Document: Phase 3 Architectural Roadmap for Autonomous Sea Turtle Biometric ID System

### **1. Dependency & Ordering**
**Key Decision**: Develop **Module A (Head Detection)** first, as it provides the essential cropped input images required by **Module B (Orientation Classifier)**. Orientation classification depends on accurate head cropping, making Module A development a prerequisite for successful pipeline integration. Hence:
- **First Priority**: Train and validate Module A.
- **Next Step**: Utilize Module A's output to train Module B seamlessly.

---

### **2. Algorithm Selection**
#### **Module A: Head Detection**
- **Architecture Recommendation**: Use **YOLOv5 Nano** or **YOLOv8 Nano** due to their:
  - Lightweight design suitable for fast inference in production.
  - Strong object detection performance in real-time environments, especially under challenging underwater conditions.
  - Compatibility with small datasets and robust performance even with minimal computational resources.

#### **Module B: Orientation Classifier**
- **Architecture Recommendation**: Use **MobileNet-V3 Small** due to:
  - High accuracy in classification tasks with lightweight inference requirements.
  - Efficient handling of preprocessed cropped head images, classifying them as “left,” “right,” or “top.”

Considerations:
- Both models should be trained with underwater-specific data augmentations to enhance domain performance.

---

### **3. Data Requirements and Augmentation**
#### **Data Needs for Module A (Head Detection)**:
- Annotated bounding boxes around sea turtle heads in raw underwater images.
- A mixture of real-world underwater environments that capture variations in lighting, turbidity, and motion blur.
- If suitable public datasets (e.g., “SeaTurtle ID” or “iNaturalist”) are unavailable or insufficient, manually annotating the project’s existing ~600-image dataset will be necessary.
  
**Augmentation Techniques**:
- **Preserve Biological Constraints**: No horizontal flips due to asymmetry of head scales.
- Vertical flips (to simulate various head orientations encountered underwater).
- Controlled ±25° rotation distortions to mimic different angles of observation.
- Brightness/contrast enhancements and elastic distortions to replicate underwater lighting and refraction.

#### **Data Needs for Module B (Orientation Classifier)**:
- Preprocessed high-quality cropped images from Module A output, labeled as “left,” “right,” or “top.”
- Ensure all cropped images maintain clear visibility of post-ocular scale patterns.

**Augmentation Techniques**:
- **Preserve Biological Constraints**: No horizontal flips; focus solely on vertical transformations and restricted ±15° rotations.
- CLAHE preprocessing to enhance visibility of critical landmark regions.
- Mask backgrounds and extraneous features to highlight post-ocular scale clarity.
- Slight color shifting to counter variability in underwater lighting.

**Critical Data Integration**: Link Module A's training dataset to Module B's by ensuring bounding box crops align correctly with orientation labels. Any discrepancy will degrade Module B performance.

---

### **4. Integration Strategy**

#### **System Workflow Overview**:
The end-to-end system must handle raw input images and return the turtle’s unique ID without manual intervention. This will entail:
1. **Step 1**: Raw photo uploaded → sent to Module A for head detection and cropping.
2. **Step 2**: Cropped head → sent to Module B for orientation classification (left, right, or top).
3. **Step 3**: Classified orientation determines which FAISS index (faiss_left.bin, faiss_right.bin, or faiss_top.bin) will be queried using the existing embedding-based pipeline.

#### **Implementation Details**:
- **Software Design Principles**: Use SOLID principles.
  - Create a `Detection` class for head detection (Module A).
  - Create a `Classifier` class for orientation classification (Module B).
  - Replace current manual bbox and `--side` flags within `identifier.py` by calling these classes.

- **Error Handling**:
  - If Module A fails to locate a head, return an informative error (e.g., “No turtle head detected”).
  - Add safeguards to ensure that Module B processes only validated outputs from Module A.

**API Integration**:
- Package the modules into callable APIs for ease of deployment in operational settings.
- Modularize preprocessing so it can be reused or adjusted for both detection and classification tasks.

---

### **5. Preprocessing Pipeline**
#### **Module A (Head Detection)**:
- **Input**: Raw underwater image resized to 640x640 (retaining aspect ratio).
- **Preprocessing Steps**:
  - CLAHE for contrast enhancement.
  - Convert BGR to LAB or HSV for color correction to address underwater lighting.
  - Bilateral filtering to remove noise while preserving edges.
- **Augmentation**: Apply vertical flips, ±25° rotations, elastic distortions, and brightness/contrast adjustments.

#### **Module B (Orientation Classification)**:
- **Input**: Cropped images from Module A, resized to 224x224.
- **Preprocessing Steps**:
  - CLAHE to enhance visibility of scales around the post-ocular region.
  - Foreground masking to isolate scale patterns from irrelevant background noise.
- **Augmentation**: Apply ±15° rotations, minor color shifts, and contrast enhancements.

Consistency across both Modules A and B preprocessing pipelines ensures smooth data flow and compatibility.

---

### **6. Lightweight Model Deployment**
- **Inference System**: Deployed models should maintain minimal latency to function efficiently in a production environment.
- **Hardware Constraints**: Both YOLO Nano and MobileNet-V3 Small architectures are optimized for low-power hardware, ensuring deployment feasibility.
- **Continuous Monitoring**: Establish a cycle for feedback-driven model refinement post-deployment, incorporating real-world input images that challenge current model performance.

---

### **7. Next Steps**
1. **Data Preparation**:
   - Review available datasets for bounding box annotations and orientation labels.
   - If gaps exist, immediately allocate resources for manual annotation of the existing 600-image dataset.

2. **Model Training**:
   - Train Module A (YOLOv5/YOLOv8 Nano) using the curated dataset with robust augmentations.
   - Use Module A’s output to create a cropped dataset for training Module B (MobileNet-V3 Small).

3. **Pipeline Integration**:
   - Code and test end-to-end flow from raw photo input to FAISS index query, ensuring accuracy and performance benchmarks are met.

4. **Validation**:
   - Conduct comprehensive testing using a diverse test set to evaluate robustness under varied underwater conditions.
   - Ensure the pipeline meets biological accuracy requirements and adheres to biometric principles.

---

### **8. Conclusion**
By prioritizing Module A's development and leveraging lightweight, efficient models for both tasks, the Sea Turtle Photo-ID system can be enhanced to a fully autonomous state. The integration of these AI-based modules into the existing SOLID framework will create a robust and scalable solution for real-world application. With focused dataset preparation, rigorous preprocessing, and planned error handling, the pipeline will provide an accurate and seamless end-to-end biometric identification system for sea turtles, meeting both technical and biological constraints.