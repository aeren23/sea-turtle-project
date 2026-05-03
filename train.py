"""
Main training entry point for SeaTurtle Photo-ID Metric Learning.
"""

import os
import sys
import torch
from torch.utils.data import DataLoader
from pytorch_metric_learning import samplers

from src.data.turtle_dataset import SeaTurtleDataset
from src.data.augmentation import get_train_transforms, get_val_transforms
from src.models.turtle_resnet import TurtleResNet
from src.training.loss import get_triplet_loss_and_miner
from src.training.metrics import get_accuracy_calculator
from src.training.trainer import MetricLearningTrainer

def main():
    # 1. Configuration
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    num_epochs = 20
    batch_size = 32
    embedding_dim = 512
    margin = 0.2
    learning_rate = 1e-4

    # 2. Datasets & DataLoaders
    print("Loading datasets...")
    # NOTE: In Metric Learning, each batch MUST contain multiple images of the same 
    # individual so the Triplet Loss can form Positive pairs.
    # We use MPerClassSampler to guarantee this.
    
    train_dataset = SeaTurtleDataset(split="train", transform=get_train_transforms())
    
    # We need labels array for the sampler
    train_labels = [train_dataset.identity_to_idx[dto.identity] for dto in train_dataset.data]
    
    # MPerClassSampler ensures each class in the batch has exactly m instances
    # Here m=4 means we pick 8 turtles, and 4 photos of each -> batch size 32
    train_sampler = samplers.MPerClassSampler(
        labels=train_labels,
        m=4, 
        batch_size=batch_size,
        length_before_new_iter=len(train_dataset)
    )
    
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        sampler=train_sampler,
        num_workers=4,
        pin_memory=True
    )

    # For evaluation, we use standard dataloaders without augmentation
    query_dataset = SeaTurtleDataset(split="valid", transform=get_val_transforms())
    gallery_dataset = SeaTurtleDataset(split="train", transform=get_val_transforms()) # Gallery can be train set + valid knowns
    
    query_loader = DataLoader(query_dataset, batch_size=batch_size, shuffle=False)
    gallery_loader = DataLoader(gallery_dataset, batch_size=batch_size, shuffle=False)

    # 3. Model, Optimizer, Loss
    print("Initializing model...")
    model = TurtleResNet(embedding_dim=embedding_dim, pretrained=True).to(device)
    
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    miner, loss_func = get_triplet_loss_and_miner(margin=margin)
    
    accuracy_calculator = get_accuracy_calculator()

    # 4. Trainer
    trainer = MetricLearningTrainer(
        model=model,
        optimizer=optimizer,
        loss_func=loss_func,
        miner=miner,
        device=device,
        save_dir="checkpoints"
    )

    # 5. Training Loop
    print("Starting training loop...")
    best_map = 0.0
    for epoch in range(1, num_epochs + 1):
        # Train
        trainer.train_epoch(train_loader, epoch)
        
        # Evaluate
        map_score = trainer.evaluate(query_loader, gallery_loader, accuracy_calculator, epoch)
        
        # Save best model
        if map_score > best_map:
            best_map = map_score
            trainer.save_checkpoint(epoch, best_map, filename="best_turtle_resnet.pth")

if __name__ == "__main__":
    # Protect entry point for multiprocessing in Windows
    main()
