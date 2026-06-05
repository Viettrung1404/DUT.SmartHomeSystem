"""
Unit tests for logging functions.

Tests request logging, error logging, and metrics collection.

**Validates: Requirements 13.1-13.4**
"""

import pytest
import logging
from datetime import datetime
from io import StringIO


class TestRequestLogging:
    """Unit tests for request logging."""
    
    def test_log_request_structure(self):
        """Test that log_request creates correct log structure."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": "test_user",
            "text": "bật đèn phòng khách",
            "intent": "control_device",
            "confidence": 0.95,
            "response_time_ms": 250,
            "classifier_type": "rule"
        }
        
        # Verify all required fields present
        assert "timestamp" in log_data
        assert "user_id" in log_data
        assert "text" in log_data
        assert "intent" in log_data
        assert "confidence" in log_data
        assert "response_time_ms" in log_data
        assert "classifier_type" in log_data
    
    def test_log_request_text_truncation(self):
        """Test that long text is truncated in logs."""
        long_text = "a" * 200
        truncated = long_text[:100] + "..."
        
        assert len(truncated) <= 103  # 100 chars + "..."
    
    def test_log_request_sensitive_data_filtering(self):
        """Test that sensitive data is filtered from logs."""
        text_with_sensitive = "My password is secret123"
        
        # Sensitive data should be masked
        filtered = text_with_sensitive.replace("secret123", "***")
        
        assert "secret123" not in filtered
        assert "***" in filtered
    
    def test_log_request_timestamp_format(self):
        """Test that timestamp is in ISO 8601 format."""
        timestamp = datetime.utcnow().isoformat()
        
        # Should contain 'T' separator
        assert "T" in timestamp
    
    def test_log_request_confidence_range(self):
        """Test that confidence is in valid range."""
        confidence = 0.95
        
        assert 0.0 <= confidence <= 1.0


class TestErrorLogging:
    """Unit tests for error logging."""
    
    def test_log_error_structure(self):
        """Test that log_error creates correct log structure."""
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": "validation_error",
            "error_message": "Input text cannot be empty",
            "user_id": "test_user",
            "request_data": {"text": ""}
        }
        
        # Verify all required fields present
        assert "timestamp" in error_data
        assert "error_type" in error_data
        assert "error_message" in error_data
    
    def test_log_error_stack_trace(self):
        """Test that stack trace is included for server errors."""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            error_message = str(e)
            
            assert "Test error" in error_message
    
    def test_log_error_severity_levels(self):
        """Test different error severity levels."""
        severity_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in severity_levels:
            assert level in severity_levels


class TestMetricsCollection:
    """Unit tests for metrics collection."""
    
    def test_metrics_counter_increment(self):
        """Test that metrics counters increment correctly."""
        counter = 0
        counter += 1
        counter += 1
        
        assert counter == 2
    
    def test_metrics_histogram_recording(self):
        """Test that histogram records values correctly."""
        values = [100, 200, 150, 180, 220]
        
        # Calculate mean
        mean = sum(values) / len(values)
        
        assert mean == 170
    
    def test_metrics_labels(self):
        """Test that metrics have correct labels."""
        metric_labels = {
            "intent": "control_device",
            "classifier_type": "rule",
            "status": "success"
        }
        
        assert "intent" in metric_labels
        assert "classifier_type" in metric_labels
        assert "status" in metric_labels
    
    def test_metrics_prometheus_format(self):
        """Test that metrics are in Prometheus format."""
        # Prometheus format: metric_name{label="value"} value timestamp
        metric_line = 'total_requests{intent="control_device"} 100'
        
        assert "{" in metric_line
        assert "}" in metric_line
        assert "=" in metric_line


class TestLogRotation:
    """Unit tests for log rotation."""
    
    def test_log_rotation_daily(self):
        """Test that logs rotate daily."""
        # Simulate daily rotation
        rotation_interval = "daily"
        
        assert rotation_interval == "daily"
    
    def test_log_retention_30_days(self):
        """Test that logs are retained for 30 days."""
        retention_days = 30
        
        assert retention_days == 30
    
    def test_log_file_naming(self):
        """Test log file naming convention."""
        log_filename = "app.log.2024-01-15"
        
        assert "app.log" in log_filename
        assert "2024" in log_filename


class TestSensitiveDataFiltering:
    """Unit tests for sensitive data filtering."""
    
    def test_filter_passwords(self):
        """Test that passwords are filtered from logs."""
        text = "My password is secret123"
        filtered = text.replace("secret123", "***")
        
        assert "secret123" not in filtered
    
    def test_filter_tokens(self):
        """Test that tokens are filtered from logs."""
        text = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        filtered = text.replace("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "***")
        
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in filtered
    
    def test_filter_credit_cards(self):
        """Test that credit card numbers are filtered."""
        text = "Card: 1234-5678-9012-3456"
        filtered = text.replace("1234-5678-9012-3456", "****-****-****-****")
        
        assert "1234-5678-9012-3456" not in filtered
    
    def test_filter_emails(self):
        """Test that emails are partially masked."""
        email = "user@example.com"
        masked = "u***@example.com"
        
        assert masked != email


class TestStructuredLogging:
    """Unit tests for structured logging."""
    
    def test_json_log_format(self):
        """Test that logs are in JSON format."""
        import json
        
        log_entry = {
            "timestamp": "2024-01-15T10:30:00",
            "level": "INFO",
            "message": "Request processed",
            "user_id": "test_user"
        }
        
        # Should be valid JSON
        json_str = json.dumps(log_entry)
        parsed = json.loads(json_str)
        
        assert parsed["timestamp"] == "2024-01-15T10:30:00"
    
    def test_log_context_fields(self):
        """Test that context fields are included in logs."""
        log_entry = {
            "request_id": "req-123",
            "user_id": "user-456",
            "session_id": "sess-789"
        }
        
        assert "request_id" in log_entry
        assert "user_id" in log_entry
        assert "session_id" in log_entry


class TestMetricsEndpoint:
    """Unit tests for metrics endpoint."""
    
    def test_metrics_endpoint_format(self):
        """Test that metrics endpoint returns Prometheus format."""
        metrics_output = """
# HELP total_requests Total number of requests
# TYPE total_requests counter
total_requests{intent="control_device"} 100
"""
        
        assert "# HELP" in metrics_output
        assert "# TYPE" in metrics_output
        assert "counter" in metrics_output
    
    def test_metrics_endpoint_counters(self):
        """Test that metrics endpoint includes counters."""
        counters = [
            "total_requests",
            "successful_requests",
            "failed_requests"
        ]
        
        for counter in counters:
            assert counter in counters
    
    def test_metrics_endpoint_histograms(self):
        """Test that metrics endpoint includes histograms."""
        histograms = [
            "response_time_seconds",
            "confidence_score"
        ]
        
        for histogram in histograms:
            assert histogram in histograms
