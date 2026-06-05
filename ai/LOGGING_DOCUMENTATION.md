# Hybrid Classifier Logging Documentation

## Overview

The HybridClassifier implements comprehensive logging for all routing decisions, fallback mechanisms, and classification results. This document describes the logging behavior implemented in Task 9.3.

## Logging Levels

### INFO Level
Used for normal operational flow and important decisions:

1. **Initialization**
   ```
   INFO - Hybrid Classifier initialized successfully
   INFO - Rule-based classifier: RuleBasedClassifier
   INFO - ML-based classifier: MLBasedClassifier
   ```

2. **Classification Start**
   ```
   INFO - Classifying text: 'bật đèn phòng khách'
   ```

3. **Rule-Based Fast Path**
   ```
   INFO - Rule-based classifier matched with confidence=1.0: intent=control_device
   ```

4. **ML Classifier Results**
   ```
   INFO - ML-based classifier result: intent=environmental_comfort, confidence=0.950
   ```

5. **Final Decision (Confidence Comparison)**
   ```
   INFO - Returning rule-based result (confidence=1.000 >= 0.500): intent=control_device
   INFO - Returning ML-based result (confidence=0.950 > 0.800): intent=environmental_comfort
   INFO - Returning ML-based result (no rule match): intent=query_sensor, confidence=0.850
   INFO - Returning rule-based result (ML not attempted): intent=control_device, confidence=1.0
   ```

### DEBUG Level
Used for detailed routing logic and confidence comparisons:

1. **Pattern Matching Details**
   ```
   DEBUG - Text 'bật đèn' matches simple command pattern (action=True, scene=False, words=2)
   ```

2. **Routing Decisions**
   ```
   DEBUG - Routing to rule-based classifier (simple command detected)
   DEBUG - Routing to ML-based classifier
   ```

3. **Confidence Comparison**
   ```
   DEBUG - Comparing confidence scores: rule=1.000 vs ml=0.500
   ```

### WARNING Level
Used for fallback scenarios:

1. **ML Failure Fallback to Rule-Based**
   ```
   WARNING - Fallback triggered: ML failed, using rule-based result (intent=control_device, confidence=1.0)
   ```

2. **Both Classifiers Failed**
   ```
   WARNING - Fallback triggered: Both classifiers failed, returning unknown (error: ML model inference failed)
   ```

3. **No Classification Result**
   ```
   WARNING - No classification result available, returning unknown
   ```

### ERROR Level
Used for ML classifier failures:

1. **ML Inference Failure**
   ```
   ERROR - ML classifier failed: ML model inference failed
   ERROR - ML classifier failed: CUDA out of memory
   ERROR - ML classifier failed: Model not loaded
   ```

## Fallback Mechanism Flow

### Scenario 1: ML Failure → Rule-Based → Success
```
INFO  - Classifying text: 'bật đèn'
DEBUG - Text 'bật đèn' matches simple command pattern (action=True, scene=False, words=2)
DEBUG - Routing to rule-based classifier (simple command detected)
INFO  - Rule-based classifier matched with confidence=1.0: intent=control_device
```
**Result:** Rule-based returns immediately with confidence=1.0 (fast path)

### Scenario 2: ML Failure → Rule-Based → Fallback
```
INFO    - Classifying text: 'bật đèn'
DEBUG   - Text 'bật đèn' matches simple command pattern (action=True, scene=False, words=2)
DEBUG   - Routing to rule-based classifier (simple command detected)
DEBUG   - Routing to ML-based classifier
ERROR   - ML classifier failed: ML model inference failed
WARNING - Fallback triggered: ML failed, using rule-based result (intent=control_device, confidence=1.0)
```
**Result:** Falls back to rule-based result after ML failure

### Scenario 3: ML Failure → No Rule Match → Unknown
```
INFO    - Classifying text: 'trời nóng quá'
DEBUG   - Routing to ML-based classifier
ERROR   - ML classifier failed: ML model inference failed
WARNING - Fallback triggered: Both classifiers failed, returning unknown (error: ML model inference failed)
```
**Result:** Returns unknown with error message

### Scenario 4: Confidence Comparison
```
INFO  - Classifying text: 'bật quạt'
DEBUG - Text 'bật quạt' matches simple command pattern (action=True, scene=False, words=2)
DEBUG - Routing to rule-based classifier (simple command detected)
DEBUG - Routing to ML-based classifier
INFO  - ML-based classifier result: intent=control_device, confidence=0.500
DEBUG - Comparing confidence scores: rule=1.000 vs ml=0.500
INFO  - Returning rule-based result (confidence=1.000 >= 0.500): intent=control_device
```
**Result:** Rule-based wins due to higher confidence

## Logging Configuration

### Recommended Production Configuration

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO for production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hybrid_classifier.log'),
        logging.StreamHandler()
    ]
)

# Set DEBUG level for development/debugging
# logging.getLogger('classifiers.hybrid').setLevel(logging.DEBUG)
```

### Log Rotation

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/hybrid_classifier.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logging.getLogger('classifiers.hybrid').addHandler(handler)
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **ML Failure Rate**
   - Count ERROR logs: "ML classifier failed"
   - Alert if > 5% of requests fail

2. **Fallback Rate**
   - Count WARNING logs: "Fallback triggered"
   - Alert if > 10% of requests use fallback

3. **Confidence Distribution**
   - Parse confidence values from INFO logs
   - Alert if average confidence < 0.7

4. **Routing Distribution**
   - Count "Routing to rule-based" vs "Routing to ML-based"
   - Monitor rule/ML ratio (expected: 30/70)

### Example Log Parsing

```python
import re

def parse_logs(log_file):
    """Parse logs to extract metrics."""
    ml_failures = 0
    fallbacks = 0
    confidences = []
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'ML classifier failed' in line:
                ml_failures += 1
            if 'Fallback triggered' in line:
                fallbacks += 1
            
            # Extract confidence scores
            match = re.search(r'confidence=(\d+\.\d+)', line)
            if match:
                confidences.append(float(match.group(1)))
    
    return {
        'ml_failures': ml_failures,
        'fallbacks': fallbacks,
        'avg_confidence': sum(confidences) / len(confidences) if confidences else 0
    }
```

## Testing Logging

### Unit Tests

The logging behavior is verified by the test suite:

```bash
# Run fallback tests
pytest ai/tests/unit/test_hybrid_classifier.py::TestHybridClassifierFallbackStrategy -v

# Run all hybrid classifier tests
pytest ai/tests/unit/test_hybrid_classifier.py -v
```

### Manual Testing

```python
import logging
from classifiers.hybrid import HybridClassifier
from classifiers.rule_based import RuleBasedClassifier
from classifiers.ml_based import MLBasedClassifier

# Enable DEBUG logging
logging.basicConfig(level=logging.DEBUG)

# Initialize classifiers
rule_classifier = RuleBasedClassifier()
ml_classifier = MLBasedClassifier()
hybrid = HybridClassifier(rule_classifier, ml_classifier)

# Test scenarios
hybrid.classify("bật đèn")  # Rule-based fast path
hybrid.classify("trời nóng quá")  # ML-based
```

## Summary

The HybridClassifier implements comprehensive logging that covers:

✅ **Routing Decisions** (INFO level)
- Classification start
- Routing to rule-based or ML-based
- Final decision with intent and confidence

✅ **ML Failures** (ERROR level)
- ML classifier exceptions with error messages

✅ **Fallback Triggers** (WARNING level)
- ML failure → rule-based fallback
- Both classifiers failed → unknown fallback

✅ **Confidence Comparisons** (DEBUG level)
- Pattern matching details
- Confidence score comparisons
- Routing logic details

✅ **Entity Preservation**
- Fallback preserves entities from rule-based classifier
- Error messages include context for debugging

This logging implementation satisfies all requirements for Task 9.3.
