"""
Unit tests for PhoBERT Intent Classifier Model.

These tests verify:
- Model architecture (forward pass, output shape)
- Context embedding concatenation
- Classification head dimensions
- Model initialization

**Validates: Requirements 9.4**
"""

import pytest
import torch
import torch.nn as nn


# ============================================================================
# MOCK PHOBERT MODEL FOR TESTING (without actual PhoBERT download)
# ============================================================================

class MockPhoBERTModel(nn.Module):
    """Mock PhoBERT model for testing without downloading actual model."""
    
    def __init__(self, hidden_size=768):
        super().__init__()
        self.hidden_size = hidden_size
        self.embeddings = nn.Embedding(1000, hidden_size)
    
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
            def __init__(self, pooled_output):
                self.pooler_output = pooled_output
                self.last_hidden_state = embeddings
        
        return MockOutputs(pooled_output)


class PhoBERTIntentClassifier(nn.Module):
    """
    PhoBERT-based Intent Classifier.
    
    Architecture:
    - PhoBERT encoder (768-dim output)
    - Optional context embedding (32-dim)
    - Classification head: 768+32 → 256 → num_intents
    """
    
    def __init__(self, num_intents: int = 12, 
                 hidden_size: int = 768,
                 context_dim: int = 32,
                 dropout: float = 0.1,
                 use_mock: bool = True):
        """
        Initialize PhoBERT Intent Classifier.
        
        Args:
            num_intents: Number of intent classes
            hidden_size: PhoBERT hidden size (default 768)
            context_dim: Context embedding dimension (default 32)
            dropout: Dropout rate (default 0.1)
            use_mock: Use mock model for testing (default True)
        """
        super().__init__()
        
        self.num_intents = num_intents
        self.hidden_size = hidden_size
        self.context_dim = context_dim
        
        # PhoBERT encoder (mock for testing)
        if use_mock:
            self.encoder = MockPhoBERTModel(hidden_size)
        else:
            # Real PhoBERT will be loaded here
            from transformers import AutoModel
            self.encoder = AutoModel.from_pretrained("vinai/phobert-base")
        
        # Classification head
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size + context_dim, 256)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(256, num_intents)
    
    def forward(self, input_ids, attention_mask=None, context_embedding=None):
        """
        Forward pass.
        
        Args:
            input_ids: Token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)
            context_embedding: Optional context embedding (batch_size, context_dim)
            
        Returns:
            Logits (batch_size, num_intents)
        """
        # Encode with PhoBERT
        outputs = self.encoder(input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output  # (batch_size, hidden_size)
        
        # Concatenate context if provided
        if context_embedding is not None:
            pooled_output = torch.cat([pooled_output, context_embedding], dim=1)
        else:
            # Pad with zeros if no context
            batch_size = pooled_output.size(0)
            zero_context = torch.zeros(batch_size, self.context_dim, device=pooled_output.device)
            pooled_output = torch.cat([pooled_output, zero_context], dim=1)
        
        # Classification head
        x = self.dropout(pooled_output)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        logits = self.fc2(x)
        
        return logits


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestPhoBERTIntentClassifier:
    """Unit tests for PhoBERT Intent Classifier."""
    
    def test_model_initialization(self):
        """Test that model initializes correctly."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        
        assert model.num_intents == 12
        assert model.hidden_size == 768
        assert model.context_dim == 32
        assert isinstance(model.encoder, MockPhoBERTModel)
        assert isinstance(model.fc1, nn.Linear)
        assert isinstance(model.fc2, nn.Linear)
    
    def test_forward_pass_without_context(self):
        """Test forward pass without context embedding."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        model.eval()
        
        # Create dummy input
        batch_size = 4
        seq_len = 32
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        attention_mask = torch.ones(batch_size, seq_len)
        
        # Forward pass
        with torch.no_grad():
            logits = model(input_ids, attention_mask)
        
        # Check output shape
        assert logits.shape == (batch_size, 12)
    
    def test_forward_pass_with_context(self):
        """Test forward pass with context embedding."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        model.eval()
        
        # Create dummy input
        batch_size = 4
        seq_len = 32
        input_ids = torch.randint(0, 1000, (batch_size, seq_len))
        attention_mask = torch.ones(batch_size, seq_len)
        context_embedding = torch.randn(batch_size, 32)
        
        # Forward pass
        with torch.no_grad():
            logits = model(input_ids, attention_mask, context_embedding)
        
        # Check output shape
        assert logits.shape == (batch_size, 12)
    
    def test_output_shape_validation(self):
        """Test that output shape is correct for different batch sizes."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        model.eval()
        
        for batch_size in [1, 2, 8, 16]:
            input_ids = torch.randint(0, 1000, (batch_size, 32))
            attention_mask = torch.ones(batch_size, 32)
            
            with torch.no_grad():
                logits = model(input_ids, attention_mask)
            
            assert logits.shape == (batch_size, 12), f"Failed for batch_size={batch_size}"
    
    def test_context_embedding_concatenation(self):
        """Test that context embedding is correctly concatenated."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        model.eval()
        
        batch_size = 2
        input_ids = torch.randint(0, 1000, (batch_size, 32))
        attention_mask = torch.ones(batch_size, 32)
        context_embedding = torch.randn(batch_size, 32)
        
        # Forward pass with context
        with torch.no_grad():
            logits_with_context = model(input_ids, attention_mask, context_embedding)
        
        # Forward pass without context
        with torch.no_grad():
            logits_without_context = model(input_ids, attention_mask, None)
        
        # Both should have same shape
        assert logits_with_context.shape == logits_without_context.shape
        
        # But different values (because context is different)
        assert not torch.allclose(logits_with_context, logits_without_context)
    
    def test_classification_head_dimensions(self):
        """Test that classification head has correct dimensions."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        
        # Check fc1 dimensions (768 + 32 → 256)
        assert model.fc1.in_features == 768 + 32
        assert model.fc1.out_features == 256
        
        # Check fc2 dimensions (256 → 12)
        assert model.fc2.in_features == 256
        assert model.fc2.out_features == 12
    
    def test_different_num_intents(self):
        """Test model with different number of intents."""
        for num_intents in [5, 10, 15, 20]:
            model = PhoBERTIntentClassifier(num_intents=num_intents, use_mock=True)
            
            input_ids = torch.randint(0, 1000, (2, 32))
            attention_mask = torch.ones(2, 32)
            
            with torch.no_grad():
                logits = model(input_ids, attention_mask)
            
            assert logits.shape == (2, num_intents)
    
    def test_dropout_in_training_mode(self):
        """Test that dropout is applied in training mode."""
        model = PhoBERTIntentClassifier(num_intents=12, dropout=0.5, use_mock=True)
        model.train()
        
        input_ids = torch.randint(0, 1000, (2, 32))
        attention_mask = torch.ones(2, 32)
        
        # Run forward pass twice
        logits1 = model(input_ids, attention_mask)
        logits2 = model(input_ids, attention_mask)
        
        # Results should be different due to dropout
        assert not torch.allclose(logits1, logits2)
    
    def test_no_dropout_in_eval_mode(self):
        """Test that dropout is not applied in eval mode."""
        model = PhoBERTIntentClassifier(num_intents=12, dropout=0.5, use_mock=True)
        model.eval()
        
        input_ids = torch.randint(0, 1000, (2, 32))
        attention_mask = torch.ones(2, 32)
        
        # Run forward pass twice
        with torch.no_grad():
            logits1 = model(input_ids, attention_mask)
            logits2 = model(input_ids, attention_mask)
        
        # Results should be identical in eval mode
        assert torch.allclose(logits1, logits2)
    
    def test_gradient_flow(self):
        """Test that gradients flow through the model."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        model.train()
        
        input_ids = torch.randint(0, 1000, (2, 32))
        attention_mask = torch.ones(2, 32)
        target = torch.randint(0, 12, (2,))
        
        # Forward pass
        logits = model(input_ids, attention_mask)
        
        # Compute loss
        criterion = nn.CrossEntropyLoss()
        loss = criterion(logits, target)
        
        # Backward pass
        loss.backward()
        
        # Check that gradients exist
        assert model.fc1.weight.grad is not None
        assert model.fc2.weight.grad is not None


class TestModelComponents:
    """Test individual model components."""
    
    def test_mock_phobert_model(self):
        """Test mock PhoBERT model."""
        model = MockPhoBERTModel(hidden_size=768)
        
        input_ids = torch.randint(0, 1000, (2, 32))
        outputs = model(input_ids)
        
        assert hasattr(outputs, 'pooler_output')
        assert outputs.pooler_output.shape == (2, 768)
    
    def test_classification_head_forward(self):
        """Test classification head forward pass."""
        model = PhoBERTIntentClassifier(num_intents=12, use_mock=True)
        
        # Create dummy pooled output
        batch_size = 4
        pooled_output = torch.randn(batch_size, 768 + 32)
        
        # Pass through classification head
        x = model.dropout(pooled_output)
        x = model.fc1(x)
        x = model.relu(x)
        x = model.dropout(x)
        logits = model.fc2(x)
        
        assert logits.shape == (batch_size, 12)
