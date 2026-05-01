# Project Specification Document (spec.md)
**Project Name:** SeaTurtle Photo-ID: AI-Powered Sea Turtle Recognition and Tracking System
**Developer:** Ali Eren Oğuztaş
**Institution:** Pamukkale University & DEKAMER (Conceptual Integration)

## 1. Project Purpose and Summary
The primary goal of this project is to develop a non-invasive biometric identification system to track sea turtle populations (Chelonia mydas, Caretta caretta, etc.), migration routes, and life cycles.

The "post-ocular" (behind-the-eye) scale patterns on the side of each sea turtle's face are entirely unique and individual-specific, much like human fingerprints[cite: 1]. This system aims to perform turtle identification (Photo-ID) automatically and with high accuracy using image processing (Computer Vision) and Deep Learning algorithms on photo data obtained from underwater cameras or researchers[cite: 1].

## 2. Problem Definition
Traditional turtle tagging methods (plastic flipper tags, PIT tags) are not only costly but can also be traumatic for the turtles, may fall off over time, or create problems such as reader incompatibility[cite: 1]. Although current Photo-ID methods are reliable and inexpensive, the process of matching photos manually or with simple software by researchers is extremely slow and prone to error[cite: 1].

Additionally, in data obtained from underwater environments (core dataset of approximately 600 images):
*   **Light Imbalances:** Underwater light refractions, blurriness, and color aberrations.
*   **Angle Differences:** Variations in distance to the camera, head tilts (roll, pitch, yaw), and perspective differences.

## 3. Solution Approach and System Architecture
The project is designed as an end-to-end software system where raw photos are taken and identity IDs are returned. The system consists of three main components:

### 3.1. Image Preprocessing (Preprocessing Pipeline)
*   **Face Detection:** A cropping process that focuses only on the profile face line by discarding unnecessary background and the turtle's body.
*   **Angle and Perspective Correction:** Alignment of the face profile to a standard horizontal plane relative to reference points (e.g., eye) using Affine Transformations.
*   **Light and Contrast Optimization:** Application of CLAHE (Contrast Limited Adaptive Histogram Equalization) and masking filters to balance shadows and light glares in underwater photos.

### 3.2. Artificial Intelligence and Classification Model (AI Core)
*   A Convolutional Neural Network (CNN) architecture (e.g., a fine-tuned model based on ResNet or EfficientNet) trained to perform feature extraction from standardized images.
*   The model predicts the IDs of turtles previously registered in the system along with a confidence score.

### 3.3. Web Platform and Backend
*   A .NET 8-based RESTful API / Microservice architecture designed according to Clean Architecture principles, where users can upload photos, register new turtles to the system, or query existing ones.
*   The AI model will be integrated into the backend system as an independent service.

## 4. Technical Requirements (Functional Requirements)
*   The system must be able to detect whether there is a turtle head in the uploaded photo.
*   The system should automatically standardize the uploaded photo (light, angle) and convert it into the format accepted by the model (e.g., 224x224 RGB).
*   The system must match a known turtle with its ID in the database with a high accuracy rate.
*   If no match is found, the system should report this as a "New/Unknown Individual."

## 5. Software Quality Requirements (Non-Functional Requirements)
The project codebase must strictly adhere to the following engineering standards:
*   **Clean Code:** Clear, self-documenting, free of magic numbers, and modular functions.
*   **SOLID Principles:**
    *   Classes must be designed according to the Single Responsibility Principle (SRP) (the class reading the image cannot be the same as the class training the model).
    *   The system should be open to new models and filters but closed to change (Open/Closed Principle).
    *   Loose coupling between modules should be ensured using Dependency Injection.

## 6. Dataset Constraints
*   Model training is limited to the existing dataset of ~600 turtle photos. Data Augmentation techniques (rotation, color shifting, etc.) will be applied to prevent model overfitting.