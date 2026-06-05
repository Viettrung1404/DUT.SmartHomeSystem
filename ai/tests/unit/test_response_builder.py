"""
Unit tests for Response Builder.

Tests response building for success, fallback, multi-intent, and error responses.

**Validates: Requirements 10.1-10.3**
"""

import pytest
from datetime import datetime
from src.api.response_builder import ResponseBuilder


class TestResponseBuilderValidation:
    """Unit tests for input validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()
    
    # ========================================================================
    # VALID INPUT TESTS
    # ========================================================================
    
    def test_valid_vietnamese_text(self):
        """Test that valid Vietnamese text passes validation."""
        result = self.builder.validate_and_build("bật đèn phòng khách")
        
        assert result["status"] == "valid"
        assert result["text"] == "bật đèn phòng khách"
    
    def test_valid_text_with_numbers(self):
        """Test that text with numbers passes validation."""
        result = self.builder.validate_and_build("đặt nhiệt độ 25 độ")
        
        assert result["status"] == "valid"
    
    def test_valid_text_with_special_chars(self):
        """Test that text with special characters passes validation."""
        result = self.builder.validate_and_build("bật đèn, tắt quạt!")
        
        assert result["status"] == "valid"
    
    def test_valid_text_at_max_length(self):
        """Test that text at max length (500 chars) passes validation."""
        text = "a" * 500
        result = self.builder.validate_and_build(text)
        
        assert result["status"] == "valid"
    
    # ========================================================================
    # INVALID INPUT TESTS
    # ========================================================================
    
    def test_empty_string_returns_error(self):
        """Test that empty string returns validation error."""
        result = self.builder.validate_and_build("")
        
        assert result["status_code"] == 400
        assert "empty" in result["message"].lower()
        assert result["error_type"] == "validation_error"
    
    def test_whitespace_only_returns_error(self):
        """Test that whitespace-only text returns validation error."""
        whitespace_texts = ["   ", "\t", "\n", "\r\n", "  \t\n  "]
        
        for text in whitespace_texts:
            result = self.builder.validate_and_build(text)
            
            assert result["status_code"] == 400
            assert "whitespace" in result["message"].lower()
    
    def test_none_input_returns_error(self):
        """Test that None input returns validation error."""
        result = self.builder.validate_and_build(None)
        
        assert result["status_code"] == 400
        assert "none" in result["message"].lower()
    
    def test_exceeds_max_length_returns_error(self):
        """Test that text exceeding max length returns validation error."""
        text = "a" * 501
        result = self.builder.validate_and_build(text)
        
        assert result["status_code"] == 400
        assert "max length" in result["message"].lower() or "exceeds" in result["message"].lower()
    
    def test_numeric_only_returns_error(self):
        """Test that numeric-only text returns validation error."""
        numeric_texts = ["123", "456789", "0000"]
        
        for text in numeric_texts:
            result = self.builder.validate_and_build(text)
            
            assert result["status_code"] == 400
            assert "alphabetic" in result["message"].lower()
    
    def test_special_chars_only_returns_error(self):
        """Test that special characters only returns validation error."""
        special_texts = ["!!!", "???", "...", "---", "***"]
        
        for text in special_texts:
            result = self.builder.validate_and_build(text)
            
            assert result["status_code"] == 400
            assert "alphabetic" in result["message"].lower()
    
    def test_non_string_input_returns_error(self):
        """Test that non-string input returns validation error."""
        non_string_inputs = [123, 45.67, True, [], {}]
        
        for input_val in non_string_inputs:
            result = self.builder.validate_and_build(input_val)
            
            assert result["status_code"] == 400
            assert "string" in result["message"].lower()


class TestSuccessResponse:
    """Unit tests for success response building."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()
    
    def test_build_success_response_structure(self):
        """Test that success response has correct structure."""
        response = self.builder.build_success_response(
            intent="control_device",
            entities={"device": "light", "action": "turn_on"},
            confidence=0.95,
            classifier_type="rule"
        )
        
        # Check required fields
        assert "intent" in response
        assert "entities" in response
        assert "confidence" in response
        assert "timestamp" in response
        assert "classifier_type" in response
    
    def test_build_success_response_values(self):
        """Test that success response has correct values."""
        response = self.builder.build_success_response(
            intent="control_device",
            entities={"device": "light", "action": "turn_on"},
            confidence=0.95,
            classifier_type="rule"
        )
        
        assert response["intent"] == "control_device"
        assert response["entities"]["device"] == "light"
        assert response["entities"]["action"] == "turn_on"
        assert response["confidence"] == 0.95
        assert response["classifier_type"] == "rule"
    
    def test_build_success_response_timestamp_format(self):
        """Test that timestamp is in ISO 8601 format."""
        response = self.builder.build_success_response(
            intent="control_device",
            entities={},
            confidence=0.85
        )
        
        # Check timestamp format (ISO 8601)
        timestamp = response["timestamp"]
        assert isinstance(timestamp, str)
        assert "T" in timestamp  # ISO 8601 has 'T' separator
    
    def test_build_success_response_empty_entities(self):
        """Test success response with empty entities."""
        response = self.builder.build_success_response(
            intent="unknown",
            entities={},
            confidence=0.3
        )
        
        assert response["intent"] == "unknown"
        assert response["entities"] == {}
        assert response["confidence"] == 0.3
    
    def test_build_success_response_default_classifier_type(self):
        """Test that default classifier_type is 'hybrid'."""
        response = self.builder.build_success_response(
            intent="control_device",
            entities={},
            confidence=0.85
        )
        
        assert response["classifier_type"] == "hybrid"


class TestFallbackResponse:
    """Unit tests for fallback response building."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()
    
    def test_build_fallback_response_structure(self):
        """Test that fallback response has correct structure."""
        response = self.builder.build_fallback_response(
            confidence=0.45,
            suggestions=["Bạn muốn bật thiết bị nào?"],
            top_intents=[{"intent": "control_device", "confidence": 0.45}]
        )
        
        # Check required fields
        assert "intent" in response
        assert "entities" in response
        assert "confidence" in response
        assert "timestamp" in response
        assert "clarification_needed" in response
        assert "suggestions" in response
        assert "top_intents" in response
    
    def test_build_fallback_response_values(self):
        """Test that fallback response has correct values."""
        suggestions = ["Bạn muốn bật thiết bị nào?", "Bạn muốn kiểm tra cảm biến nào?"]
        top_intents = [
            {"intent": "control_device", "confidence": 0.45},
            {"intent": "query_sensor", "confidence": 0.32}
        ]
        
        response = self.builder.build_fallback_response(
            confidence=0.45,
            suggestions=suggestions,
            top_intents=top_intents
        )
        
        assert response["intent"] == "unknown"
        assert response["entities"] == {}
        assert response["confidence"] == 0.45
        assert response["clarification_needed"] is True
        assert response["suggestions"] == suggestions
        assert response["top_intents"] == top_intents
    
    def test_build_fallback_response_empty_suggestions(self):
        """Test fallback response with empty suggestions."""
        response = self.builder.build_fallback_response(
            confidence=0.2,
            suggestions=[],
            top_intents=[]
        )
        
        assert response["suggestions"] == []
        assert response["top_intents"] == []


class TestMultiIntentResponse:
    """Unit tests for multi-intent response building."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()
    
    def test_build_multi_intent_response_structure(self):
        """Test that multi-intent response has correct structure."""
        intents = [
            {"intent": "control_device", "entities": {"device": "light"}},
            {"intent": "control_device", "entities": {"device": "fan"}}
        ]
        
        response = self.builder.build_multi_intent_response(intents)
        
        # Check required fields
        assert "intents" in response
        assert "timestamp" in response
        assert "count" in response
    
    def test_build_multi_intent_response_values(self):
        """Test that multi-intent response has correct values."""
        intents = [
            {"intent": "control_device", "entities": {"device": "light"}},
            {"intent": "control_device", "entities": {"device": "fan"}}
        ]
        
        response = self.builder.build_multi_intent_response(intents)
        
        assert response["intents"] == intents
        assert response["count"] == 2
    
    def test_build_multi_intent_response_single_intent(self):
        """Test multi-intent response with single intent."""
        intents = [{"intent": "control_device", "entities": {}}]
        
        response = self.builder.build_multi_intent_response(intents)
        
        assert response["count"] == 1
    
    def test_build_multi_intent_response_empty_intents(self):
        """Test multi-intent response with empty intents list."""
        response = self.builder.build_multi_intent_response([])
        
        assert response["intents"] == []
        assert response["count"] == 0


class TestErrorResponse:
    """Unit tests for error response building."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()
    
    def test_build_error_response_structure(self):
        """Test that error response has correct structure."""
        response = self.builder.build_error_response(
            status_code=400,
            message="Invalid input",
            error_type="validation_error"
        )
        
        # Check required fields
        assert "status_code" in response
        assert "message" in response
        assert "error_type" in response
        assert "timestamp" in response
    
    def test_build_error_response_400(self):
        """Test building 400 error response."""
        response = self.builder.build_error_response(
            status_code=400,
            message="Input text cannot be empty",
            error_type="validation_error"
        )
        
        assert response["status_code"] == 400
        assert response["message"] == "Input text cannot be empty"
        assert response["error_type"] == "validation_error"
    
    def test_build_error_response_401(self):
        """Test building 401 error response."""
        response = self.builder.build_error_response(
            status_code=401,
            message="Invalid JWT token",
            error_type="authentication_error"
        )
        
        assert response["status_code"] == 401
        assert response["error_type"] == "authentication_error"
    
    def test_build_error_response_429(self):
        """Test building 429 error response."""
        response = self.builder.build_error_response(
            status_code=429,
            message="Rate limit exceeded",
            error_type="rate_limit_error"
        )
        
        assert response["status_code"] == 429
        assert response["error_type"] == "rate_limit_error"
    
    def test_build_error_response_500(self):
        """Test building 500 error response."""
        response = self.builder.build_error_response(
            status_code=500,
            message="Internal server error",
            error_type="server_error"
        )
        
        assert response["status_code"] == 500
        assert response["error_type"] == "server_error"
    
    def test_build_error_response_503(self):
        """Test building 503 error response."""
        response = self.builder.build_error_response(
            status_code=503,
            message="Service unavailable",
            error_type="service_unavailable"
        )
        
        assert response["status_code"] == 503
        assert response["error_type"] == "service_unavailable"
    
    def test_build_error_response_default_error_type(self):
        """Test that default error_type is 'error'."""
        response = self.builder.build_error_response(
            status_code=500,
            message="Something went wrong"
        )
        
        assert response["error_type"] == "error"


class TestResponseBuilderEdgeCases:
    """Unit tests for edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = ResponseBuilder()
    
    def test_max_length_constant(self):
        """Test that MAX_LENGTH constant is 500."""
        assert self.builder.MAX_LENGTH == 500
    
    def test_min_length_constant(self):
        """Test that MIN_LENGTH constant is 1."""
        assert self.builder.MIN_LENGTH == 1
    
    def test_validation_with_leading_trailing_spaces(self):
        """Test validation with leading/trailing spaces."""
        result = self.builder.validate_and_build("  bật đèn  ")
        
        # Should pass validation (has alphabetic chars after strip)
        assert result["status"] == "valid"
    
    def test_validation_with_mixed_content(self):
        """Test validation with mixed Vietnamese and English."""
        result = self.builder.validate_and_build("bật light phòng khách")
        
        assert result["status"] == "valid"
    
    def test_validation_with_unicode_characters(self):
        """Test validation with Vietnamese unicode characters."""
        texts = [
            "bật đèn",
            "tắt quạt",
            "nhiệt độ",
            "phòng ngủ",
            "điều hòa"
        ]
        
        for text in texts:
            result = self.builder.validate_and_build(text)
            assert result["status"] == "valid", f"Text '{text}' should be valid"
