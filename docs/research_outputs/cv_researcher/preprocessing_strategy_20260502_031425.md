# OpenCV-Based Image Preprocessing Pipeline for Underwater Sea Turtle Photographs

## Overview
This pipeline is designed to normalize underwater sea turtle photographs for consistent model input. It addresses common issues like non-uniform lighting, color casts, and varying angles to prepare images for a CNN-based identification system.

## Pipeline Steps

### 1. Face Detection & Cropping
**Objective**: Isolate the turtle's head profile, discarding the body and background.
- **OpenCV Function**: `cv2.CascadeClassifier`, `cv2.findContours`
- **Parameters**:
    - Use a pre-trained Haar cascade for turtle face detection.
- **Process**:
    - Convert the image to grayscale: `gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`
    - Load the classifier: `face_cascade = cv2.CascadeClassifier('path_to_cascade.xml')`
    - Detect faces: `faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)`
    - Crop the image around the detected face for further processing.

### 2. Angle/Perspective Correction
**Objective**: Align the face profile to a standard horizontal orientation using eye landmarks.
- **OpenCV Function**: `cv2.getAffineTransform`, `cv2.warpAffine`
- **Parameters**:
    - Points for Eye Landmark Detection: Choose points around the eyes and mouth.
    - Standard Points: Define a reference frame for alignment.
- **Process**:
    - Calculate the affine transform matrix: `M = cv2.getAffineTransform(np.float32(src_points), np.float32(dst_points))`
    - Apply the transformation: `corrected_image = cv2.warpAffine(cropped_image, M, (output_width, output_height))`

### 3. Light & Contrast Optimization
**Objective**: Apply CLAHE to equalize underwater lighting variations.
- **OpenCV Function**: `cv2.createCLAHE`
- **Parameters**:
    - Clip Limit: Set to 2.0 to enhance local contrast.
    - Tile Size: Use (8, 8) to focus on local regions of the image.
- **Process**:
    - Convert the image to LAB color space: `lab_image = cv2.cvtColor(corrected_image, cv2.COLOR_BGR2LAB)`
    - Split channels: `L_channel, A_channel, B_channel = cv2.split(lab_image)`
    - Apply CLAHE: `clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))` and then `L_channel = clahe.apply(L_channel)`
    - Merge channels back: `clahe_image = cv2.merge((L_channel, A_channel, B_channel))`
    - Convert back to BGR: `final_image = cv2.cvtColor(clahe_image, cv2.COLOR_LAB2BGR)`

### 4. Underwater Color Correction
**Objective**: Compensate for blue/green color cast typical of underwater environments.
- **OpenCV Function**: `cv2.cvtColor`, `cv2.addWeighted`
- **Parameters**:
    - Calculate gains for corrections based on the average RGB values.
- **Process**:
    - Convert to LAB or HSV color space to adjust colors: `hsv_image = cv2.cvtColor(final_image, cv2.COLOR_BGR2HSV)`.
    - Adjust the S (saturation) and V (value) channels to reduce blue/green: `hsv_image[:,:,1] = hsv_image[:,:,1] * saturation_factor`
    - Convert back to BGR for further processing.

### 5. Output Standardization
**Objective**: Produce 224x224 RGB images suitable for CNN input.
- **OpenCV Function**: `cv2.resize`
- **Parameters**:
    - Interpolation Method: Use `cv2.INTER_LINEAR` for resizing.
- **Process**:
    - Resize the final image: `standardized_image = cv2.resize(final_image, (224, 224), interpolation=cv2.INTER_LINEAR)`

## Rationale for Execution Order
1. **Face Detection & Cropping**: It is crucial to isolate the turtle's head for subsequent steps, reducing noise from the body and background.
2. **Angle/Perspective Correction**: Correcting the orientation early ensures that issues related to lighting and color optimization affect the turtle's face rather than other parts of the image.
3. **Light & Contrast Optimization**: After correcting the orientation, enhancing contrast helps in revealing features in underwater environments.
4. **Underwater Color Correction**: After optimizing the light conditions, adjusting colors ensures that color casts are remedied effectively, enhancing visibility of features.
5. **Output Standardization**: Finally, resizing the image ensures that it fits the input dimensions required by the model consistently.

## Conclusion
This preprocessing pipeline utilizes key OpenCV techniques to create standardized images of underwater sea turtles, significantly improving the image quality for better identification in a CNN framework.