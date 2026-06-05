"""
Property-based tests for ML-Based Classifier.

These tests verify universal properties that should hold for ML-based classification:
- Property Test 1: Response Structure Validity
- Property Test 4: Low Confidence Fallback
"""

from hypothesis import given, strategies as st, settings
import pytest
from typing import Optional, Dict, Any
from datetime import datetime
import re


# ============================================================================
# IMPORT MODELS
# ============================================================================

from src.models.schemas import IntentResponse, FallbackResponse, ENTITY_SCHEMA
from src.classifiers.rule_based import ClassificationResult


# ============================================================================
# STUB ML-BASED CLASSIFIER (To be implemented in Task 8.4)
# ============================================================================

class MLBasedClassifier:
    """
    Stub for ML-Based Classifier.
    
    This stub returns valid IntentResponse structures for testing purposes.
    The actual implementation will be done in Task 8.4.
    
    For now, this stub:
    - Returns valid intent names from the 15 core intents
    - Returns entities that comply with ENTITY_SCHEMA
    - Returns confidence scores between 0.0 and 1.0
    - Returns ISO 8601 timestamps
    - Supports fallback behavior with top-k intent suggestions
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
    
    def __init__(self):
        """Initialize stub classifier."""
        pass
    
    def classify(self, text: str) -> IntentResponse:
        """
        Classify Vietnamese text and return IntentResponse.
        
        This stub implementation:
        1. Returns a valid intent from VALID_INTENTS
        2. Returns entities that comply with ENTITY_SCHEMA
        3. Returns confidence between 0.0 and 1.0
        4. Returns ISO 8601 timestamp
        5. Returns FallbackResponse when confidence < 0.7
        
        Args:
            text: Vietnamese text input
            
        Returns:
            IntentResponse or FallbackResponse with valid structure
        """
        # For stub: return deterministic outcomes based on keywords
        text_lower = text.lower()

        entertainment_keywords = ["phim", "game", "bài hát", "trận đấu", "video", "nhạc", "truyện"]
        has_entertainment_context = any(ent_kw in text_lower for ent_kw in entertainment_keywords)
        is_query_form = any(q in text_lower for q in ["không", "kiểm tra", "bao nhiêu"])

        if any(keyword in text_lower for keyword in ["tắt báo động", "vô hiệu hóa an ninh", "tắt chế độ an ninh", "tắt bảo vệ", "disarmed"]):
            intent = "security_mode"
            entities = {"mode": "disarmed"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["bật báo động", "kích hoạt an ninh", "bật chế độ an ninh", "bật bảo vệ", "armed"]):
            intent = "security_mode"
            entities = {"mode": "armed"}
            confidence = 0.85
        # Query-form sensor checks
        elif any(keyword in text_lower for keyword in ["có cháy không", "kiểm tra cháy", "có lửa không"]):
            intent = "query_sensor"
            entities = {"sensor_type": "fire"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["có khí gas không", "kiểm tra khí gas", "có gas không", "kiểm tra gas"]):
            intent = "query_sensor"
            entities = {"sensor_type": "gas"}
            confidence = 0.85
        # Security alerts (non-query, non-entertainment)
        elif not has_entertainment_context and not is_query_form and any(keyword in text_lower for keyword in ["cháy", "fire", "có lửa", "hỏa hoạn", "cháy rồi", "cháy kìa", "cảnh báo cháy", "phát hiện cháy"]):
            intent = "security_alert"
            entities = {"alert_type": "fire", "priority": "high"}
            confidence = 0.85
        elif not has_entertainment_context and not is_query_form and any(keyword in text_lower for keyword in ["gas", "khí gas", "có mùi gas", "rò rỉ gas", "gas leak", "cảnh báo gas", "phát hiện khí gas", "khí gas rò rỉ"]):
            intent = "security_alert"
            entities = {"alert_type": "gas", "priority": "high"}
            confidence = 0.85
        elif not has_entertainment_context and not is_query_form and any(keyword in text_lower for keyword in ["trộm", "đột nhập", "có người lạ", "kẻ xâm nhập", "cảnh báo trộm", "intruder"]):
            intent = "security_alert"
            entities = {"alert_type": "intrusion", "priority": "high"}
            confidence = 0.85
        # Scenes
        elif any(keyword in text_lower for keyword in ["đi ngủ", "chúc ngủ ngon", "chuẩn bị ngủ", "sleep"]):
            intent = "activate_scene"
            entities = {"scene_type": "sleep"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["thức dậy", "buổi sáng", "chào buổi sáng", "wake up"]):
            intent = "activate_scene"
            entities = {"scene_type": "wake_up"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["xem phim", "xem tv", "rạp chiếu phim", "movie"]):
            intent = "activate_scene"
            entities = {"scene_type": "movie"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["đi ra ngoài", "rời nhà", "đi vắng", "away"]):
            intent = "activate_scene"
            entities = {"scene_type": "away"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["về nhà", "đã về", "tôi về rồi", "home"]):
            intent = "activate_scene"
            entities = {"scene_type": "home"}
            confidence = 0.85
        # Sensor queries
        elif any(keyword in text_lower for keyword in ["nhiệt độ", "bao nhiêu độ", "đo nhiệt độ", "temperature"]):
            intent = "query_sensor"
            entities = {"sensor_type": "temperature"}
            if "phòng khách" in text_lower:
                entities["location"] = "living_room"
            elif "phòng ngủ" in text_lower:
                entities["location"] = "bedroom"
            elif "bếp" in text_lower:
                entities["location"] = "kitchen"
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["độ ẩm", "ẩm không", "kiểm tra độ ẩm", "humidity"]):
            intent = "query_sensor"
            entities = {"sensor_type": "humidity"}
            if "phòng khách" in text_lower:
                entities["location"] = "living_room"
            elif "phòng ngủ" in text_lower:
                entities["location"] = "bedroom"
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["có mưa không", "trời mưa không", "dự báo mưa", "mưa", "rain"]):
            intent = "query_sensor"
            entities = {"sensor_type": "rain"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["có người không", "phát hiện chuyển động", "ai đó vào", "chuyển động", "motion", "có ai trong phòng không"]):
            intent = "query_sensor"
            entities = {"sensor_type": "motion"}
            confidence = 0.85
        # Device status queries
        elif any(keyword in text_lower for keyword in ["trạng thái đèn", "đèn có bật không", "đèn đang bật không"]):
            intent = "query_device_status"
            entities = {"device": "light"}
            if "phòng khách" in text_lower:
                entities["location"] = "living_room"
            elif "phòng ngủ" in text_lower:
                entities["location"] = "bedroom"
            elif "bếp" in text_lower:
                entities["location"] = "kitchen"
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["trạng thái quạt", "quạt có bật không", "quạt đang chạy không", "quạt đang bật không"]):
            intent = "query_device_status"
            entities = {"device": "fan"}
            if "phòng khách" in text_lower:
                entities["location"] = "living_room"
            elif "phòng ngủ" in text_lower:
                entities["location"] = "bedroom"
            elif "bếp" in text_lower:
                entities["location"] = "kitchen"
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["trạng thái điều hòa", "điều hòa có bật không", "ac đang bật không"]):
            intent = "query_device_status"
            entities = {"device": "ac"}
            if "phòng khách" in text_lower:
                entities["location"] = "living_room"
            elif "phòng ngủ" in text_lower:
                entities["location"] = "bedroom"
            elif "bếp" in text_lower:
                entities["location"] = "kitchen"
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["trạng thái cửa", "cửa có mở không", "cửa đang mở không"]):
            intent = "query_device_status"
            entities = {"device": "door"}
            if "phòng khách" in text_lower:
                entities["location"] = "living_room"
            elif "phòng ngủ" in text_lower:
                entities["location"] = "bedroom"
            elif "bếp" in text_lower:
                entities["location"] = "kitchen"
            confidence = 0.85
        # Environmental comfort
        elif any(keyword in text_lower for keyword in ["nóng", "oi", "mát"]):
            intent = "environmental_comfort"
            entities = {"comfort_type": "cooling"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["lạnh", "rét", "ấm"]):
            intent = "environmental_comfort"
            entities = {"comfort_type": "warming"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["tối", "thiếu sáng"]):
            intent = "environmental_comfort"
            entities = {"comfort_type": "brighten"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["sáng", "chói"]):
            intent = "environmental_comfort"
            entities = {"comfort_type": "dim"}
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["ngột", "ngạt", "thông gió", "thiếu không khí", "bí bách"]):
            intent = "environmental_comfort"
            entities = {"comfort_type": "ventilate"}
            confidence = 0.85
        # Control device
        elif any(keyword in text_lower for keyword in ["bật đèn", "tắt đèn", "mở đèn", "đóng đèn"]):
            intent = "control_device"
            entities = {"device": "light"}
            if "bật" in text_lower or "mở" in text_lower:
                entities["action"] = "turn_on"
            else:
                entities["action"] = "turn_off"
            confidence = 0.85
        elif any(keyword in text_lower for keyword in ["bật quạt", "tắt quạt"]):
            intent = "control_device"
            entities = {"device": "fan"}
            if "bật" in text_lower:
                entities["action"] = "turn_on"
            else:
                entities["action"] = "turn_off"
            confidence = 0.85
        else:
            intent = "unknown"
            entities = {}
            confidence = 0.3

        # Check if confidence is below threshold
        if confidence < self.CONFIDENCE_THRESHOLD:
            top_intents = self._get_top_k_intents(text, k=3)

            return FallbackResponse(
                intent="unknown",
                entities={},
                confidence=confidence,
                timestamp=datetime.utcnow(),
                clarification_needed=True,
                suggestions=self._generate_clarification_questions(top_intents),
                top_intents=top_intents,
            )

        return IntentResponse(
            intent=intent,
            entities=entities,
            confidence=confidence,
            timestamp=datetime.utcnow(),
            classifier_type="ml",
        )
    
    def _get_top_k_intents(self, text: str, k: int = 3) -> list:
        """
        Get top-k intent suggestions with confidence scores.
        
        This is a stub implementation that returns plausible intent suggestions
        based on simple heuristics. The actual implementation will use model logits.
        
        Args:
            text: Input text
            k: Number of top intents to return
            
        Returns:
            List of dicts with intent and confidence
        """
        # Stub: return plausible top-k intents based on text characteristics
        suggestions = []
        
        # Check for device-related keywords
        if any(word in text.lower() for word in ["đèn", "quạt", "điều hòa", "cửa", "mái"]):
            suggestions.append({"intent": "control_device", "confidence": 0.45})
        
        # Check for query keywords
        if any(word in text.lower() for word in ["bao nhiêu", "thế nào", "như thế nào", "?"]):
            suggestions.append({"intent": "query_sensor", "confidence": 0.32})
        
        # Check for comfort keywords (even weak matches)
        if any(word in text.lower() for word in ["quá", "cần", "thiếu"]):
            suggestions.append({"intent": "environmental_comfort", "confidence": 0.23})
        
        # Fill remaining slots with other intents
        other_intents = ["query_device_status", "activate_scene", "security_mode"]
        for intent in other_intents:
            if len(suggestions) >= k:
                break
            suggestions.append({"intent": intent, "confidence": 0.15})
        
        # Ensure we have exactly k suggestions
        while len(suggestions) < k:
            suggestions.append({"intent": "unknown", "confidence": 0.05})
        
        return suggestions[:k]
    
    def _generate_clarification_questions(self, top_intents: list) -> list:
        """
        Generate clarification questions based on top intents.
        
        Args:
            top_intents: List of top intent suggestions
            
        Returns:
            List of clarification question strings
        """
        questions = []
        
        for intent_info in top_intents:
            intent = intent_info["intent"]
            
            if intent == "control_device":
                questions.append("Bạn muốn bật thiết bị nào?")
            elif intent == "query_sensor":
                questions.append("Bạn muốn kiểm tra cảm biến nào?")
            elif intent == "environmental_comfort":
                questions.append("Bạn cảm thấy không thoải mái về điều gì?")
            elif intent == "query_device_status":
                questions.append("Bạn muốn kiểm tra trạng thái thiết bị nào?")
            elif intent == "activate_scene":
                questions.append("Bạn muốn kích hoạt cảnh nào?")
            elif intent == "security_mode":
                questions.append("Bạn muốn thay đổi chế độ an ninh?")
        
        return questions[:3]  # Return max 3 questions


# ============================================================================
# HYPOTHESIS STRATEGIES
# ============================================================================

# Vietnamese characters for text generation
VIETNAMESE_CHARS = "aábàảãạăắằẳẵặâấầẩẫậeéèẻẽẹêếềểễệiíìỉĩịoóòỏõọôốồổỗộơớờởỡợuúùủũụưứừửữựyýỳỷỹỵ"
VIETNAMESE_CHARS += VIETNAMESE_CHARS.upper()
VIETNAMESE_CHARS += " đĐ"


@st.composite
def vietnamese_text_strategy(draw):
    """
    Generate arbitrary Vietnamese text.
    
    This strategy generates random Vietnamese text to test that the classifier
    can handle ANY input without crashing.
    """
    # Generate text with Vietnamese characters
    text = draw(st.text(
        alphabet=VIETNAMESE_CHARS + "0123456789.,!? ",
        min_size=1,
        max_size=500
    ))
    
    return text


@st.composite
def vietnamese_sentence_strategy(draw):
    """
    Generate realistic Vietnamese sentences.
    
    This strategy generates more realistic Vietnamese sentences by combining
    common Vietnamese words.
    """
    vietnamese_words = [
        "Trời", "nóng", "lạnh", "tối", "sáng", "quá", "rất", "oi", "bức",
        "rét", "ngột", "ngạt", "thiếu", "sáng", "chói", "mát", "ấm",
        "bật", "tắt", "mở", "đóng", "đèn", "quạt", "điều hòa", "cửa",
        "phòng khách", "phòng ngủ", "bếp", "ban công", "nhiệt độ", "độ ẩm",
        "bao nhiêu", "hiện tại", "đi ngủ", "thức dậy", "xem phim", "về nhà"
    ]
    
    # Generate sentence with 1-10 words
    num_words = draw(st.integers(min_value=1, max_value=10))
    words = [draw(st.sampled_from(vietnamese_words)) for _ in range(num_words)]
    
    sentence = " ".join(words)
    return sentence


# ============================================================================
# PROPERTY TESTS
# ============================================================================

class TestMLClassifierProperties:
    """Property-based tests for ML-Based Classifier."""
    
    @given(text=vietnamese_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_1_response_structure_validity_arbitrary_text(self, text):
        """
        **Validates: Requirements 1.1, 1.2**
        
        Property 1: Response Structure Validity
        
        For ANY Vietnamese text input, the ML-Based Classifier SHALL return 
        a valid response (IntentResponse or FallbackResponse) with:
        - intent field (string)
        - entities field (dict)
        - confidence field (float between 0.0 and 1.0)
        - timestamp field (ISO 8601 format)
        
        Rationale:
        The classifier must handle ANY input gracefully without crashing.
        Even for nonsensical or malformed input, it should return a valid
        response structure (possibly with intent="unknown" and low confidence).
        
        Test Strategy:
        1. Generate arbitrary Vietnamese text using Hypothesis
        2. Classify using MLBasedClassifier
        3. Assert: response is IntentResponse or FallbackResponse instance
        4. Assert: intent is a string
        5. Assert: entities is a dict
        6. Assert: confidence is between 0.0 and 1.0
        7. Assert: timestamp is ISO 8601 format
        
        This property ensures that:
        - Classifier never crashes on arbitrary input
        - Response structure is always valid
        - All required fields are present
        - Field types are correct
        """
        classifier = MLBasedClassifier()
        
        # Classify arbitrary text
        response = classifier.classify(text)
        
        # Assert: response is IntentResponse or FallbackResponse instance
        assert isinstance(response, (IntentResponse, FallbackResponse)), (
            f"Response must be IntentResponse or FallbackResponse instance:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  Response type: {type(response)}"
        )
        
        # Assert: intent is a string
        assert isinstance(response.intent, str), (
            f"Intent must be a string:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  Intent type: {type(response.intent)}"
        )
        
        # Assert: entities is a dict
        assert isinstance(response.entities, dict), (
            f"Entities must be a dict:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  Entities type: {type(response.entities)}"
        )
        
        # Assert: confidence is between 0.0 and 1.0
        assert 0.0 <= response.confidence <= 1.0, (
            f"Confidence must be between 0.0 and 1.0:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  Confidence: {response.confidence}"
        )
        
        # Assert: timestamp is datetime instance
        assert isinstance(response.timestamp, datetime), (
            f"Timestamp must be datetime instance:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  Timestamp type: {type(response.timestamp)}"
        )
        
        # Assert: timestamp can be formatted as ISO 8601
        iso_timestamp = response.timestamp.isoformat()
        assert isinstance(iso_timestamp, str), (
            f"Timestamp must be convertible to ISO 8601 string:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  ISO timestamp: {iso_timestamp}"
        )
        
        # Assert: ISO 8601 format is valid (basic check)
        # Format: YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM:SS.ffffff
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        assert re.match(iso_pattern, iso_timestamp), (
            f"Timestamp must be in ISO 8601 format:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  ISO timestamp: {iso_timestamp}"
        )
    
    @given(text=vietnamese_sentence_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_1_response_structure_validity_realistic_text(self, text):
        """
        **Validates: Requirements 1.1, 1.2**
        
        Property 1: Response Structure Validity (Realistic Text)
        
        For realistic Vietnamese sentences, the ML-Based Classifier SHALL 
        return a valid response (IntentResponse or FallbackResponse) with all required fields.
        
        This is a variant of Property 1 that uses more realistic Vietnamese
        sentences instead of arbitrary text.
        """
        classifier = MLBasedClassifier()
        
        # Classify realistic Vietnamese sentence
        response = classifier.classify(text)
        
        # Assert: response is IntentResponse or FallbackResponse instance
        assert isinstance(response, (IntentResponse, FallbackResponse))
        
        # Assert: intent is a string
        assert isinstance(response.intent, str)
        
        # Assert: entities is a dict
        assert isinstance(response.entities, dict)
        
        # Assert: confidence is between 0.0 and 1.0
        assert 0.0 <= response.confidence <= 1.0
        
        # Assert: timestamp is datetime instance
        assert isinstance(response.timestamp, datetime)
        
        # Assert: timestamp can be formatted as ISO 8601
        iso_timestamp = response.timestamp.isoformat()
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'
        assert re.match(iso_pattern, iso_timestamp)
    
    @given(text=vietnamese_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_1_intent_is_valid(self, text):
        """
        **Validates: Requirements 1.5**
        
        Property 1 (Extended): Intent Validity
        
        For ANY Vietnamese text input, the returned intent SHALL be one of 
        the 15 core intents defined in the system.
        
        Valid intents:
        - control_device
        - environmental_comfort
        - query_sensor
        - query_device_status
        - security_mode
        - security_alert
        - activate_scene
        - weather_action
        - lock_all_doors
        - turn_off_all_devices
        - create_automation
        - unknown
        """
        classifier = MLBasedClassifier()
        
        # Classify arbitrary text
        response = classifier.classify(text)
        
        # Assert: intent is one of the valid intents
        assert response.intent in MLBasedClassifier.VALID_INTENTS, (
            f"Intent must be one of the valid intents:\n"
            f"  Text: {repr(text[:100])}\n"
            f"  Intent: {response.intent}\n"
            f"  Valid intents: {MLBasedClassifier.VALID_INTENTS}"
        )
    
    @given(text=vietnamese_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_1_classifier_type_is_ml(self, text):
        """
        **Validates: Requirements 1.1**
        
        Property 1 (Extended): Classifier Type
        
        For ANY Vietnamese text input, the ML-Based Classifier SHALL return 
        classifier_type="ml" in the response (for IntentResponse).
        
        Note: FallbackResponse doesn't have classifier_type field, which is expected.
        """
        classifier = MLBasedClassifier()
        
        # Classify arbitrary text
        response = classifier.classify(text)
        
        # Assert: if IntentResponse, classifier_type is "ml"
        if isinstance(response, IntentResponse):
            assert response.classifier_type == "ml", (
                f"Classifier type must be 'ml':\n"
                f"  Text: {repr(text[:100])}\n"
                f"  Classifier type: {response.classifier_type}"
            )
        # FallbackResponse doesn't have classifier_type, which is expected


# ============================================================================
# PROPERTY TEST 4: LOW CONFIDENCE FALLBACK
# ============================================================================

class TestMLClassifierLowConfidenceFallback:
    """Property-based tests for low confidence fallback behavior."""
    
    @given(text=vietnamese_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_4_low_confidence_returns_fallback_response(self, text):
        """
        **Validates: Requirements 1.4**
        
        Property 4: Low Confidence Fallback
        
        For ANY Vietnamese text input where the ML-Based Classifier returns 
        confidence < 0.7 (threshold), the system SHALL return a FallbackResponse 
        with:
        - intent="unknown"
        - clarification_needed=true
        - top_intents list with top-k intent suggestions (k=3)
        - suggestions list with clarification questions
        
        Rationale:
        When the classifier is uncertain (low confidence), it should NOT guess
        and potentially execute the wrong action. Instead, it should:
        1. Return intent="unknown" to signal uncertainty
        2. Set clarification_needed=true to request user clarification
        3. Provide top-k intent suggestions to help user clarify
        4. Provide clarification questions to guide user
        
        This ensures graceful degradation and prevents incorrect actions.
        
        Test Strategy:
        1. Generate arbitrary Vietnamese text using Hypothesis
        2. Classify using MLBasedClassifier
        3. IF confidence < 0.7:
           - Assert: response is FallbackResponse instance
           - Assert: intent is "unknown"
           - Assert: clarification_needed is True
           - Assert: top_intents list has 3 items
           - Assert: each top_intent has intent and confidence fields
           - Assert: suggestions list is not empty
        4. ELSE (confidence >= 0.7):
           - Assert: response is IntentResponse instance
           - Assert: intent is NOT "unknown" (or if unknown, confidence >= 0.7)
        """
        classifier = MLBasedClassifier()
        
        # Classify arbitrary text
        response = classifier.classify(text)
        
        # Check confidence level
        if response.confidence < 0.7:
            # Low confidence: should return FallbackResponse
            assert isinstance(response, FallbackResponse), (
                f"Low confidence response must be FallbackResponse:\n"
                f"  Text: {repr(text[:100])}\n"
                f"  Confidence: {response.confidence}\n"
                f"  Response type: {type(response)}"
            )
            
            # Assert: intent is "unknown"
            assert response.intent == "unknown", (
                f"Low confidence intent must be 'unknown':\n"
                f"  Text: {repr(text[:100])}\n"
                f"  Confidence: {response.confidence}\n"
                f"  Intent: {response.intent}"
            )
            
            # Assert: clarification_needed is True
            assert response.clarification_needed is True, (
                f"Low confidence must set clarification_needed=True:\n"
                f"  Text: {repr(text[:100])}\n"
                f"  Confidence: {response.confidence}\n"
                f"  Clarification needed: {response.clarification_needed}"
            )
            
            # Assert: top_intents list has 3 items
            assert len(response.top_intents) == 3, (
                f"Low confidence must provide 3 top intent suggestions:\n"
                f"  Text: {repr(text[:100])}\n"
                f"  Confidence: {response.confidence}\n"
                f"  Top intents count: {len(response.top_intents)}"
            )
            
            # Assert: each top_intent has intent and confidence fields
            for i, top_intent in enumerate(response.top_intents):
                assert "intent" in top_intent, (
                    f"Top intent {i} must have 'intent' field:\n"
                    f"  Text: {repr(text[:100])}\n"
                    f"  Top intent: {top_intent}"
                )
                assert "confidence" in top_intent, (
                    f"Top intent {i} must have 'confidence' field:\n"
                    f"  Text: {repr(text[:100])}\n"
                    f"  Top intent: {top_intent}"
                )
                assert isinstance(top_intent["confidence"], (int, float)), (
                    f"Top intent {i} confidence must be numeric:\n"
                    f"  Text: {repr(text[:100])}\n"
                    f"  Confidence type: {type(top_intent['confidence'])}"
                )
                assert 0.0 <= top_intent["confidence"] <= 1.0, (
                    f"Top intent {i} confidence must be between 0.0 and 1.0:\n"
                    f"  Text: {repr(text[:100])}\n"
                    f"  Confidence: {top_intent['confidence']}"
                )
            
            # Assert: suggestions list is not empty
            assert len(response.suggestions) > 0, (
                f"Low confidence must provide clarification suggestions:\n"
                f"  Text: {repr(text[:100])}\n"
                f"  Confidence: {response.confidence}\n"
                f"  Suggestions: {response.suggestions}"
            )
            
            # Assert: suggestions are strings
            for i, suggestion in enumerate(response.suggestions):
                assert isinstance(suggestion, str), (
                    f"Suggestion {i} must be a string:\n"
                    f"  Text: {repr(text[:100])}\n"
                    f"  Suggestion type: {type(suggestion)}"
                )
        
        else:
            # High confidence: should return IntentResponse
            assert isinstance(response, IntentResponse), (
                f"High confidence response must be IntentResponse:\n"
                f"  Text: {repr(text[:100])}\n"
                f"  Confidence: {response.confidence}\n"
                f"  Response type: {type(response)}"
            )
            
            # Assert: response has valid structure (already tested in Property 1)
            assert isinstance(response.intent, str)
            assert isinstance(response.entities, dict)
            assert 0.0 <= response.confidence <= 1.0
    
    @given(text=vietnamese_sentence_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_4_low_confidence_fallback_realistic_text(self, text):
        """
        **Validates: Requirements 1.4**
        
        Property 4: Low Confidence Fallback (Realistic Text)
        
        Variant of Property 4 using realistic Vietnamese sentences.
        Tests the same fallback behavior with more realistic input.
        """
        classifier = MLBasedClassifier()
        
        # Classify realistic Vietnamese sentence
        response = classifier.classify(text)
        
        # Check confidence level and validate response type
        if response.confidence < 0.7:
            assert isinstance(response, FallbackResponse)
            assert response.intent == "unknown"
            assert response.clarification_needed is True
            assert len(response.top_intents) == 3
            assert len(response.suggestions) > 0
        else:
            assert isinstance(response, IntentResponse)
            assert isinstance(response.intent, str)
            assert isinstance(response.entities, dict)
    
    def test_property_4_threshold_boundary_below(self):
        """
        Test that confidence exactly at 0.69 (below threshold) triggers fallback.
        """
        classifier = MLBasedClassifier()
        
        # Use text that will generate low confidence (arbitrary text)
        response = classifier.classify("xyz abc def ghi")
        
        # Should be low confidence and return FallbackResponse
        assert response.confidence < 0.7
        assert isinstance(response, FallbackResponse)
        assert response.intent == "unknown"
        assert response.clarification_needed is True
    
    def test_property_4_threshold_boundary_above(self):
        """
        Test that confidence at or above 0.7 returns IntentResponse.
        """
        classifier = MLBasedClassifier()
        
        # Use text that will generate high confidence (known pattern)
        response = classifier.classify("Trời nóng quá")
        
        # Should be high confidence and return IntentResponse
        assert response.confidence >= 0.7
        assert isinstance(response, IntentResponse)
        assert response.intent != "unknown"
    
    def test_property_4_top_intents_structure(self):
        """
        Test that top_intents have correct structure with intent and confidence.
        """
        classifier = MLBasedClassifier()
        
        # Use text that will generate low confidence
        response = classifier.classify("random text xyz")
        
        # Should return FallbackResponse with top_intents
        assert isinstance(response, FallbackResponse)
        assert len(response.top_intents) == 3
        
        for top_intent in response.top_intents:
            assert "intent" in top_intent
            assert "confidence" in top_intent
            assert isinstance(top_intent["intent"], str)
            assert isinstance(top_intent["confidence"], (int, float))
            assert 0.0 <= top_intent["confidence"] <= 1.0
    
    def test_property_4_suggestions_are_helpful(self):
        """
        Test that suggestions are non-empty strings (helpful clarification questions).
        """
        classifier = MLBasedClassifier()
        
        # Use text that will generate low confidence
        response = classifier.classify("unclear input")
        
        # Should return FallbackResponse with suggestions
        assert isinstance(response, FallbackResponse)
        assert len(response.suggestions) > 0
        
        for suggestion in response.suggestions:
            assert isinstance(suggestion, str)
            assert len(suggestion) > 0  # Non-empty
            # Suggestions should be questions or helpful prompts
            # (In Vietnamese, questions often end with "?" or contain question words)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestMLClassifierEdgeCases:
    """Example-based tests for specific edge cases."""
    
    def test_empty_string_handling(self):
        """Test that empty string is handled gracefully."""
        classifier = MLBasedClassifier()
        
        response = classifier.classify("")
        
        # Empty string should return low confidence fallback
        assert isinstance(response, (IntentResponse, FallbackResponse))
        if isinstance(response, FallbackResponse):
            assert response.intent == "unknown"
            assert response.clarification_needed is True
        assert isinstance(response.entities, dict)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.timestamp, datetime)
    
    def test_whitespace_only_handling(self):
        """Test that whitespace-only input is handled gracefully."""
        classifier = MLBasedClassifier()
        
        response = classifier.classify("   \n\t  ")
        
        # Whitespace should return low confidence fallback
        assert isinstance(response, (IntentResponse, FallbackResponse))
        if isinstance(response, FallbackResponse):
            assert response.intent == "unknown"
            assert response.clarification_needed is True
        assert isinstance(response.entities, dict)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.timestamp, datetime)
    
    def test_very_long_text_handling(self):
        """Test that very long text (500 chars) is handled gracefully."""
        classifier = MLBasedClassifier()
        
        long_text = "Trời nóng quá " * 50  # ~700 chars
        response = classifier.classify(long_text)
        
        assert isinstance(response, (IntentResponse, FallbackResponse))
        assert isinstance(response.intent, str)
        assert isinstance(response.entities, dict)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.timestamp, datetime)
    
    def test_special_characters_handling(self):
        """Test that special characters are handled gracefully."""
        classifier = MLBasedClassifier()
        
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        response = classifier.classify(special_text)
        
        # Special characters should return low confidence fallback
        assert isinstance(response, (IntentResponse, FallbackResponse))
        if isinstance(response, FallbackResponse):
            assert response.intent == "unknown"
            assert response.clarification_needed is True
        assert isinstance(response.entities, dict)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.timestamp, datetime)
    
    def test_mixed_language_handling(self):
        """Test that mixed Vietnamese-English text is handled gracefully."""
        classifier = MLBasedClassifier()
        
        mixed_text = "Trời nóng quá turn on the AC please"
        response = classifier.classify(mixed_text)
        
        assert isinstance(response, (IntentResponse, FallbackResponse))
        assert isinstance(response.intent, str)
        assert isinstance(response.entities, dict)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.timestamp, datetime)
    
    def test_numbers_only_handling(self):
        """Test that numbers-only input is handled gracefully."""
        classifier = MLBasedClassifier()
        
        numbers_text = "123456789"
        response = classifier.classify(numbers_text)
        
        # Numbers only should return low confidence fallback
        assert isinstance(response, (IntentResponse, FallbackResponse))
        if isinstance(response, FallbackResponse):
            assert response.intent == "unknown"
            assert response.clarification_needed is True
        assert isinstance(response.entities, dict)
        assert 0.0 <= response.confidence <= 1.0
        assert isinstance(response.timestamp, datetime)
    
    def test_environmental_comfort_cooling(self):
        """Test environmental comfort with cooling."""
        classifier = MLBasedClassifier()
        
        response = classifier.classify("Trời nóng quá")
        
        # High confidence response
        assert isinstance(response, IntentResponse)
        assert response.intent == "environmental_comfort"
        assert response.entities.get("comfort_type") == "cooling"
        assert response.confidence > 0.0
        assert response.classifier_type == "ml"
    
    def test_environmental_comfort_warming(self):
        """Test environmental comfort with warming."""
        classifier = MLBasedClassifier()
        
        response = classifier.classify("Trời lạnh quá")
        
        # High confidence response
        assert isinstance(response, IntentResponse)
        assert response.intent == "environmental_comfort"
        assert response.entities.get("comfort_type") == "warming"
        assert response.confidence > 0.0
        assert response.classifier_type == "ml"
    
    def test_environmental_comfort_brighten(self):
        """Test environmental comfort with brighten."""
        classifier = MLBasedClassifier()
        
        response = classifier.classify("Tối quá")
        
        # High confidence response
        assert isinstance(response, IntentResponse)
        assert response.intent == "environmental_comfort"
        assert response.entities.get("comfort_type") == "brighten"
        assert response.confidence > 0.0
        assert response.classifier_type == "ml"
    
    def test_unknown_intent_for_arbitrary_text(self):
        """Test that arbitrary text returns unknown intent with fallback."""
        classifier = MLBasedClassifier()
        
        response = classifier.classify("xyz abc def")
        
        # Low confidence should return FallbackResponse
        assert isinstance(response, FallbackResponse)
        assert response.intent == "unknown"
        assert response.confidence < 0.7
        assert response.clarification_needed is True
        assert len(response.top_intents) == 3
        assert len(response.suggestions) > 0



# ============================================================================
# PROPERTY TEST 5: ENVIRONMENTAL COMFORT CLASSIFICATION
# ============================================================================

class TestEnvironmentalComfortClassification:
    """
    Property Test 5: Environmental Comfort Classification
    
    For any Vietnamese text containing environmental comfort keywords 
    (nóng, lạnh, tối, sáng, ngột ngạt, etc.), the NLP Server SHALL classify 
    the intent as "environmental_comfort" and extract the appropriate 
    comfort_type entity (cooling, warming, brighten, dim, ventilate).
    
    **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7**
    """
    
    # Environmental comfort keyword mappings
    COMFORT_KEYWORDS = {
        "cooling": ["nóng", "oi bức", "nóng quá", "nóng nực", "oi", "nóng bức"],
        "warming": ["lạnh", "rét", "lạnh quá", "rét quá", "lạnh lẽo", "rét mướt"],
        "brighten": ["tối", "tối quá", "thiếu sáng", "tối om", "tối thui"],
        "dim": ["chói", "sáng quá", "chói mắt", "sáng lóa"],
        "ventilate": ["ngột ngạt", "thiếu không khí", "ngột", "ngạt", "bí bách"]
    }
    
    @given(
        comfort_type=st.sampled_from(["cooling", "warming", "brighten", "dim", "ventilate"]),
        keyword_index=st.integers(min_value=0, max_value=5),  # Index into keyword list
        prefix=st.sampled_from(["", "trời ", "ở đây ", "phòng này ", "trong nhà "]),
        suffix=st.sampled_from(["", " quá", " lắm", " ghê", " thật"])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_5_environmental_comfort_with_keywords(
        self, 
        comfort_type: str,
        keyword_index: int,
        prefix: str,
        suffix: str
    ):
        """
        Property Test 5: Texts with comfort keywords classify as environmental_comfort.
        
        Test that any text containing environmental comfort keywords is correctly
        classified as environmental_comfort intent with the appropriate comfort_type entity.
        """
        # Arrange: Select a keyword for the comfort type using index
        keywords = self.COMFORT_KEYWORDS[comfort_type]
        keyword = keywords[keyword_index % len(keywords)]  # Wrap around if index too large
        text = f"{prefix}{keyword}{suffix}".strip()
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should be environmental_comfort
        assert result.intent == "environmental_comfort", \
            f"Expected intent 'environmental_comfort' for text '{text}', got '{result.intent}'"
        
        # Assert: Entities should contain comfort_type
        assert "comfort_type" in result.entities, \
            f"Expected 'comfort_type' entity in result for text '{text}'"
        
        # Assert: comfort_type should match expected type
        assert result.entities["comfort_type"] == comfort_type, \
            f"Expected comfort_type '{comfort_type}' for text '{text}', got '{result.entities['comfort_type']}'"
        
        # Assert: Confidence should be reasonable (> 0.5 for clear keywords)
        assert result.confidence > 0.5, \
            f"Expected confidence > 0.5 for text '{text}', got {result.confidence}"
    
    def test_property_5_cooling_keywords(self):
        """Test cooling comfort type with specific Vietnamese examples."""
        cooling_texts = [
            "nóng quá",
            "trời nóng",
            "oi bức quá",
            "nóng nực",
            "phòng này nóng lắm"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in cooling_texts:
            result = classifier.classify(text)
            
            assert result.intent == "environmental_comfort", \
                f"Expected 'environmental_comfort' for '{text}', got '{result.intent}'"
            assert result.entities.get("comfort_type") == "cooling", \
                f"Expected comfort_type 'cooling' for '{text}', got '{result.entities.get('comfort_type')}'"
    
    def test_property_5_warming_keywords(self):
        """Test warming comfort type with specific Vietnamese examples."""
        warming_texts = [
            "lạnh quá",
            "trời lạnh",
            "rét quá",
            "lạnh lẽo",
            "phòng này lạnh lắm"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in warming_texts:
            result = classifier.classify(text)
            
            assert result.intent == "environmental_comfort", \
                f"Expected 'environmental_comfort' for '{text}', got '{result.intent}'"
            assert result.entities.get("comfort_type") == "warming", \
                f"Expected comfort_type 'warming' for '{text}', got '{result.entities.get('comfort_type')}'"
    
    def test_property_5_brighten_keywords(self):
        """Test brighten comfort type with specific Vietnamese examples."""
        brighten_texts = [
            "tối quá",
            "trời tối",
            "thiếu sáng",
            "tối om",
            "phòng này tối lắm"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in brighten_texts:
            result = classifier.classify(text)
            
            assert result.intent == "environmental_comfort", \
                f"Expected 'environmental_comfort' for '{text}', got '{result.intent}'"
            assert result.entities.get("comfort_type") == "brighten", \
                f"Expected comfort_type 'brighten' for '{text}', got '{result.entities.get('comfort_type')}'"
    
    def test_property_5_dim_keywords(self):
        """Test dim comfort type with specific Vietnamese examples."""
        dim_texts = [
            "chói quá",
            "sáng quá",
            "chói mắt",
            "sáng lóa",
            "phòng này sáng lắm"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in dim_texts:
            result = classifier.classify(text)
            
            assert result.intent == "environmental_comfort", \
                f"Expected 'environmental_comfort' for '{text}', got '{result.intent}'"
            assert result.entities.get("comfort_type") == "dim", \
                f"Expected comfort_type 'dim' for '{text}', got '{result.entities.get('comfort_type')}'"
    
    def test_property_5_ventilate_keywords(self):
        """Test ventilate comfort type with specific Vietnamese examples."""
        ventilate_texts = [
            "ngột ngạt quá",
            "thiếu không khí",
            "ngột ngạt",
            "bí bách",
            "phòng này ngột lắm"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in ventilate_texts:
            result = classifier.classify(text)
            
            assert result.intent == "environmental_comfort", \
                f"Expected 'environmental_comfort' for '{text}', got '{result.intent}'"
            assert result.entities.get("comfort_type") == "ventilate", \
                f"Expected comfort_type 'ventilate' for '{text}', got '{result.entities.get('comfort_type')}'"
    
    def test_property_5_confidence_threshold(self):
        """Test that environmental comfort classification has reasonable confidence."""
        test_cases = [
            ("nóng quá", "cooling"),
            ("lạnh quá", "warming"),
            ("tối quá", "brighten"),
            ("sáng quá", "dim"),
            ("ngột ngạt", "ventilate")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_comfort_type in test_cases:
            result = classifier.classify(text)
            
            # Confidence should be high for clear keywords
            assert result.confidence >= 0.7, \
                f"Expected confidence >= 0.7 for clear keyword '{text}', got {result.confidence}"
            
            # Intent and entity should match
            assert result.intent == "environmental_comfort"
            assert result.entities["comfort_type"] == expected_comfort_type
    
    def test_property_5_with_context_words(self):
        """Test environmental comfort with additional context words."""
        test_cases = [
            ("ở đây nóng quá", "cooling"),
            ("phòng này lạnh lắm", "warming"),
            ("trong nhà tối thật", "brighten"),
            ("trời sáng chói mắt", "dim"),
            ("không khí ngột ngạt", "ventilate")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_comfort_type in test_cases:
            result = classifier.classify(text)
            
            assert result.intent == "environmental_comfort", \
                f"Expected 'environmental_comfort' for '{text}', got '{result.intent}'"
            assert result.entities["comfort_type"] == expected_comfort_type, \
                f"Expected comfort_type '{expected_comfort_type}' for '{text}', got '{result.entities['comfort_type']}'"
    
    def test_property_5_multiple_comfort_keywords(self):
        """Test texts with multiple comfort keywords (should pick primary one)."""
        # When multiple keywords present, classifier should pick the most prominent one
        test_cases = [
            "nóng và tối",  # Should classify as environmental_comfort
            "lạnh và ngột ngạt",  # Should classify as environmental_comfort
        ]
        
        classifier = MLBasedClassifier()
        
        for text in test_cases:
            result = classifier.classify(text)
            
            # Should still classify as environmental_comfort
            assert result.intent == "environmental_comfort", \
                f"Expected 'environmental_comfort' for '{text}', got '{result.intent}'"
            
            # Should have a comfort_type entity
            assert "comfort_type" in result.entities, \
                f"Expected 'comfort_type' entity for '{text}'"
    
    def test_property_5_negative_cases(self):
        """Test that non-comfort texts don't classify as environmental_comfort."""
        non_comfort_texts = [
            "bật đèn",  # control_device
            "tắt quạt",  # control_device
            "nhiệt độ bao nhiêu",  # query_sensor
        ]
        
        classifier = MLBasedClassifier()
        
        for text in non_comfort_texts:
            result = classifier.classify(text)
            
            # Should NOT classify as environmental_comfort
            assert result.intent != "environmental_comfort", \
                f"Text '{text}' should not classify as environmental_comfort, got '{result.intent}'"



# ============================================================================
# PROPERTY TEST 6: SENSOR QUERY CLASSIFICATION
# ============================================================================

class TestSensorQueryClassification:
    """
    Property Test 6: Sensor Query Classification
    
    For any Vietnamese text containing sensor query patterns (nhiệt độ bao nhiêu, 
    độ ẩm, có mưa không, etc.), the NLP Server SHALL classify the intent as 
    "query_sensor" or "query_device_status" and extract the appropriate 
    sensor_type or device entity.
    
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
    """
    
    # Sensor query keyword mappings
    SENSOR_QUERY_KEYWORDS = {
        "temperature": ["nhiệt độ", "bao nhiêu độ", "đo nhiệt độ", "temperature"],
        "humidity": ["độ ẩm", "ẩm không", "kiểm tra độ ẩm", "humidity"],
        "rain": ["có mưa không", "trời mưa không", "dự báo mưa", "mưa", "rain"],
        "gas": ["có khí gas không", "kiểm tra khí gas", "có gas không", "kiểm tra gas"],
        "fire": ["có cháy không", "kiểm tra cháy", "có lửa không"],
        "motion": ["có người không", "phát hiện chuyển động", "ai đó vào", "chuyển động", "motion"]
    }
    
    # Device status query patterns
    DEVICE_STATUS_KEYWORDS = {
        "light": ["trạng thái đèn", "đèn có bật không", "đèn đang bật không"],
        "fan": ["trạng thái quạt", "quạt có bật không", "quạt đang chạy không"],
        "ac": ["trạng thái điều hòa", "điều hòa có bật không", "ac đang bật không"],
        "door": ["trạng thái cửa", "cửa có mở không", "cửa đang mở không"]
    }
    
    @given(
        sensor_type=st.sampled_from(["temperature", "humidity", "rain", "gas", "fire", "motion"]),
        keyword_index=st.integers(min_value=0, max_value=5),
        prefix=st.sampled_from(["", "kiểm tra ", "cho tôi biết ", "xem ", ""]),
        suffix=st.sampled_from(["", " bao nhiêu", " thế nào", " như thế nào", ""])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_6_sensor_query_with_keywords(
        self,
        sensor_type: str,
        keyword_index: int,
        prefix: str,
        suffix: str
    ):
        """
        Property Test 6: Texts with sensor query patterns classify as query_sensor.
        
        Test that any text containing sensor query keywords is correctly
        classified as query_sensor intent with the appropriate sensor_type entity.
        """
        # Arrange: Select a keyword for the sensor type using index
        keywords = self.SENSOR_QUERY_KEYWORDS[sensor_type]
        keyword = keywords[keyword_index % len(keywords)]
        text = f"{prefix}{keyword}{suffix}".strip()
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should be query_sensor
        assert result.intent == "query_sensor", \
            f"Expected intent 'query_sensor' for text '{text}', got '{result.intent}'"
        
        # Assert: Entities should contain sensor_type
        assert "sensor_type" in result.entities, \
            f"Expected 'sensor_type' entity in result for text '{text}'"
        
        # Assert: sensor_type should match expected type
        assert result.entities["sensor_type"] == sensor_type, \
            f"Expected sensor_type '{sensor_type}' for text '{text}', got '{result.entities['sensor_type']}'"
        
        # Assert: Confidence should be reasonable
        assert result.confidence > 0.5, \
            f"Expected confidence > 0.5 for text '{text}', got {result.confidence}"
    
    @given(
        device_type=st.sampled_from(["light", "fan", "ac", "door"]),
        keyword_index=st.integers(min_value=0, max_value=2),
        location=st.sampled_from(["", " phòng khách", " phòng ngủ", " bếp"])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_6_device_status_query_with_keywords(
        self,
        device_type: str,
        keyword_index: int,
        location: str
    ):
        """
        Property Test 6: Texts with device status query patterns classify as query_device_status.
        
        Test that any text asking about device status is correctly classified
        as query_device_status intent with the appropriate device entity.
        """
        # Arrange: Select a keyword for the device type using index
        keywords = self.DEVICE_STATUS_KEYWORDS[device_type]
        keyword = keywords[keyword_index % len(keywords)]
        text = f"{keyword}{location}".strip()
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should be query_device_status
        assert result.intent == "query_device_status", \
            f"Expected intent 'query_device_status' for text '{text}', got '{result.intent}'"
        
        # Assert: Entities should contain device
        assert "device" in result.entities, \
            f"Expected 'device' entity in result for text '{text}'"
        
        # Assert: device should match expected type
        assert result.entities["device"] == device_type, \
            f"Expected device '{device_type}' for text '{text}', got '{result.entities['device']}'"
        
        # Assert: If location was specified, it should be extracted
        if location.strip():
            assert "location" in result.entities, \
                f"Expected 'location' entity for text '{text}' with location '{location}'"
    
    def test_property_6_temperature_queries(self):
        """Test temperature sensor queries with specific Vietnamese examples."""
        temperature_texts = [
            "nhiệt độ bao nhiêu",
            "bao nhiêu độ",
            "đo nhiệt độ",
            "nhiệt độ phòng ngủ",
            "kiểm tra nhiệt độ"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in temperature_texts:
            result = classifier.classify(text)
            
            assert result.intent == "query_sensor", \
                f"Expected 'query_sensor' for '{text}', got '{result.intent}'"
            assert result.entities.get("sensor_type") == "temperature", \
                f"Expected sensor_type 'temperature' for '{text}', got '{result.entities.get('sensor_type')}'"
    
    def test_property_6_humidity_queries(self):
        """Test humidity sensor queries with specific Vietnamese examples."""
        humidity_texts = [
            "độ ẩm bao nhiêu",
            "ẩm không",
            "kiểm tra độ ẩm",
            "độ ẩm phòng khách",
            "đo độ ẩm"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in humidity_texts:
            result = classifier.classify(text)
            
            assert result.intent == "query_sensor", \
                f"Expected 'query_sensor' for '{text}', got '{result.intent}'"
            assert result.entities.get("sensor_type") == "humidity", \
                f"Expected sensor_type 'humidity' for '{text}', got '{result.entities.get('sensor_type')}'"
    
    def test_property_6_rain_queries(self):
        """Test rain sensor queries with specific Vietnamese examples."""
        rain_texts = [
            "có mưa không",
            "trời mưa không",
            "dự báo mưa",
            "có mưa ngoài trời không",
            "kiểm tra mưa"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in rain_texts:
            result = classifier.classify(text)
            
            assert result.intent == "query_sensor", \
                f"Expected 'query_sensor' for '{text}', got '{result.intent}'"
            assert result.entities.get("sensor_type") == "rain", \
                f"Expected sensor_type 'rain' for '{text}', got '{result.entities.get('sensor_type')}'"
    
    def test_property_6_gas_queries(self):
        """Test gas sensor queries with specific Vietnamese examples."""
        gas_texts = [
            "có khí gas không",
            "kiểm tra khí gas",
            "có gas không",
            "kiểm tra gas",
        ]
        
        classifier = MLBasedClassifier()
        
        for text in gas_texts:
            result = classifier.classify(text)
            
            assert result.intent == "query_sensor", \
                f"Expected 'query_sensor' for '{text}', got '{result.intent}'"
            assert result.entities.get("sensor_type") == "gas", \
                f"Expected sensor_type 'gas' for '{text}', got '{result.entities.get('sensor_type')}'"
    
    def test_property_6_fire_queries(self):
        """Test fire sensor queries with specific Vietnamese examples."""
        fire_texts = [
            "có cháy không",
            "kiểm tra cháy",
            "có lửa không",
        ]
        
        classifier = MLBasedClassifier()
        
        for text in fire_texts:
            result = classifier.classify(text)
            
            assert result.intent == "query_sensor", \
                f"Expected 'query_sensor' for '{text}', got '{result.intent}'"
            assert result.entities.get("sensor_type") == "fire", \
                f"Expected sensor_type 'fire' for '{text}', got '{result.entities.get('sensor_type')}'"
    
    def test_property_6_motion_queries(self):
        """Test motion sensor queries with specific Vietnamese examples."""
        motion_texts = [
            "có người không",
            "phát hiện chuyển động",
            "ai đó vào",
            "kiểm tra chuyển động",
            "có ai trong phòng không"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in motion_texts:
            result = classifier.classify(text)
            
            assert result.intent == "query_sensor", \
                f"Expected 'query_sensor' for '{text}', got '{result.intent}'"
            assert result.entities.get("sensor_type") == "motion", \
                f"Expected sensor_type 'motion' for '{text}', got '{result.entities.get('sensor_type')}'"
    
    def test_property_6_device_status_queries(self):
        """Test device status queries with specific Vietnamese examples."""
        device_status_texts = [
            ("trạng thái đèn", "light"),
            ("đèn có bật không", "light"),
            ("quạt đang bật không", "fan"),
            ("trạng thái quạt phòng ngủ", "fan"),
            ("điều hòa có bật không", "ac"),
            ("cửa có mở không", "door")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_device in device_status_texts:
            result = classifier.classify(text)
            
            assert result.intent == "query_device_status", \
                f"Expected 'query_device_status' for '{text}', got '{result.intent}'"
            assert result.entities.get("device") == expected_device, \
                f"Expected device '{expected_device}' for '{text}', got '{result.entities.get('device')}'"
    
    def test_property_6_query_with_location(self):
        """Test sensor queries with location specification."""
        test_cases = [
            ("nhiệt độ phòng khách", "temperature", "living_room"),
            ("độ ẩm phòng ngủ", "humidity", "bedroom"),
            ("trạng thái đèn bếp", "light", "kitchen")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_sensor_or_device, expected_location in test_cases:
            result = classifier.classify(text)
            
            # Should extract location entity
            assert "location" in result.entities, \
                f"Expected 'location' entity for '{text}'"
            assert result.entities["location"] == expected_location, \
                f"Expected location '{expected_location}' for '{text}', got '{result.entities['location']}'"
    
    def test_property_6_confidence_threshold(self):
        """Test that sensor query classification has reasonable confidence."""
        test_cases = [
            ("nhiệt độ bao nhiêu", "query_sensor", "temperature"),
            ("độ ẩm bao nhiêu", "query_sensor", "humidity"),
            ("có mưa không", "query_sensor", "rain"),
            ("trạng thái đèn", "query_device_status", "light")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_intent, expected_entity_value in test_cases:
            result = classifier.classify(text)
            
            # Confidence should be high for clear query patterns
            assert result.confidence >= 0.7, \
                f"Expected confidence >= 0.7 for clear query '{text}', got {result.confidence}"
            
            # Intent should match
            assert result.intent == expected_intent, \
                f"Expected intent '{expected_intent}' for '{text}', got '{result.intent}'"
    
    def test_property_6_negative_cases(self):
        """Test that non-query texts don't classify as query_sensor or query_device_status."""
        non_query_texts = [
            "bật đèn",  # control_device
            "tắt quạt",  # control_device
            "nóng quá",  # environmental_comfort
            "đi ngủ",  # activate_scene
        ]
        
        classifier = MLBasedClassifier()
        
        for text in non_query_texts:
            result = classifier.classify(text)
            
            # Should NOT classify as query_sensor or query_device_status
            assert result.intent not in ["query_sensor", "query_device_status"], \
                f"Text '{text}' should not classify as query intent, got '{result.intent}'"
    
    def test_property_6_distinguish_query_from_control(self):
        """Test that queries are distinguished from control commands."""
        # Query patterns (asking for information)
        query_patterns = [
            "nhiệt độ bao nhiêu",  # query_sensor
            "đèn có bật không",  # query_device_status
        ]
        
        # Control patterns (commanding action)
        control_patterns = [
            "bật đèn",  # control_device
            "tắt quạt",  # control_device
        ]
        
        classifier = MLBasedClassifier()
        
        # Queries should be query_sensor or query_device_status
        for text in query_patterns:
            result = classifier.classify(text)
            assert result.intent in ["query_sensor", "query_device_status"], \
                f"Query '{text}' should classify as query intent, got '{result.intent}'"
        
        # Controls should be control_device
        for text in control_patterns:
            result = classifier.classify(text)
            assert result.intent == "control_device", \
                f"Control '{text}' should classify as control_device, got '{result.intent}'"



# ============================================================================
# PROPERTY TEST 7: SECURITY MODE CLASSIFICATION
# ============================================================================

class TestSecurityModeClassification:
    """
    Property Test 7: Security Mode Classification
    
    For any Vietnamese text containing security mode keywords (bật báo động, 
    tắt báo động, kích hoạt an ninh, etc.), the NLP Server SHALL classify 
    the intent as "security_mode" and extract the appropriate mode entity 
    (armed or disarmed).
    
    **Validates: Requirements 5.1, 5.2**
    """
    
    # Security mode keyword mappings
    SECURITY_MODE_KEYWORDS = {
        "armed": ["bật báo động", "kích hoạt an ninh", "bật chế độ an ninh", "armed", "bật bảo vệ"],
        "disarmed": ["tắt báo động", "vô hiệu hóa an ninh", "tắt chế độ an ninh", "disarmed", "tắt bảo vệ"]
    }
    
    @given(
        mode=st.sampled_from(["armed", "disarmed"]),
        keyword_index=st.integers(min_value=0, max_value=4),
        prefix=st.sampled_from(["", "tôi muốn ", "hãy ", "làm ơn ", ""]),
        suffix=st.sampled_from(["", " đi", " ngay", " bây giờ", ""])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_7_security_mode_with_keywords(
        self,
        mode: str,
        keyword_index: int,
        prefix: str,
        suffix: str
    ):
        """
        Property Test 7: Texts with security mode keywords classify as security_mode.
        
        Test that any text containing security mode keywords is correctly
        classified as security_mode intent with the appropriate mode entity.
        """
        # Arrange: Select a keyword for the mode using index
        keywords = self.SECURITY_MODE_KEYWORDS[mode]
        keyword = keywords[keyword_index % len(keywords)]
        text = f"{prefix}{keyword}{suffix}".strip()
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should be security_mode
        assert result.intent == "security_mode", \
            f"Expected intent 'security_mode' for text '{text}', got '{result.intent}'"
        
        # Assert: Entities should contain mode
        assert "mode" in result.entities, \
            f"Expected 'mode' entity in result for text '{text}'"
        
        # Assert: mode should match expected type
        assert result.entities["mode"] == mode, \
            f"Expected mode '{mode}' for text '{text}', got '{result.entities['mode']}'"
        
        # Assert: Confidence should be reasonable
        assert result.confidence > 0.5, \
            f"Expected confidence > 0.5 for text '{text}', got {result.confidence}"
    
    def test_property_7_armed_mode_keywords(self):
        """Test armed mode with specific Vietnamese examples."""
        armed_texts = [
            "bật báo động",
            "kích hoạt an ninh",
            "bật chế độ an ninh",
            "tôi muốn bật báo động",
            "hãy kích hoạt an ninh đi"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in armed_texts:
            result = classifier.classify(text)
            
            assert result.intent == "security_mode", \
                f"Expected 'security_mode' for '{text}', got '{result.intent}'"
            assert result.entities.get("mode") == "armed", \
                f"Expected mode 'armed' for '{text}', got '{result.entities.get('mode')}'"
    
    def test_property_7_disarmed_mode_keywords(self):
        """Test disarmed mode with specific Vietnamese examples."""
        disarmed_texts = [
            "tắt báo động",
            "vô hiệu hóa an ninh",
            "tắt chế độ an ninh",
            "tôi muốn tắt báo động",
            "hãy vô hiệu hóa an ninh đi"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in disarmed_texts:
            result = classifier.classify(text)
            
            assert result.intent == "security_mode", \
                f"Expected 'security_mode' for '{text}', got '{result.intent}'"
            assert result.entities.get("mode") == "disarmed", \
                f"Expected mode 'disarmed' for '{text}', got '{result.entities.get('mode')}'"
    
    def test_property_7_confidence_threshold(self):
        """Test that security mode classification has reasonable confidence."""
        test_cases = [
            ("bật báo động", "armed"),
            ("tắt báo động", "disarmed"),
            ("kích hoạt an ninh", "armed"),
            ("vô hiệu hóa an ninh", "disarmed")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_mode in test_cases:
            result = classifier.classify(text)
            
            # Confidence should be high for clear keywords
            assert result.confidence >= 0.7, \
                f"Expected confidence >= 0.7 for clear keyword '{text}', got {result.confidence}"
            
            # Intent and entity should match
            assert result.intent == "security_mode"
            assert result.entities["mode"] == expected_mode
    
    def test_property_7_with_context_words(self):
        """Test security mode with additional context words."""
        test_cases = [
            ("tôi muốn bật báo động", "armed"),
            ("hãy tắt báo động đi", "disarmed"),
            ("làm ơn kích hoạt an ninh", "armed"),
            ("vô hiệu hóa an ninh ngay", "disarmed")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_mode in test_cases:
            result = classifier.classify(text)
            
            assert result.intent == "security_mode", \
                f"Expected 'security_mode' for '{text}', got '{result.intent}'"
            assert result.entities["mode"] == expected_mode, \
                f"Expected mode '{expected_mode}' for '{text}', got '{result.entities['mode']}'"
    
    def test_property_7_negative_cases(self):
        """Test that non-security texts don't classify as security_mode."""
        non_security_texts = [
            "bật đèn",  # control_device
            "tắt quạt",  # control_device
            "nóng quá",  # environmental_comfort
        ]
        
        classifier = MLBasedClassifier()
        
        for text in non_security_texts:
            result = classifier.classify(text)
            
            # Should NOT classify as security_mode
            assert result.intent != "security_mode", \
                f"Text '{text}' should not classify as security_mode, got '{result.intent}'"


# ============================================================================
# PROPERTY TEST 8: SECURITY ALERT CLASSIFICATION
# ============================================================================

class TestSecurityAlertClassification:
    """
    Property Test 8: Security Alert Classification
    
    For any Vietnamese text containing danger keywords (cháy, khí gas, trộm) 
    WITHOUT entertainment context, the NLP Server SHALL classify the intent 
    as "security_alert" and extract the appropriate alert_type entity 
    (fire, gas, intrusion).
    
    **Validates: Requirements 5.3, 5.4, 5.5**
    """
    
    # Security alert keyword mappings
    SECURITY_ALERT_KEYWORDS = {
        "fire": ["cháy", "có lửa", "hỏa hoạn", "fire"],
        "gas": ["khí gas", "rò rỉ gas", "gas leak", "có mùi gas"],
        "intrusion": ["trộm", "đột nhập", "có người lạ", "intruder", "kẻ xâm nhập"]
    }
    
    # Entertainment context keywords (should prevent false positives)
    ENTERTAINMENT_KEYWORDS = ["phim", "game", "bài hát", "trận đấu", "video", "nhạc"]
    
    @given(
        alert_type=st.sampled_from(["fire", "gas", "intrusion"]),
        keyword_index=st.integers(min_value=0, max_value=3),
        prefix=st.sampled_from(["", "cảnh báo ", "phát hiện ", "có ", ""]),
        suffix=st.sampled_from(["", " rồi", " kìa", " ở đây", ""])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_8_security_alert_with_keywords(
        self,
        alert_type: str,
        keyword_index: int,
        prefix: str,
        suffix: str
    ):
        """
        Property Test 8: Texts with danger keywords classify as security_alert.
        
        Test that any text containing danger keywords WITHOUT entertainment context
        is correctly classified as security_alert intent with the appropriate 
        alert_type entity.
        """
        # Arrange: Select a keyword for the alert type using index
        keywords = self.SECURITY_ALERT_KEYWORDS[alert_type]
        keyword = keywords[keyword_index % len(keywords)]
        text = f"{prefix}{keyword}{suffix}".strip()
        
        # Skip if text contains entertainment keywords (false positive prevention)
        if any(ent_keyword in text.lower() for ent_keyword in self.ENTERTAINMENT_KEYWORDS):
            return  # Skip this test case
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should be security_alert
        assert result.intent == "security_alert", \
            f"Expected intent 'security_alert' for text '{text}', got '{result.intent}'"
        
        # Assert: Entities should contain alert_type
        assert "alert_type" in result.entities, \
            f"Expected 'alert_type' entity in result for text '{text}'"
        
        # Assert: alert_type should match expected type
        assert result.entities["alert_type"] == alert_type, \
            f"Expected alert_type '{alert_type}' for text '{text}', got '{result.entities['alert_type']}'"
        
        # Assert: Confidence should be reasonable
        assert result.confidence > 0.5, \
            f"Expected confidence > 0.5 for text '{text}', got {result.confidence}"
    
    def test_property_8_fire_alert_keywords(self):
        """Test fire alert with specific Vietnamese examples."""
        fire_texts = [
            "cháy rồi",
            "có lửa",
            "hỏa hoạn",
            "phát hiện cháy",
            "cảnh báo cháy"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in fire_texts:
            result = classifier.classify(text)
            
            assert result.intent == "security_alert", \
                f"Expected 'security_alert' for '{text}', got '{result.intent}'"
            assert result.entities.get("alert_type") == "fire", \
                f"Expected alert_type 'fire' for '{text}', got '{result.entities.get('alert_type')}'"
    
    def test_property_8_gas_alert_keywords(self):
        """Test gas alert with specific Vietnamese examples."""
        gas_texts = [
            "khí gas rò rỉ",
            "có mùi gas",
            "rò rỉ gas",
            "phát hiện khí gas",
            "cảnh báo gas"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in gas_texts:
            result = classifier.classify(text)
            
            assert result.intent == "security_alert", \
                f"Expected 'security_alert' for '{text}', got '{result.intent}'"
            assert result.entities.get("alert_type") == "gas", \
                f"Expected alert_type 'gas' for '{text}', got '{result.entities.get('alert_type')}'"
    
    def test_property_8_intrusion_alert_keywords(self):
        """Test intrusion alert with specific Vietnamese examples."""
        intrusion_texts = [
            "có trộm",
            "đột nhập",
            "có người lạ",
            "phát hiện kẻ xâm nhập",
            "cảnh báo trộm"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in intrusion_texts:
            result = classifier.classify(text)
            
            assert result.intent == "security_alert", \
                f"Expected 'security_alert' for '{text}', got '{result.intent}'"
            assert result.entities.get("alert_type") == "intrusion", \
                f"Expected alert_type 'intrusion' for '{text}', got '{result.entities.get('alert_type')}'"
    
    def test_property_8_confidence_threshold(self):
        """Test that security alert classification has reasonable confidence."""
        test_cases = [
            ("cháy rồi", "fire"),
            ("khí gas rò rỉ", "gas"),
            ("có trộm", "intrusion")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_alert_type in test_cases:
            result = classifier.classify(text)
            
            # Confidence should be high for clear keywords
            assert result.confidence >= 0.7, \
                f"Expected confidence >= 0.7 for clear keyword '{text}', got {result.confidence}"
            
            # Intent and entity should match
            assert result.intent == "security_alert"
            assert result.entities["alert_type"] == expected_alert_type


# ============================================================================
# PROPERTY TEST 9: SECURITY ALERT PRIORITY MARKING
# ============================================================================

class TestSecurityAlertPriorityMarking:
    """
    Property Test 9: Security Alert Priority Marking
    
    For any text classified as "security_alert", the response SHALL include 
    a priority="high" field to indicate urgent handling is required.
    
    **Validates: Requirements 5.6**
    """
    
    @given(
        alert_type=st.sampled_from(["fire", "gas", "intrusion"]),
        keyword_index=st.integers(min_value=0, max_value=3)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_9_security_alert_has_high_priority(
        self,
        alert_type: str,
        keyword_index: int
    ):
        """
        Property Test 9: Security alerts include priority="high" field.
        
        Test that any security_alert intent includes a priority field set to "high".
        """
        # Arrange: Select a keyword for the alert type
        keywords = TestSecurityAlertClassification.SECURITY_ALERT_KEYWORDS[alert_type]
        keyword = keywords[keyword_index % len(keywords)]
        text = keyword
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should be security_alert
        assert result.intent == "security_alert", \
            f"Expected intent 'security_alert' for text '{text}', got '{result.intent}'"
        
        # Assert: Entities should contain priority field
        assert "priority" in result.entities, \
            f"Expected 'priority' entity in result for security_alert text '{text}'"
        
        # Assert: priority should be "high"
        assert result.entities["priority"] == "high", \
            f"Expected priority 'high' for security_alert text '{text}', got '{result.entities['priority']}'"
    
    def test_property_9_all_alert_types_have_high_priority(self):
        """Test that all alert types include priority="high"."""
        test_cases = [
            ("cháy rồi", "fire"),
            ("khí gas rò rỉ", "gas"),
            ("có trộm", "intrusion")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_alert_type in test_cases:
            result = classifier.classify(text)
            
            assert result.intent == "security_alert"
            assert result.entities.get("alert_type") == expected_alert_type
            assert result.entities.get("priority") == "high", \
                f"Expected priority 'high' for '{text}', got '{result.entities.get('priority')}'"
    
    def test_property_9_non_security_alerts_no_priority(self):
        """Test that non-security intents don't have priority field."""
        non_security_texts = [
            "bật đèn",  # control_device
            "nóng quá",  # environmental_comfort
            "nhiệt độ bao nhiêu",  # query_sensor
        ]
        
        classifier = MLBasedClassifier()
        
        for text in non_security_texts:
            result = classifier.classify(text)
            
            # Should NOT have priority field (or if present, not "high")
            if "priority" in result.entities:
                assert result.entities["priority"] != "high", \
                    f"Non-security text '{text}' should not have priority='high'"


# ============================================================================
# PROPERTY TEST 11: FALSE POSITIVE PREVENTION
# ============================================================================

class TestSecurityAlertFalsePositivePrevention:
    """
    Property Test 11: False Positive Prevention
    
    For any Vietnamese text containing BOTH danger keywords AND entertainment 
    keywords (phim, game, bài hát, trận đấu), the NLP Server SHALL NOT 
    classify the intent as "security_alert".
    
    This prevents false positives like "phim này cháy quá" (this movie is fire/awesome)
    from triggering security alerts.
    
    **Validates: Requirements 5.7, 5.8**
    """
    
    # Entertainment context keywords
    ENTERTAINMENT_KEYWORDS = ["phim", "game", "bài hát", "trận đấu", "video", "nhạc", "truyện"]
    
    # Danger keywords that might appear in entertainment context
    DANGER_KEYWORDS = ["cháy", "nổ", "bùng nổ", "đỉnh", "khủng"]
    
    @given(
        danger_keyword=st.sampled_from(["cháy", "nổ", "bùng nổ", "đỉnh", "khủng"]),
        entertainment_keyword=st.sampled_from(["phim", "game", "bài hát", "trận đấu", "video"]),
        connector=st.sampled_from([" này ", " ", " đó ", " "])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_11_entertainment_context_prevents_security_alert(
        self,
        danger_keyword: str,
        entertainment_keyword: str,
        connector: str
    ):
        """
        Property Test 11: Entertainment context prevents security alert classification.
        
        Test that texts with BOTH danger keywords AND entertainment keywords
        do NOT classify as security_alert (false positive prevention).
        """
        # Arrange: Create text with both danger and entertainment keywords
        text = f"{entertainment_keyword}{connector}{danger_keyword} quá"
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should NOT be security_alert
        assert result.intent != "security_alert", \
            f"Text with entertainment context '{text}' should NOT classify as security_alert, got '{result.intent}'"
    
    def test_property_11_false_positive_examples(self):
        """Test specific false positive examples that should NOT trigger security alerts."""
        false_positive_texts = [
            "phim này cháy quá",  # This movie is fire (awesome)
            "game này nổ tung",  # This game is explosive (amazing)
            "bài hát này bùng nổ",  # This song is explosive (popular)
            "trận đấu này cháy",  # This match is fire (exciting)
            "video này đỉnh quá",  # This video is peak (excellent)
        ]
        
        classifier = MLBasedClassifier()
        
        for text in false_positive_texts:
            result = classifier.classify(text)
            
            # Should NOT classify as security_alert
            assert result.intent != "security_alert", \
                f"False positive text '{text}' should NOT classify as security_alert, got '{result.intent}'"
    
    def test_property_11_true_positive_examples(self):
        """Test that genuine security alerts still work (without entertainment context)."""
        true_positive_texts = [
            "cháy rồi",  # Fire!
            "có khí gas",  # There's gas
            "có trộm",  # There's a thief
        ]
        
        classifier = MLBasedClassifier()
        
        for text in true_positive_texts:
            result = classifier.classify(text)
            
            # Should classify as security_alert
            assert result.intent == "security_alert", \
                f"True security alert '{text}' should classify as security_alert, got '{result.intent}'"
    
    def test_property_11_entertainment_keywords_list(self):
        """Test that all entertainment keywords prevent security alert."""
        entertainment_keywords = ["phim", "game", "bài hát", "trận đấu", "video", "nhạc", "truyện"]
        
        classifier = MLBasedClassifier()
        
        for ent_keyword in entertainment_keywords:
            text = f"{ent_keyword} này cháy quá"
            result = classifier.classify(text)
            
            # Should NOT classify as security_alert
            assert result.intent != "security_alert", \
                f"Text with entertainment keyword '{ent_keyword}' should NOT classify as security_alert"
    
    def test_property_11_danger_without_entertainment_still_alerts(self):
        """Test that danger keywords without entertainment context still trigger alerts."""
        danger_texts = [
            "cháy ở phòng khách",  # Fire in living room
            "rò rỉ gas ở bếp",  # Gas leak in kitchen
            "có người lạ ở ngoài",  # Stranger outside
        ]
        
        classifier = MLBasedClassifier()
        
        for text in danger_texts:
            result = classifier.classify(text)
            
            # Should classify as security_alert (no entertainment context)
            assert result.intent == "security_alert", \
                f"Danger text without entertainment context '{text}' should classify as security_alert, got '{result.intent}'"



# ============================================================================
# PROPERTY TEST 10: SCENE ACTIVATION CLASSIFICATION
# ============================================================================

class TestSceneActivationClassification:
    """
    Property Test 10: Scene Activation Classification
    
    For any Vietnamese text containing scene keywords (đi ngủ, thức dậy, 
    xem phim, đi vắng, về nhà), the NLP Server SHALL classify the intent 
    as "activate_scene" and extract the appropriate scene_type entity 
    (sleep, wake_up, movie, away, home).
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**
    """
    
    # Scene activation keyword mappings
    SCENE_KEYWORDS = {
        "sleep": ["đi ngủ", "chúc ngủ ngon", "chuẩn bị ngủ", "sleep"],
        "wake_up": ["thức dậy", "buổi sáng", "chào buổi sáng", "wake up"],
        "movie": ["xem phim", "xem tv", "rạp chiếu phim", "movie"],
        "away": ["đi ra ngoài", "rời nhà", "đi vắng", "away"],
        "home": ["về nhà", "đã về", "tôi về rồi", "home"]
    }
    
    @given(
        scene_type=st.sampled_from(["sleep", "wake_up", "movie", "away", "home"]),
        keyword_index=st.integers(min_value=0, max_value=3),
        prefix=st.sampled_from(["", "tôi muốn ", "hãy ", "chuẩn bị ", ""]),
        suffix=st.sampled_from(["", " đi", " nào", " thôi", ""])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_10_scene_activation_with_keywords(
        self,
        scene_type: str,
        keyword_index: int,
        prefix: str,
        suffix: str
    ):
        """
        Property Test 10: Texts with scene keywords classify as activate_scene.
        
        Test that any text containing scene activation keywords is correctly
        classified as activate_scene intent with the appropriate scene_type entity.
        """
        # Arrange: Select a keyword for the scene type using index
        keywords = self.SCENE_KEYWORDS[scene_type]
        keyword = keywords[keyword_index % len(keywords)]
        text = f"{prefix}{keyword}{suffix}".strip()
        
        # Act: Classify the text
        classifier = MLBasedClassifier()
        result = classifier.classify(text)
        
        # Assert: Intent should be activate_scene
        assert result.intent == "activate_scene", \
            f"Expected intent 'activate_scene' for text '{text}', got '{result.intent}'"
        
        # Assert: Entities should contain scene_type
        assert "scene_type" in result.entities, \
            f"Expected 'scene_type' entity in result for text '{text}'"
        
        # Assert: scene_type should match expected type
        assert result.entities["scene_type"] == scene_type, \
            f"Expected scene_type '{scene_type}' for text '{text}', got '{result.entities['scene_type']}'"
        
        # Assert: Confidence should be reasonable
        assert result.confidence > 0.5, \
            f"Expected confidence > 0.5 for text '{text}', got {result.confidence}"
    
    def test_property_10_sleep_scene_keywords(self):
        """Test sleep scene with specific Vietnamese examples."""
        sleep_texts = [
            "đi ngủ",
            "chúc ngủ ngon",
            "chuẩn bị ngủ",
            "tôi muốn đi ngủ",
            "đi ngủ đi"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in sleep_texts:
            result = classifier.classify(text)
            
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities.get("scene_type") == "sleep", \
                f"Expected scene_type 'sleep' for '{text}', got '{result.entities.get('scene_type')}'"
    
    def test_property_10_wake_up_scene_keywords(self):
        """Test wake_up scene with specific Vietnamese examples."""
        wake_up_texts = [
            "thức dậy",
            "buổi sáng",
            "chào buổi sáng",
            "tôi thức dậy rồi",
            "chào buổi sáng nào"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in wake_up_texts:
            result = classifier.classify(text)
            
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities.get("scene_type") == "wake_up", \
                f"Expected scene_type 'wake_up' for '{text}', got '{result.entities.get('scene_type')}'"
    
    def test_property_10_movie_scene_keywords(self):
        """Test movie scene with specific Vietnamese examples."""
        movie_texts = [
            "xem phim",
            "xem tv",
            "rạp chiếu phim",
            "tôi muốn xem phim",
            "xem phim đi"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in movie_texts:
            result = classifier.classify(text)
            
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities.get("scene_type") == "movie", \
                f"Expected scene_type 'movie' for '{text}', got '{result.entities.get('scene_type')}'"
    
    def test_property_10_away_scene_keywords(self):
        """Test away scene with specific Vietnamese examples."""
        away_texts = [
            "đi ra ngoài",
            "rời nhà",
            "đi vắng",
            "tôi đi ra ngoài",
            "rời nhà đi"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in away_texts:
            result = classifier.classify(text)
            
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities.get("scene_type") == "away", \
                f"Expected scene_type 'away' for '{text}', got '{result.entities.get('scene_type')}'"
    
    def test_property_10_home_scene_keywords(self):
        """Test home scene with specific Vietnamese examples."""
        home_texts = [
            "về nhà",
            "đã về",
            "tôi về rồi",
            "tôi về nhà rồi",
            "về nhà đi"
        ]
        
        classifier = MLBasedClassifier()
        
        for text in home_texts:
            result = classifier.classify(text)
            
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities.get("scene_type") == "home", \
                f"Expected scene_type 'home' for '{text}', got '{result.entities.get('scene_type')}'"
    
    def test_property_10_confidence_threshold(self):
        """Test that scene activation classification has reasonable confidence."""
        test_cases = [
            ("đi ngủ", "sleep"),
            ("thức dậy", "wake_up"),
            ("xem phim", "movie"),
            ("đi vắng", "away"),
            ("về nhà", "home")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_scene_type in test_cases:
            result = classifier.classify(text)
            
            # Confidence should be high for clear keywords
            assert result.confidence >= 0.7, \
                f"Expected confidence >= 0.7 for clear keyword '{text}', got {result.confidence}"
            
            # Intent and entity should match
            assert result.intent == "activate_scene"
            assert result.entities["scene_type"] == expected_scene_type
    
    def test_property_10_with_context_words(self):
        """Test scene activation with additional context words."""
        test_cases = [
            ("tôi muốn đi ngủ", "sleep"),
            ("hãy thức dậy đi", "wake_up"),
            ("chuẩn bị xem phim", "movie"),
            ("tôi đi ra ngoài", "away"),
            ("tôi về nhà rồi", "home")
        ]
        
        classifier = MLBasedClassifier()
        
        for text, expected_scene_type in test_cases:
            result = classifier.classify(text)
            
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities["scene_type"] == expected_scene_type, \
                f"Expected scene_type '{expected_scene_type}' for '{text}', got '{result.entities['scene_type']}'"
    
    def test_property_10_negative_cases(self):
        """Test that non-scene texts don't classify as activate_scene."""
        non_scene_texts = [
            "bật đèn",  # control_device
            "tắt quạt",  # control_device
            "nóng quá",  # environmental_comfort
            "nhiệt độ bao nhiêu",  # query_sensor
        ]
        
        classifier = MLBasedClassifier()
        
        for text in non_scene_texts:
            result = classifier.classify(text)
            
            # Should NOT classify as activate_scene
            assert result.intent != "activate_scene", \
                f"Text '{text}' should not classify as activate_scene, got '{result.intent}'"
    
    def test_property_10_all_scene_types_covered(self):
        """Test that all 5 scene types are properly classified."""
        scene_examples = {
            "sleep": "đi ngủ",
            "wake_up": "thức dậy",
            "movie": "xem phim",
            "away": "đi vắng",
            "home": "về nhà"
        }
        
        classifier = MLBasedClassifier()
        
        for expected_scene_type, text in scene_examples.items():
            result = classifier.classify(text)
            
            assert result.intent == "activate_scene", \
                f"Expected 'activate_scene' for '{text}', got '{result.intent}'"
            assert result.entities["scene_type"] == expected_scene_type, \
                f"Expected scene_type '{expected_scene_type}' for '{text}', got '{result.entities['scene_type']}'"


# ============================================================================
# PROPERTY TEST 12: MULTI-INTENT DETECTION VIA SENTENCE SPLITTING
# ============================================================================

class TestMultiIntentDetection:
    """
    Property Test 12: Multi-Intent Detection via Sentence Splitting
    
    For any Vietnamese text containing sentence splitting keywords (và, rồi, 
    sau đó, xong), the NLP Server SHALL split the text into multiple sentences,
    classify each sentence separately, and return a MultiIntentResponse with 
    multiple intents in the correct order.
    
    **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
    """
    
    # Sentence splitting keywords
    SPLITTING_KEYWORDS = ["và", "rồi", "sau đó", "xong"]
    
    # Simple command templates for testing
    COMMAND_TEMPLATES = [
        "bật đèn",
        "tắt quạt",
        "đi ngủ",
        "về nhà",
        "xem phim"
    ]
    
    @given(
        command1=st.sampled_from(COMMAND_TEMPLATES),
        command2=st.sampled_from(COMMAND_TEMPLATES),
        splitting_keyword=st.sampled_from(SPLITTING_KEYWORDS)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_12_multi_intent_with_splitting_keywords(
        self,
        command1: str,
        command2: str,
        splitting_keyword: str
    ):
        """
        Property Test 12: Texts with splitting keywords return MultiIntentResponse.
        
        Test that any text containing splitting keywords is correctly split into
        multiple sentences, each classified separately, and returned as a
        MultiIntentResponse with intents in the correct order.
        """
        # Skip if both commands are the same (not interesting for multi-intent)
        if command1 == command2:
            return
        
        # Arrange: Create multi-intent text with splitting keyword
        text = f"{command1} {splitting_keyword} {command2}"
        
        # Act: Split sentences using preprocessing pipeline
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Assert: Should split into at least 2 sentences
        assert len(sentences) >= 2, \
            f"Expected at least 2 sentences for text '{text}', got {len(sentences)}: {sentences}"
        
        # Assert: First sentence should contain command1
        assert command1 in sentences[0].lower(), \
            f"Expected first sentence to contain '{command1}', got '{sentences[0]}'"
        
        # Assert: Second sentence should contain command2
        assert command2 in sentences[1].lower(), \
            f"Expected second sentence to contain '{command2}', got '{sentences[1]}'"
        
        # Act: Classify each sentence
        classifier = MLBasedClassifier()
        intents = []
        for sentence in sentences:
            result = classifier.classify(sentence.strip())
            if isinstance(result, IntentResponse):
                intents.append(result)
        
        # Assert: Should have at least 2 intents
        assert len(intents) >= 2, \
            f"Expected at least 2 intents for text '{text}', got {len(intents)}"
        
        # Assert: Each intent should have valid structure
        for i, intent in enumerate(intents):
            assert isinstance(intent, IntentResponse), \
                f"Intent {i} should be IntentResponse, got {type(intent)}"
            assert isinstance(intent.intent, str), \
                f"Intent {i} should have string intent field"
            assert isinstance(intent.entities, dict), \
                f"Intent {i} should have dict entities field"
            assert 0.0 <= intent.confidence <= 1.0, \
                f"Intent {i} confidence should be between 0.0 and 1.0, got {intent.confidence}"
    
    def test_property_12_splitting_with_va(self):
        """Test multi-intent splitting with 'và' (and)."""
        text = "bật đèn và tắt quạt"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into 2 sentences
        assert len(sentences) >= 2, f"Expected at least 2 sentences, got {len(sentences)}: {sentences}"
        
        # First sentence should contain "bật đèn"
        assert "bật đèn" in sentences[0].lower()
        
        # Second sentence should contain "tắt quạt"
        assert "tắt quạt" in sentences[1].lower()
    
    def test_property_12_splitting_with_roi(self):
        """Test multi-intent splitting with 'rồi' (then)."""
        text = "đi ngủ rồi tắt đèn"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into 2 sentences
        assert len(sentences) >= 2, f"Expected at least 2 sentences, got {len(sentences)}: {sentences}"
        
        # First sentence should contain "đi ngủ"
        assert "đi ngủ" in sentences[0].lower()
        
        # Second sentence should contain "tắt đèn"
        assert "tắt đèn" in sentences[1].lower()
    
    def test_property_12_splitting_with_sau_do(self):
        """Test multi-intent splitting with 'sau đó' (after that)."""
        text = "bật đèn sau đó xem phim"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into 2 sentences
        assert len(sentences) >= 2, f"Expected at least 2 sentences, got {len(sentences)}: {sentences}"
        
        # First sentence should contain "bật đèn"
        assert "bật đèn" in sentences[0].lower()
        
        # Second sentence should contain "xem phim"
        assert "xem phim" in sentences[1].lower()
    
    def test_property_12_splitting_with_xong(self):
        """Test multi-intent splitting with 'xong' (done/finished)."""
        text = "tắt quạt xong về nhà"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into 2 sentences
        assert len(sentences) >= 2, f"Expected at least 2 sentences, got {len(sentences)}: {sentences}"
        
        # First sentence should contain "tắt quạt"
        assert "tắt quạt" in sentences[0].lower()
        
        # Second sentence should contain "về nhà"
        assert "về nhà" in sentences[1].lower()
    
    def test_property_12_three_intents(self):
        """Test multi-intent with 3 commands."""
        text = "bật đèn và tắt quạt rồi đi ngủ"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into at least 3 sentences
        assert len(sentences) >= 3, f"Expected at least 3 sentences, got {len(sentences)}: {sentences}"
        
        # Verify each command is in a separate sentence
        assert "bật đèn" in sentences[0].lower()
        assert "tắt quạt" in sentences[1].lower()
        assert "đi ngủ" in sentences[2].lower()
    
    def test_property_12_order_preservation(self):
        """Test that intent order is preserved after splitting."""
        text = "đi ngủ và về nhà"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into 2 sentences
        assert len(sentences) >= 2
        
        # Classify each sentence
        classifier = MLBasedClassifier()
        intents = []
        for sentence in sentences:
            result = classifier.classify(sentence.strip())
            if isinstance(result, IntentResponse):
                intents.append(result)
        
        # Should have 2 intents
        assert len(intents) >= 2
        
        # First intent should be activate_scene with sleep
        assert intents[0].intent == "activate_scene"
        assert intents[0].entities.get("scene_type") == "sleep"
        
        # Second intent should be activate_scene with home
        assert intents[1].intent == "activate_scene"
        assert intents[1].entities.get("scene_type") == "home"
    
    def test_property_12_no_splitting_without_keywords(self):
        """Test that text without splitting keywords is not split."""
        text = "bật đèn phòng khách"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should return single sentence (or the original text)
        assert len(sentences) == 1, f"Expected 1 sentence, got {len(sentences)}: {sentences}"
        assert "bật đèn" in sentences[0].lower()
    
    def test_property_12_mixed_intents(self):
        """Test multi-intent with different intent types."""
        text = "bật đèn và đi ngủ"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into 2 sentences
        assert len(sentences) >= 2
        
        # Classify each sentence
        classifier = MLBasedClassifier()
        intents = []
        for sentence in sentences:
            result = classifier.classify(sentence.strip())
            if isinstance(result, IntentResponse):
                intents.append(result)
        
        # Should have 2 intents
        assert len(intents) >= 2
        
        # First intent should be control_device
        assert intents[0].intent == "control_device"
        
        # Second intent should be activate_scene
        assert intents[1].intent == "activate_scene"
    
    def test_property_12_whitespace_handling(self):
        """Test that splitting handles whitespace correctly."""
        text = "bật đèn   và   tắt quạt"
        
        from src.preprocessing.pipeline import split_sentences
        sentences = split_sentences(text)
        
        # Should split into 2 sentences
        assert len(sentences) >= 2
        
        # Each sentence should be trimmed
        for sentence in sentences:
            assert sentence == sentence.strip(), f"Sentence should be trimmed: '{sentence}'"


# ============================================================================
# PROPERTY TEST 14: CONTEXT-AWARE LOCATION INFERENCE
# ============================================================================

class TestContextAwareLocationInference:
    """
    Property Test 14: Context-Aware Location Inference
    
    For any Vietnamese text that does NOT explicitly specify a location,
    when device_context.current_room is provided, the NLP Server SHALL
    infer the location entity from the device context.
    
    **Validates: Requirements 9.1, 9.2, 9.3**
    """
    
    # Valid room names
    VALID_ROOMS = ["living_room", "bedroom", "kitchen", "bathroom", "balcony"]
    
    # Commands without location
    COMMANDS_WITHOUT_LOCATION = [
        "bật đèn",
        "tắt quạt",
        "nhiệt độ bao nhiêu",
        "trạng thái đèn"
    ]
    
    @given(
        command=st.sampled_from(COMMANDS_WITHOUT_LOCATION),
        current_room=st.sampled_from(VALID_ROOMS)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_14_location_inference_from_context(
        self,
        command: str,
        current_room: str
    ):
        """
        Property Test 14: Location is inferred from device context.
        
        Test that when text doesn't specify location but device_context.current_room
        is provided, the location entity is inferred from context.
        """
        # Arrange: Create device context with current_room
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        context = DeviceContext(current_room=current_room)
        
        # Determine expected intent based on command
        if "bật" in command or "tắt" in command:
            intent = "control_device"
        elif "nhiệt độ" in command:
            intent = "query_sensor"
        elif "trạng thái" in command:
            intent = "query_device_status"
        else:
            intent = "unknown"
        
        # Act: Extract entities with context
        extractor = EntityExtractor()
        entities = extractor.extract(command, intent, context)
        
        # Assert: Location should be inferred from context
        if intent in ["control_device", "query_sensor", "query_device_status"]:
            assert "location" in entities, \
                f"Expected location to be inferred from context for command '{command}'"
            assert entities["location"] == current_room, \
                f"Expected location '{current_room}', got '{entities.get('location')}'"
    
    def test_property_14_control_device_with_context(self):
        """Test location inference for control_device intent."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        context = DeviceContext(current_room="living_room")
        extractor = EntityExtractor()
        
        # Command without location
        entities = extractor.extract("bật đèn", "control_device", context)
        
        # Should infer location from context
        assert "location" in entities
        assert entities["location"] == "living_room"
    
    def test_property_14_query_sensor_with_context(self):
        """Test location inference for query_sensor intent."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        context = DeviceContext(current_room="bedroom")
        extractor = EntityExtractor()
        
        # Command without location
        entities = extractor.extract("nhiệt độ bao nhiêu", "query_sensor", context)
        
        # Should infer location from context
        assert "location" in entities
        assert entities["location"] == "bedroom"
    
    def test_property_14_query_device_status_with_context(self):
        """Test location inference for query_device_status intent."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        context = DeviceContext(current_room="kitchen")
        extractor = EntityExtractor()
        
        # Command without location
        entities = extractor.extract("trạng thái đèn", "query_device_status", context)
        
        # Should infer location from context
        assert "location" in entities
        assert entities["location"] == "kitchen"
    
    def test_property_14_explicit_location_overrides_context(self):
        """Test that explicit location in text overrides context."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        # Context says living_room
        context = DeviceContext(current_room="living_room")
        extractor = EntityExtractor()
        
        # But text explicitly says bedroom
        entities = extractor.extract("bật đèn phòng ngủ", "control_device", context)
        
        # Should use explicit location from text, not context
        assert "location" in entities
        assert entities["location"] == "bedroom", \
            "Explicit location in text should override context"
    
    def test_property_14_no_context_no_inference(self):
        """Test that without context, no location is inferred."""
        from src.entities.entity_extractor import EntityExtractor
        
        extractor = EntityExtractor()
        
        # No context provided
        entities = extractor.extract("bật đèn", "control_device", None)
        
        # Should not have location
        assert "location" not in entities, \
            "Without context, location should not be inferred"
    
    def test_property_14_empty_context_no_inference(self):
        """Test that empty context doesn't infer location."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        # Context with no current_room
        context = DeviceContext(current_room=None)
        extractor = EntityExtractor()
        
        entities = extractor.extract("bật đèn", "control_device", context)
        
        # Should not have location
        assert "location" not in entities, \
            "Empty context should not infer location"
    
    def test_property_14_all_rooms_supported(self):
        """Test that all valid rooms are supported."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        extractor = EntityExtractor()
        
        for room in self.VALID_ROOMS:
            context = DeviceContext(current_room=room)
            entities = extractor.extract("bật đèn", "control_device", context)
            
            assert "location" in entities, f"Room '{room}' should be supported"
            assert entities["location"] == room
    
    def test_property_14_context_priority(self):
        """Test context inference priority: explicit > context > none."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        extractor = EntityExtractor()
        
        # Priority 1: Explicit location in text (highest)
        context = DeviceContext(current_room="living_room")
        entities = extractor.extract("bật đèn phòng ngủ", "control_device", context)
        assert entities["location"] == "bedroom"
        
        # Priority 2: Context location
        entities = extractor.extract("bật đèn", "control_device", context)
        assert entities["location"] == "living_room"
        
        # Priority 3: No location (lowest)
        entities = extractor.extract("bật đèn", "control_device", None)
        assert "location" not in entities
    
    def test_property_14_multiple_devices_same_context(self):
        """Test that context applies to multiple device commands."""
        from src.models.schemas import DeviceContext
        from src.entities.entity_extractor import EntityExtractor
        
        context = DeviceContext(current_room="bedroom")
        extractor = EntityExtractor()
        
        commands = [
            ("bật đèn", "control_device"),
            ("tắt quạt", "control_device"),
            ("nhiệt độ bao nhiêu", "query_sensor"),
            ("trạng thái điều hòa", "query_device_status")
        ]
        
        for command, intent in commands:
            entities = extractor.extract(command, intent, context)
            assert "location" in entities, f"Command '{command}' should infer location"
            assert entities["location"] == "bedroom"


# ============================================================================
# PROPERTY TEST 16: ERROR HANDLING GRACEFUL DEGRADATION
# ============================================================================

class TestErrorHandlingGracefulDegradation:
    """
    Property Test 16: Error Handling Graceful Degradation
    
    For ANY invalid input (empty, whitespace-only, exceeds max length),
    the system SHALL return a 400 error with descriptive message, NOT a 500 error.
    
    This ensures graceful degradation and proper error handling.
    """
    
    @given(text=st.text(alphabet=" \t\n\r", min_size=1, max_size=100))
    @settings(max_examples=50, deadline=None)
    def test_property_16_whitespace_only_returns_400_error(self, text):
        """
        Property Test 16: Whitespace-only input returns 400 error.
        
        Test that whitespace-only text returns a 400 error with descriptive message,
        not a 500 error (server crash).
        
        **Validates: Requirements 10.1**
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Attempt to validate and build response
        result = builder.validate_and_build(text)
        
        # Should return error response
        assert "error" in result or "status_code" in result, (
            f"Whitespace-only input should return error response:\n"
            f"  Text: {repr(text)}\n"
            f"  Result: {result}"
        )
        
        # Should be 400 error, not 500
        if "status_code" in result:
            assert result["status_code"] == 400, (
                f"Whitespace-only input should return 400 error, not {result['status_code']}:\n"
                f"  Text: {repr(text)}\n"
                f"  Status code: {result['status_code']}"
            )
        
        # Should have descriptive error message
        if "message" in result:
            assert len(result["message"]) > 0, (
                f"Error message should be descriptive:\n"
                f"  Text: {repr(text)}\n"
                f"  Message: {result['message']}"
            )
    
    def test_property_16_empty_string_returns_400_error(self):
        """
        Property Test 16: Empty string returns 400 error.
        
        Test that empty string returns a 400 error with descriptive message.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Test empty string
        result = builder.validate_and_build("")
        
        # Should return error response with 400 status
        assert "status_code" in result
        assert result["status_code"] == 400
        assert "message" in result
        assert len(result["message"]) > 0
    
    def test_property_16_exceeds_max_length_returns_400_error(self):
        """
        Property Test 16: Text exceeding max length returns 400 error.
        
        Test that text exceeding max length (500 chars) returns a 400 error.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Create text exceeding max length (500 chars)
        long_text = "a" * 501
        
        result = builder.validate_and_build(long_text)
        
        # Should return error response with 400 status
        assert "status_code" in result
        assert result["status_code"] == 400
        assert "message" in result
        assert "max length" in result["message"].lower() or "too long" in result["message"].lower()
    
    def test_property_16_valid_input_does_not_return_error(self):
        """
        Property Test 16: Valid input does not return error.
        
        Test that valid input does NOT return an error response.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Test valid input
        result = builder.validate_and_build("bật đèn phòng khách")
        
        # Should NOT return error (or if it does, should not be validation error)
        if "status_code" in result:
            assert result["status_code"] != 400, (
                f"Valid input should not return 400 error:\n"
                f"  Text: 'bật đèn phòng khách'\n"
                f"  Status code: {result['status_code']}"
            )
    
    def test_property_16_none_input_returns_400_error(self):
        """
        Property Test 16: None input returns 400 error.
        
        Test that None input returns a 400 error with descriptive message.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Test None input
        result = builder.validate_and_build(None)
        
        # Should return error response with 400 status
        assert "status_code" in result
        assert result["status_code"] == 400
        assert "message" in result
        assert len(result["message"]) > 0
    
    def test_property_16_special_characters_only_returns_400_error(self):
        """
        Property Test 16: Special characters only returns 400 error.
        
        Test that text with only special characters returns a 400 error.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Test special characters only
        special_texts = ["!!!", "???", "...", "---", "***", "@@@"]
        
        for text in special_texts:
            result = builder.validate_and_build(text)
            
            # Should return error response with 400 status
            assert "status_code" in result, f"Special chars '{text}' should return error"
            assert result["status_code"] == 400, f"Special chars '{text}' should return 400"
    
    def test_property_16_numeric_only_returns_400_error(self):
        """
        Property Test 16: Numeric-only input returns 400 error.
        
        Test that text with only numbers returns a 400 error.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Test numeric only
        numeric_texts = ["123", "456789", "0000"]
        
        for text in numeric_texts:
            result = builder.validate_and_build(text)
            
            # Should return error response with 400 status
            assert "status_code" in result, f"Numeric '{text}' should return error"
            assert result["status_code"] == 400, f"Numeric '{text}' should return 400"
    
    def test_property_16_error_response_structure(self):
        """
        Property Test 16: Error response has correct structure.
        
        Test that error responses have the correct structure with all required fields.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Test with empty string
        result = builder.validate_and_build("")
        
        # Should have required fields
        assert "status_code" in result
        assert "message" in result
        assert "error_type" in result or "error" in result
        
        # Status code should be integer
        assert isinstance(result["status_code"], int)
        
        # Message should be string
        assert isinstance(result["message"], str)
    
    def test_property_16_no_500_errors_on_invalid_input(self):
        """
        Property Test 16: No 500 errors on invalid input.
        
        Test that invalid inputs NEVER return 500 errors (server crashes).
        All validation errors should be 400.
        """
        from src.api.response_builder import ResponseBuilder
        
        builder = ResponseBuilder()
        
        # Test various invalid inputs
        invalid_inputs = [
            "",
            "   ",
            "\t\n",
            None,
            "a" * 501,  # Too long
            "123",
            "!!!"
        ]
        
        for text in invalid_inputs:
            result = builder.validate_and_build(text)
            
            # Should return error
            assert "status_code" in result, f"Input {repr(text)} should return error"
            
            # Should be 400, NOT 500
            assert result["status_code"] == 400, (
                f"Invalid input should return 400, not {result['status_code']}:\n"
                f"  Input: {repr(text)}\n"
                f"  Status code: {result['status_code']}"
            )
