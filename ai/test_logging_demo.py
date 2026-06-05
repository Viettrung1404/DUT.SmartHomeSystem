"""
Demo script to show hybrid classifier logging output.

This script demonstrates the comprehensive logging for:
- Routing decisions (INFO level)
- ML failures and fallback triggers (ERROR/WARNING level)
- Confidence comparisons (DEBUG level)
- Final classification results (INFO level)
"""

import logging
from typing import Optional, Dict, Any

# Mock classifiers for demo
class MockRuleBasedClassifier:
    """Mock rule-based classifier for demo."""
    
    def classify(self, text: str):
        """Mock classify method."""
        simple_patterns = ["bật đèn", "tắt quạt", "mở cửa", "đóng mái che"]
        text_lower = text.lower().strip()
        
        for pattern in simple_patterns:
            if pattern in text_lower:
                class Result:
                    intent = "control_device"
                    entities = {"device": "light" if "đèn" in pattern else "fan"}
                    confidence = 1.0
                    classifier_type = "rule"
                return Result()
        return None


class MockMLBasedClassifier:
    """Mock ML-based classifier for demo."""
    
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
    
    def classify(self, text: str, context: Optional[Dict[str, Any]] = None):
        """Mock classify method."""
        if self.should_fail:
            raise RuntimeError("ML model inference failed")
        
        text_lower = text.lower().strip()
        
        if any(phrase in text_lower for phrase in ["nóng quá", "lạnh quá", "tối quá"]):
            return {
                "intent": "environmental_comfort",
                "entities": {"comfort_type": "cooling"},
                "confidence": 0.95,
                "classifier_type": "ml"
            }
        else:
            return {
                "intent": "control_device",
                "entities": {},
                "confidence": 0.50,
                "classifier_type": "ml"
            }


# Import HybridClassifier
from classifiers.hybrid import HybridClassifier

# Configure logging to show all levels
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

def main():
    """Run demo scenarios to show logging."""
    
    print("=" * 80)
    print("HYBRID CLASSIFIER LOGGING DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Initialize classifiers
    rule_classifier = MockRuleBasedClassifier()
    ml_classifier = MockMLBasedClassifier()
    hybrid = HybridClassifier(rule_classifier, ml_classifier)
    
    print("\n" + "=" * 80)
    print("SCENARIO 1: Simple Command (Rule-Based Fast Path)")
    print("=" * 80)
    result = hybrid.classify("bật đèn phòng khách")
    print(f"Result: {result}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 2: Natural Language (ML-Based)")
    print("=" * 80)
    result = hybrid.classify("trời nóng quá")
    print(f"Result: {result}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 3: ML Failure Fallback to Rule-Based")
    print("=" * 80)
    failing_ml = MockMLBasedClassifier(should_fail=True)
    hybrid_with_failing_ml = HybridClassifier(rule_classifier, failing_ml)
    result = hybrid_with_failing_ml.classify("bật đèn")
    print(f"Result: {result}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 4: Both Classifiers Fail (Unknown Fallback)")
    print("=" * 80)
    result = hybrid_with_failing_ml.classify("xyz abc 123")
    print(f"Result: {result}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 5: Confidence Comparison (Rule vs ML)")
    print("=" * 80)
    result = hybrid.classify("bật quạt")
    print(f"Result: {result}")
    
    print("\n" + "=" * 80)
    print("LOGGING DEMONSTRATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
