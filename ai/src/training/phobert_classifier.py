"""
PhoBERT Intent Classifier for Vietnamese NLP.

This module implements the PhoBERT-based intent classification model
with context-aware features and classification head.

**Validates: Requirements 9.4**
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PhoBERTIntentClassifier(nn.Module):
    """
    PhoBERT-based Intent Classifier with context awareness.
    
    Architecture:
    - PhoBERT encoder (vinai/phobert-base): 768-dim output
    - Optional context embedding: 32-dim
    - Classification head: (768+32) → 256 → num_intents
      - Dropout for regularization
      - ReLU activation
    
    The model can optionally incorporate device context (current room,
    device states, time of day) to improve classification accuracy.
    """
    
    def __init__(self, 
                 num_intents: int = 12,
                 model_name: str = "vinai/phobert-base",
                 hidden_size: int = 768,
                 context_dim: int = 32,
                 intermediate_dim: int = 256,
                 dropout: float = 0.1,
                 freeze_encoder: bool = False):
        """
        Initialize PhoBERT Intent Classifier.
        
        Args:
            num_intents: Number of intent classes (default 12)
            model_name: HuggingFace model name (default "vinai/phobert-base")
            hidden_size: PhoBERT hidden size (default 768)
            context_dim: Context embedding dimension (default 32)
            intermediate_dim: Intermediate layer dimension (default 256)
            dropout: Dropout rate (default 0.1)
            freeze_encoder: Whether to freeze PhoBERT encoder (default False)
        """
        super().__init__()
        
        self.num_intents = num_intents
        self.model_name = model_name
        self.hidden_size = hidden_size
        self.context_dim = context_dim
        self.intermediate_dim = intermediate_dim
        
        # Load PhoBERT encoder
        logger.info(f"Loading PhoBERT model: {model_name}")
        self.encoder = AutoModel.from_pretrained(model_name)
        
        # Freeze encoder if specified
        if freeze_encoder:
            logger.info("Freezing PhoBERT encoder parameters")
            for param in self.encoder.parameters():
                param.requires_grad = False
        
        # Classification head
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_size + context_dim, intermediate_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(intermediate_dim, num_intents)
        
        # Initialize weights
        self._init_weights()
        
        logger.info(f"PhoBERT Intent Classifier initialized:")
        logger.info(f"  - Num intents: {num_intents}")
        logger.info(f"  - Hidden size: {hidden_size}")
        logger.info(f"  - Context dim: {context_dim}")
        logger.info(f"  - Intermediate dim: {intermediate_dim}")
        logger.info(f"  - Dropout: {dropout}")
        logger.info(f"  - Freeze encoder: {freeze_encoder}")
    
    def _init_weights(self):
        """Initialize classification head weights."""
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.zeros_(self.fc1.bias)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.zeros_(self.fc2.bias)
    
    def forward(self, 
                input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None,
                context_embedding: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Forward pass through the model.
        
        Args:
            input_ids: Token IDs from tokenizer (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)
            context_embedding: Optional context embedding (batch_size, context_dim)
            
        Returns:
            Logits for each intent class (batch_size, num_intents)
        """
        # Encode with PhoBERT
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        
        # Get pooled output (CLS token representation)
        pooled_output = outputs.pooler_output  # (batch_size, hidden_size)
        
        # Concatenate context embedding if provided
        if context_embedding is not None:
            # Ensure context has correct shape
            if context_embedding.size(1) != self.context_dim:
                raise ValueError(
                    f"Context embedding dimension mismatch: "
                    f"expected {self.context_dim}, got {context_embedding.size(1)}"
                )
            pooled_output = torch.cat([pooled_output, context_embedding], dim=1)
        else:
            # Pad with zeros if no context provided
            batch_size = pooled_output.size(0)
            zero_context = torch.zeros(
                batch_size, self.context_dim,
                device=pooled_output.device,
                dtype=pooled_output.dtype
            )
            pooled_output = torch.cat([pooled_output, zero_context], dim=1)
        
        # Pass through classification head
        x = self.dropout(pooled_output)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.dropout(x)
        logits = self.fc2(x)
        
        return logits
    
    def predict(self,
                input_ids: torch.Tensor,
                attention_mask: Optional[torch.Tensor] = None,
                context_embedding: Optional[torch.Tensor] = None) -> Dict[str, Any]:
        """
        Predict intent with confidence scores.
        
        Args:
            input_ids: Token IDs from tokenizer
            attention_mask: Attention mask
            context_embedding: Optional context embedding
            
        Returns:
            Dictionary with:
            - predicted_intent: Index of predicted intent
            - confidence: Confidence score (0-1)
            - probabilities: Probability distribution over all intents
        """
        self.eval()
        
        with torch.no_grad():
            logits = self.forward(input_ids, attention_mask, context_embedding)
            probabilities = torch.softmax(logits, dim=-1)
            confidence, predicted_intent = torch.max(probabilities, dim=-1)
        
        return {
            "predicted_intent": predicted_intent.item() if predicted_intent.dim() == 0 else predicted_intent.tolist(),
            "confidence": confidence.item() if confidence.dim() == 0 else confidence.tolist(),
            "probabilities": probabilities.squeeze().tolist() if probabilities.size(0) == 1 else probabilities.tolist()
        }
    
    def get_top_k_intents(self,
                         input_ids: torch.Tensor,
                         attention_mask: Optional[torch.Tensor] = None,
                         context_embedding: Optional[torch.Tensor] = None,
                         k: int = 3) -> Dict[str, Any]:
        """
        Get top-k predicted intents with confidence scores.
        
        Args:
            input_ids: Token IDs from tokenizer
            attention_mask: Attention mask
            context_embedding: Optional context embedding
            k: Number of top intents to return
            
        Returns:
            Dictionary with:
            - top_intents: List of top-k intent indices
            - top_confidences: List of top-k confidence scores
        """
        self.eval()
        
        with torch.no_grad():
            logits = self.forward(input_ids, attention_mask, context_embedding)
            probabilities = torch.softmax(logits, dim=-1)
            top_confidences, top_intents = torch.topk(probabilities, k, dim=-1)
        
        return {
            "top_intents": top_intents.squeeze().tolist() if top_intents.size(0) == 1 else top_intents.tolist(),
            "top_confidences": top_confidences.squeeze().tolist() if top_confidences.size(0) == 1 else top_confidences.tolist()
        }
    
    def save_pretrained(self, save_directory: str):
        """
        Save model to directory.
        
        Args:
            save_directory: Directory to save model
        """
        import os
        os.makedirs(save_directory, exist_ok=True)
        
        # Save model state dict
        model_path = os.path.join(save_directory, "pytorch_model.bin")
        torch.save(self.state_dict(), model_path)
        
        # Save config
        config = {
            "num_intents": self.num_intents,
            "model_name": self.model_name,
            "hidden_size": self.hidden_size,
            "context_dim": self.context_dim,
            "intermediate_dim": self.intermediate_dim
        }
        
        import json
        config_path = os.path.join(save_directory, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"Model saved to {save_directory}")
    
    @classmethod
    def from_pretrained(cls, load_directory: str):
        """
        Load model from directory.
        
        Args:
            load_directory: Directory containing saved model
            
        Returns:
            Loaded PhoBERTIntentClassifier instance
        """
        import os
        import json
        
        # Load config
        config_path = os.path.join(load_directory, "config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create model
        model = cls(**config)
        
        # Load state dict
        model_path = os.path.join(load_directory, "pytorch_model.bin")
        state_dict = torch.load(model_path, map_location='cpu')
        model.load_state_dict(state_dict)
        
        logger.info(f"Model loaded from {load_directory}")
        
        return model


class ContextEncoder:
    """
    Encoder for device context into fixed-size embedding.
    
    Context features:
    - Current room (one-hot encoded)
    - Device states (binary vector for each device type)
    - Time of day (sin/cos encoding)
    """
    
    def __init__(self, context_dim: int = 32):
        """
        Initialize context encoder.
        
        Args:
            context_dim: Output embedding dimension
        """
        self.context_dim = context_dim
        
        # Define feature dimensions
        self.num_rooms = 6  # living_room, bedroom, kitchen, bathroom, balcony, garage
        self.num_devices = 8  # light, fan, ac, door, awning, lock, curtain, camera
        self.time_features = 2  # sin, cos
        
        # Total features
        self.total_features = self.num_rooms + self.num_devices + self.time_features
        
        # Linear projection to context_dim
        self.projection = nn.Linear(self.total_features, context_dim)
    
    def encode(self, device_context: Dict[str, Any]) -> torch.Tensor:
        """
        Encode device context into embedding vector.
        
        Args:
            device_context: Dictionary with:
                - current_room: str (e.g., "living_room")
                - devices: List of device states
                - time_of_day: str (e.g., "morning", "afternoon")
                
        Returns:
            Context embedding (1, context_dim)
        """
        # Initialize feature vector
        features = torch.zeros(self.total_features)
        
        # Encode current room (one-hot)
        room_mapping = {
            "living_room": 0, "bedroom": 1, "kitchen": 2,
            "bathroom": 3, "balcony": 4, "garage": 5
        }
        current_room = device_context.get("current_room")
        if current_room and current_room in room_mapping:
            features[room_mapping[current_room]] = 1.0
        
        # Encode device states (binary)
        device_mapping = {
            "light": 0, "fan": 1, "ac": 2, "door": 3,
            "awning": 4, "lock": 5, "curtain": 6, "camera": 7
        }
        devices = device_context.get("devices", [])
        for device in devices:
            device_type = device.get("type")
            device_state = device.get("state")
            if device_type in device_mapping and device_state == "on":
                features[self.num_rooms + device_mapping[device_type]] = 1.0
        
        # Encode time of day (sin/cos)
        time_mapping = {
            "morning": 0, "afternoon": 90, "evening": 180, "night": 270
        }
        time_of_day = device_context.get("time_of_day", "morning")
        angle = time_mapping.get(time_of_day, 0)
        angle_rad = angle * 3.14159 / 180
        features[self.num_rooms + self.num_devices] = torch.sin(torch.tensor(angle_rad))
        features[self.num_rooms + self.num_devices + 1] = torch.cos(torch.tensor(angle_rad))
        
        # Project to context_dim
        with torch.no_grad():
            context_embedding = self.projection(features.unsqueeze(0))
        
        return context_embedding
