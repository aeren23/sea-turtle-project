### Report on Architectural Roadmap  

#### **1. Dependency & Ordering**  
- **Module A (Head Detection)** must be developed first because the outputs (accurately cropped turtle heads) are essential inputs for **Module B (Orientation Classifier)**. Module B’s accuracy depends on the consistent input quality from Module A.  

#### **2. Algorithm Selection**  

##### **For Module A (Head Detection):**  
- **Architecture Recommendation:** YOLO-based models such as YOLOv5n (nano version) or YOLOv8n. These lightweight architectures are optimized for speed and accuracy in real-time inference pipelines.  
- **Reasoning:** YOLO excels in object detection while keeping computational costs minimal, ensuring robust detection in varied underwater conditions.  

##### **For Module B (Orientation Classifier):**  
- **Architecture Recommendation:** A MobileNetV2 or EfficientNet-B0 based classifier. These models are lightweight, computationally efficient, and suited for edge-based or production environments.  
- **Reasoning:** High accuracy in multi-class classification tasks with the ability to run inference quickly on GPU/CPU.  

#### **3. Integration Strategy**  
- **Step 1:** Replace manual bounding box input in `identifier.py` with automated cropping using Module A. Confirm bounding box accuracy with evaluation metrics (e.g., mAP).  
- **Step 2:** Feed cropped images into Module B. Use its prediction (`left`, `right`, or `top`) to directly select the appropriate FAISS database for querying (`faiss_left.bin`, `faiss_right.bin`, `faiss_top.bin`).  
- **Step 3:** Integrate preprocessing into the pipeline:  
  - Apply **CLAHE** for contrast enhancement of underwater images pre-Module A.  
  - Perform **color correction** using BGR→LAB or BGR→HSV for natural light normalization.  
  - Apply **Gaussian/Bilateral filtering** for noise reduction while preserving edge details (critical for detecting scale patterns).  
  - Standardize image size to 224x224 with padding/cropping after cropping in Module A.  
- **Step 4:** Modularize Python functions for head detection, orientation classification, and preprocessing as microservices, adhering to SOLID principles for easy updates.  

#### **4. Additional Considerations**  
- **Dataset Curation:** Collaborate with marine biologists to curate and label a dataset tailored for both modules. Consider both public and custom datasets.  
- **Augmentations:** Focus on underwater-specific augmentations like brightness changes, fog simulation, and motion blur for Module A. Rotation and scaling for Module B should respect biologically valid constraints.