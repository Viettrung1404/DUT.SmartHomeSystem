"""
Dataset Quality Validation Script for Vietnamese NLP Intent Classification.

This script validates dataset quality by checking:
- Duplicate samples
- Entity schema compliance
- Minimum samples per intent
- Text quality (empty, too short, too long)
- Entity consistency with intent

**Validates: Requirements 9.3**

Usage:
    python scripts/validate_dataset.py --input data/processed/train.json
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
from collections import Counter


# Import ENTITY_SCHEMA
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.models.schemas import ENTITY_SCHEMA


class DatasetValidator:
    """Validator for dataset quality checks."""
    
    def __init__(self, min_samples_per_intent: int = 100):
        """
        Initialize validator.
        
        Args:
            min_samples_per_intent: Minimum required samples per intent
        """
        self.min_samples_per_intent = min_samples_per_intent
        self.errors = []
        self.warnings = []
    
    def check_duplicates(self, samples: List[Dict[str, Any]]) -> Tuple[int, List[str]]:
        """
        Check for duplicate text samples.
        
        Args:
            samples: List of samples
            
        Returns:
            Tuple of (num_duplicates, duplicate_texts)
        """
        text_counts = Counter(sample["text"] for sample in samples)
        duplicates = [(text, count) for text, count in text_counts.items() if count > 1]
        
        if duplicates:
            self.warnings.append(f"Found {len(duplicates)} duplicate texts")
            for text, count in duplicates[:5]:  # Show first 5
                self.warnings.append(f"  - '{text}' appears {count} times")
        
        return len(duplicates), [text for text, _ in duplicates]
    
    def check_entity_schema_compliance(self, samples: List[Dict[str, Any]]) -> int:
        """
        Verify all entities comply with ENTITY_SCHEMA.
        
        Args:
            samples: List of samples
            
        Returns:
            Number of non-compliant samples
        """
        non_compliant = 0
        
        for i, sample in enumerate(samples):
            intent = sample["intent"]
            entities = sample.get("entities", {})
            
            # Check entity keys and values
            for entity_key, entity_value in entities.items():
                # Check if entity key is valid
                if entity_key == "device" and entity_value not in ENTITY_SCHEMA["device_types"]:
                    self.errors.append(
                        f"Sample {i}: Invalid device '{entity_value}' not in ENTITY_SCHEMA"
                    )
                    non_compliant += 1
                
                elif entity_key == "action" and entity_value not in ENTITY_SCHEMA["actions"]:
                    self.errors.append(
                        f"Sample {i}: Invalid action '{entity_value}' not in ENTITY_SCHEMA"
                    )
                    non_compliant += 1
                
                elif entity_key == "location" and entity_value not in ENTITY_SCHEMA["locations"]:
                    self.errors.append(
                        f"Sample {i}: Invalid location '{entity_value}' not in ENTITY_SCHEMA"
                    )
                    non_compliant += 1
                
                elif entity_key == "scene_type" and entity_value not in ENTITY_SCHEMA["scene_types"]:
                    self.errors.append(
                        f"Sample {i}: Invalid scene_type '{entity_value}' not in ENTITY_SCHEMA"
                    )
                    non_compliant += 1
                
                elif entity_key == "sensor_type" and entity_value not in ENTITY_SCHEMA["sensor_types"]:
                    self.errors.append(
                        f"Sample {i}: Invalid sensor_type '{entity_value}' not in ENTITY_SCHEMA"
                    )
                    non_compliant += 1
                
                elif entity_key == "comfort_type" and entity_value not in ENTITY_SCHEMA["comfort_types"]:
                    self.errors.append(
                        f"Sample {i}: Invalid comfort_type '{entity_value}' not in ENTITY_SCHEMA"
                    )
                    non_compliant += 1
        
        return non_compliant
    
    def check_minimum_samples(self, samples: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Check if each intent has minimum required samples.
        
        Args:
            samples: List of samples
            
        Returns:
            Dictionary of intents with insufficient samples
        """
        intent_counts = Counter(sample["intent"] for sample in samples)
        insufficient = {}
        
        for intent, count in intent_counts.items():
            if count < self.min_samples_per_intent:
                insufficient[intent] = count
                self.warnings.append(
                    f"Intent '{intent}' has only {count} samples (minimum: {self.min_samples_per_intent})"
                )
        
        return insufficient
    
    def check_text_quality(self, samples: List[Dict[str, Any]]) -> int:
        """
        Check text quality (empty, too short, too long).
        
        Args:
            samples: List of samples
            
        Returns:
            Number of samples with text quality issues
        """
        issues = 0
        
        for i, sample in enumerate(samples):
            text = sample.get("text", "")
            
            # Check empty
            if not text or not text.strip():
                self.errors.append(f"Sample {i}: Empty text")
                issues += 1
            
            # Check too short (< 2 characters)
            elif len(text.strip()) < 2:
                self.warnings.append(f"Sample {i}: Text too short ('{text}')")
                issues += 1
            
            # Check too long (> 500 characters)
            elif len(text) > 500:
                self.warnings.append(f"Sample {i}: Text too long ({len(text)} chars)")
                issues += 1
        
        return issues
    
    def check_entity_intent_consistency(self, samples: List[Dict[str, Any]]) -> int:
        """
        Check if entities are consistent with intent type.
        
        Args:
            samples: List of samples
            
        Returns:
            Number of inconsistent samples
        """
        inconsistent = 0
        
        for i, sample in enumerate(samples):
            intent = sample["intent"]
            entities = sample.get("entities", {})
            
            # Check control_device intent
            if intent == "control_device":
                if "device" not in entities or "action" not in entities:
                    self.warnings.append(
                        f"Sample {i}: control_device intent missing required entities (device, action)"
                    )
                    inconsistent += 1
            
            # Check environmental_comfort intent
            elif intent == "environmental_comfort":
                if "comfort_type" not in entities:
                    self.warnings.append(
                        f"Sample {i}: environmental_comfort intent missing comfort_type entity"
                    )
                    inconsistent += 1
            
            # Check activate_scene intent
            elif intent == "activate_scene":
                if "scene_type" not in entities:
                    self.warnings.append(
                        f"Sample {i}: activate_scene intent missing scene_type entity"
                    )
                    inconsistent += 1
            
            # Check query_sensor intent
            elif intent == "query_sensor":
                if "sensor_type" not in entities:
                    self.warnings.append(
                        f"Sample {i}: query_sensor intent missing sensor_type entity"
                    )
                    inconsistent += 1
        
        return inconsistent
    
    def validate(self, samples: List[Dict[str, Any]]) -> bool:
        """
        Run all validation checks.
        
        Args:
            samples: List of samples to validate
            
        Returns:
            True if validation passed (no errors), False otherwise
        """
        print("\n" + "="*60)
        print("DATASET QUALITY VALIDATION")
        print("="*60)
        
        print(f"\nTotal samples: {len(samples)}")
        
        # Check duplicates
        print("\n1. Checking for duplicates...")
        num_duplicates, _ = self.check_duplicates(samples)
        if num_duplicates == 0:
            print("   ✓ No duplicates found")
        else:
            print(f"   ⚠ Found {num_duplicates} duplicate texts")
        
        # Check entity schema compliance
        print("\n2. Checking entity schema compliance...")
        non_compliant = self.check_entity_schema_compliance(samples)
        if non_compliant == 0:
            print("   ✓ All entities comply with ENTITY_SCHEMA")
        else:
            print(f"   ✗ Found {non_compliant} non-compliant samples")
        
        # Check minimum samples per intent
        print("\n3. Checking minimum samples per intent...")
        insufficient = self.check_minimum_samples(samples)
        if not insufficient:
            print(f"   ✓ All intents have >= {self.min_samples_per_intent} samples")
        else:
            print(f"   ⚠ {len(insufficient)} intents have insufficient samples")
        
        # Check text quality
        print("\n4. Checking text quality...")
        text_issues = self.check_text_quality(samples)
        if text_issues == 0:
            print("   ✓ All texts have good quality")
        else:
            print(f"   ⚠ Found {text_issues} samples with text quality issues")
        
        # Check entity-intent consistency
        print("\n5. Checking entity-intent consistency...")
        inconsistent = self.check_entity_intent_consistency(samples)
        if inconsistent == 0:
            print("   ✓ All entities are consistent with intent")
        else:
            print(f"   ⚠ Found {inconsistent} samples with inconsistent entities")
        
        # Print summary
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"\n✗ ERRORS ({len(self.errors)}):")
            for error in self.errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")
        
        if self.warnings:
            print(f"\n⚠ WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  - {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        if not self.errors and not self.warnings:
            print("\n✓ All validation checks passed!")
            return True
        elif not self.errors:
            print("\n✓ Validation passed with warnings")
            return True
        else:
            print("\n✗ Validation failed with errors")
            return False


def main():
    """Main function for dataset validation."""
    parser = argparse.ArgumentParser(description="Validate dataset quality")
    parser.add_argument("--input", type=str, required=True, help="Input JSON file to validate")
    parser.add_argument("--min-samples", type=int, default=100, 
                       help="Minimum samples per intent (default: 100)")
    
    args = parser.parse_args()
    
    print(f"Loading dataset from: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        samples = json.load(f)
    
    # Validate dataset
    validator = DatasetValidator(min_samples_per_intent=args.min_samples)
    passed = validator.validate(samples)
    
    # Exit with appropriate code
    if passed:
        print("\n" + "="*60)
        print("✓ Dataset validation completed successfully!")
        print("="*60)
        exit(0)
    else:
        print("\n" + "="*60)
        print("✗ Dataset validation failed!")
        print("="*60)
        exit(1)


if __name__ == "__main__":
    main()
