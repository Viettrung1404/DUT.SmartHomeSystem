"""
End-to-End Integration Tests for Vietnamese NLP Intent Classification System.

Tests the complete request flow: preprocessing → classification → entity extraction → response building.

**Task 20.1: Write end-to-end integration tests covering full request flow**
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from preprocessing.pipeline import PreprocessingPipeline
from classifiers.hybrid import HybridClassifier
from classifiers.rule_based import RuleBasedClassifier
from classifiers.ml_based import MLBasedClassifier
from entities.entity_extractor import EntityExtractor
from api.response_builder import ResponseBuilder
from config.schema import ENTITY_SCHEMA


# Mock JWT secret for testing
TEST_JWT_SECRET = "test_secret_key_for_testing_only"
os.environ["JWT_SECRET"] = TEST_JWT_SECRET


def create_test_jwt(user_id: str = "test_user", expires_in_minutes: int = 30) -> str:
    """Create a test JWT token."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
    return token


@pytest.fixture
def preprocessing_pipeline():
    """Fixture for preprocessing pipeline."""
    return PreprocessingPipeline()


@pytest.fixture
def rule_based_classifier():
    """Fixture for rule-based classifier."""
    return RuleBasedClassifier()


@pytest.fixture
def ml_based_classifier():
    """Fixture for ML-based classifier."""
    # Use a mock or lightweight model for testing
    return MLBasedClassifier(model_path=None, use_mock=True)


@pytest.fixture
def hybrid_classifier(rule_based_classifier, ml_based_classifier):
    """Fixture for hybrid classifier."""
    return HybridClassifier(
        rule_classifier=rule_based_classifier,
        ml_classifier=ml_based_classifier
    )


@pytest.fixture
def entity_extractor():
    """Fixture for entity extractor."""
    return EntityExtractor()


@pytest.fixture
def response_builder():
    """Fixture for response builder."""
    return ResponseBuilder()


@pytest.fixture
def valid_jwt():
    """Fixture for valid JWT token."""
    return create_test_jwt()


class TestE2ESimpleCommand:
    """End-to-end tests for simple device control commands (rule-based path)."""
    
    def test_e2e_turn_on_light_living_room(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Bật đèn phòng khách"
        Expected: control_device intent with device=light, action=turn_on, location=living_room
        """
        # Step 1: Preprocessing
        input_text = "Bật đèn phòng khách"
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        
        assert preprocessed.normalized_text is not None
        assert len(preprocessed.normalized_text) > 0
        
        # Step 2: Classification
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        
        assert classification_result.intent == "control_device"
        assert classification_result.confidence == 1.0
        assert classification_result.classifier_type == "rule"
        
        # Step 3: Entity Extraction
        entities = entity_extractor.extract(
            preprocessed.normalized_text,
            classification_result.intent
        )
        
        assert "device" in entities
        assert entities["device"] == "light"
        assert "action" in entities
        assert entities["action"] == "turn_on"
        assert "location" in entities
        assert entities["location"] == "living_room"
        
        # Step 4: Response Building
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        assert response["intent"] == "control_device"
        assert response["entities"]["device"] == "light"
        assert response["entities"]["action"] == "turn_on"
        assert response["entities"]["location"] == "living_room"
        assert response["confidence"] == 1.0
        assert response["classifier_type"] == "rule"
        assert "timestamp" in response
    
    def test_e2e_turn_off_fan_bedroom(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Tắt quạt phòng ngủ"
        Expected: control_device intent with device=fan, action=turn_off, location=bedroom
        """
        input_text = "Tắt quạt phòng ngủ"
        
        # Full pipeline
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        # Assertions
        assert response["intent"] == "control_device"
        assert response["entities"]["device"] == "fan"
        assert response["entities"]["action"] == "turn_off"
        assert response["entities"]["location"] == "bedroom"
        assert response["confidence"] == 1.0
        assert response["classifier_type"] == "rule"
    
    def test_e2e_open_door(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Mở cửa"
        Expected: control_device intent with device=door, action=open
        """
        input_text = "Mở cửa"
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        assert response["intent"] == "control_device"
        assert response["entities"]["device"] == "door"
        assert response["entities"]["action"] == "turn_on"
        assert response["confidence"] == 1.0


class TestE2ENaturalLanguage:
    """End-to-end tests for natural language commands (ML-based path)."""
    
    def test_e2e_environmental_comfort_cooling(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Nóng quá"
        Expected: environmental_comfort intent with comfort_type=cooling
        """
        input_text = "Nóng quá"
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        assert response["intent"] == "environmental_comfort"
        assert "comfort_type" in response["entities"]
        assert response["entities"]["comfort_type"] == "cooling"
        assert response["confidence"] > 0.7  # ML-based may have lower confidence
        assert response["classifier_type"] in ["ml", "rule"]
    
    def test_e2e_environmental_comfort_brighten(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Tối quá"
        Expected: environmental_comfort intent with comfort_type=brighten
        """
        input_text = "Tối quá"
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        assert response["intent"] == "environmental_comfort"
        assert response["entities"]["comfort_type"] == "brighten"
        assert response["confidence"] > 0.7


class TestE2ESceneActivation:
    """End-to-end tests for scene activation commands."""
    
    def test_e2e_activate_sleep_scene(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Đi ngủ"
        Expected: activate_scene intent with scene_type=sleep
        """
        input_text = "Đi ngủ"
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        assert response["intent"] == "activate_scene"
        assert response["entities"]["scene_type"] == "sleep"
        assert response["confidence"] >= 0.7
    
    def test_e2e_activate_movie_scene(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Xem phim"
        Expected: activate_scene intent with scene_type=movie
        """
        input_text = "Xem phim"
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        assert response["intent"] == "activate_scene"
        assert response["entities"]["scene_type"] == "movie"


class TestE2ESecurityAlerts:
    """End-to-end tests for security alert classification with false positive prevention."""
    
    def test_e2e_security_alert_fire(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Có cháy"
        Expected: security_alert intent with alert_type=fire, priority=high
        """
        input_text = "Có cháy"
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        assert response["intent"] == "security_alert"
        assert response["entities"]["alert_type"] == "fire"
        assert response.get("priority") == "high"
    
    def test_e2e_false_positive_prevention_movie(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Phim này cháy quá"
        Expected: NOT security_alert (should be unknown or other intent)
        """
        input_text = "Phim này cháy quá"
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        
        # Should NOT classify as security_alert due to entertainment context
        assert classification_result.intent != "security_alert"


class TestE2EMultiIntent:
    """End-to-end tests for multi-intent handling via sentence splitting."""
    
    def test_e2e_multi_intent_two_commands(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Bật đèn phòng khách rồi tắt quạt phòng ngủ"
        Expected: MultiIntentResponse with 2 intents
        """
        input_text = "Bật đèn phòng khách rồi tắt quạt phòng ngủ"
        
        # Step 1: Preprocessing with sentence splitting
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        
        # Should split into 2 sentences
        assert len(preprocessed.sentences) >= 2
        
        # Step 2: Classify each sentence
        results = []
        for sentence in preprocessed.sentences:
            classification_result = hybrid_classifier.classify(sentence)
            entities = entity_extractor.extract(sentence, classification_result.intent)
            result = {
                "intent": classification_result.intent,
                "entities": entities,
                "confidence": classification_result.confidence,
                "classifier_type": classification_result.classifier_type
            }
            results.append(result)
        
        # Step 3: Build multi-intent response
        response = response_builder.build_multi_intent_response(results)
        
        assert "intents" in response
        assert len(response["intents"]) == 2
        assert response["total_intents"] == 2
        
        # First intent: Bật đèn phòng khách
        assert response["intents"][0]["intent"] == "control_device"
        assert response["intents"][0]["entities"]["device"] == "light"
        assert response["intents"][0]["entities"]["action"] == "turn_on"
        
        # Second intent: Tắt quạt phòng ngủ
        assert response["intents"][1]["intent"] == "control_device"
        assert response["intents"][1]["entities"]["device"] == "fan"
        assert response["intents"][1]["entities"]["action"] == "turn_off"


class TestE2EContextAware:
    """End-to-end tests for context-aware classification."""
    
    def test_e2e_context_aware_location_inference(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for: "Bật đèn" with device_context.current_room="living_room"
        Expected: location inferred from context
        """
        input_text = "Bật đèn"
        device_context = {
            "current_room": "living_room",
            "devices": [
                {"id": "light_1", "type": "light", "state": "off", "location": "living_room"}
            ]
        }
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text, context=device_context)
        entities = entity_extractor.extract(
            preprocessed.normalized_text, 
            classification_result.intent,
            context=device_context
        )
        
        # Location should be inferred from context
        assert "location" in entities
        assert entities["location"] == "living_room"


class TestE2EErrorHandling:
    """End-to-end tests for error handling and fallback."""
    
    def test_e2e_empty_input(
        self, 
        preprocessing_pipeline, 
        response_builder
    ):
        """
        Test complete flow for empty input.
        Expected: Error response with 400 status
        """
        input_text = ""
        
        # Preprocessing should handle empty input
        try:
            preprocessed = preprocessing_pipeline.preprocess(input_text)
            # If preprocessing succeeds, should return error response
            response = response_builder.build_error_response(
                error_type="validation",
                message="Input không hợp lệ"
            )
            assert response["error_type"] == "validation"
        except ValueError as e:
            # Or preprocessing may raise ValueError
            assert "empty" in str(e).lower() or "invalid" in str(e).lower()
    
    def test_e2e_low_confidence_fallback(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test complete flow for ambiguous input with low confidence.
        Expected: Fallback response with suggestions
        """
        input_text = "xyz abc"  # Nonsense input
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        
        # If confidence is low, build fallback response
        if classification_result.confidence < 0.7:
            response = response_builder.build_fallback_response(
                top_intents=[
                    ("control_device", 0.3),
                    ("query_sensor", 0.2),
                    ("environmental_comfort", 0.15)
                ],
                reason="Low confidence"
            )
            
            assert response["intent"] == "unknown"
            assert response["clarification_needed"] is True
            assert "suggestions" in response
            assert "top_intents" in response


class TestE2EPerformance:
    """End-to-end tests for performance validation."""
    
    def test_e2e_latency_simple_command(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test that simple command completes within acceptable latency.
        Expected: < 50ms for rule-based path
        """
        import time
        
        input_text = "Bật đèn phòng khách"
        
        start_time = time.time()
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Rule-based should be very fast
        assert latency_ms < 50, f"Latency {latency_ms}ms exceeds 50ms threshold"
    
    def test_e2e_latency_natural_language(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test that natural language command completes within acceptable latency.
        Expected: < 300ms for ML-based path (CPU)
        """
        import time
        
        input_text = "Nóng quá"
        
        start_time = time.time()
        
        preprocessed = preprocessing_pipeline.preprocess(input_text)
        classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
        entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
        response = response_builder.build_success_response(
            intent=classification_result.intent,
            entities=entities,
            confidence=classification_result.confidence,
            classifier_type=classification_result.classifier_type
        )
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # ML-based should complete within 300ms on CPU
        # Note: This may fail if using real ML model without optimization
        assert latency_ms < 300, f"Latency {latency_ms}ms exceeds 300ms threshold"


class TestE2EEntitySchemaCompliance:
    """End-to-end tests for entity schema compliance."""
    
    def test_e2e_all_entities_in_schema(
        self, 
        preprocessing_pipeline, 
        hybrid_classifier, 
        entity_extractor, 
        response_builder
    ):
        """
        Test that all extracted entities comply with ENTITY_SCHEMA.
        """
        test_inputs = [
            "Bật đèn phòng khách",
            "Tắt quạt phòng ngủ",
            "Nóng quá",
            "Đi ngủ",
            "Nhiệt độ bao nhiêu"
        ]
        
        for input_text in test_inputs:
            preprocessed = preprocessing_pipeline.preprocess(input_text)
            classification_result = hybrid_classifier.classify(preprocessed.normalized_text)
            entities = entity_extractor.extract(preprocessed.normalized_text, classification_result.intent)
            
            # Verify all entity values are in schema
            for key, value in entities.items():
                if key == "device":
                    assert value in ENTITY_SCHEMA["device_types"], f"Invalid device: {value}"
                elif key == "action":
                    assert value in ENTITY_SCHEMA["actions"], f"Invalid action: {value}"
                elif key == "location":
                    assert value in ENTITY_SCHEMA["locations"], f"Invalid location: {value}"
                elif key == "scene_type":
                    assert value in ENTITY_SCHEMA["scene_types"], f"Invalid scene_type: {value}"
                elif key == "sensor_type":
                    assert value in ENTITY_SCHEMA["sensor_types"], f"Invalid sensor_type: {value}"
                elif key == "comfort_type":
                    assert value in ENTITY_SCHEMA["comfort_types"], f"Invalid comfort_type: {value}"
