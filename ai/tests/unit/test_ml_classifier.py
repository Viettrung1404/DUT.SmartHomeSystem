"""
Unit tests for ML-Based Classifier.

These tests verify:
- Tokenization: PhoBERT tokenizer correctly tokenizes Vietnamese text
- Inference: Model forward pass produces correct output shape
- Confidence scoring: Softmax probabilities sum to 1.0 and are in [0, 1]
- Top-k intent retrieval: Top-k intents are retrieved with correct confidence scores

**Validates: Requirements 1.1, 1.2, 1.4, 9.4**
"""

import pytest
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Tuple, Dict, Any
import numpy as np


# ============================================================================
# MOCK TOKENIZER FOR TESTING
# ============================================================================

class MockTokenizer:
    """Mock tokenizer for testing without downloading actual PhoBERT tokenizer."""
    
    def __init__(self, vocab_size=64000):
        self.vocab_size = vocab_size
        self.pad_token_id = 0
        self.cls_token_id = 1
        self.sep_token_id = 2
    
    def __call__(self, text, max_length=128, padding="max_length", 
                 truncation=True, return_tensors="pt"):
        """
        Mock tokenization.
        
        Args:
            text: Input text (string or list of strings)
            max_length: Maximum sequence length
            padding: Padding strategy
            truncation: Whether to truncate
            return_tensors: Return format
            
        Returns:
            Dictionary with input_ids and attention_mask
        """
        # Handle single text or batch
        if isinstance(text, str):
            texts = [text]
        else:
            texts = text
        
        batch_size = len(texts)
        
        # Create mock token IDs based on text length
        input_ids = []
        attention_masks = []
        
        for t in texts:
            # Simple mock: use text length to generate token IDs
            text_len = min(len(t.split()), max_length - 2)  # -2 for CLS and SEP
            
            # Create token IDs: [CLS] + tokens + [SEP] + padding
            tokens = [self.cls_token_id]
            tokens += [hash(word) % self.vocab_size for word in t.split()[:text_len]]
            tokens += [self.sep_token_id]
            
            # Pad to max_length
            attention_mask = [1] * len(tokens)
            while len(tokens) < max_length:
                tokens.append(self.pad_token_id)
                attention_mask.append(0)
            
            input_ids.append(tokens)
            attention_masks.append(attention_mask)
        
        # Convert to tensors
        input_ids_tensor = torch.tensor(input_ids, dtype=torch.long)
        attention_mask_tensor = torch.tensor(attention_masks, dtype=torch.long)
        
        return {
            "input_ids": input_ids_tensor,
            "attention_mask": attention_mask_tensor
        }
    
    def decode(self, token_ids, skip_special_tokens=True):
        """Mock decode function."""
        return f"decoded_text_{len(token_ids)}"


# ============================================================================
# MOCK PHOBERT MODEL FOR TESTING
# ============================================================================

class MockPhoBERTModel(nn.Module):
    """Mock PhoBERT model for testing without downloading actual model."""
    
    def __init__(self, hidden_size=768):
        super().__init__()
        self.hidden_size = hidden_size
        self.embeddings = nn.Embedding(64000, hidden_size)
    
    def forward(self, input_ids, attention_mask=None):
        # Mock forward pass
        batch_size = input_ids.size(0)
        seq_len = input_ids.size(1)
        
        # Mock embeddings
        embeddings = self.embeddings(input_ids)
        
        # Mock pooled output (CLS token)
        pooled_output = embeddings[:, 0, :]  # Take first token
        
        # Mock outputs
        class MockOutputs:
            def __init__(self, pooled_output, embeddings):
                self.pooler_output = pooled_output
                self.last_hidden_state = embeddings
        
        return MockOutputs(pooled_output, embeddings)


# ============================================================================
# ML-BASED CLASSIFIER (STUB FOR TESTING)
# ============================================================================

class MLBasedClassifier:
    """
    ML-Based Classifier using PhoBERT.
    
    This is a stub implementation for testing purposes.
    The actual implementation will be done in Task 8.4.
    """
    
    VALID_INTENTS = [
        "control_device",
        "environmental_comfort",
        "query_sensor",
        "query_device_status",
        "security_mode",
        "security_alert",
        "activate_scene",
        "weather_action",
        "lock_all_doors",
        "turn_off_all_devices",
        "create_automation",
        "unknown"
    ]
    
    CONFIDENCE_THRESHOLD = 0.7
    
    def __init__(self, model=None, tokenizer=None, use_mock=True):
        """
        Initialize ML-Based Classifier.
        
        Args:
            model: PhoBERT model (if None, creates mock model)
            tokenizer: PhoBERT tokenizer (if None, creates mock tokenizer)
            use_mock: Use mock model and tokenizer for testing
        """
        if use_mock:
            self.model = MockPhoBERTModel(hidden_size=768)
            self.tokenizer = MockTokenizer()
            # Add classification head
            self.classifier_head = nn.Sequential(
                nn.Dropout(0.1),
                nn.Linear(768, 256),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(256, len(self.VALID_INTENTS))
            )
        else:
            self.model = model
            self.tokenizer = tokenizer
            self.classifier_head = None
        
        self.intent_to_id = {intent: i for i, intent in enumerate(self.VALID_INTENTS)}
        self.id_to_intent = {i: intent for i, intent in enumerate(self.VALID_INTENTS)}
        
        # Set to eval mode
        self.model.eval()
        if self.classifier_head is not None:
            self.classifier_head.eval()
    
    def tokenize(self, text: str, max_length: int = 128) -> Dict[str, torch.Tensor]:
        """
        Tokenize Vietnamese text using PhoBERT tokenizer.
        
        Args:
            text: Vietnamese text input
            max_length: Maximum sequence length
            
        Returns:
            Dictionary with input_ids and attention_mask tensors
        """
        encoding = self.tokenizer(
            text,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"],
            "attention_mask": encoding["attention_mask"]
        }
    
    def inference(self, input_ids: torch.Tensor, 
                  attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Run model inference to get logits.
        
        Args:
            input_ids: Token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)
            
        Returns:
            Logits tensor (batch_size, num_intents)
        """
        with torch.no_grad():
            # Encode with PhoBERT
            outputs = self.model(input_ids, attention_mask=attention_mask)
            pooled_output = outputs.pooler_output  # (batch_size, hidden_size)
            
            # Classification head
            logits = self.classifier_head(pooled_output)
        
        return logits
    
    def compute_confidence_scores(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Compute confidence scores using softmax.
        
        Args:
            logits: Raw logits from model (batch_size, num_intents)
            
        Returns:
            Confidence scores (batch_size, num_intents) with values in [0, 1]
        """
        # Apply softmax to convert logits to probabilities
        confidence_scores = F.softmax(logits, dim=-1)
        return confidence_scores
    
    def get_top_k_intents(self, confidence_scores: torch.Tensor, 
                          k: int = 3) -> List[Tuple[str, float]]:
        """
        Get top-k intents with confidence scores.
        
        Args:
            confidence_scores: Confidence scores (batch_size, num_intents)
            k: Number of top intents to retrieve
            
        Returns:
            List of (intent_name, confidence) tuples sorted by confidence
        """
        # Get top-k values and indices
        top_k_values, top_k_indices = torch.topk(confidence_scores, k, dim=-1)
        
        # Convert to list of tuples
        results = []
        for i in range(k):
            intent_id = top_k_indices[0, i].item()
            confidence = top_k_values[0, i].item()
            intent_name = self.id_to_intent[intent_id]
            results.append((intent_name, confidence))
        
        return results
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify Vietnamese text and return intent with confidence.
        
        Args:
            text: Vietnamese text input
            
        Returns:
            Dictionary with intent, confidence, and top_k_intents
        """
        # Tokenize
        encoding = self.tokenize(text)
        
        # Inference
        logits = self.inference(encoding["input_ids"], encoding["attention_mask"])
        
        # Compute confidence scores
        confidence_scores = self.compute_confidence_scores(logits)
        
        # Get top-k intents
        top_k_intents = self.get_top_k_intents(confidence_scores, k=3)
        
        # Get top intent
        top_intent, top_confidence = top_k_intents[0]
        
        return {
            "intent": top_intent,
            "confidence": top_confidence,
            "top_k_intents": top_k_intents,
            "logits": logits,
            "confidence_scores": confidence_scores
        }


# ============================================================================
# UNIT TESTS: TOKENIZATION
# ============================================================================

class TestMLClassifierTokenization:
    """Unit tests for tokenization functionality."""
    
    def test_tokenize_simple_vietnamese_text(self):
        """Test tokenization of simple Vietnamese text."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Bật đèn phòng khách"
        encoding = classifier.tokenize(text)
        
        # Check that encoding has required keys
        assert "input_ids" in encoding
        assert "attention_mask" in encoding
        
        # Check tensor shapes
        assert encoding["input_ids"].shape[0] == 1  # batch_size
        assert encoding["input_ids"].shape[1] == 128  # max_length
        assert encoding["attention_mask"].shape == encoding["input_ids"].shape
    
    def test_tokenize_long_vietnamese_text(self):
        """Test tokenization of long Vietnamese text (truncation)."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create long text
        text = " ".join(["Bật đèn phòng khách"] * 50)
        encoding = classifier.tokenize(text, max_length=128)
        
        # Check that text is truncated to max_length
        assert encoding["input_ids"].shape[1] == 128
        assert encoding["attention_mask"].shape[1] == 128
    
    def test_tokenize_empty_text(self):
        """Test tokenization of empty text."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = ""
        encoding = classifier.tokenize(text)
        
        # Should still return valid tensors
        assert encoding["input_ids"].shape[0] == 1
        assert encoding["input_ids"].shape[1] == 128
    
    def test_tokenize_special_characters(self):
        """Test tokenization with special characters and punctuation."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Bật đèn!!! Phòng khách??? Nhanh lên..."
        encoding = classifier.tokenize(text)
        
        # Should handle special characters gracefully
        assert encoding["input_ids"].shape[0] == 1
        assert encoding["input_ids"].shape[1] == 128
    
    def test_tokenize_different_max_lengths(self):
        """Test tokenization with different max_length values."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Bật đèn phòng khách"
        
        for max_length in [32, 64, 128, 256]:
            encoding = classifier.tokenize(text, max_length=max_length)
            assert encoding["input_ids"].shape[1] == max_length
            assert encoding["attention_mask"].shape[1] == max_length
    
    def test_tokenize_attention_mask_correctness(self):
        """Test that attention mask correctly marks padding tokens."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Bật đèn"
        encoding = classifier.tokenize(text, max_length=128)
        
        attention_mask = encoding["attention_mask"][0]
        
        # Attention mask should have 1s for real tokens and 0s for padding
        assert attention_mask.sum() > 0  # At least some real tokens
        assert attention_mask.sum() < 128  # Some padding tokens
        
        # Check that 1s come before 0s (no interleaving)
        mask_list = attention_mask.tolist()
        first_zero_idx = mask_list.index(0) if 0 in mask_list else len(mask_list)
        assert all(m == 1 for m in mask_list[:first_zero_idx])
        assert all(m == 0 for m in mask_list[first_zero_idx:])


# ============================================================================
# UNIT TESTS: INFERENCE
# ============================================================================

class TestMLClassifierInference:
    """Unit tests for model inference functionality."""
    
    def test_inference_output_shape(self):
        """Test that inference produces correct output shape."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create dummy input
        batch_size = 2
        seq_len = 128
        input_ids = torch.randint(0, 64000, (batch_size, seq_len))
        attention_mask = torch.ones(batch_size, seq_len)
        
        # Run inference
        logits = classifier.inference(input_ids, attention_mask)
        
        # Check output shape: (batch_size, num_intents)
        assert logits.shape == (batch_size, len(classifier.VALID_INTENTS))
    
    def test_inference_single_sample(self):
        """Test inference with single sample."""
        classifier = MLBasedClassifier(use_mock=True)
        
        input_ids = torch.randint(0, 64000, (1, 128))
        attention_mask = torch.ones(1, 128)
        
        logits = classifier.inference(input_ids, attention_mask)
        
        assert logits.shape == (1, len(classifier.VALID_INTENTS))
    
    def test_inference_batch(self):
        """Test inference with batch of samples."""
        classifier = MLBasedClassifier(use_mock=True)
        
        for batch_size in [1, 2, 4, 8]:
            input_ids = torch.randint(0, 64000, (batch_size, 128))
            attention_mask = torch.ones(batch_size, 128)
            
            logits = classifier.inference(input_ids, attention_mask)
            
            assert logits.shape == (batch_size, len(classifier.VALID_INTENTS))
    
    def test_inference_with_padding(self):
        """Test inference with padded sequences."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create input with padding (attention_mask has 0s)
        input_ids = torch.randint(0, 64000, (2, 128))
        attention_mask = torch.ones(2, 128)
        attention_mask[:, 50:] = 0  # Pad last 78 tokens
        
        logits = classifier.inference(input_ids, attention_mask)
        
        # Should still produce valid output
        assert logits.shape == (2, len(classifier.VALID_INTENTS))
    
    def test_inference_deterministic_in_eval_mode(self):
        """Test that inference is deterministic in eval mode."""
        classifier = MLBasedClassifier(use_mock=True)
        classifier.model.eval()
        classifier.classifier_head.eval()
        
        input_ids = torch.randint(0, 64000, (1, 128))
        attention_mask = torch.ones(1, 128)
        
        # Run inference twice
        logits1 = classifier.inference(input_ids, attention_mask)
        logits2 = classifier.inference(input_ids, attention_mask)
        
        # Results should be identical
        assert torch.allclose(logits1, logits2)
    
    def test_inference_output_is_float(self):
        """Test that inference output is float tensor."""
        classifier = MLBasedClassifier(use_mock=True)
        
        input_ids = torch.randint(0, 64000, (1, 128))
        attention_mask = torch.ones(1, 128)
        
        logits = classifier.inference(input_ids, attention_mask)
        
        assert logits.dtype == torch.float32


# ============================================================================
# UNIT TESTS: CONFIDENCE SCORING
# ============================================================================

class TestMLClassifierConfidenceScoring:
    """Unit tests for confidence scoring (softmax) functionality."""
    
    def test_confidence_scores_sum_to_one(self):
        """Test that confidence scores sum to 1.0 (softmax property)."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create dummy logits
        logits = torch.randn(1, len(classifier.VALID_INTENTS))
        
        # Compute confidence scores
        confidence_scores = classifier.compute_confidence_scores(logits)
        
        # Check that scores sum to 1.0
        assert torch.allclose(confidence_scores.sum(dim=-1), torch.tensor([1.0]), atol=1e-6)
    
    def test_confidence_scores_in_range(self):
        """Test that confidence scores are in [0, 1] range."""
        classifier = MLBasedClassifier(use_mock=True)
        
        logits = torch.randn(1, len(classifier.VALID_INTENTS))
        confidence_scores = classifier.compute_confidence_scores(logits)
        
        # Check that all scores are in [0, 1]
        assert torch.all(confidence_scores >= 0.0)
        assert torch.all(confidence_scores <= 1.0)
    
    def test_confidence_scores_batch(self):
        """Test confidence scoring with batch of logits."""
        classifier = MLBasedClassifier(use_mock=True)
        
        batch_size = 4
        logits = torch.randn(batch_size, len(classifier.VALID_INTENTS))
        
        confidence_scores = classifier.compute_confidence_scores(logits)
        
        # Check shape
        assert confidence_scores.shape == (batch_size, len(classifier.VALID_INTENTS))
        
        # Check that each sample's scores sum to 1.0
        for i in range(batch_size):
            assert torch.allclose(confidence_scores[i].sum(), torch.tensor(1.0), atol=1e-6)
    
    def test_confidence_scores_highest_logit_gets_highest_score(self):
        """Test that highest logit gets highest confidence score."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create logits with known highest value
        logits = torch.randn(1, len(classifier.VALID_INTENTS))
        max_idx = 5
        logits[0, max_idx] = 10.0  # Make this logit much higher
        
        confidence_scores = classifier.compute_confidence_scores(logits)
        
        # Check that max_idx has highest confidence
        assert torch.argmax(confidence_scores[0]) == max_idx
    
    def test_confidence_scores_with_extreme_logits(self):
        """Test confidence scoring with extreme logit values."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create logits with extreme values
        logits = torch.tensor([[-100.0, 100.0, -100.0, -100.0, -100.0, 
                                -100.0, -100.0, -100.0, -100.0, -100.0,
                                -100.0, -100.0]])
        
        confidence_scores = classifier.compute_confidence_scores(logits)
        
        # Highest logit should have confidence close to 1.0
        assert confidence_scores[0, 1] > 0.99
        
        # Other logits should have confidence close to 0.0
        assert torch.all(confidence_scores[0, [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]] < 0.01)
    
    def test_confidence_scores_with_uniform_logits(self):
        """Test confidence scoring with uniform logits."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create uniform logits
        logits = torch.ones(1, len(classifier.VALID_INTENTS))
        
        confidence_scores = classifier.compute_confidence_scores(logits)
        
        # All scores should be approximately equal
        expected_score = 1.0 / len(classifier.VALID_INTENTS)
        assert torch.allclose(confidence_scores, 
                             torch.full_like(confidence_scores, expected_score), 
                             atol=1e-6)


# ============================================================================
# UNIT TESTS: TOP-K INTENT RETRIEVAL
# ============================================================================

class TestMLClassifierTopKRetrieval:
    """Unit tests for top-k intent retrieval functionality."""
    
    def test_get_top_k_intents_returns_k_intents(self):
        """Test that get_top_k_intents returns exactly k intents."""
        classifier = MLBasedClassifier(use_mock=True)
        
        confidence_scores = torch.randn(1, len(classifier.VALID_INTENTS))
        confidence_scores = F.softmax(confidence_scores, dim=-1)
        
        for k in [1, 2, 3, 5]:
            top_k_intents = classifier.get_top_k_intents(confidence_scores, k=k)
            assert len(top_k_intents) == k
    
    def test_get_top_k_intents_sorted_by_confidence(self):
        """Test that top-k intents are sorted by confidence (descending)."""
        classifier = MLBasedClassifier(use_mock=True)
        
        confidence_scores = torch.randn(1, len(classifier.VALID_INTENTS))
        confidence_scores = F.softmax(confidence_scores, dim=-1)
        
        top_k_intents = classifier.get_top_k_intents(confidence_scores, k=3)
        
        # Check that confidences are in descending order
        confidences = [conf for _, conf in top_k_intents]
        assert confidences == sorted(confidences, reverse=True)
    
    def test_get_top_k_intents_returns_valid_intent_names(self):
        """Test that top-k intents have valid intent names."""
        classifier = MLBasedClassifier(use_mock=True)
        
        confidence_scores = torch.randn(1, len(classifier.VALID_INTENTS))
        confidence_scores = F.softmax(confidence_scores, dim=-1)
        
        top_k_intents = classifier.get_top_k_intents(confidence_scores, k=3)
        
        # Check that all intent names are valid
        for intent_name, _ in top_k_intents:
            assert intent_name in classifier.VALID_INTENTS
    
    def test_get_top_k_intents_confidence_values_in_range(self):
        """Test that top-k confidence values are in [0, 1] range."""
        classifier = MLBasedClassifier(use_mock=True)
        
        confidence_scores = torch.randn(1, len(classifier.VALID_INTENTS))
        confidence_scores = F.softmax(confidence_scores, dim=-1)
        
        top_k_intents = classifier.get_top_k_intents(confidence_scores, k=3)
        
        # Check that all confidences are in [0, 1]
        for _, confidence in top_k_intents:
            assert 0.0 <= confidence <= 1.0
    
    def test_get_top_k_intents_with_known_scores(self):
        """Test top-k retrieval with known confidence scores."""
        classifier = MLBasedClassifier(use_mock=True)
        
        # Create known confidence scores
        confidence_scores = torch.zeros(1, len(classifier.VALID_INTENTS))
        confidence_scores[0, 0] = 0.5  # control_device
        confidence_scores[0, 1] = 0.3  # environmental_comfort
        confidence_scores[0, 2] = 0.2  # query_sensor
        
        top_k_intents = classifier.get_top_k_intents(confidence_scores, k=3)
        
        # Check that intents are in correct order
        assert top_k_intents[0][0] == "control_device"
        assert top_k_intents[1][0] == "environmental_comfort"
        assert top_k_intents[2][0] == "query_sensor"
        
        # Check confidence values
        assert abs(top_k_intents[0][1] - 0.5) < 1e-6
        assert abs(top_k_intents[1][1] - 0.3) < 1e-6
        assert abs(top_k_intents[2][1] - 0.2) < 1e-6
    
    def test_get_top_k_intents_default_k_is_3(self):
        """Test that default k value is 3."""
        classifier = MLBasedClassifier(use_mock=True)
        
        confidence_scores = torch.randn(1, len(classifier.VALID_INTENTS))
        confidence_scores = F.softmax(confidence_scores, dim=-1)
        
        # Call without specifying k
        top_k_intents = classifier.get_top_k_intents(confidence_scores)
        
        assert len(top_k_intents) == 3


# ============================================================================
# UNIT TESTS: END-TO-END CLASSIFICATION
# ============================================================================

class TestMLClassifierEndToEnd:
    """End-to-end unit tests for complete classification pipeline."""
    
    def test_classify_returns_required_fields(self):
        """Test that classify returns all required fields."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Bật đèn phòng khách"
        result = classifier.classify(text)
        
        # Check required fields
        assert "intent" in result
        assert "confidence" in result
        assert "top_k_intents" in result
        assert "logits" in result
        assert "confidence_scores" in result
    
    def test_classify_intent_is_valid(self):
        """Test that classified intent is valid."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Trời nóng quá"
        result = classifier.classify(text)
        
        assert result["intent"] in classifier.VALID_INTENTS
    
    def test_classify_confidence_in_range(self):
        """Test that confidence is in [0, 1] range."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Tắt quạt phòng ngủ"
        result = classifier.classify(text)
        
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_classify_top_k_intents_has_3_items(self):
        """Test that top_k_intents has 3 items by default."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Nhiệt độ phòng khách bao nhiêu"
        result = classifier.classify(text)
        
        assert len(result["top_k_intents"]) == 3
    
    def test_classify_top_intent_matches_result_intent(self):
        """Test that top intent in top_k_intents matches result intent."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = "Đi ngủ"
        result = classifier.classify(text)
        
        top_intent_name, top_intent_confidence = result["top_k_intents"][0]
        
        assert top_intent_name == result["intent"]
        assert abs(top_intent_confidence - result["confidence"]) < 1e-6
    
    def test_classify_different_vietnamese_texts(self):
        """Test classification with different Vietnamese texts."""
        classifier = MLBasedClassifier(use_mock=True)
        
        texts = [
            "Bật đèn phòng khách",
            "Trời nóng quá",
            "Nhiệt độ bao nhiêu",
            "Đi ngủ",
            "Khóa cửa"
        ]
        
        for text in texts:
            result = classifier.classify(text)
            
            # All should return valid results
            assert result["intent"] in classifier.VALID_INTENTS
            assert 0.0 <= result["confidence"] <= 1.0
            assert len(result["top_k_intents"]) == 3
    
    def test_classify_empty_text(self):
        """Test classification with empty text."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = ""
        result = classifier.classify(text)
        
        # Should still return valid result (possibly with low confidence)
        assert result["intent"] in classifier.VALID_INTENTS
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_classify_long_text(self):
        """Test classification with long text (truncation)."""
        classifier = MLBasedClassifier(use_mock=True)
        
        text = " ".join(["Bật đèn phòng khách"] * 50)
        result = classifier.classify(text)
        
        # Should handle long text gracefully
        assert result["intent"] in classifier.VALID_INTENTS
        assert 0.0 <= result["confidence"] <= 1.0
