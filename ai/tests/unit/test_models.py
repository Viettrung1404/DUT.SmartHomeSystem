"""
Unit tests for Pydantic models.

Tests all request and response models for the Vietnamese NLP Intent Classification API:
- IntentClassificationRequest
- IntentResponse
- FallbackResponse
- MultiIntentResponse
- ErrorResponse
- DeviceContext
- DeviceState

Test categories:
- Valid data tests (should pass validation)
- Invalid data tests (should raise ValidationError)
- Boundary tests (min/max values)
- Optional field tests (with and without optional fields)
- Nested model tests (DeviceContext, DeviceState)
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from typing import Dict, Any, List


# Import models (these will be implemented in Task 2.2)
# For now, we'll define placeholder imports that will be replaced
try:
    from src.models.schemas import (
        DeviceState,
        DeviceContext,
        IntentClassificationRequest,
        IntentResponse,
        FallbackResponse,
        MultiIntentResponse,
        ErrorResponse,
    )
except ImportError:
    # Models not yet implemented - tests will be skipped
    pytest.skip("Models not yet implemented", allow_module_level=True)


class TestDeviceState:
    """Test DeviceState model validation."""
    
    def test_device_state_valid_minimal(self):
        """Test DeviceState with minimal required fields."""
        device = DeviceState(
            id="light_1",
            type="light",
            state="on"
        )
        
        assert device.id == "light_1"
        assert device.type == "light"
        assert device.state == "on"
        assert device.location is None
        assert device.attributes is None
    
    def test_device_state_valid_complete(self):
        """Test DeviceState with all fields."""
        device = DeviceState(
            id="light_1",
            type="light",
            state="on",
            location="living_room",
            attributes={"brightness": 80, "color": "warm_white"}
        )
        
        assert device.id == "light_1"
        assert device.type == "light"
        assert device.state == "on"
        assert device.location == "living_room"
        assert device.attributes == {"brightness": 80, "color": "warm_white"}
    
    def test_device_state_missing_required_fields(self):
        """Test DeviceState fails without required fields."""
        with pytest.raises(ValidationError) as exc_info:
            DeviceState(id="light_1", type="light")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("state",) for error in errors)
    
    def test_device_state_empty_id(self):
        """Test DeviceState fails with empty id."""
        with pytest.raises(ValidationError):
            DeviceState(id="", type="light", state="on")
    
    def test_device_state_various_types(self):
        """Test DeviceState with various device types."""
        device_types = ["light", "fan", "ac", "door", "awning", "lock", "curtain", "camera"]
        
        for device_type in device_types:
            device = DeviceState(
                id=f"{device_type}_1",
                type=device_type,
                state="on"
            )
            assert device.type == device_type


class TestDeviceContext:
    """Test DeviceContext model validation."""
    
    def test_device_context_empty(self):
        """Test DeviceContext with no devices."""
        context = DeviceContext()
        
        assert context.current_room is None
        assert context.devices == []
        assert context.time_of_day is None
    
    def test_device_context_with_room(self):
        """Test DeviceContext with current room."""
        context = DeviceContext(current_room="living_room")
        
        assert context.current_room == "living_room"
        assert context.devices == []
    
    def test_device_context_with_devices(self):
        """Test DeviceContext with device list."""
        devices = [
            DeviceState(id="light_1", type="light", state="off", location="living_room"),
            DeviceState(id="fan_1", type="fan", state="on", location="living_room")
        ]
        
        context = DeviceContext(
            current_room="living_room",
            devices=devices,
            time_of_day="evening"
        )
        
        assert context.current_room == "living_room"
        assert len(context.devices) == 2
        assert context.devices[0].id == "light_1"
        assert context.devices[1].id == "fan_1"
        assert context.time_of_day == "evening"
    
    def test_device_context_time_of_day_values(self):
        """Test DeviceContext with various time_of_day values."""
        time_values = ["morning", "afternoon", "evening", "night"]
        
        for time_value in time_values:
            context = DeviceContext(time_of_day=time_value)
            assert context.time_of_day == time_value
    
    def test_device_context_invalid_device(self):
        """Test DeviceContext fails with invalid device data."""
        with pytest.raises(ValidationError):
            DeviceContext(
                devices=[
                    {"id": "light_1", "type": "light"}  # Missing required 'state' field
                ]
            )


class TestIntentClassificationRequest:
    """Test IntentClassificationRequest model validation."""
    
    def test_request_valid_minimal(self):
        """Test request with only required field (text)."""
        request = IntentClassificationRequest(text="Bật đèn phòng khách")
        
        assert request.text == "Bật đèn phòng khách"
        assert request.user_id is None
        assert request.home_id is None
        assert request.device_context is None
    
    def test_request_valid_complete(self):
        """Test request with all fields."""
        request = IntentClassificationRequest(
            text="Bật đèn phòng khách",
            user_id="user_123",
            home_id="home_456",
            device_context=DeviceContext(
                current_room="living_room",
                devices=[
                    DeviceState(id="light_1", type="light", state="off", location="living_room")
                ]
            )
        )
        
        assert request.text == "Bật đèn phòng khách"
        assert request.user_id == "user_123"
        assert request.home_id == "home_456"
        assert request.device_context is not None
        assert request.device_context.current_room == "living_room"
    
    def test_request_text_min_length(self):
        """Test request with minimum valid text length (1 character)."""
        request = IntentClassificationRequest(text="a")
        assert request.text == "a"
    
    def test_request_text_max_length(self):
        """Test request with maximum valid text length (500 characters)."""
        long_text = "a" * 500
        request = IntentClassificationRequest(text=long_text)
        assert len(request.text) == 500
    
    def test_request_text_empty_fails(self):
        """Test request fails with empty text."""
        with pytest.raises(ValidationError) as exc_info:
            IntentClassificationRequest(text="")
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("text",) for error in errors)
    
    def test_request_text_too_long_fails(self):
        """Test request fails with text exceeding max length."""
        long_text = "a" * 501
        
        with pytest.raises(ValidationError) as exc_info:
            IntentClassificationRequest(text=long_text)
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("text",) for error in errors)
    
    def test_request_missing_text_fails(self):
        """Test request fails without text field."""
        with pytest.raises(ValidationError) as exc_info:
            IntentClassificationRequest()
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("text",) for error in errors)
    
    def test_request_with_vietnamese_text(self):
        """Test request with various Vietnamese text inputs."""
        vietnamese_texts = [
            "Bật đèn phòng khách",
            "Tắt quạt phòng ngủ",
            "Điều hòa 25 độ",
            "Mở cửa ra vào",
            "Trời nóng quá"
        ]
        
        for text in vietnamese_texts:
            request = IntentClassificationRequest(text=text)
            assert request.text == text
    
    def test_request_example_data(self):
        """Test request with example data from schema_extra."""
        request = IntentClassificationRequest(
            text="Bật đèn phòng khách",
            user_id="user_123",
            home_id="home_456",
            device_context=DeviceContext(
                current_room="living_room",
                devices=[
                    DeviceState(id="light_1", type="light", state="off", location="living_room"),
                    DeviceState(id="fan_1", type="fan", state="on", location="living_room")
                ]
            )
        )
        
        assert request.text == "Bật đèn phòng khách"
        assert request.user_id == "user_123"
        assert request.home_id == "home_456"
        assert len(request.device_context.devices) == 2


class TestIntentResponse:
    """Test IntentResponse model validation."""
    
    def test_response_valid_minimal(self):
        """Test response with minimal required fields."""
        response = IntentResponse(
            intent="control_device",
            confidence=0.95,
            classifier_type="rule"
        )
        
        assert response.intent == "control_device"
        assert response.entities == {}
        assert response.confidence == 0.95
        assert isinstance(response.timestamp, datetime)
        assert response.classifier_type == "rule"
        assert response.priority is None
    
    def test_response_valid_complete(self):
        """Test response with all fields."""
        response = IntentResponse(
            intent="control_device",
            entities={"device": "light", "action": "turn_on", "location": "living_room"},
            confidence=1.0,
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            classifier_type="rule",
            priority="high"
        )
        
        assert response.intent == "control_device"
        assert response.entities == {"device": "light", "action": "turn_on", "location": "living_room"}
        assert response.confidence == 1.0
        assert response.timestamp == datetime(2024, 1, 15, 10, 30, 0)
        assert response.classifier_type == "rule"
        assert response.priority == "high"
    
    def test_response_confidence_boundaries(self):
        """Test response with confidence at boundaries (0.0 and 1.0)."""
        # Minimum confidence
        response_min = IntentResponse(
            intent="unknown",
            confidence=0.0,
            classifier_type="ml"
        )
        assert response_min.confidence == 0.0
        
        # Maximum confidence
        response_max = IntentResponse(
            intent="control_device",
            confidence=1.0,
            classifier_type="rule"
        )
        assert response_max.confidence == 1.0
    
    def test_response_confidence_below_zero_fails(self):
        """Test response fails with confidence below 0.0."""
        with pytest.raises(ValidationError) as exc_info:
            IntentResponse(
                intent="control_device",
                confidence=-0.1,
                classifier_type="rule"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("confidence",) for error in errors)
    
    def test_response_confidence_above_one_fails(self):
        """Test response fails with confidence above 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            IntentResponse(
                intent="control_device",
                confidence=1.1,
                classifier_type="rule"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("confidence",) for error in errors)
    
    def test_response_missing_required_fields(self):
        """Test response fails without required fields."""
        with pytest.raises(ValidationError) as exc_info:
            IntentResponse(intent="control_device")
        
        errors = exc_info.value.errors()
        field_names = [error["loc"][0] for error in errors]
        assert "confidence" in field_names
        assert "classifier_type" in field_names
    
    def test_response_classifier_types(self):
        """Test response with different classifier types."""
        classifier_types = ["rule", "ml"]
        
        for classifier_type in classifier_types:
            response = IntentResponse(
                intent="control_device",
                confidence=0.9,
                classifier_type=classifier_type
            )
            assert response.classifier_type == classifier_type
    
    def test_response_various_intents(self):
        """Test response with various intent types."""
        intents = [
            "control_device",
            "query_sensor",
            "environmental_comfort",
            "scene_activation",
            "security_alert",
            "unknown"
        ]
        
        for intent in intents:
            response = IntentResponse(
                intent=intent,
                confidence=0.85,
                classifier_type="ml"
            )
            assert response.intent == intent
    
    def test_response_example_data(self):
        """Test response with example data from schema_extra."""
        response = IntentResponse(
            intent="control_device",
            entities={
                "device": "light",
                "action": "turn_on",
                "location": "living_room"
            },
            confidence=1.0,
            classifier_type="rule",
            priority=None
        )
        
        assert response.intent == "control_device"
        assert response.entities["device"] == "light"
        assert response.entities["action"] == "turn_on"
        assert response.entities["location"] == "living_room"
        assert response.confidence == 1.0


class TestFallbackResponse:
    """Test FallbackResponse model validation."""
    
    def test_fallback_response_minimal(self):
        """Test fallback response with minimal fields."""
        response = FallbackResponse(confidence=0.45)
        
        assert response.intent == "unknown"
        assert response.entities == {}
        assert response.confidence == 0.45
        assert isinstance(response.timestamp, datetime)
        assert response.clarification_needed is True
        assert response.suggestions == []
        assert response.top_intents == []
    
    def test_fallback_response_complete(self):
        """Test fallback response with all fields."""
        response = FallbackResponse(
            intent="unknown",
            entities={},
            confidence=0.45,
            clarification_needed=True,
            suggestions=[
                "Bạn muốn bật thiết bị nào?",
                "Bạn muốn kiểm tra cảm biến nào?"
            ],
            top_intents=[
                {"intent": "control_device", "confidence": 0.45},
                {"intent": "query_sensor", "confidence": 0.32},
                {"intent": "environmental_comfort", "confidence": 0.23}
            ]
        )
        
        assert response.intent == "unknown"
        assert response.confidence == 0.45
        assert response.clarification_needed is True
        assert len(response.suggestions) == 2
        assert len(response.top_intents) == 3
    
    def test_fallback_response_confidence_boundaries(self):
        """Test fallback response with confidence boundaries."""
        # Low confidence
        response_low = FallbackResponse(confidence=0.0)
        assert response_low.confidence == 0.0
        
        # Medium confidence (typical fallback range)
        response_mid = FallbackResponse(confidence=0.5)
        assert response_mid.confidence == 0.5
        
        # High confidence (edge case for fallback)
        response_high = FallbackResponse(confidence=1.0)
        assert response_high.confidence == 1.0
    
    def test_fallback_response_confidence_invalid(self):
        """Test fallback response fails with invalid confidence."""
        with pytest.raises(ValidationError):
            FallbackResponse(confidence=-0.1)
        
        with pytest.raises(ValidationError):
            FallbackResponse(confidence=1.5)
    
    def test_fallback_response_clarification_false(self):
        """Test fallback response with clarification_needed=False."""
        response = FallbackResponse(
            confidence=0.65,
            clarification_needed=False
        )
        
        assert response.clarification_needed is False
    
    def test_fallback_response_with_suggestions(self):
        """Test fallback response with various suggestions."""
        suggestions = [
            "Bạn muốn bật thiết bị nào?",
            "Bạn muốn kiểm tra cảm biến nào?",
            "Bạn muốn kích hoạt cảnh nào?"
        ]
        
        response = FallbackResponse(
            confidence=0.4,
            suggestions=suggestions
        )
        
        assert len(response.suggestions) == 3
        assert response.suggestions == suggestions
    
    def test_fallback_response_with_top_intents(self):
        """Test fallback response with top intents."""
        top_intents = [
            {"intent": "control_device", "confidence": 0.45},
            {"intent": "query_sensor", "confidence": 0.32},
            {"intent": "environmental_comfort", "confidence": 0.23}
        ]
        
        response = FallbackResponse(
            confidence=0.45,
            top_intents=top_intents
        )
        
        assert len(response.top_intents) == 3
        assert response.top_intents[0]["intent"] == "control_device"
        assert response.top_intents[0]["confidence"] == 0.45
    
    def test_fallback_response_example_data(self):
        """Test fallback response with example data from schema_extra."""
        response = FallbackResponse(
            intent="unknown",
            entities={},
            confidence=0.45,
            clarification_needed=True,
            suggestions=[
                "Bạn muốn bật thiết bị nào?",
                "Bạn muốn kiểm tra cảm biến nào?"
            ],
            top_intents=[
                {"intent": "control_device", "confidence": 0.45},
                {"intent": "query_sensor", "confidence": 0.32},
                {"intent": "environmental_comfort", "confidence": 0.23}
            ]
        )
        
        assert response.intent == "unknown"
        assert response.confidence == 0.45
        assert len(response.suggestions) == 2
        assert len(response.top_intents) == 3


class TestMultiIntentResponse:
    """Test MultiIntentResponse model validation."""
    
    def test_multi_intent_response_single_intent(self):
        """Test multi-intent response with single intent."""
        intent = IntentResponse(
            intent="control_device",
            entities={"device": "light", "action": "turn_on"},
            confidence=1.0,
            classifier_type="rule"
        )
        
        response = MultiIntentResponse(
            intents=[intent],
            total_intents=1
        )
        
        assert len(response.intents) == 1
        assert response.total_intents == 1
        assert isinstance(response.timestamp, datetime)
    
    def test_multi_intent_response_multiple_intents(self):
        """Test multi-intent response with multiple intents."""
        intents = [
            IntentResponse(
                intent="control_device",
                entities={"device": "light", "action": "turn_on", "location": "living_room"},
                confidence=1.0,
                classifier_type="rule"
            ),
            IntentResponse(
                intent="control_device",
                entities={"device": "fan", "action": "turn_off", "location": "bedroom"},
                confidence=1.0,
                classifier_type="rule"
            )
        ]
        
        response = MultiIntentResponse(
            intents=intents,
            total_intents=2
        )
        
        assert len(response.intents) == 2
        assert response.total_intents == 2
        assert response.intents[0].entities["device"] == "light"
        assert response.intents[1].entities["device"] == "fan"
    
    def test_multi_intent_response_empty_intents_fails(self):
        """Test multi-intent response fails with empty intents list."""
        with pytest.raises(ValidationError):
            MultiIntentResponse(
                intents=[],
                total_intents=0
            )
    
    def test_multi_intent_response_missing_fields(self):
        """Test multi-intent response fails without required fields."""
        with pytest.raises(ValidationError) as exc_info:
            MultiIntentResponse()
        
        errors = exc_info.value.errors()
        field_names = [error["loc"][0] for error in errors]
        assert "intents" in field_names
        assert "total_intents" in field_names
    
    def test_multi_intent_response_example_data(self):
        """Test multi-intent response with example data from schema_extra."""
        intents = [
            IntentResponse(
                intent="control_device",
                entities={"device": "light", "action": "turn_on", "location": "living_room"},
                confidence=1.0,
                classifier_type="rule"
            ),
            IntentResponse(
                intent="control_device",
                entities={"device": "fan", "action": "turn_off", "location": "bedroom"},
                confidence=1.0,
                classifier_type="rule"
            )
        ]
        
        response = MultiIntentResponse(
            intents=intents,
            total_intents=2
        )
        
        assert response.total_intents == 2
        assert len(response.intents) == 2


class TestErrorResponse:
    """Test ErrorResponse model validation."""
    
    def test_error_response_minimal(self):
        """Test error response with minimal required fields."""
        response = ErrorResponse(
            error_type="validation",
            message="Input không hợp lệ"
        )
        
        assert response.error_type == "validation"
        assert response.message == "Input không hợp lệ"
        assert response.details is None
        assert isinstance(response.timestamp, datetime)
    
    def test_error_response_complete(self):
        """Test error response with all fields."""
        response = ErrorResponse(
            error_type="validation",
            message="Input không hợp lệ",
            details={"field": "text", "reason": "Text cannot be empty"},
            timestamp=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        assert response.error_type == "validation"
        assert response.message == "Input không hợp lệ"
        assert response.details == {"field": "text", "reason": "Text cannot be empty"}
        assert response.timestamp == datetime(2024, 1, 15, 10, 30, 0)
    
    def test_error_response_missing_required_fields(self):
        """Test error response fails without required fields."""
        with pytest.raises(ValidationError) as exc_info:
            ErrorResponse()
        
        errors = exc_info.value.errors()
        field_names = [error["loc"][0] for error in errors]
        assert "error_type" in field_names
        assert "message" in field_names
    
    def test_error_response_various_error_types(self):
        """Test error response with various error types."""
        error_types = ["validation", "authentication", "server", "not_found", "rate_limit"]
        
        for error_type in error_types:
            response = ErrorResponse(
                error_type=error_type,
                message=f"Error: {error_type}"
            )
            assert response.error_type == error_type
    
    def test_error_response_with_details(self):
        """Test error response with various detail structures."""
        details_examples = [
            {"field": "text", "reason": "Text cannot be empty"},
            {"code": 400, "path": "/api/v1/classify"},
            {"stack_trace": "...", "line": 42}
        ]
        
        for details in details_examples:
            response = ErrorResponse(
                error_type="validation",
                message="Error occurred",
                details=details
            )
            assert response.details == details
    
    def test_error_response_example_data(self):
        """Test error response with example data from schema_extra."""
        response = ErrorResponse(
            error_type="validation",
            message="Input không hợp lệ",
            details={"field": "text", "reason": "Text cannot be empty"}
        )
        
        assert response.error_type == "validation"
        assert response.message == "Input không hợp lệ"
        assert response.details["field"] == "text"
        assert response.details["reason"] == "Text cannot be empty"


class TestModelIntegration:
    """Integration tests for nested models and complex scenarios."""
    
    def test_request_with_nested_device_context(self):
        """Test request with fully nested device context."""
        request = IntentClassificationRequest(
            text="Bật đèn",
            user_id="user_123",
            home_id="home_456",
            device_context=DeviceContext(
                current_room="living_room",
                devices=[
                    DeviceState(
                        id="light_1",
                        type="light",
                        state="off",
                        location="living_room",
                        attributes={"brightness": 0, "color": "white"}
                    ),
                    DeviceState(
                        id="fan_1",
                        type="fan",
                        state="on",
                        location="living_room",
                        attributes={"speed": 2}
                    )
                ],
                time_of_day="evening"
            )
        )
        
        assert request.text == "Bật đèn"
        assert request.device_context.current_room == "living_room"
        assert len(request.device_context.devices) == 2
        assert request.device_context.devices[0].attributes["brightness"] == 0
        assert request.device_context.devices[1].attributes["speed"] == 2
    
    def test_multi_intent_with_various_responses(self):
        """Test multi-intent response with different intent types."""
        intents = [
            IntentResponse(
                intent="control_device",
                entities={"device": "light", "action": "turn_on"},
                confidence=1.0,
                classifier_type="rule"
            ),
            IntentResponse(
                intent="query_sensor",
                entities={"sensor": "temperature"},
                confidence=0.95,
                classifier_type="ml"
            ),
            IntentResponse(
                intent="scene_activation",
                entities={"scene": "movie"},
                confidence=0.98,
                classifier_type="rule",
                priority="high"
            )
        ]
        
        response = MultiIntentResponse(
            intents=intents,
            total_intents=3
        )
        
        assert response.total_intents == 3
        assert response.intents[0].intent == "control_device"
        assert response.intents[1].intent == "query_sensor"
        assert response.intents[2].intent == "scene_activation"
        assert response.intents[2].priority == "high"
    
    def test_model_serialization(self):
        """Test that models can be serialized to dict."""
        request = IntentClassificationRequest(
            text="Bật đèn phòng khách",
            user_id="user_123"
        )
        
        request_dict = request.model_dump()
        
        assert isinstance(request_dict, dict)
        assert request_dict["text"] == "Bật đèn phòng khách"
        assert request_dict["user_id"] == "user_123"
    
    def test_model_json_serialization(self):
        """Test that models can be serialized to JSON."""
        response = IntentResponse(
            intent="control_device",
            entities={"device": "light"},
            confidence=0.95,
            classifier_type="rule"
        )
        
        json_str = response.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "control_device" in json_str
        assert "0.95" in json_str
