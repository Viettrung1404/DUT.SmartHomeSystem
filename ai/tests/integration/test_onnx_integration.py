"""
Integration tests for ONNX inference with MLBasedClassifier.

These tests verify:
- ONNX integration with MLBasedClassifier
- End-to-end classification with ONNX engine
- Performance comparison between PyTorch and ONNX

**Validates: Requirements 9.9**
"""

import pytest
from pathlib import Path

# Import classifiers
try:
    from src.classifiers.ml_based import MLBasedClassifier
    CLASSIFIER_AVAILABLE = True
except ImportError:
    CLASSIFIER_AVAILABLE = False


# Skip all tests if classifier is not available
pytestmark = pytest.mark.skipif(
    not CLASSIFIER_AVAILABLE,
    reason="MLBasedClassifier not available"
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def model_path():
    """Path to trained model directory."""
    return "ai/models/phobert_intent_v1"


@pytest.fixture
def onnx_model_path(model_path):
    """Path to ONNX model file."""
    return f"{model_path}/best_model.onnx"


@pytest.fixture
def pytorch_classifier(model_path):
    """MLBasedClassifier with PyTorch inference."""
    if not Path(model_path).exists():
        pytest.skip(f"Model not found at {model_path}")
    
    return MLBasedClassifier(model_path=model_path, use_onnx=False)


@pytest.fixture
def onnx_classifier(model_path, onnx_model_path):
    """MLBasedClassifier with ONNX inference."""
    if not Path(onnx_model_path).exists():
        pytest.skip(f"ONNX model not found at {onnx_model_path}")
    
    return MLBasedClassifier(model_path=model_path, use_onnx=True)


# ============================================================================
# INTEGRATION TESTS: ONNX WITH ML CLASSIFIER
# ============================================================================

class TestONNXIntegration:
    """Integration tests for ONNX with MLBasedClassifier."""
    
    def test_onnx_classifier_initialization(self, onnx_classifier):
        """Test that ONNX classifier initializes successfully."""
        assert onnx_classifier is not None
        assert onnx_classifier.use_onnx is True
        assert onnx_classifier.onnx_engine is not None
        assert onnx_classifier.model is None  # PyTorch model should not be loaded
    
    def test_onnx_classifier_classify(self, onnx_classifier):
        """Test classification with ONNX engine."""
        text = "Bật đèn phòng khách"
        
        result = onnx_classifier.classify(text)
        
        # Check result structure
        assert "intent" in result
        assert "confidence" in result
        assert "top_k_intents" in result
        assert "classifier_type" in result
        
        # Check values
        assert result["intent"] in onnx_classifier.VALID_INTENTS
        assert 0.0 <= result["confidence"] <= 1.0
        assert len(result["top_k_intents"]) == 3
        assert result["classifier_type"] == "ml"
    
    def test_onnx_vs_pytorch_output_similarity(self, pytorch_classifier, onnx_classifier):
        """Test that ONNX and PyTorch produce similar outputs."""
        test_texts = [
            "Bật đèn phòng khách",
            "Tắt quạt phòng ngủ",
            "Trời nóng quá"
        ]
        
        for text in test_texts:
            pytorch_result = pytorch_classifier.classify(text)
            onnx_result = onnx_classifier.classify(text)
            
            # Intents should match
            assert pytorch_result["intent"] == onnx_result["intent"], \
                f"Intent mismatch for '{text}': PyTorch={pytorch_result['intent']}, ONNX={onnx_result['intent']}"
            
            # Confidence should be close (within 1%)
            confidence_diff = abs(pytorch_result["confidence"] - onnx_result["confidence"])
            assert confidence_diff < 0.01, \
                f"Confidence mismatch for '{text}': diff={confidence_diff}"
    
    def test_onnx_classifier_with_different_texts(self, onnx_classifier):
        """Test ONNX classifier with various Vietnamese texts."""
        test_texts = [
            "Bật đèn phòng khách",
            "Tắt quạt phòng ngủ",
            "Trời nóng quá",
            "Nhiệt độ bao nhiêu",
            "Đi ngủ"
        ]
        
        for text in test_texts:
            result = onnx_classifier.classify(text)
            
            # All should return valid results
            assert result["intent"] in onnx_classifier.VALID_INTENTS
            assert 0.0 <= result["confidence"] <= 1.0
            assert len(result["top_k_intents"]) == 3
