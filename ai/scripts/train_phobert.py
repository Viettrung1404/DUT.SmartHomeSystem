"""
Training Script for PhoBERT Intent Classifier.

This script trains the PhoBERT-based intent classification model with:
- AdamW optimizer with learning rate warmup
- Cross-entropy loss with class weights
- Early stopping based on validation loss
- Model checkpointing
- Training metrics logging

**Validates: Requirements 9.4, 9.7, 9.9**

Usage:
    python scripts/train_phobert.py --train data/processed/train.json --val data/processed/val.json --output models/phobert_intent_v1
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, get_linear_schedule_with_warmup
from tqdm import tqdm
import numpy as np

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.training.phobert_classifier import PhoBERTIntentClassifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATASET CLASS
# ============================================================================

class IntentDataset(Dataset):
    """Dataset for intent classification."""
    
    def __init__(self, samples: List[Dict[str, Any]], 
                 tokenizer, 
                 intent_to_id: Dict[str, int],
                 max_length: int = 128):
        """
        Initialize dataset.
        
        Args:
            samples: List of training samples
            tokenizer: PhoBERT tokenizer
            intent_to_id: Mapping from intent name to ID
            max_length: Maximum sequence length
        """
        self.samples = samples
        self.tokenizer = tokenizer
        self.intent_to_id = intent_to_id
        self.max_length = max_length
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            sample["text"],
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Get intent ID
        intent_id = self.intent_to_id[sample["intent"]]
        
        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "label": torch.tensor(intent_id, dtype=torch.long)
        }


# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================

def load_class_weights(weights_file: str, intent_to_id: Dict[str, int]) -> torch.Tensor:
    """
    Load class weights from file.
    
    Args:
        weights_file: Path to class weights JSON file
        intent_to_id: Mapping from intent name to ID
        
    Returns:
        Tensor of class weights
    """
    with open(weights_file, 'r') as f:
        class_weights_dict = json.load(f)
    
    # Create tensor of weights in correct order
    num_classes = len(intent_to_id)
    class_weights = torch.ones(num_classes)
    
    for intent, weight in class_weights_dict.items():
        if intent in intent_to_id:
            class_weights[intent_to_id[intent]] = weight
    
    return class_weights


def train_epoch(model, dataloader, optimizer, scheduler, criterion, device):
    """
    Train for one epoch.
    
    Args:
        model: PhoBERT model
        dataloader: Training dataloader
        optimizer: Optimizer
        scheduler: Learning rate scheduler
        criterion: Loss function
        device: Device (cuda/cpu)
        
    Returns:
        Average training loss
    """
    model.train()
    total_loss = 0
    
    progress_bar = tqdm(dataloader, desc="Training")
    for batch in progress_bar:
        # Move to device
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["label"].to(device)
        
        # Forward pass
        optimizer.zero_grad()
        logits = model(input_ids, attention_mask)
        loss = criterion(logits, labels)
        
        # Backward pass
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        
        # Update metrics
        total_loss += loss.item()
        progress_bar.set_postfix({"loss": loss.item()})
    
    return total_loss / len(dataloader)


def evaluate(model, dataloader, criterion, device):
    """
    Evaluate model on validation set.
    
    Args:
        model: PhoBERT model
        dataloader: Validation dataloader
        criterion: Loss function
        device: Device (cuda/cpu)
        
    Returns:
        Tuple of (average loss, accuracy)
    """
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Evaluating"):
            # Move to device
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["label"].to(device)
            
            # Forward pass
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)
            
            # Calculate accuracy
            predictions = torch.argmax(logits, dim=-1)
            correct += (predictions == labels).sum().item()
            total += labels.size(0)
            
            total_loss += loss.item()
    
    avg_loss = total_loss / len(dataloader)
    accuracy = correct / total
    
    return avg_loss, accuracy


def save_checkpoint(model, optimizer, scheduler, epoch, val_loss, val_acc, save_path):
    """
    Save model checkpoint.
    
    Args:
        model: PhoBERT model
        optimizer: Optimizer
        scheduler: Learning rate scheduler
        epoch: Current epoch
        val_loss: Validation loss
        val_acc: Validation accuracy
        save_path: Path to save checkpoint
    """
    checkpoint = {
        "epoch": epoch,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "scheduler_state_dict": scheduler.state_dict(),
        "val_loss": val_loss,
        "val_acc": val_acc
    }
    
    torch.save(checkpoint, save_path)
    logger.info(f"Checkpoint saved to {save_path}")


# ============================================================================
# MAIN TRAINING FUNCTION
# ============================================================================

def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train PhoBERT Intent Classifier")
    parser.add_argument("--train", type=str, required=True, help="Training data JSON file")
    parser.add_argument("--val", type=str, required=True, help="Validation data JSON file")
    parser.add_argument("--weights", type=str, default="data/processed/class_weights.json", 
                       help="Class weights JSON file")
    parser.add_argument("--output", type=str, required=True, help="Output directory for model")
    parser.add_argument("--model-name", type=str, default="vinai/phobert-base", 
                       help="PhoBERT model name")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size")
    parser.add_argument("--lr", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--warmup-steps", type=int, default=500, help="Warmup steps")
    parser.add_argument("--max-length", type=int, default=128, help="Max sequence length")
    parser.add_argument("--patience", type=int, default=3, help="Early stopping patience")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    # Set random seed
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    logger.info(f"Loading training data from {args.train}")
    with open(args.train, 'r', encoding='utf-8') as f:
        train_samples = json.load(f)
    
    logger.info(f"Loading validation data from {args.val}")
    with open(args.val, 'r', encoding='utf-8') as f:
        val_samples = json.load(f)
    
    logger.info(f"Train samples: {len(train_samples)}")
    logger.info(f"Val samples: {len(val_samples)}")
    
    # Create intent mapping
    all_intents = sorted(set(s["intent"] for s in train_samples))
    intent_to_id = {intent: idx for idx, intent in enumerate(all_intents)}
    id_to_intent = {idx: intent for intent, idx in intent_to_id.items()}
    num_intents = len(all_intents)
    
    logger.info(f"Number of intents: {num_intents}")
    logger.info(f"Intents: {all_intents}")
    
    # Save intent mapping
    with open(output_dir / "intent_mapping.json", 'w') as f:
        json.dump({"intent_to_id": intent_to_id, "id_to_intent": id_to_intent}, f, indent=2)
    
    # Load tokenizer
    logger.info(f"Loading tokenizer: {args.model_name}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    
    # Create datasets
    train_dataset = IntentDataset(train_samples, tokenizer, intent_to_id, args.max_length)
    val_dataset = IntentDataset(val_samples, tokenizer, intent_to_id, args.max_length)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False)
    
    # Load class weights
    logger.info(f"Loading class weights from {args.weights}")
    class_weights = load_class_weights(args.weights, intent_to_id)
    class_weights = class_weights.to(device)
    
    # Create model
    logger.info("Creating PhoBERT Intent Classifier")
    model = PhoBERTIntentClassifier(
        num_intents=num_intents,
        model_name=args.model_name,
        dropout=0.1
    )
    model = model.to(device)
    
    # Create optimizer and scheduler
    optimizer = AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    
    total_steps = len(train_loader) * args.epochs
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=args.warmup_steps,
        num_training_steps=total_steps
    )
    
    # Create loss function with class weights
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    
    # Training loop
    logger.info("Starting training...")
    logger.info(f"Total epochs: {args.epochs}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Learning rate: {args.lr}")
    logger.info(f"Warmup steps: {args.warmup_steps}")
    
    best_val_loss = float('inf')
    patience_counter = 0
    training_history = []
    
    for epoch in range(args.epochs):
        logger.info(f"\nEpoch {epoch + 1}/{args.epochs}")
        
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, scheduler, criterion, device)
        logger.info(f"Train loss: {train_loss:.4f}")
        
        # Evaluate
        val_loss, val_acc = evaluate(model, val_loader, criterion, device)
        logger.info(f"Val loss: {val_loss:.4f}, Val accuracy: {val_acc:.4f}")
        
        # Save history
        training_history.append({
            "epoch": epoch + 1,
            "train_loss": train_loss,
            "val_loss": val_loss,
            "val_accuracy": val_acc
        })
        
        # Save checkpoint
        checkpoint_path = output_dir / f"checkpoint_epoch_{epoch + 1}.pt"
        save_checkpoint(model, optimizer, scheduler, epoch + 1, val_loss, val_acc, checkpoint_path)
        
        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            
            # Save best model
            best_model_path = output_dir / "best_model.pt"
            torch.save(model.state_dict(), best_model_path)
            logger.info(f"New best model saved! Val loss: {val_loss:.4f}")
        else:
            patience_counter += 1
            logger.info(f"No improvement. Patience: {patience_counter}/{args.patience}")
            
            if patience_counter >= args.patience:
                logger.info("Early stopping triggered!")
                break
    
    # Save final model
    logger.info("Saving final model...")
    model.save_pretrained(str(output_dir))
    
    # Save training history
    history_path = output_dir / "training_history.json"
    with open(history_path, 'w') as f:
        json.dump(training_history, f, indent=2)
    
    logger.info(f"\nTraining completed!")
    logger.info(f"Best validation loss: {best_val_loss:.4f}")
    logger.info(f"Model saved to: {output_dir}")


if __name__ == "__main__":
    main()
