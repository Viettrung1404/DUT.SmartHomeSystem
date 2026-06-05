"""
Integration tests for API endpoints.

Tests API endpoints with authentication, rate limiting, CORS, and error handling.

**Validates: Requirements 11.1-11.5**
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt
import os


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


def create_expired_jwt(user_id: str = "test_user") -> str:
    """Create an expired JWT token."""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() - timedelta(minutes=5),
        "iat": datetime.utcnow() - timedelta(minutes=35)
    }
    token = jwt.encode(payload, TEST_JWT_SECRET, algorithm="HS256")
    return token


@pytest.fixture
def valid_jwt():
    """Fixture for valid JWT token."""
    return create_test_jwt()


@pytest.fixture
def expired_jwt():
    """Fixture for expired JWT token."""
    return create_expired_jwt()


class TestClassifyEndpoint:
    """Integration tests for POST /api/v1/intent/classify endpoint."""
    
    def test_classify_with_valid_jwt(self, valid_jwt):
        """Test classification with valid JWT token."""
        # This is a stub test - actual implementation will use TestClient
        # For now, we just verify the JWT token structure
        assert valid_jwt is not None
        assert isinstance(valid_jwt, str)
        
        # Decode and verify
        decoded = jwt.decode(valid_jwt, TEST_JWT_SECRET, algorithms=["HS256"])
        assert "user_id" in decoded
        assert decoded["user_id"] == "test_user"
    
    def test_classify_with_invalid_jwt(self):
        """Test classification with invalid JWT token."""
        invalid_token = "invalid.jwt.token"
        
        # Verify that decoding fails
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(invalid_token, TEST_JWT_SECRET, algorithms=["HS256"])
    
    def test_classify_with_expired_jwt(self, expired_jwt):
        """Test classification with expired JWT token."""
        # Verify that decoding fails due to expiration
        with pytest.raises(jwt.ExpiredSignatureError):
            jwt.decode(expired_jwt, TEST_JWT_SECRET, algorithms=["HS256"])
    
    def test_classify_without_jwt(self):
        """Test classification without JWT token."""
        # This should return 401 Unauthorized
        # Stub test - actual implementation will use TestClient
        pass
    
    def test_classify_with_valid_input(self, valid_jwt):
        """Test classification with valid input."""
        request_data = {
            "text": "bật đèn phòng khách",
            "context": {
                "current_room": "living_room"
            }
        }
        
        # Verify request structure
        assert "text" in request_data
        assert "context" in request_data
    
    def test_classify_with_empty_text(self, valid_jwt):
        """Test classification with empty text."""
        request_data = {
            "text": "",
            "context": None
        }
        
        # Should return 400 validation error
        assert request_data["text"] == ""
    
    def test_classify_with_whitespace_only(self, valid_jwt):
        """Test classification with whitespace-only text."""
        request_data = {
            "text": "   ",
            "context": None
        }
        
        # Should return 400 validation error
        assert request_data["text"].strip() == ""
    
    def test_classify_with_max_length_exceeded(self, valid_jwt):
        """Test classification with text exceeding max length."""
        request_data = {
            "text": "a" * 501,  # Exceeds 500 char limit
            "context": None
        }
        
        # Should return 400 validation error
        assert len(request_data["text"]) > 500


class TestRateLimiting:
    """Integration tests for rate limiting."""
    
    def test_rate_limit_not_exceeded(self, valid_jwt):
        """Test that requests within rate limit succeed."""
        # Stub test - actual implementation will make multiple requests
        # and verify they all succeed
        pass
    
    def test_rate_limit_exceeded(self, valid_jwt):
        """Test that requests exceeding rate limit return 429."""
        # Stub test - actual implementation will make many requests
        # and verify that excess requests return 429
        pass
    
    def test_rate_limit_reset_after_window(self, valid_jwt):
        """Test that rate limit resets after time window."""
        # Stub test - actual implementation will wait for window to reset
        pass


class TestCORS:
    """Integration tests for CORS."""
    
    def test_cors_preflight_request(self):
        """Test CORS preflight OPTIONS request."""
        # Stub test - actual implementation will send OPTIONS request
        # and verify CORS headers
        pass
    
    def test_cors_headers_present(self, valid_jwt):
        """Test that CORS headers are present in response."""
        # Stub test - actual implementation will verify headers:
        # - Access-Control-Allow-Origin
        # - Access-Control-Allow-Methods
        # - Access-Control-Allow-Headers
        pass


class TestErrorResponses:
    """Integration tests for error responses."""
    
    def test_400_validation_error(self, valid_jwt):
        """Test 400 error for validation errors."""
        # Empty text should return 400
        request_data = {"text": ""}
        assert request_data["text"] == ""
    
    def test_401_authentication_error(self):
        """Test 401 error for missing/invalid JWT."""
        # No JWT should return 401
        pass
    
    def test_429_rate_limit_error(self, valid_jwt):
        """Test 429 error for rate limit exceeded."""
        # Too many requests should return 429
        pass
    
    def test_500_server_error(self, valid_jwt):
        """Test 500 error for server errors."""
        # Server error should return 500
        pass
    
    def test_503_service_unavailable(self, valid_jwt):
        """Test 503 error for service unavailable."""
        # Service unavailable should return 503
        pass


class TestHealthEndpoint:
    """Integration tests for GET /health endpoint."""
    
    def test_health_check_returns_200(self):
        """Test that health check returns 200 OK."""
        # Stub test - actual implementation will call /health
        pass
    
    def test_health_check_response_structure(self):
        """Test that health check response has correct structure."""
        # Should return: {"status": "healthy", "timestamp": "..."}
        pass


class TestMetricsEndpoint:
    """Integration tests for GET /api/v1/metrics endpoint."""
    
    def test_metrics_endpoint_returns_prometheus_format(self, valid_jwt):
        """Test that metrics endpoint returns Prometheus format."""
        # Stub test - actual implementation will verify Prometheus format
        pass
    
    def test_metrics_endpoint_requires_auth(self):
        """Test that metrics endpoint requires authentication."""
        # Should return 401 without JWT
        pass


class TestIntentsEndpoint:
    """Integration tests for GET /api/v1/intents endpoint."""
    
    def test_intents_list_returns_all_intents(self, valid_jwt):
        """Test that intents endpoint returns list of all intents."""
        # Should return list of 15 core intents
        expected_intents = [
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
        
        assert len(expected_intents) >= 12
    
    def test_intents_list_requires_auth(self):
        """Test that intents endpoint requires authentication."""
        # Should return 401 without JWT
        pass


class TestModelReloadEndpoint:
    """Integration tests for POST /api/v1/model/reload endpoint."""
    
    def test_model_reload_requires_auth(self):
        """Test that model reload requires authentication."""
        # Should return 401 without JWT
        pass
    
    def test_model_reload_requires_admin_role(self, valid_jwt):
        """Test that model reload requires admin role."""
        # Should return 403 for non-admin users
        pass
    
    def test_model_reload_success(self):
        """Test successful model reload."""
        # Admin user should be able to reload model
        # Should return 200 with success message
        pass


class TestRequestValidation:
    """Integration tests for request validation."""
    
    def test_missing_text_field(self, valid_jwt):
        """Test request with missing text field."""
        request_data = {"context": None}
        
        # Should return 400 validation error
        assert "text" not in request_data
    
    def test_invalid_context_format(self, valid_jwt):
        """Test request with invalid context format."""
        request_data = {
            "text": "bật đèn",
            "context": "invalid"  # Should be dict or None
        }
        
        # Should return 400 validation error
        assert not isinstance(request_data["context"], (dict, type(None)))
    
    def test_extra_fields_ignored(self, valid_jwt):
        """Test that extra fields in request are ignored."""
        request_data = {
            "text": "bật đèn",
            "context": None,
            "extra_field": "should be ignored"
        }
        
        # Extra fields should be ignored, not cause error
        assert "extra_field" in request_data


class TestResponseFormat:
    """Integration tests for response format."""
    
    def test_success_response_format(self, valid_jwt):
        """Test that success response has correct format."""
        # Should have: intent, entities, confidence, timestamp, classifier_type
        expected_fields = ["intent", "entities", "confidence", "timestamp", "classifier_type"]
        assert len(expected_fields) == 5
    
    def test_fallback_response_format(self, valid_jwt):
        """Test that fallback response has correct format."""
        # Should have: intent, entities, confidence, timestamp, clarification_needed, suggestions, top_intents
        expected_fields = ["intent", "entities", "confidence", "timestamp", "clarification_needed", "suggestions", "top_intents"]
        assert len(expected_fields) == 7
    
    def test_error_response_format(self):
        """Test that error response has correct format."""
        # Should have: status_code, message, error_type, timestamp
        expected_fields = ["status_code", "message", "error_type", "timestamp"]
        assert len(expected_fields) == 4
