"""
Export PhoBERT Intent Classifier to ONNX Format.

This script exports a trained PyTorch model to ONNX format for optimized inference.
It also validates that ONNX outputs match PyTorch outputs.

**Validates: Requirements 9.9**

Usage:
    python scripts/export_to_onnx.py --model models/phobert_intent_v1 --output models/phobert_intent_v1.onnx
"""

import json
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

import torch
import torch.nn as nn
import onnx
import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer

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
# ONNX EXPORT FUNCTIONS
# ============================================================================

def export_to_onnx(model: nn.Module, 
                   tokenizer,
                   output_path: str,
                   opset_version: int = 14,
                   dynamic_axes: bool = True):
    """
    Export PyTorch model to ONNX format.
    
    Args:
        model: PyTorch model to export
        tokenizer: Tokenizer for creating dummy input
        output_path: Path to save ONNX model
        opset_version: ONNX opset version (default 14)
        dynamic_axes: Whether to use dynamic axes for batch size and sequence length
    """
    logger.info("Exporting model to ONNX format...")
    
    # Set model to eval mode
    model.eval()
    
    # Create dummy input
    dummy_text = "Bật đèn phòng khách"
    inputs = tokenizer(
        dummy_text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=128
    )
    
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    
    logger.info(f"Dummy input shape: input_ids={input_ids.shape}, attention_mask={attention_mask.shape}")
    
    # Define input/output names
    input_names = ["input_ids", "attention_mask"]
    output_names = ["logits"]
    
    # Define dynamic axes if enabled
    if dynamic_axes:
        dynamic_axes_dict = {
            "input_ids": {0: "batch_size", 1: "sequence_length"},
            "attention_mask": {0: "batch_size", 1: "sequence_length"},
            "logits": {0: "batch_size"}
        }
    else:
        dynamic_axes_dict = None
    
    # Export to ONNX
    try:
        torch.onnx.export(
            model,
            (input_ids, attention_mask),
            output_path,
            input_names=input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes_dict,
            opset_version=opset_version,
            do_constant_folding=True,
            export_params=True,
            verbose=False
        )
        logger.info(f"Model exported to {output_path}")
    except Exception as e:
        logger.error(f"Failed to export model: {e}")
        raise


def validate_onnx_model(onnx_path: str):
    """
    Validate ONNX model structure.
    
    Args:
        onnx_path: Path to ONNX model
    """
    logger.info("Validating ONNX model...")
    
    try:
        # Load ONNX model
        onnx_model = onnx.load(onnx_path)
        
        # Check model
        onnx.checker.check_model(onnx_model)
        
        logger.info("ONNX model is valid!")
        
        # Print model info
        logger.info(f"ONNX opset version: {onnx_model.opset_import[0].version}")
        logger.info(f"Model inputs: {[input.name for input in onnx_model.graph.input]}")
        logger.info(f"Model outputs: {[output.name for output in onnx_model.graph.output]}")
        
    except Exception as e:
        logger.error(f"ONNX model validation failed: {e}")
        raise


def compare_outputs(pytorch_model: nn.Module,
                   onnx_path: str,
                   tokenizer,
                   test_texts: list,
                   tolerance: float = 1e-5) -> bool:
    """
    Compare PyTorch and ONNX model outputs to ensure they match.
    
    Args:
        pytorch_model: PyTorch model
        onnx_path: Path to ONNX model
        tokenizer: Tokenizer
        test_texts: List of test texts
        tolerance: Tolerance for numerical differences
        
    Returns:
        True if outputs match within tolerance, False otherwise
    """
    logger.info("Comparing PyTorch and ONNX outputs...")
    
    # Load ONNX model
    ort_session = ort.InferenceSession(
        onnx_path,
        providers=['CPUExecutionProvider']
    )
    
    pytorch_model.eval()
    
    all_match = True
    max_diff = 0.0
    
    for text in test_texts:
        # Tokenize
        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=128
        )
        
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]
        
        # PyTorch inference
        with torch.no_grad():
            pytorch_logits = pytorch_model(input_ids, attention_mask)
            pytorch_logits = pytorch_logits.numpy()
        
        # ONNX inference
        onnx_inputs = {
            "input_ids": input_ids.numpy(),
            "attention_mask": attention_mask.numpy()
        }
        onnx_logits = ort_session.run(["logits"], onnx_inputs)[0]
        
        # Compare outputs
        diff = np.abs(pytorch_logits - onnx_logits).max()
        max_diff = max(max_diff, diff)
        
        if diff > tolerance:
            logger.warning(f"Output mismatch for text '{text}': max diff = {diff}")
            all_match = False
        else:
            logger.info(f"✓ Outputs match for text '{text}' (max diff = {diff:.2e})")
    
    logger.info(f"Maximum difference across all tests: {max_diff:.2e}")
    
    if all_match:
        logger.info("✓ All outputs match within tolerance!")
    else:
        logger.warning("⚠ Some outputs do not match within tolerance")
    
    return all_match


def benchmark_inference_speed(pytorch_model: nn.Module,
                              onnx_path: str,
                              tokenizer,
                              num_iterations: int = 100):
    """
    Benchmark inference speed for PyTorch vs ONNX.
    
    Args:
        pytorch_model: PyTorch model
        onnx_path: Path to ONNX model
        tokenizer: Tokenizer
        num_iterations: Number of iterations for benchmarking
    """
    import time
    
    logger.info(f"Benchmarking inference speed ({num_iterations} iterations)...")
    
    # Load ONNX model
    ort_session = ort.InferenceSession(
        onnx_path,
        providers=['CPUExecutionProvider']
    )
    
    pytorch_model.eval()
    
    # Prepare input
    text = "Bật đèn phòng khách"
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding="max_length",
        truncation=True,
        max_length=128
    )
    
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    
    # Warmup
    for _ in range(10):
        with torch.no_grad():
            _ = pytorch_model(input_ids, attention_mask)
        _ = ort_session.run(["logits"], {
            "input_ids": input_ids.numpy(),
            "attention_mask": attention_mask.numpy()
        })
    
    # Benchmark PyTorch
    pytorch_times = []
    for _ in range(num_iterations):
        start = time.time()
        with torch.no_grad():
            _ = pytorch_model(input_ids, attention_mask)
        pytorch_times.append((time.time() - start) * 1000)  # ms
    
    # Benchmark ONNX
    onnx_times = []
    onnx_inputs = {
        "input_ids": input_ids.numpy(),
        "attention_mask": attention_mask.numpy()
    }
    for _ in range(num_iterations):
        start = time.time()
        _ = ort_session.run(["logits"], onnx_inputs)
        onnx_times.append((time.time() - start) * 1000)  # ms
    
    # Calculate statistics
    pytorch_mean = np.mean(pytorch_times)
    pytorch_std = np.std(pytorch_times)
    onnx_mean = np.mean(onnx_times)
    onnx_std = np.std(onnx_times)
    speedup = pytorch_mean / onnx_mean
    
    logger.info(f"PyTorch inference time: {pytorch_mean:.2f} ± {pytorch_std:.2f} ms")
    logger.info(f"ONNX inference time: {onnx_mean:.2f} ± {onnx_std:.2f} ms")
    logger.info(f"Speedup: {speedup:.2f}x")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main export function."""
    parser = argparse.ArgumentParser(description="Export PhoBERT Intent Classifier to ONNX")
    parser.add_argument("--model", type=str, required=True, help="Path to trained model directory")
    parser.add_argument("--output", type=str, required=True, help="Output ONNX file path")
    parser.add_argument("--opset", type=int, default=14, help="ONNX opset version")
    parser.add_argument("--validate", action="store_true", help="Validate ONNX model")
    parser.add_argument("--compare", action="store_true", help="Compare PyTorch and ONNX outputs")
    parser.add_argument("--benchmark", action="store_true", help="Benchmark inference speed")
    parser.add_argument("--tolerance", type=float, default=1e-5, help="Tolerance for output comparison")
    
    args = parser.parse_args()
    
    model_dir = Path(args.model)
    output_path = Path(args.output)
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load model config
    config_path = model_dir / "config.json"
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    logger.info(f"Loading model from {model_dir}")
    logger.info(f"Model config: {config}")
    
    # Load model
    try:
        model = PhoBERTIntentClassifier.from_pretrained(str(model_dir))
        model.eval()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return
    
    # Load tokenizer
    model_name = config.get("model_name", "vinai/phobert-base")
    logger.info(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Export to ONNX
    try:
        export_to_onnx(
            model=model,
            tokenizer=tokenizer,
            output_path=str(output_path),
            opset_version=args.opset,
            dynamic_axes=True
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return
    
    # Validate ONNX model
    if args.validate:
        try:
            validate_onnx_model(str(output_path))
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return
    
    # Compare outputs
    if args.compare:
        test_texts = [
            "Bật đèn phòng khách",
            "Tắt quạt phòng ngủ",
            "Trời nóng quá",
            "Nhiệt độ bao nhiêu",
            "Đi ngủ"
        ]
        
        try:
            match = compare_outputs(
                pytorch_model=model,
                onnx_path=str(output_path),
                tokenizer=tokenizer,
                test_texts=test_texts,
                tolerance=args.tolerance
            )
            
            if not match:
                logger.warning("Outputs do not match! Consider adjusting tolerance or checking model.")
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            return
    
    # Benchmark inference speed
    if args.benchmark:
        try:
            benchmark_inference_speed(
                pytorch_model=model,
                onnx_path=str(output_path),
                tokenizer=tokenizer,
                num_iterations=100
            )
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            return
    
    logger.info(f"\n✓ Export completed successfully!")
    logger.info(f"ONNX model saved to: {output_path}")


if __name__ == "__main__":
    main()
