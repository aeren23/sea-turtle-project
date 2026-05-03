# 🧠 SeaTurtle Photo-ID: Model Training Flow (ResNet-50 Fine-Tuning)

**Date:** 2026-05-03  
**Status:** ✅ Logged & Explained  
**Project:** DEKAMER Sea Turtle Recognition System  

---

## 🌊 Overview: Why ResNet-50?
In this project, we utilize **ResNet-50**. However, we do not use it merely as a static image processor. Instead, **ResNet-50 IS the model we are training**. 

We employ **Transfer Learning (Fine-Tuning)**. The model begins pre-trained on ImageNet (general objects) and already knows how to detect edges and textures. Through our training loop in `train.py`, we teach it to specialize exclusively in "Sea Turtle Post-Ocular Scales."

---

## ⚙️ The Deep Learning Training Flow

The training cycle runs for a specified number of epochs (e.g., 20). During each epoch, the following sequence occurs hundreds of times in the background:

### Step 1: Data Loading (Dataloader & Sampler)
*   The system selects a "Batch" of images (e.g., 32 images).
*   *Crucial Constraint:* It ensures that within this batch, there are multiple images of the *same* turtle (e.g., 8 turtles, 4 photos each).
*   Data augmentation (Rotation, Color Jitter, Elastic Deformation) is applied on the fly.

### Step 2: Vector Embedding (Forward Pass)
*   The 32 images are fed into our custom `TurtleResNet`.
*   The network acts as an automatic **Keypoint/Edge Detector**. Instead of manually finding scale corners, the deep convolutional layers naturally lock onto the most distinct patterns.
*   The final layer compresses these patterns into a **512-dimensional vector (fingerprint)** for each image.
*   *Initial State:* At Epoch 1, the model is ignorant. It might produce completely different vectors for photos of the same turtle.

### Step 3: The Penalty (Triplet Loss)
*   The `loss.py` module evaluates the vectors.
*   It looks at an "Anchor" (Turtle A), a "Positive" (another photo of Turtle A), and a "Negative" (Turtle B).
*   If the model produced similar vectors for A and B, or different vectors for the two photos of A, the Triplet Loss algorithm calculates a massive **Error Score (Loss)**.
*   *Hard Negative Mining:* The system specifically hunts for the most difficult mistakes (e.g., Turtle A and Turtle B look identical to the human eye but are different).

### Step 4: Learning (Backward Pass & Optimizer)
*   The optimizer (AdamW) takes the Error Score and performs **Backpropagation**.
*   It updates the ~25 million mathematical weights inside ResNet-50.
*   The model "learns" from its mistake, mathematically adjusting its internal filters to push the "Positive" vectors closer together and the "Negative" vectors further apart in the 512-d hyperspace.

### Step 5: Specialization (Epochs)
*   This cycle repeats for the entire dataset of ~600 images over 20 epochs.
*   By the end of the training, the model transitions from a general-purpose object detector into an elite **Sea Turtle Expert**, capable of generating consistent, distinct digital fingerprints for every individual turtle.
