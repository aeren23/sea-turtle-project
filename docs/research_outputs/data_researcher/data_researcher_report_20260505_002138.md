# Dataset Considerations Report for Phase 3 Production Inference Pipeline

## Objective:
This report focuses on dataset constraints, augmentation needs, and image quality for building an end-to-end production inference pipeline for the automated biometric identification of sea turtles. Our responsibility is to address the dataset implications for two modules:
- **Module A (Head Detection)**: Detect and crop the head of a sea turtle from raw, uncropped photographs.
- **Module B (Orientation Classifier)**: Classify the cropped turtle head into one of three orientations: "left," "right," or "top."

This response excludes algorithmic design and focuses on imaging challenges and dataset preparation.

---

## **1. Dependency & Ordering: Which Model Must Be Developed First?**

### Dataset Implication:
The development of **Module A (Head Detection)** must precede Module B because:
1. **Bounding Box Input Dependency**: The Orientation Classifier for Module B only requires cropped head images for training and inference. Therefore, generating a dataset of cropped turtle heads necessitates the functionality provided by Module A first.
2. **Data Source Workflow**: The primary dataset will consist of raw, uncropped underwater turtle photographs. Without a reliable head detection module (Module A), it is impossible to create a focused and labeled dataset for Module B.
3. **Error Propagation**: The quality and accuracy of Module B are tightly linked to Module A. Poorly cropped heads from Module A would degrade the orientation classification performance.

**Conclusion**: Module A absolutely must be completed first to define reliable downstream input for Module B.

---

## **2. Dataset Considerations and Challenges**

### **Module A: Head Detection Dataset Considerations**
#### Data Collection Requirements:
- **Real-World Representation**:
  - Images should be collected from diverse aquatic environments to represent the variability in water visibility, turbidity, and lighting conditions to avoid a biased detection model.
  - Images should include multiple species (e.g., *Caretta caretta* and *Chelonia mydas*) and capture variability in postures, sizes, and environmental occlusions.
  - Dataset must include all possible positions of the turtle relative to the camera plane (head-on, side-facing, partially turned heads, etc.).

#### Data Annotation:
- **Bounding Box Annotations**:
  - Each sea turtle head in the image must have manually labeled bounding boxes (*x_min, y_min, x_max, y_max*). These annotations should ignore the body of the turtle if it's visible and explicitly isolate the head for clarity.
- Recommended Tool: LabelImg (open source, simple to use, and widely supported).

#### Challenges:
- **Underwater Quality Issues**:
  - Lighting: Dim or artificially colored light.
  - Mid-water obstructions: Errors due to floating particles, sediment, or marine plants.
  - Angle Diversity: Images where turtle heads appear very small or are partially obscured might require pre-selection or be designated as "hard negatives."
  
#### Dataset Augmentation for Module A:
To increase dataset size while accurately modeling underwater conditions:
- **Safe Transformations**:
  - **Random Cropping with Margin Preservation**: Augment bounding boxes by adjusting their surrounding margins slightly, simulating different head sizes and slightly shifted crops.
  - **Rotation**: Minimal angles only (<15 degrees), simulating natural head or camera tilt.
  - **Scale Transformations**: Increase/decrease turtle head size to incorporate varied camera distances.
  - **Blur and Noise Injection**: Replicate turbidity by adding Gaussian blur or noise.
  
- **Prohibited Transformations**:
  - Horizontal flipping must be avoided due to asymmetry in head patterns and subsequent use in Module B.

### **Module B: Orientation Classification Dataset Considerations**
#### Data Collection Requirements:
- **Cropped Head Dataset**: Derived from the Module A output, containing tightly cropped images of turtle heads along with proper orientation labels (“left,” “right,” or “top”).
- **Orientation Diversity**:
  - The dataset must include sufficient examples of all three orientations with balanced class distribution.
  - "Ambiguous orientations" (e.g., between "left" and "top") should be labeled explicitly and separated into test sets to evaluate edge-case performance.

#### Challenges:
- **Consistency vs. Ambiguity**:
  - Due to the curved structure of a sea turtle’s head, some orientations may overlap marginally (e.g., "top-right"). This overlap may confuse the classifier, so edges cases require high-quality labeling by marine experts.
- **Transfer of Augmentation Artifacts**:
  - Since this model is unavoidably dependent on the data from Module A, any augmentation pipeline used for head detection *must not introduce patterns* that could bias orientation classification (e.g., tilts caused by imbalanced rotation augmentations).

#### Dataset Augmentation for Module B:
- **Safe Transformations**:
  - **Rotation**: Permitted but should not excessively alter the labeled orientation (e.g., 15-degree clockwise rotation of a “left”-oriented head remains “left”).
  - **Supervised Horizontal Shifting**: Minor shifts to mimic slight positional differences.
  - **Color Adjustments**: Adjust chromaticity (hue/saturation) to model variations in underwater lighting.
  - **Gaussian Noise**: Simulate random environmental blur.
- **Prohibited Transformations**:
  - Horizontal flipping is strictly forbidden to avoid unnecessary orientation mislabeling.

---

## **3. Integration of Dataset into the Pipeline**

### Integrating Module A:
1. **Pretraining**:
   - Start training with generalized object detection datasets (such as COCO or OpenImages) to initialize weights before fine-tuning on the turtle-specific dataset.
2. **Evaluation Dataset**:
   - A subset of uncommon variations (e.g., murky water, partial head visibility) must be reserved for evaluation to mimic real-world deployment conditions.
3. **Dataset Split**:
   - **Train Set**: 75% of labeled images.
   - **Validation Set**: 15%, ensuring it includes edge cases.
   - **Test Set**: 10%, emphasizing hard-to-detect examples.

### Integrating Module B:
1. **Cropped Head Dataset**:
   - Annotation for cropped head orientation must come from marine biology experts. The dataset must ensure mutually exclusive "left," "right," and "top" labels for all samples.
2. **Dataset Split**:
   - **Train Set**: 70%, covering all three orientations in similar proportions.
   - **Validation Set**: 20%, balanced representation to monitor classification learning.
   - **Test Set**: 10%, enriched with ambiguous edge cases for orientation assessment.
   
3. **Hard Negative Mining**:
   - Images where Module A produces incorrect crops should specifically be added to the training/validation set, to improve robustness against detection misclassifications.
---

## **Key Dataset Sources**
1. **Public Image Repositories**:
   - Kaggle (Potential search terms: “sea turtle image datasets,” “marine wildlife datasets”)
   - Mendeley Data (Oceanographic research repositories)
   - ImageNet subcategories (might include marine animals but will require filtering).

2. **Scientific Open-Access Repositories**:
   - OBIS SEAMAP: Includes wildlife photos and geodata for marine species.
   - GBIF (Global Biodiversity Information Facility) Datasets: Images of *Caretta caretta* and *Chelonia mydas* are often linked to specimen records.

3. **Citizen Science Contributions**:
   - iNaturalist and Wildbook platforms could be potential sources of additional labeled imagery for turtles. Cross-referencing with research communities can provide higher-quality annotation data.

4. **Specialized Partnerships**:
   - Collaborate with local marine research institutes or NGOs specializing in sea turtle conversation (e.g., The Sea Turtle Conservancy), many of which have robust photo-identification databases.

---

## Dataset Summary Table

| **Module**    | **Data Needed**             | **Challenges**                                     | **Augmentation**                                                                     |
|----------------|-----------------------------|---------------------------------------------------|-------------------------------------------------------------------------------------|
| **Module A**   | Uncropped sea turtle images with bounding box labels for heads. | Light refraction, turbidity, visibility changes; head-size variations.               | Random cropping, slight rotation, blur/noise addition, brightness/contrast changes. |
| **Module B**   | Cropped head images labeled "left," "right," or "top".          | Border orientations (e.g., top-right, left-top), class balance.                      | Rotation, hue/saturation adjustment, supervised horizontal shifts.                  |

---

This report outlines the dataset requirements, potential sources, challenges, and augmentation strategies required to train and deploy the new AI modules effectively.