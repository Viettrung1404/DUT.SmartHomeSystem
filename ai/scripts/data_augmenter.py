"""
Data Augmentation Module for Vietnamese NLP Intent Classification.

This module provides various data augmentation techniques to increase
training dataset diversity and improve model robustness:
- Synonym replacement
- Typo simulation
- Slang variation
- Paraphrase generation

**Validates: Requirements 9.5**

Usage:
    from scripts.data_augmenter import DataAugmenter
    
    augmenter = DataAugmenter()
    augmented_samples = augmenter.augment_dataset(samples, augmentation_factor=2)
"""

import json
import random
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class DataAugmenter:
    """
    Data augmentation for Vietnamese text samples.
    
    Techniques:
    1. Synonym replacement: Replace words with Vietnamese synonyms
    2. Typo simulation: Introduce common Vietnamese typing errors
    3. Slang variation: Replace standard words with Vietnamese slang
    4. Paraphrase generation: Rephrase sentences while keeping meaning
    """
    
    def __init__(self):
        """Initialize augmenter with Vietnamese synonym and slang dictionaries."""
        
        # Vietnamese synonym dictionary
        self.synonyms = {
            "bật": ["mở", "khởi động", "chạy"],
            "tắt": ["đóng", "dừng", "ngừng"],
            "đèn": ["ánh sáng", "bóng đèn"],
            "quạt": ["quạt trần", "quạt máy"],
            "điều hòa": ["máy lạnh", "ac"],
            "cửa": ["cửa ra vào", "cửa chính"],
            "mái che": ["mái hiên", "mái bạt"],
            "rèm": ["rèm cửa"],
            "khóa": ["ổ khóa"],
            "phòng khách": ["living room"],
            "phòng ngủ": ["bedroom"],
            "bếp": ["nhà bếp", "kitchen"],
            "phòng tắm": ["nhà vệ sinh", "toilet", "bathroom"],
            "ban công": ["balcony", "sân thượng"],
            "nóng": ["oi bức"],
            "lạnh": ["rét"],
            "tối": ["thiếu sáng"],
            "sáng": ["chói"],
            "ngột ngạt": ["thiếu không khí"],
            "đi ngủ": ["chuẩn bị ngủ"],
            "thức dậy": ["dậy rồi"],
            "xem phim": ["xem TV", "coi phim", "xem tivi"],
            "đi ra ngoài": ["rời nhà", "ra ngoài"],
            "về nhà": ["đã về", "về rồi"],
            "nhiệt độ": ["temperature"],
            "độ ẩm": ["humidity"],
            "bao nhiêu": ["là bao nhiêu", "thế nào"],
            "quá": ["quá đi", "lắm"],
            "cần": ["muốn"],
        }
        
        # Vietnamese slang dictionary (standard → slang)
        self.slang_variations = {
            "không": ["k", "ko", "hok"],
            "được": ["đc", "dc"],
            "với": ["vs"],
            "gì": ["j"],
            "rồi": ["r"],
            "vậy": ["v", "z"],
            "phải": ["fải"],
            "của": ["của"],
            "thì": ["thì"],
            "có": ["có"],
            "bật": ["bật"],
            "tắt": ["tắt"],
        }
        
        # Common Vietnamese typos (correct → typo)
        self.typo_patterns = {
            "đ": ["d"],
            "ă": ["a"],
            "â": ["a"],
            "ê": ["e"],
            "ô": ["o"],
            "ơ": ["o"],
            "ư": ["u"],
            "á": ["a"],
            "à": ["a"],
            "ả": ["a"],
            "ã": ["a"],
            "ạ": ["a"],
        }
        
        # Paraphrase templates for common patterns
        self.paraphrase_templates = {
            "Bật {device} {location}": [
                "Mở {device} {location}",
                "Khởi động {device} {location}",
                "{device} {location} bật lên",
                "Cho tôi bật {device} {location}",
            ],
            "Tắt {device} {location}": [
                "Đóng {device} {location}",
                "Dừng {device} {location}",
                "{device} {location} tắt đi",
                "Cho tôi tắt {device} {location}",
            ],
            "Trời {condition} quá": [
                "{condition} quá đi",
                "{condition} lắm",
                "Cảm thấy {condition}",
                "{condition} quá rồi",
            ],
            "{sensor_type} {location} bao nhiêu": [
                "{sensor_type} {location} là bao nhiêu",
                "Cho biết {sensor_type} {location}",
                "Kiểm tra {sensor_type} {location}",
                "{sensor_type} ở {location} thế nào",
            ],
        }
    
    def synonym_replacement(self, text: str, prob: float = 0.3) -> str:
        """
        Replace words with Vietnamese synonyms.
        
        Args:
            text: Input text
            prob: Probability of replacing each word
            
        Returns:
            Text with some words replaced by synonyms
        """
        words = text.split()
        new_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in self.synonyms and random.random() < prob:
                # Replace with random synonym
                synonym = random.choice(self.synonyms[word_lower])
                # Preserve capitalization
                if word[0].isupper():
                    synonym = synonym.capitalize()
                new_words.append(synonym)
            else:
                new_words.append(word)
        
        return " ".join(new_words)
    
    def typo_simulation(self, text: str, prob: float = 0.1) -> str:
        """
        Introduce common Vietnamese typing errors.
        
        Args:
            text: Input text
            prob: Probability of introducing typo per character
            
        Returns:
            Text with simulated typos
        """
        new_text = []
        
        for char in text:
            if char.lower() in self.typo_patterns and random.random() < prob:
                # Replace with typo
                typo = random.choice(self.typo_patterns[char.lower()])
                # Preserve capitalization
                if char.isupper():
                    typo = typo.upper()
                new_text.append(typo)
            else:
                new_text.append(char)
        
        return "".join(new_text)
    
    def slang_variation(self, text: str, prob: float = 0.2) -> str:
        """
        Replace standard words with Vietnamese slang.
        
        Args:
            text: Input text
            prob: Probability of replacing each word with slang
            
        Returns:
            Text with some words replaced by slang
        """
        words = text.split()
        new_words = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower in self.slang_variations and random.random() < prob:
                # Replace with random slang
                slang = random.choice(self.slang_variations[word_lower])
                new_words.append(slang)
            else:
                new_words.append(word)
        
        return " ".join(new_words)
    
    def paraphrase_generation(self, text: str) -> Optional[str]:
        """
        Generate paraphrase using template matching.
        
        Args:
            text: Input text
            
        Returns:
            Paraphrased text or None if no template matches
        """
        # Try to match text with paraphrase templates
        for pattern, paraphrases in self.paraphrase_templates.items():
            # Extract placeholders from pattern
            placeholders = re.findall(r'\{(\w+)\}', pattern)
            
            # Create regex pattern
            regex_pattern = pattern
            for placeholder in placeholders:
                regex_pattern = regex_pattern.replace(f"{{{placeholder}}}", r"(\S+)")
            
            # Try to match
            match = re.search(regex_pattern, text, re.IGNORECASE)
            if match:
                # Extract values
                values = match.groups()
                
                # Choose random paraphrase template
                paraphrase_template = random.choice(paraphrases)
                
                # Fill in values
                paraphrase = paraphrase_template
                for i, placeholder in enumerate(placeholders):
                    paraphrase = paraphrase.replace(f"{{{placeholder}}}", values[i])
                
                return paraphrase
        
        return None
    
    def augment_sample(self, sample: Dict[str, Any], techniques: List[str] = None) -> List[Dict[str, Any]]:
        """
        Augment a single sample using specified techniques.
        
        Args:
            sample: Original sample with text, intent, entities, metadata
            techniques: List of augmentation techniques to apply
                       Options: ["synonym", "typo", "slang", "paraphrase"]
                       If None, applies all techniques
            
        Returns:
            List of augmented samples (including original)
        """
        if techniques is None:
            techniques = ["synonym", "typo", "slang", "paraphrase"]
        
        augmented_samples = [sample]  # Include original
        original_text = sample["text"]
        
        # Apply each technique
        if "synonym" in techniques:
            augmented_text = self.synonym_replacement(original_text, prob=0.3)
            if augmented_text != original_text:
                augmented_sample = sample.copy()
                augmented_sample["text"] = augmented_text
                augmented_sample["metadata"] = sample["metadata"].copy()
                augmented_sample["metadata"]["augmentation"] = "synonym_replacement"
                augmented_samples.append(augmented_sample)
        
        if "typo" in techniques:
            augmented_text = self.typo_simulation(original_text, prob=0.1)
            if augmented_text != original_text:
                augmented_sample = sample.copy()
                augmented_sample["text"] = augmented_text
                augmented_sample["metadata"] = sample["metadata"].copy()
                augmented_sample["metadata"]["augmentation"] = "typo_simulation"
                augmented_samples.append(augmented_sample)
        
        if "slang" in techniques:
            augmented_text = self.slang_variation(original_text, prob=0.2)
            if augmented_text != original_text:
                augmented_sample = sample.copy()
                augmented_sample["text"] = augmented_text
                augmented_sample["metadata"] = sample["metadata"].copy()
                augmented_sample["metadata"]["augmentation"] = "slang_variation"
                augmented_samples.append(augmented_sample)
        
        if "paraphrase" in techniques:
            augmented_text = self.paraphrase_generation(original_text)
            if augmented_text and augmented_text != original_text:
                augmented_sample = sample.copy()
                augmented_sample["text"] = augmented_text
                augmented_sample["metadata"] = sample["metadata"].copy()
                augmented_sample["metadata"]["augmentation"] = "paraphrase_generation"
                augmented_samples.append(augmented_sample)
        
        return augmented_samples
    
    def augment_dataset(self, samples: List[Dict[str, Any]], 
                       augmentation_factor: int = 2,
                       techniques: List[str] = None) -> List[Dict[str, Any]]:
        """
        Augment entire dataset.
        
        Args:
            samples: List of original samples
            augmentation_factor: Target multiplier for dataset size
                                (e.g., 2 means double the dataset)
            techniques: List of augmentation techniques to apply
            
        Returns:
            Augmented dataset (includes original samples)
        """
        augmented_dataset = []
        
        for sample in samples:
            # Augment sample
            augmented_samples = self.augment_sample(sample, techniques)
            
            # Add original
            augmented_dataset.append(sample)
            
            # Add augmented samples (up to augmentation_factor - 1)
            num_to_add = min(len(augmented_samples) - 1, augmentation_factor - 1)
            if num_to_add > 0:
                augmented_dataset.extend(augmented_samples[1:num_to_add + 1])
        
        # Shuffle
        random.shuffle(augmented_dataset)
        
        return augmented_dataset


# ============================================================================
# MAIN SCRIPT FOR TESTING
# ============================================================================

def main():
    """Test data augmentation on sample data."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Augment training dataset")
    parser.add_argument("--input", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", type=str, required=True, help="Output JSON file")
    parser.add_argument("--factor", type=int, default=2, help="Augmentation factor")
    parser.add_argument("--techniques", type=str, nargs="+", 
                       default=["synonym", "typo", "slang", "paraphrase"],
                       help="Augmentation techniques to apply")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    print(f"Loading dataset from: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    print(f"Original dataset size: {len(samples)} samples")
    print(f"Augmentation factor: {args.factor}x")
    print(f"Techniques: {', '.join(args.techniques)}")
    print()
    
    # Augment dataset
    augmenter = DataAugmenter()
    augmented_samples = augmenter.augment_dataset(
        samples, 
        augmentation_factor=args.factor,
        techniques=args.techniques
    )
    
    print(f"Augmented dataset size: {len(augmented_samples)} samples")
    print(f"Increase: {len(augmented_samples) - len(samples)} samples (+{((len(augmented_samples) / len(samples) - 1) * 100):.1f}%)")
    
    # Save augmented dataset
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(augmented_samples, f, ensure_ascii=False, indent=2)
    
    print(f"\nAugmented dataset saved to: {args.output}")
    
    # Print augmentation statistics
    augmentation_counts = {}
    for sample in augmented_samples:
        aug_type = sample["metadata"].get("augmentation", "original")
        augmentation_counts[aug_type] = augmentation_counts.get(aug_type, 0) + 1
    
    print("\nAugmentation statistics:")
    for aug_type, count in sorted(augmentation_counts.items()):
        print(f"  {aug_type}: {count} samples")
    
    print("\n✓ Data augmentation completed!")


if __name__ == "__main__":
    main()
