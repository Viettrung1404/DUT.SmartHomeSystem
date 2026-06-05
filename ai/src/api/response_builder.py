"""
Response Builder for Vietnamese NLP Intent Classification.

This module provides response building and validation functionality.

**Validates: Requirements 10.1-10.3**
"""

from typing import Dict, Any, Optional, List
import re


class ResponseBuilder:
    """
    Response Builder for constructing API responses.
    
    This builder:
    - Validates input text
    - Builds success responses (IntentResponse)
    - Builds fallback responses (FallbackResponse)
    - Builds multi-intent responses (MultiIntentResponse)
    - Builds error responses (ErrorResponse)
    
    Validation rules:
    - Text must not be None
    - Text must not be empty or whitespace-only
    - Text must not exceed max length (500 chars)
    - Text must contain at least one alphabetic character
    """
    
    MAX_LENGTH = 500
    MIN_LENGTH = 1
    
    def __init__(self):
        """Initialize response builder."""
        pass
    
    def validate_and_build(self, text: Any) -> Dict[str, Any]:
        """
        Validate input text and return validation result.
        
        This method validates the input and returns either:
        - A dict indicating validation passed (for valid input)
        - An error response dict (for invalid input)
        
        Args:
            text: Input text to validate
            
        Returns:
            Dictionary with validation result or error response
        """
        # Validate input
        validation_error = self._validate_input(text)
        
        if validation_error:
            return validation_error
        
        # If validation passed, return success indicator
        return {"status": "valid", "text": text}
    
    def _validate_input(self, text: Any) -> Optional[Dict[str, Any]]:
        """
        Validate input text.
        
        Returns None if valid, or error response dict if invalid.
        
        Args:
            text: Input text to validate
            
        Returns:
            None if valid, error response dict if invalid
        """
        # Check if text is None
        if text is None:
            return self.build_error_response(
                status_code=400,
                message="Input text cannot be None",
                error_type="validation_error"
            )
        
        # Check if text is string
        if not isinstance(text, str):
            return self.build_error_response(
                status_code=400,
                message=f"Input text must be a string, got {type(text).__name__}",
                error_type="validation_error"
            )
        
        # Check if text is empty
        if len(text) == 0:
            return self.build_error_response(
                status_code=400,
                message="Input text cannot be empty",
                error_type="validation_error"
            )
        
        # Check if text is whitespace-only
        if text.strip() == "":
            return self.build_error_response(
                status_code=400,
                message="Input text cannot be whitespace-only",
                error_type="validation_error"
            )
        
        # Check if text exceeds max length
        if len(text) > self.MAX_LENGTH:
            return self.build_error_response(
                status_code=400,
                message=f"Input text exceeds max length of {self.MAX_LENGTH} characters (got {len(text)})",
                error_type="validation_error"
            )
        
        # Check if text contains at least one alphabetic character
        if not re.search(r'[a-zA-ZàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđĐ]', text):
            return self.build_error_response(
                status_code=400,
                message="Input text must contain at least one alphabetic character",
                error_type="validation_error"
            )
        
        # Validation passed
        return None
    
    def build_success_response(
        self,
        intent: str,
        entities: Dict[str, Any],
        confidence: float,
        classifier_type: str = "hybrid",
        priority: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build success response (IntentResponse).
        
        Args:
            intent: Predicted intent
            entities: Extracted entities
            confidence: Confidence score (0-1)
            classifier_type: Type of classifier used ("rule", "ml", "hybrid")
            
        Returns:
            IntentResponse dictionary
        """
        from datetime import datetime
        
        if priority is None and "priority" in entities:
            priority = entities.pop("priority")

        return {
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "classifier_type": classifier_type,
            "priority": priority,
        }
    
    def build_fallback_response(
        self,
        confidence: float = 0.0,
        suggestions: Optional[List[str]] = None,
        top_intents: Optional[List[Any]] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Build fallback response (FallbackResponse).
        
        Args:
            confidence: Confidence score (0-1)
            suggestions: List of clarification questions
            top_intents: List of top intent suggestions
            
        Returns:
            FallbackResponse dictionary
        """
        from datetime import datetime
        
        normalized_top_intents: List[Dict[str, Any]] = []
        if top_intents:
            if isinstance(top_intents[0], tuple):
                normalized_top_intents = [
                    {"intent": intent, "confidence": float(conf)}
                    for intent, conf in top_intents
                ]
            else:
                normalized_top_intents = list(top_intents)

        if suggestions is None:
            suggestions = [reason] if reason else []

        return {
            "intent": "unknown",
            "entities": {},
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "clarification_needed": True,
            "suggestions": suggestions,
            "top_intents": normalized_top_intents,
        }
    
    def build_multi_intent_response(self,
                                    intents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build multi-intent response (MultiIntentResponse).
        
        Args:
            intents: List of intent responses
            
        Returns:
            MultiIntentResponse dictionary
        """
        from datetime import datetime
        
        return {
            "intents": intents,
            "timestamp": datetime.utcnow().isoformat(),
            "total_intents": len(intents),
            # Backward-compatible alias (older docs/tests may expect this)
            "count": len(intents),
        }
    
    def build_error_response(
        self,
        status_code: int = 400,
        message: str = "",
        error_type: str = "error",
    ) -> Dict[str, Any]:
        """
        Build error response (ErrorResponse).
        
        Args:
            status_code: HTTP status code (400, 401, 403, 429, 500, 503)
            message: Error message
            error_type: Type of error
            
        Returns:
            ErrorResponse dictionary
        """
        from datetime import datetime
        
        return {
            "status_code": status_code,
            "message": message,
            "error_type": error_type,
            "timestamp": datetime.utcnow().isoformat()
        }
