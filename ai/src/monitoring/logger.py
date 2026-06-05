"""
Structured Logging for Vietnamese NLP Intent Classification API.

This module provides structured logging with sensitive data filtering.

**Validates: Requirements 13.1-13.4**
"""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import re


class StructuredLogger:
    """
    Structured logger with JSON formatting and sensitive data filtering.
    
    This logger:
    - Logs in JSON format
    - Filters sensitive data (passwords, tokens, etc.)
    - Truncates long text
    - Includes context fields
    """
    
    MAX_TEXT_LENGTH = 100
    
    def __init__(self, name: str = __name__):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
    
    def _filter_sensitive_data(self, text: str) -> str:
        """
        Filter sensitive data from text.
        
        Args:
            text: Text to filter
            
        Returns:
            Filtered text
        """
        # Filter passwords
        text = re.sub(r'password["\s:=]+\S+', 'password=***', text, flags=re.IGNORECASE)
        
        # Filter tokens (JWT, Bearer, etc.)
        text = re.sub(r'(Bearer|Token)\s+\S+', r'\1 ***', text, flags=re.IGNORECASE)
        
        # Filter credit cards
        text = re.sub(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', '****-****-****-****', text)
        
        return text
    
    def _truncate_text(self, text: str) -> str:
        """
        Truncate long text.
        
        Args:
            text: Text to truncate
            
        Returns:
            Truncated text
        """
        if len(text) > self.MAX_TEXT_LENGTH:
            return text[:self.MAX_TEXT_LENGTH] + "..."
        return text
    
    def log_request(self,
                   user_id: str,
                   text: str,
                   intent: str,
                   confidence: float,
                   response_time_ms: float,
                   classifier_type: str,
                   **extra_fields):
        """
        Log API request.
        
        Args:
            user_id: User ID
            text: Input text
            intent: Predicted intent
            confidence: Confidence score
            response_time_ms: Response time in milliseconds
            classifier_type: Type of classifier used
            **extra_fields: Additional fields to log
        """
        # Filter and truncate text
        filtered_text = self._filter_sensitive_data(text)
        truncated_text = self._truncate_text(filtered_text)
        
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "request",
            "user_id": user_id,
            "text": truncated_text,
            "intent": intent,
            "confidence": confidence,
            "response_time_ms": response_time_ms,
            "classifier_type": classifier_type,
            **extra_fields
        }
        
        self.logger.info(json.dumps(log_data))
    
    def log_error(self,
                 error_type: str,
                 error_message: str,
                 user_id: Optional[str] = None,
                 **extra_fields):
        """
        Log error.
        
        Args:
            error_type: Type of error
            error_message: Error message
            user_id: Optional user ID
            **extra_fields: Additional fields to log
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            **extra_fields
        }
        
        if user_id:
            log_data["user_id"] = user_id
        
        self.logger.error(json.dumps(log_data))


def log_request(user_id: str,
               text: str,
               intent: str,
               confidence: float,
               response_time_ms: float,
               classifier_type: str):
    """
    Log API request (convenience function).
    
    Args:
        user_id: User ID
        text: Input text
        intent: Predicted intent
        confidence: Confidence score
        response_time_ms: Response time in milliseconds
        classifier_type: Type of classifier used
    """
    logger = StructuredLogger()
    logger.log_request(
        user_id=user_id,
        text=text,
        intent=intent,
        confidence=confidence,
        response_time_ms=response_time_ms,
        classifier_type=classifier_type
    )
