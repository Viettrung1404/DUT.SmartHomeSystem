"""
ML-Based Classifier for Vietnamese NLP Intent Classification.

This classifier uses a fine-tuned PhoBERT model for natural language
intent classification with optional device context encoding.

**Validates: Requirements 1.1-1.5, 8.1-8.11, 9.1-9.11, 10.1-10.3**
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer
from typing import Optional, Dict, Any, List, Tuple
import logging
import json
import os
from pathlib import Path

from src.training.phobert_classifier import PhoBERTIntentClassifier

logger = logging.getLogger(__name__)

try:
    from src.classifiers.onnx_engine import ONNXInferenceEngine
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    logger.warning("ONNX Runtime not available. Install onnxruntime for optimized inference.")


class MLBasedClassifier:
    """
    ML-Based Classifier using PhoBERT for Vietnamese intent classification.
    
    This classifier:
    - Loads trained PhoBERT model from disk
    - Tokenizes Vietnamese text using PhoBERT tokenizer
    - Runs inference to get intent predictions
    - Supports device context encoding (MVP scope)
    - Returns top-k intents with confidence scores
    
    Confidence threshold: 0.7 (from requirements)
    """
    
    CONFIDENCE_THRESHOLD = 0.7
    VALID_INTENTS = [
        "control_device",
        "environmental_comfort",
        "query_sensor",
        "query_device_status",
        "security_mode",
        "security_alert",
        "activate_scene",
        "unknown",
    ]
    
    def __init__(
        self,
        model_path: Optional[str] = "models/phobert_intent_v1",
        device: Optional[str] = None,
        use_onnx: bool = False,
        use_mock: bool = False,
    ):
        """
        Initialize ML-Based Classifier.
        
        Args:
            model_path: Path to trained model directory
            device: Device to run model on ("cpu", "cuda", or None for auto)
            use_onnx: Whether to use ONNX Runtime for optimized inference (default False)
        """
        self.use_mock = use_mock
        self.use_onnx = use_onnx

        if self.use_mock:
            self.model_path = Path(model_path or ".")
            self.device = torch.device("cpu")
            self.intent_to_id = {intent: i for i, intent in enumerate(self.VALID_INTENTS)}
            self.id_to_intent = {i: intent for i, intent in enumerate(self.VALID_INTENTS)}
            self.model = None
            self.onnx_engine = None
            self.tokenizer = None
            logger.info("ML-Based Classifier initialized in mock mode")
            return

        if model_path is None:
            raise ValueError("model_path is required when use_mock=False")

        self.model_path = Path(model_path)
        
        # Set device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        logger.info(f"Initializing ML-Based Classifier on device: {self.device}")
        
        # Load intent mapping
        self.intent_mapping = self._load_intent_mapping()
        self.intent_to_id = self.intent_mapping["intent_to_id"]
        self.id_to_intent = {int(k): v for k, v in self.intent_mapping["id_to_intent"].items()}
        
        # Initialize inference engine
        if use_onnx:
            if not ONNX_AVAILABLE:
                raise ImportError(
                    "ONNX Runtime is not available. "
                    "Install onnxruntime or onnxruntime-gpu to use ONNX inference."
                )
            self.onnx_engine = self._load_onnx_engine()
            self.model = None  # Don't load PyTorch model if using ONNX
            logger.info("Using ONNX Runtime for inference")
        else:
            # Load PyTorch model
            self.model = self._load_model()
            self.model.to(self.device)
            self.model.eval()
            self.onnx_engine = None
            logger.info("Using PyTorch for inference")
        
        # Load tokenizer
        self.tokenizer = self._load_tokenizer()
        
        logger.info(f"ML-Based Classifier initialized successfully")
        logger.info(f"  - Model path: {self.model_path}")
        logger.info(f"  - Number of intents: {len(self.intent_to_id)}")
        logger.info(f"  - Device: {self.device}")
        logger.info(f"  - Inference engine: {'ONNX' if use_onnx else 'PyTorch'}")
    
    def _load_intent_mapping(self) -> Dict[str, Any]:
        """
        Load intent mapping from JSON file.
        
        Returns:
            Dictionary with intent_to_id and id_to_intent mappings
            
        Raises:
            FileNotFoundError: If intent_mapping.json not found
        """
        mapping_path = self.model_path / "intent_mapping.json"
        
        if not mapping_path.exists():
            raise FileNotFoundError(
                f"Intent mapping not found at {mapping_path}. "
                f"Please ensure the model is trained and intent_mapping.json exists."
            )
        
        with open(mapping_path, 'r', encoding='utf-8') as f:
            intent_mapping = json.load(f)
        
        logger.info(f"Loaded intent mapping with {len(intent_mapping['intent_to_id'])} intents")
        
        return intent_mapping
    
    def _load_model(self) -> PhoBERTIntentClassifier:
        """
        Load trained PhoBERT model from disk.
        
        Returns:
            Loaded PhoBERTIntentClassifier instance
            
        Raises:
            FileNotFoundError: If model files not found
        """
        model_file = self.model_path / "best_model.pt"
        config_file = self.model_path / "config.json"
        
        if not model_file.exists():
            raise FileNotFoundError(
                f"Model file not found at {model_file}. "
                f"Please train the model first using scripts/train_phobert.py"
            )
        
        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found at {config_file}. "
                f"Please ensure the model is trained and config.json exists."
            )
        
        # Load config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Create model instance
        model = PhoBERTIntentClassifier(
            num_intents=config["num_intents"],
            model_name=config["model_name"],
            hidden_size=config["hidden_size"],
            context_dim=config["context_dim"],
            intermediate_dim=config["intermediate_dim"]
        )
        
        # Load state dict
        state_dict = torch.load(model_file, map_location='cpu')
        model.load_state_dict(state_dict)
        
        logger.info(f"Loaded model from {model_file}")
        
        return model
    
    def _load_onnx_engine(self) -> 'ONNXInferenceEngine':
        """
        Load ONNX inference engine.
        
        Returns:
            ONNXInferenceEngine instance
            
        Raises:
            FileNotFoundError: If ONNX model file not found
        """
        onnx_model_file = self.model_path / "best_model.onnx"
        
        if not onnx_model_file.exists():
            raise FileNotFoundError(
                f"ONNX model file not found at {onnx_model_file}. "
                f"Please export the model first using scripts/export_to_onnx.py"
            )
        
        # Create ONNX engine with GPU support if available
        use_gpu = self.device.type == "cuda"
        engine = ONNXInferenceEngine(str(onnx_model_file), use_gpu=use_gpu)
        
        logger.info(f"Loaded ONNX engine from {onnx_model_file}")
        
        return engine
    
    def _load_tokenizer(self) -> AutoTokenizer:
        """
        Load PhoBERT tokenizer.
        
        Returns:
            AutoTokenizer instance for vinai/phobert-base
        """
        tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")
        logger.info("Loaded PhoBERT tokenizer")
        return tokenizer
    
    def tokenize(self, text: str, max_length: int = 128) -> Dict[str, torch.Tensor]:
        """
        Tokenize Vietnamese text using PhoBERT tokenizer.
        
        Args:
            text: Vietnamese text input
            max_length: Maximum sequence length (default 128)
            
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
            "input_ids": encoding["input_ids"].to(self.device),
            "attention_mask": encoding["attention_mask"].to(self.device)
        }
    
    def encode_context(self, context: Optional[Dict[str, Any]]) -> Optional[torch.Tensor]:
        """
        Encode device context into embedding vector (MVP scope).
        
        Context features:
        - Current room (one-hot encoded): 6 rooms
        - Device states (binary vector): 8 device types
        - Time of day (sin/cos encoding): 2 features
        
        Total features: 16, projected to context_dim=32
        
        Args:
            context: Dictionary with:
                - current_room: str (e.g., "living_room")
                - devices: List of device states
                - time_of_day: str (e.g., "morning", "afternoon")
                
        Returns:
            Context embedding tensor (1, context_dim) or None if no context
        """
        if context is None:
            return None
        
        # Define feature dimensions
        num_rooms = 6
        num_devices = 8
        time_features = 2
        total_features = num_rooms + num_devices + time_features
        
        # Initialize feature vector
        features = torch.zeros(total_features, device=self.device)
        
        # Encode current room (one-hot)
        room_mapping = {
            "living_room": 0, "bedroom": 1, "kitchen": 2,
            "bathroom": 3, "balcony": 4, "garage": 5
        }
        current_room = context.get("current_room")
        if current_room and current_room in room_mapping:
            features[room_mapping[current_room]] = 1.0
        
        # Encode device states (binary)
        device_mapping = {
            "light": 0, "fan": 1, "ac": 2, "door": 3,
            "awning": 4, "lock": 5, "curtain": 6, "camera": 7
        }
        devices = context.get("devices", [])
        for device in devices:
            device_type = device.get("type")
            device_state = device.get("state")
            if device_type in device_mapping and device_state == "on":
                features[num_rooms + device_mapping[device_type]] = 1.0
        
        # Encode time of day (sin/cos)
        time_mapping = {
            "morning": 0, "afternoon": 90, "evening": 180, "night": 270
        }
        time_of_day = context.get("time_of_day", "morning")
        angle = time_mapping.get(time_of_day, 0)
        angle_rad = angle * 3.14159 / 180
        features[num_rooms + num_devices] = torch.sin(torch.tensor(angle_rad, device=self.device))
        features[num_rooms + num_devices + 1] = torch.cos(torch.tensor(angle_rad, device=self.device))
        
        # Simple projection to context_dim (using linear transformation)
        # For MVP, we'll use a simple approach: repeat and truncate/pad to context_dim
        context_dim = 32
        if total_features < context_dim:
            # Pad with zeros
            padding = torch.zeros(context_dim - total_features, device=self.device)
            context_embedding = torch.cat([features, padding]).unsqueeze(0)
        else:
            # Truncate
            context_embedding = features[:context_dim].unsqueeze(0)
        
        return context_embedding
    
    def inference(self, 
                  input_ids: torch.Tensor,
                  attention_mask: torch.Tensor,
                  context_embedding: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Run model inference to get logits.
        
        Supports both PyTorch and ONNX Runtime inference based on initialization.
        
        Args:
            input_ids: Token IDs (batch_size, seq_len)
            attention_mask: Attention mask (batch_size, seq_len)
            context_embedding: Optional context embedding (batch_size, context_dim)
                              Note: ONNX model doesn't support context embedding yet
            
        Returns:
            Logits tensor (batch_size, num_intents)
        """
        if self.use_onnx:
            # ONNX inference
            if context_embedding is not None:
                logger.warning(
                    "Context embedding is not supported with ONNX inference yet. "
                    "Ignoring context_embedding parameter."
                )
            
            # Use ONNX engine
            logits = self.onnx_engine.predict_from_torch(input_ids, attention_mask)
        else:
            # PyTorch inference
            with torch.no_grad():
                logits = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    context_embedding=context_embedding
                )
        
        return logits
    
    def compute_confidence_scores(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Apply softmax to get confidence scores (probabilities).
        
        Args:
            logits: Raw logits from model (batch_size, num_intents)
            
        Returns:
            Confidence scores (batch_size, num_intents) with values in [0, 1]
        """
        confidence_scores = F.softmax(logits, dim=-1)
        return confidence_scores
    
    def get_top_k_intents(self, 
                          confidence_scores: torch.Tensor,
                          k: int = 3) -> List[Tuple[str, float]]:
        """
        Get top-k intents with confidence scores.
        
        Args:
            confidence_scores: Confidence scores (batch_size, num_intents)
            k: Number of top intents to retrieve (default 3)
            
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
    
    def classify(self, 
                 text: str,
                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify Vietnamese text and return intent with confidence.
        
        Main classification method that:
        1. Tokenizes text using PhoBERT tokenizer
        2. Encodes device context if provided (MVP scope)
        3. Runs model inference to get logits
        4. Applies softmax to get confidence scores
        5. Returns top intent with confidence and top-k suggestions
        
        Args:
            text: Vietnamese text input
            context: Optional device context for context-aware classification
            
        Returns:
            Dictionary with:
            - intent: Predicted intent name
            - confidence: Confidence score (0-1)
            - top_k_intents: List of (intent, confidence) tuples
            - classifier_type: "ml"
        """
        if self.use_mock:
            return self._mock_classify(text)

        # Tokenize text
        encoding = self.tokenize(text)
        
        # Encode context if provided
        context_embedding = self.encode_context(context)
        
        # Run inference
        logits = self.inference(
            input_ids=encoding["input_ids"],
            attention_mask=encoding["attention_mask"],
            context_embedding=context_embedding
        )
        
        # Compute confidence scores
        confidence_scores = self.compute_confidence_scores(logits)
        
        # Get top-k intents
        top_k_intents = self.get_top_k_intents(confidence_scores, k=3)
        
        # Get top intent
        top_intent, top_confidence = top_k_intents[0]
        
        # Check confidence threshold
        if top_confidence < self.CONFIDENCE_THRESHOLD:
            logger.warning(
                f"Low confidence ({top_confidence:.3f}) for intent '{top_intent}'. "
                f"Threshold: {self.CONFIDENCE_THRESHOLD}"
            )
        
        return {
            "intent": top_intent,
            "confidence": top_confidence,
            "top_k_intents": top_k_intents,
            "classifier_type": "ml"
        }

    def _mock_classify(self, text: str) -> Dict[str, Any]:
        text_lower = text.lower().strip()

        entertainment_keywords = ["phim", "game", "bài hát", "trận đấu", "video", "nhạc", "truyện"]
        has_entertainment_context = any(ent in text_lower for ent in entertainment_keywords)

        intent = "unknown"
        confidence = 0.3

        # Security mode
        if any(k in text_lower for k in ["tắt báo động", "vô hiệu hóa an ninh", "tắt chế độ an ninh", "tắt bảo vệ", "disarmed"]):
            intent = "security_mode"
            confidence = 0.85
        elif any(k in text_lower for k in ["bật báo động", "kích hoạt an ninh", "bật chế độ an ninh", "bật bảo vệ", "armed"]):
            intent = "security_mode"
            confidence = 0.85
        # Security alerts (skip entertainment context)
        elif not has_entertainment_context and any(k in text_lower for k in ["cháy", "fire", "có lửa", "hỏa hoạn", "cháy rồi", "cháy kìa", "cảnh báo cháy", "phát hiện cháy"]):
            intent = "security_alert"
            confidence = 0.85
        elif not has_entertainment_context and any(k in text_lower for k in ["gas", "khí gas", "có mùi gas", "rò rỉ gas", "gas leak", "cảnh báo gas", "phát hiện gas", "phát hiện khí gas", "khí gas rò rỉ"]):
            intent = "security_alert"
            confidence = 0.85
        elif not has_entertainment_context and any(k in text_lower for k in ["trộm", "đột nhập", "có người lạ", "kẻ xâm nhập", "cảnh báo trộm", "intruder"]):
            intent = "security_alert"
            confidence = 0.85
        # Scene activation
        elif any(k in text_lower for k in ["đi ngủ", "chúc ngủ ngon", "chuẩn bị ngủ", "sleep"]):
            intent = "activate_scene"
            confidence = 0.85
        elif any(k in text_lower for k in ["thức dậy", "buổi sáng", "chào buổi sáng", "wake up"]):
            intent = "activate_scene"
            confidence = 0.85
        elif any(k in text_lower for k in ["xem phim", "xem tv", "rạp chiếu phim", "movie"]):
            intent = "activate_scene"
            confidence = 0.85
        # Environmental comfort
        elif any(k in text_lower for k in ["nóng", "oi", "mát"]):
            intent = "environmental_comfort"
            confidence = 0.85
        elif any(k in text_lower for k in ["lạnh", "rét", "ấm"]):
            intent = "environmental_comfort"
            confidence = 0.85
        elif any(k in text_lower for k in ["tối", "thiếu sáng"]):
            intent = "environmental_comfort"
            confidence = 0.85
        elif any(k in text_lower for k in ["sáng", "chói"]):
            intent = "environmental_comfort"
            confidence = 0.85
        elif any(k in text_lower for k in ["ngột", "ngạt", "thông gió", "bí bách"]):
            intent = "environmental_comfort"
            confidence = 0.85

        top_k_intents = [
            (intent, confidence),
            ("control_device", 0.1),
            ("query_sensor", 0.1),
        ]

        return {
            "intent": intent,
            "confidence": confidence,
            "top_k_intents": top_k_intents,
            "classifier_type": "ml",
        }
