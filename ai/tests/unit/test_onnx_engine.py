"""
Unit tests for ONNX Inference Engine.

These tests verify:
- ONNX engine initialization with CPU and GPU providers
- Model loading from ONNX file
- Inference with numpy arrays
- Inference with PyTorch tensors
- Provider selection and configuration
- Output shape and correctness

**Validates: Requirements 9.9**
"""

import pytest
import numpy as np
import torch
from pathlib import Path

# Import ONNX engine
try:
    from src.classifiers.onnx_engine import ONNXInferenceEngine
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False


# Skip all tests if ONNX is not available
pytestmark = pytest.mark.skipif(
    not ONNX_AVAILABLE,
    reason="ONNX Runtime not available"
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def onnx_model_path():
    """Path to ONNX model file."""
    return "ai/models/phobert_intent_v1/best_model.onnx"


@pytest.fixture
def onnx_engine_cpu(onnx_model_path):
    """ONNX engine with CPU provider."""
    if not Path(onnx_model_path).exists():
        pytest.skip(f"ONNX model not found at {onnx_model_path}")
    
    return ONNXInferenceEngine(onnx_model_path, use_gpu=False)


@pytest.fixture
def onnx_engine_gpu(onnx_model_path):
    """ONNX engine with GPU provider (if available)."""
    if not Path(onnx_model_path).exists():
        pytest.skip(f"ONNX model not found at {onnx_model_path}")
    
    return ONNXInferenceEngine(onnx_model_path, use_gpu=True)


@pytest.fixture
def dummy_input():
    """Dummy input for testing."""
    batch_size = 2
    seq_len = 128
    
    input_ids = np.random.randint(0, 64000, (batch_size, seq_len), dtype=np.int64)
    attention_mask = np.ones((batch_size, seq_len), dtype=np.int64)
    
    return input_ids, attention_mask


# ============================================================================
# UNIT TESTS: INITIALIZATION
# ============================================================================

class TestONNXEngineInitialization:
    """Unit tests for ONNX engine initialization."""
    
    def test_init_with_cpu_provider(self, onnx_model_path):
        """Test initialization with CPU provider."""
        if not Path(onnx_model_path).exists():
            pytest.skip(f"ONNX model not found at {onnx_model_path}")
        
        engine = ONNXInferenceEngine(onnx_model_path, use_gpu=False)
        
        # Check that engine is initialized
        assert engine is not None
        assert engine.session is not None
        
        # Check that CPU provider is used
        provider_info = engine.get_provider_info()
        assert provider_info["device"] == "CPU"
    
    def test_init_with_gpu_provider(self, onnx_model_path):
        """Test initialization with GPU provider (if available)."""
        if not Path(onnx_model_path).exists():
            pytest.skip(f"ONNX model not found at {onnx_model_path}")
        
        engine = ONNXInferenceEngine(onnx_model_path, use_gpu=True)
        
        # Check that engine is initialized
        assert engine is not None
        assert engine.session is not None
        
        # Provider info should indicate GPU or CPU (fallback)
        provider_info = engine.get_provider_info()
        assert provider_info["device"] in ["GPU", "CPU"]
    
    def test_init_with_invalid_path(self):
        """Test initialization with invalid model path."""
        with pytest.raises(FileNotFoundError):
            ONNXInferenceEngine("invalid/path/model.onnx")
    
    def test_input_output_names(self, onnx_engine_cpu):
        """Test that input/output names are correctly loaded."""
        # Check input names
        assert "input_ids" in onnx_engine_cpu.input_names
        assert "attention_mask" in onnx_engine_cpu.input_names
        
        # Check output names
        assert "logits" in onnx_engine_cpu.output_names
    
    def test_repr(self, onnx_engine_cpu):
        """Test string representation of engine."""
        repr_str = repr(onnx_engine_cpu)
        
        assert "ONNXInferenceEngine" in repr_str
        assert "model_path" in repr_str
        assert "provider" in repr_str


# ============================================================================
# UNIT TESTS: INFERENCE WITH NUMPY
# ============================================================================

class TestONNXEngineInferenceNumpy:
    """Unit tests for ONNX inference with numpy arrays."""
    
    def test_predict_with_numpy(self, onnx_engine_cpu, dummy_input):
        """Test inference with numpy arrays."""
        input_ids, attention_mask = dummy_input
        
        # Run inference
        logits = onnx_engine_cpu.predict(input_ids, attention_mask)
        
        # Check output shape
        assert logits.shape == (2, 12)  # (batch_size, num_intents)
        
        # Check output type
        assert isinstance(logits, np.ndarray)
    
    def test_predict_single_sample(self, onnx_engine_cpu):
        """Test inference with single sample."""
        input_ids = np.random.randint(0, 64000, (1, 128), dtype=np.int64)
        attention_mask = np.ones((1, 128), dtype=np.int64)
        
        logits = onnx_engine_cpu.predict(input_ids, attention_mask)
        
        assert logits.shape == (1, 12)
    
    def test_predict_batch(self, onnx_engine_cpu):
        """Test inference with batch of samples."""
        for batch_size in [1, 2, 4, 8]:
            input_ids = np.random.randint(0, 64000, (batch_size, 128), dtype=np.int64)
            attention_mask = np.ones((batch_size, 128), dtype=np.int64)
            
            logits = onnx_engine_cpu.predict(input_ids, attention_mask)
            
            assert logits.shape == (batch_size, 12)
    
    def test_predict_output_is_float(self, onnx_engine_cpu, dummy_input):
        """Test that inference output is float."""
        input_ids, attention_mask = dummy_input
        
        logits = onnx_engine_cpu.predict(input_ids, attention_mask)
        
        assert logits.dtype == np.float32


# ============================================================================
# UNIT TESTS: INFERENCE WITH PYTORCH
# ============================================================================

class TestONNXEngineInferencePyTorch:
    """Unit tests for ONNX inference with PyTorch tensors."""
    
    def test_predict_from_torch(self, onnx_engine_cpu):
        """Test inference with PyTorch tensors."""
        input_ids = torch.randint(0, 64000, (2, 128), dtype=torch.long)
        attention_mask = torch.ones(2, 128, dtype=torch.long)
        
        # Run inference
        logits = onnx_engine_cpu.predict_from_torch(input_ids, attention_mask)
        
        # Check output shape
        assert logits.shape == (2, 12)
        
        # Check output type
        assert isinstance(logits, torch.Tensor)
    
    def test_predict_from_torch_single_sample(self, onnx_engine_cpu):
        """Test inference with single PyTorch sample."""
        input_ids = torch.randint(0, 64000, (1, 128), dtype=torch.long)
        attention_mask = torch.ones(1, 128, dtype=torch.long)
        
        logits = onnx_engine_cpu.predict_from_torch(input_ids, attention_mask)
        
        assert logits.shape == (1, 12)
    
    def test_predict_from_torch_batch(self, onnx_engine_cpu):
        """Test inference with batch of PyTorch samples."""
        for batch_size in [1, 2, 4, 8]:
            input_ids = torch.randint(0, 64000, (batch_size, 128), dtype=torch.long)
            attention_mask = torch.ones(batch_size, 128, dtype=torch.long)
            
            logits = onnx_engine_cpu.predict_from_torch(input_ids, attention_mask)
            
            assert logits.shape == (batch_size, 12)
    
    def test_predict_from_torch_output_is_float(self, onnx_engine_cpu):
        """Test that PyTorch inference output is float."""
        input_ids = torch.randint(0, 64000, (2, 128), dtype=torch.long)
        attention_mask = torch.ones(2, 128, dtype=torch.long)
        
        logits = onnx_engine_cpu.predict_from_torch(input_ids, attention_mask)
        
        assert logits.dtype == torch.float32


# ============================================================================
# UNIT TESTS: PROVIDER CONFIGURATION
# ============================================================================

class TestONNXEngineProviderConfiguration:
    """Unit tests for provider configuration."""
    
    def test_get_provider_info(self, onnx_engine_cpu):
        """Test getting provider information."""
        provider_info = onnx_engine_cpu.get_provider_info()
        
        # Check required keys
        assert "provider" in provider_info
        assert "device" in provider_info
        assert "available_providers" in provider_info
        
        # Check device type
        assert provider_info["device"] in ["GPU", "CPU"]
        
        # Check available providers is a list
        assert isinstance(provider_info["available_providers"], list)
    
    def test_cpu_provider_is_always_available(self, onnx_engine_cpu):
        """Test that CPU provider is always available."""
        provider_info = onnx_engine_cpu.get_provider_info()
        
        assert "CPUExecutionProvider" in provider_info["available_providers"]
    
    def test_provider_fallback_to_cpu(self, onnx_model_path):
        """Test that engine falls back to CPU if GPU is not available."""
        if not Path(onnx_model_path).exists():
            pytest.skip(f"ONNX model not found at {onnx_model_path}")
        
        # Try to create engine with GPU
        engine = ONNXInferenceEngine(onnx_model_path, use_gpu=True)
        
        # Should have at least CPU provider
        provider_info = engine.get_provider_info()
        assert provider_info["provider"] in ["CUDAExecutionProvider", "CPUExecutionProvider"]


# ============================================================================
# UNIT TESTS: DETERMINISM
# ============================================================================

class TestONNXEngineDeterminism:
    """Unit tests for inference determinism."""
    
    def test_inference_is_deterministic(self, onnx_engine_cpu):
        """Test that inference is deterministic (same input -> same output)."""
        input_ids = np.random.randint(0, 64000, (1, 128), dtype=np.int64)
        attention_mask = np.ones((1, 128), dtype=np.int64)
        
        # Run inference twice
        logits1 = onnx_engine_cpu.predict(input_ids, attention_mask)
        logits2 = onnx_engine_cpu.predict(input_ids, attention_mask)
        
        # Results should be identical
        np.testing.assert_allclose(logits1, logits2, rtol=1e-6, atol=1e-6)
    
    def test_inference_from_torch_is_deterministic(self, onnx_engine_cpu):
        """Test that PyTorch inference is deterministic."""
        input_ids = torch.randint(0, 64000, (1, 128), dtype=torch.long)
        attention_mask = torch.ones(1, 128, dtype=torch.long)
        
        # Run inference twice
        logits1 = onnx_engine_cpu.predict_from_torch(input_ids, attention_mask)
        logits2 = onnx_engine_cpu.predict_from_torch(input_ids, attention_mask)
        
        # Results should be identical
        assert torch.allclose(logits1, logits2, rtol=1e-6, atol=1e-6)
