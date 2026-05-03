"""
Trainer module for SeaTurtle Photo-ID Metric Learning.
"""

import os
import logging
import torch
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm

class MetricLearningTrainer:
    """
    Handles the training and validation loops for Metric Learning.
    
    This trainer utilizes the pytorch-metric-learning miner and loss function.
    """
    
    def __init__(self, model, optimizer, loss_func, miner, device, save_dir="checkpoints"):
        self.model = model
        self.optimizer = optimizer
        self.loss_func = loss_func
        self.miner = miner
        self.device = device
        self.save_dir = save_dir
        self.writer = SummaryWriter(log_dir=os.path.join(save_dir, "logs"))
        
        os.makedirs(save_dir, exist_ok=True)
        
        # Setup text file logger
        self.logger = logging.getLogger("TrainingLogger")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            fh = logging.FileHandler(os.path.join(save_dir, "training_history.log"))
            formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
        
    def train_epoch(self, dataloader, epoch):
        self.model.train()
        total_loss = 0.0
        num_batches = len(dataloader)
        
        progress_bar = tqdm(dataloader, desc=f"Epoch {epoch} [Train]", leave=False)
        
        for batch_idx, (images, labels) in enumerate(progress_bar):
            images, labels = images.to(self.device), labels.to(self.device)
            
            self.optimizer.zero_grad()
            
            # Forward pass: Generate embeddings
            embeddings = self.model(images)
            
            # Mine hard triplets
            hard_pairs = self.miner(embeddings, labels)
            
            # Compute loss on the hard triplets
            loss = self.loss_func(embeddings, labels, hard_pairs)
            
            # Backward pass & Optimize
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            
            progress_bar.set_postfix({"Loss": f"{loss.item():.4f}"})
            
            # Log to TensorBoard
            global_step = epoch * num_batches + batch_idx
            self.writer.add_scalar("Training/Loss", loss.item(), global_step)
            
        avg_loss = total_loss / num_batches
        msg = f"Epoch {epoch} Training Loss: {avg_loss:.4f}"
        print(msg)
        self.logger.info(msg)
        return avg_loss

    def evaluate(self, query_loader, gallery_loader, accuracy_calculator, epoch):
        """
        Evaluates the model by calculating embeddings for all queries and gallery images,
        and then computing mAP and precision_at_1.
        """
        self.model.eval()
        
        print("Extracting query embeddings...")
        query_embeddings, query_labels = self._get_all_embeddings(query_loader)
        
        print("Extracting gallery embeddings...")
        gallery_embeddings, gallery_labels = self._get_all_embeddings(gallery_loader)
        
        print("Computing metrics...")
        metrics = accuracy_calculator.get_accuracy(
            query=query_embeddings,
            query_labels=query_labels,
            reference=gallery_embeddings,
            reference_labels=gallery_labels,
            ref_includes_query=False
        )
        
        map_score = metrics["mean_average_precision"]
        top1_score = metrics["precision_at_1"]
        
        msg = f"Epoch {epoch} Eval -> mAP: {map_score:.4f} | Top-1: {top1_score:.4f}"
        print(msg)
        self.logger.info(msg)
        
        self.writer.add_scalar("Eval/mAP", map_score, epoch)
        self.writer.add_scalar("Eval/Top1", top1_score, epoch)
        
        return map_score
        
    def _get_all_embeddings(self, dataloader):
        all_embeddings = []
        all_labels = []
        
        with torch.no_grad():
            for images, labels in tqdm(dataloader, desc="Extracting", leave=False):
                images = images.to(self.device)
                embeddings = self.model(images)
                all_embeddings.append(embeddings.cpu())
                all_labels.append(labels.cpu())
                
        return torch.cat(all_embeddings), torch.cat(all_labels)
        
    def save_checkpoint(self, epoch, map_score, filename="best_model.pth"):
        path = os.path.join(self.save_dir, filename)
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'map_score': map_score,
        }, path)
        msg = f"Model saved to {path} (mAP: {map_score:.4f})"
        print(msg)
        self.logger.info(msg)
