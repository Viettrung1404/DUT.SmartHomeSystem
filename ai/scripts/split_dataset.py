"""
Dataset Splitting Script for Vietnamese NLP Intent Classification.

This script splits the dataset into train/validation/test sets with 70/15/15 ratio
and computes class weights for handling imbalanced classes.

**Validates: Requirements 9.2, 9.6**

Usage:
    python scripts/split_dataset.py --input data/augmented/training_data_augmented.json --output data/processed/
"""

import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import Counter
import numpy as np


def stratified_split(samples: List[Dict[str, Any]], 
                     train_ratio: float = 0.7,
                     val_ratio: float = 0.15,
                     test_ratio: float = 0.15) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Perform stratified split to maintain intent distribution across splits.
    
    Args:
        samples: List of all samples
        train_ratio: Ratio for training set (default 0.7)
        val_ratio: Ratio for validation set (default 0.15)
        test_ratio: Ratio for test set (default 0.15)
        
    Returns:
        Tuple of (train_samples, val_samples, test_samples)
    """
    # Group samples by intent
    intent_groups = {}
    for sample in samples:
        intent = sample["intent"]
        if intent not in intent_groups:
            intent_groups[intent] = []
        intent_groups[intent].append(sample)
    
    train_samples = []
    val_samples = []
    test_samples = []
    
    # Split each intent group
    for intent, intent_samples in intent_groups.items():
        # Shuffle samples within intent
        random.shuffle(intent_samples)
        
        # Calculate split indices
        n = len(intent_samples)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        # Split
        train_samples.extend(intent_samples[:train_end])
        val_samples.extend(intent_samples[train_end:val_end])
        test_samples.extend(intent_samples[val_end:])
    
    # Shuffle final splits
    random.shuffle(train_samples)
    random.shuffle(val_samples)
    random.shuffle(test_samples)
    
    return train_samples, val_samples, test_samples


def compute_class_weights(samples: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Compute class weights for handling imbalanced classes.
    
    Uses inverse frequency weighting:
    weight(class) = total_samples / (num_classes * class_count)
    
    Args:
        samples: List of training samples
        
    Returns:
        Dictionary mapping intent to weight
    """
    # Count samples per intent
    intent_counts = Counter(sample["intent"] for sample in samples)
    
    # Total samples and number of classes
    total_samples = len(samples)
    num_classes = len(intent_counts)
    
    # Compute weights
    class_weights = {}
    for intent, count in intent_counts.items():
        weight = total_samples / (num_classes * count)
        class_weights[intent] = weight
    
    return class_weights


def print_split_statistics(train_samples: List[Dict[str, Any]], 
                          val_samples: List[Dict[str, Any]], 
                          test_samples: List[Dict[str, Any]]):
    """
    Print statistics about the dataset splits.
    
    Args:
        train_samples: Training samples
        val_samples: Validation samples
        test_samples: Test samples
    """
    total = len(train_samples) + len(val_samples) + len(test_samples)
    
    print("\n" + "="*60)
    print("DATASET SPLIT STATISTICS")
    print("="*60)
    
    print(f"\nTotal samples: {total}")
    print(f"  Train: {len(train_samples)} ({len(train_samples)/total*100:.1f}%)")
    print(f"  Val:   {len(val_samples)} ({len(val_samples)/total*100:.1f}%)")
    print(f"  Test:  {len(test_samples)} ({len(test_samples)/total*100:.1f}%)")
    
    # Intent distribution
    print("\nIntent distribution:")
    print(f"{'Intent':<25} {'Train':<10} {'Val':<10} {'Test':<10} {'Total':<10}")
    print("-" * 60)
    
    # Get all intents
    all_intents = set()
    for samples in [train_samples, val_samples, test_samples]:
        all_intents.update(sample["intent"] for sample in samples)
    
    # Count per intent
    for intent in sorted(all_intents):
        train_count = sum(1 for s in train_samples if s["intent"] == intent)
        val_count = sum(1 for s in val_samples if s["intent"] == intent)
        test_count = sum(1 for s in test_samples if s["intent"] == intent)
        total_count = train_count + val_count + test_count
        
        print(f"{intent:<25} {train_count:<10} {val_count:<10} {test_count:<10} {total_count:<10}")


def print_class_weights(class_weights: Dict[str, float]):
    """
    Print class weights for imbalanced classes.
    
    Args:
        class_weights: Dictionary mapping intent to weight
    """
    print("\n" + "="*60)
    print("CLASS WEIGHTS (for handling imbalanced classes)")
    print("="*60)
    
    print(f"\n{'Intent':<25} {'Weight':<10}")
    print("-" * 35)
    
    for intent in sorted(class_weights.keys()):
        weight = class_weights[intent]
        print(f"{intent:<25} {weight:.4f}")
    
    print(f"\nNote: Higher weights for minority classes, lower for majority classes")


def save_splits(train_samples: List[Dict[str, Any]], 
               val_samples: List[Dict[str, Any]], 
               test_samples: List[Dict[str, Any]],
               class_weights: Dict[str, float],
               output_dir: str):
    """
    Save train/val/test splits and class weights to files.
    
    Args:
        train_samples: Training samples
        val_samples: Validation samples
        test_samples: Test samples
        class_weights: Class weights dictionary
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save train set
    train_file = output_path / "train.json"
    with open(train_file, 'w', encoding='utf-8') as f:
        json.dump(train_samples, f, ensure_ascii=False, indent=2)
    print(f"\nTrain set saved to: {train_file}")
    
    # Save validation set
    val_file = output_path / "val.json"
    with open(val_file, 'w', encoding='utf-8') as f:
        json.dump(val_samples, f, ensure_ascii=False, indent=2)
    print(f"Validation set saved to: {val_file}")
    
    # Save test set
    test_file = output_path / "test.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_samples, f, ensure_ascii=False, indent=2)
    print(f"Test set saved to: {test_file}")
    
    # Save class weights
    weights_file = output_path / "class_weights.json"
    with open(weights_file, 'w', encoding='utf-8') as f:
        json.dump(class_weights, f, ensure_ascii=False, indent=2)
    print(f"Class weights saved to: {weights_file}")
    
    # Save split metadata
    metadata = {
        "total_samples": len(train_samples) + len(val_samples) + len(test_samples),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "test_samples": len(test_samples),
        "train_ratio": len(train_samples) / (len(train_samples) + len(val_samples) + len(test_samples)),
        "val_ratio": len(val_samples) / (len(train_samples) + len(val_samples) + len(test_samples)),
        "test_ratio": len(test_samples) / (len(train_samples) + len(val_samples) + len(test_samples)),
        "num_intents": len(class_weights),
        "intents": sorted(class_weights.keys())
    }
    
    metadata_file = output_path / "split_metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Split metadata saved to: {metadata_file}")


def main():
    """Main function for dataset splitting."""
    parser = argparse.ArgumentParser(description="Split dataset into train/val/test sets")
    parser.add_argument("--input", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", type=str, required=True, help="Output directory")
    parser.add_argument("--train-ratio", type=float, default=0.7, help="Training set ratio (default: 0.7)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Validation set ratio (default: 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test set ratio (default: 0.15)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Validate ratios
    total_ratio = args.train_ratio + args.val_ratio + args.test_ratio
    if abs(total_ratio - 1.0) > 0.01:
        raise ValueError(f"Ratios must sum to 1.0, got {total_ratio}")
    
    # Set random seed
    random.seed(args.seed)
    np.random.seed(args.seed)
    
    print(f"Loading dataset from: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    print(f"Total samples: {len(samples)}")
    print(f"Split ratios: Train={args.train_ratio}, Val={args.val_ratio}, Test={args.test_ratio}")
    print(f"Random seed: {args.seed}")
    
    # Perform stratified split
    print("\nPerforming stratified split...")
    train_samples, val_samples, test_samples = stratified_split(
        samples, 
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio
    )
    
    # Compute class weights from training set
    print("\nComputing class weights...")
    class_weights = compute_class_weights(train_samples)
    
    # Print statistics
    print_split_statistics(train_samples, val_samples, test_samples)
    print_class_weights(class_weights)
    
    # Save splits
    save_splits(train_samples, val_samples, test_samples, class_weights, args.output)
    
    print("\n" + "="*60)
    print("✓ Dataset splitting completed!")
    print("="*60)


if __name__ == "__main__":
    main()
