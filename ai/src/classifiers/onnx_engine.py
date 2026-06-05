"""
ONNX Inference Engine for Vietnamese NLP Intent Classification.

This module provides an optimized inference engine using ONNX Runtime
for faster model inference (1.5-2x speedup compared to PyTorch).

**Validates: Requirements 9.9**
"""

import onnxruntime as ort
import numpy as np
import torch
from typing import Optional, List, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ONNXInferenceEngine:
    """
    ONNX Runtime Inference Engine for optimized model inference.
    
    This engine:
    - Loads ONNX model exported from PyTorch
    - Creates ONNX Runtime session with CPU and GPU providers
    - Runs inference on ONNX model (1.5-2x faster than PyTorch)
    - Automatically selects best available provider (CUDA > CPU)
    - Handles numpy arrays as input/output
    
    Performance:
    - CPU: ~1.5x faster than PyTorch
    - GPU (CUDA): ~2x faster than PyTorch
    """
    
    def __init__(self, model_path: str, use_gpu: bool = True):
        """
        Initialize ONNX Inference Engine.
        
        Args:
            model_path: Path to ONNX model file (.onnx)
            use_gpu: Whether to use GPU (CUDA) if available (default True)
        """
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ONNX model not found at {self.model_path}. "
                f"Please export the model first using scripts/export_to_onnx.py"
            )
        
        # Configure execution providers
        self.providers = self._configure_providers(use_gpu)
        
        # Create ONNX Runtime session
        self.session = self._create_session()
        
        # Get input/output names
        self.input_names = [input.name for input in self.session.get_inputs()]
        self.output_names = [output.name for output in self.session.get_outputs()]
        
        logger.info(f"ONNX Inference Engine initialized successfully")
        logger.info(f"  - Model path: {self.model_path}")
        logger.info(f"  - Providers: {self.providers}")
        logger.info(f"  - Input names: {self.input_names}")
        logger.info(f"  - Output names: {self.output_names}")
    
    def _configure_providers(self, use_gpu: bool) -> List[str]:
        """
        Configure execution providers based on availability.
        
        Priority order:
        1. CUDAExecutionProvider (GPU) - if available and use_gpu=True
        2. CPUExecutionProvider (CPU) - always available
        
        Args:
            use_gpu: Whether to use GPU if available
            
        Returns:
            List of provider names in priority order
        """
        available_providers = ort.get_available_providers()
        
        providers = []
        
        # Add CUDA provider if available and requested
        if use_gpu and 'CUDAExecutionProvider' in available_providers:
            providers.append('CUDAExecutionProvider')
            logger.info("CUDA provider available - using GPU acceleration")
        elif use_gpu:
            logger.warning("CUDA provider not available - falling back to CPU")
        
        # Always add CPU provider as fallback
        providers.append('CPUExecutionProvider')
        
        return providers
    
    def _create_session(self) -> ort.InferenceSession:
        """
        Create ONNX Runtime inference session.
        
        Returns:
            ONNX Runtime InferenceSession
        """
        # Configure session options
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        # Create session
        session = ort.InferenceSession(
            str(self.model_path),
            sess_options=sess_options,
            providers=self.providers
        )
        
        # Log which provider is actually being used
        actual_provider = session.get_providers()[0]
        logger.info(f"Using execution provider: {actual_provider}")
        
        return session
    
    def predict(self, 
                input_ids: np.ndarray, 
                attention_mask: np.ndarray) -> np.ndarray:
        """
        Run inference on ONNX model.
        
        Args:
            input_ids: Token IDs as numpy array (batch_size, seq_len)
            attention_mask: Attention mask as numpy array (batch_size, seq_len)
            
        Returns:
            Logits as numpy array (batch_size, num_intents)
        """
        # Prepare inputs
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
        
        # Run inference
        outputs = self.session.run(self.output_names, inputs)
        
        # Extract logits (first output)
        logits = outputs[0]
        
        return logits
    
    def predict_from_torch(self,
                           input_ids: torch.Tensor,
                           attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Run inference with PyTorch tensors as input/output.
        
        This is a convenience method that converts PyTorch tensors to numpy,
        runs inference, and converts back to PyTorch tensors.
        
        Args:
            input_ids: Token IDs as PyTorch tensor (batch_size, seq_len)
            attention_mask: Attention mask as PyTorch tensor (batch_size, seq_len)
            
        Returns:
            Logits as PyTorch tensor (batch_size, num_intents)
        """
        # Convert to numpy
        input_ids_np = input_ids.cpu().numpy()
        attention_mask_np = attention_mask.cpu().numpy()
        
        # Run inference
        logits_np = self.predict(input_ids_np, attention_mask_np)
        
        # Convert back to PyTorch tensor
        logits = torch.from_numpy(logits_np)
        
        return logits
    
    def get_provider_info(self) -> dict:
        """
        Get information about the execution provider being used.
        
        Returns:
            Dictionary with provider information:
            - provider: Name of the provider (e.g., "CUDAExecutionProvider")
            - device: Device type ("GPU" or "CPU")
            - available_providers: List of all available providers
        """
        actual_provider = self.session.get_providers()[0]
        
        device = "GPU" if "CUDA" in actual_provider else "CPU"
        
        return {
            "provider": actual_provider,
            "device": device,
            "available_providers": ort.get_available_providers()
        }
    
    def __repr__(self) -> str:
        """String representation of the engine."""
        provider_info = self.get_provider_info()
        return (
            f"ONNXInferenceEngine("
            f"model_path={self.model_path}, "
            f"provider={provider_info['provider']}, "
            f"device={provider_info['device']})"
        )
