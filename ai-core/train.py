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
from src.training.loss import get_arcface_loss
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

    # Datasets & DataLoaders
    print("Loading datasets...")
    train_dataset = SeaTurtleDataset(split="train", transform=get_train_transforms())
    num_classes = len(train_dataset.identity_to_idx)
    
    # ArcFace does not require a special sampler, standard shuffle is fine
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True,
        num_workers=0,
        pin_memory=True
    )

    # For evaluation, we use standard dataloaders without augmentation
    query_dataset = SeaTurtleDataset(split="valid", transform=get_val_transforms())
    gallery_dataset = SeaTurtleDataset(split="train", transform=get_val_transforms()) # Gallery can be train set + valid knowns
    
    query_loader = DataLoader(query_dataset, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=True)
    gallery_loader = DataLoader(gallery_dataset, batch_size=batch_size, shuffle=False, num_workers=0, pin_memory=True)

    # 3. Model, Optimizer, Loss
    print("Initializing model...")
    model = TurtleResNet(embedding_dim=embedding_dim, pretrained=True).to(device)
    
    # ArcFace Loss (has learnable parameters!)
    loss_func = get_arcface_loss(
        num_classes=num_classes, embedding_dim=embedding_dim
    ).to(device)
    
    # Optimizer: MUST include both model AND loss parameters
    optimizer = torch.optim.AdamW([
        {"params": model.parameters(), "lr": learning_rate},
        {"params": loss_func.parameters(), "lr": learning_rate},
    ], weight_decay=5e-4)
    
    # LR Scheduler
    scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2, eta_min=1e-6
    )
    
    accuracy_calculator = get_accuracy_calculator()

    # 4. Trainer
    trainer = MetricLearningTrainer(
        model=model,
        optimizer=optimizer,
        loss_func=loss_func,
        device=device,
        miner=None,
        save_dir="checkpoints"
    )

    # 5. Training Loop
    print("Starting training loop...")
    best_map = 0.0
    WARMUP_EPOCHS = 3
    
    for epoch in range(1, num_epochs + 1):
        # Linear warmup for first WARMUP_EPOCHS
        if epoch <= WARMUP_EPOCHS:
            warmup_factor = epoch / WARMUP_EPOCHS
            for param_group in optimizer.param_groups:
                param_group["lr"] = learning_rate * warmup_factor
                
        # Train
        trainer.train_epoch(train_loader, epoch)
        
        # Step scheduler after warmup
        if epoch > WARMUP_EPOCHS:
            scheduler.step()
        
        # Evaluate
        map_score = trainer.evaluate(query_loader, gallery_loader, accuracy_calculator, epoch)
        
        # Save best model
        if map_score > best_map:
            best_map = map_score
            trainer.save_checkpoint(epoch, best_map, filename="best_turtle_resnet_orientation.pth")

if __name__ == "__main__":
    # Protect entry point for multiprocessing in Windows
    main()
