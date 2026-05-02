# Sea Turtle Photo Datasets for Photo-ID Research

## 1. Sea Turtle ID 2022 Dataset
- **Source**: [Project URL](https://www.seaturtleid2022.org)
- **Size**: 8,729 photographs
- **Species Covered**: Caretta caretta (Loggerhead), Chelonia mydas (Green), and Kemp's ridley (Lepidochelys kempii)
- **Image Quality**: High quality, collected over 13 years with diverse environmental conditions.
- **Annotation Type**: Individual tracker based on unique facial markings and patterns.
- **Relevance to Facial Scale Pattern Recognition**: Specifically designed for Photo-ID procedures, emphasizing the unique facial scale patterns behind the eyes of turtles.

## 2. WildlifeDatasets Sea Turtle Dataset
- **Source**: [GitHub Repository](https://github.com/wildlife-datasets/wildlife_datasets)
- **Size**: 7,582 photographs of 400 unique individuals
- **Species Covered**: Primarily Caretta caretta and Chelonia mydas
- **Image Quality**: Quality varies; includes both close-up and wider shots; some images affected by underwater conditions.
- **Annotation Type**: Markings documented for individual ID.
- **Relevance to Facial Scale Pattern Recognition**: Supports photo-ID through detailed annotations of individuals which include scale patterns.

## 3. Kaggle Wildlife Dataset
- **Source**: [Kaggle Dataset](https://www.kaggle.com/datasets)
- **Size**: Around 5,400 images involving various wildlife including sea turtles.
- **Species Covered**: Varies, includes multiple species.
- **Image Quality**: Diverse quality; recommendations for utilizing specific images suited for close-up facial recognition if applicable.
- **Annotation Type**: General species classification with potential specific annotations available upon request.
- **Relevance to Facial Scale Pattern Recognition**: Limited, as it includes broader wildlife; focus on individual sea turtle images may be low.

## Data Augmentation Strategies
1. **Rotation**: Apply small rotations (up to 10 degrees) to simulate different angles while preserving scale patterns.
2. **Color Jitter**: Modify brightness, contrast, and saturation to mimic changing underwater lighting conditions, ensuring biological validity.
3. **Horizontal Flip**: Randomly flip images horizontally; anatomical features should remain consistent for individual identification.
4. **Elastic Deformation**: Introduce slight deformations to mimic natural variations in scale patterns, promoting better generalization without altering species-specific features.

These augmentation techniques can expand the existing dataset of approximately 600 images, improving model robustness and preventing overfitting during training.