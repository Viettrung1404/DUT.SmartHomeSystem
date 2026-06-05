"""
Timeout Handler for Vietnamese NLP Intent Classification API.

This module provides timeout handling with fallback to rule-based classifier.

**Validates: Requirements 10.4**
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class TimeoutHandler:
    """
    Timeout Handler for inference operations.
    
    This handler:
    - Enforces 5-second timeout for ML inference
    - Falls back to rule-based classifier on timeout
    - Logs timeout events
    """
    
    INFERENCE_TIMEOUT = 5.0  # 5 seconds
    
    def __init__(self, rule_based_classifier=None):
        """
        Initialize timeout handler.
        
        Args:
            rule_based_classifier: Rule-based classifier for fallback
        """
        self.rule_based_classifier = rule_based_classifier
    
    async def classify_with_timeout(self,
                                    ml_classifier,
                                    text: str,
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify text with timeout and fallback.
        
        Args:
            ml_classifier: ML-based classifier
            text: Input text
            context: Optional device context
            
        Returns:
            Classification result
        """
        try:
            # Try ML classification with timeout
            result = await asyncio.wait_for(
                self._async_ml_classify(ml_classifier, text, context),
                timeout=self.INFERENCE_TIMEOUT
            )
            return result
        
        except asyncio.TimeoutError:
            logger.warning(
                f"ML inference timeout after {self.INFERENCE_TIMEOUT}s, "
                f"falling back to rule-based classifier"
            )
            
            # Fallback to rule-based classifier
            if self.rule_based_classifier:
                return self._fallback_to_rule_based(text, context)
            else:
                raise TimeoutError(
                    f"ML inference timeout after {self.INFERENCE_TIMEOUT}s "
                    f"and no fallback classifier available"
                )
    
    async def _async_ml_classify(self,
                                 ml_classifier,
                                 text: str,
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Async wrapper for ML classification.
        
        Args:
            ml_classifier: ML-based classifier
            text: Input text
            context: Optional device context
            
        Returns:
            Classification result
        """
        # Run ML classification in executor (since it's CPU-bound)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            ml_classifier.classify,
            text,
            context
        )
        return result
    
    def _fallback_to_rule_based(self,
                                text: str,
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Fallback to rule-based classifier.
        
        Args:
            text: Input text
            context: Optional device context
            
        Returns:
            Classification result from rule-based classifier
        """
        from src.entities.entity_extractor import EntityExtractor
        
        # Classify with rule-based classifier
        result = self.rule_based_classifier.classify(text)
        
        if result is None:
            # No pattern matched, return unknown
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0,
                "classifier_type": "rule",
                "fallback_reason": "timeout"
            }
        
        # Extract entities
        extractor = EntityExtractor()
        entities = extractor.extract(text, result.intent, context)
        
        return {
            "intent": result.intent,
            "entities": entities,
            "confidence": result.confidence,
            "classifier_type": "rule",
            "fallback_reason": "timeout"
        }


def with_timeout(timeout_seconds: float = 5.0):
    """
    Decorator for adding timeout to sync functions.
    
    Args:
        timeout_seconds: Timeout in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Run function with timeout
                result = await asyncio.wait_for(
                    asyncio.to_thread(func, *args, **kwargs),
                    timeout=timeout_seconds
                )
                return result
            except asyncio.TimeoutError:
                logger.warning(f"Function {func.__name__} timeout after {timeout_seconds}s")
                raise TimeoutError(f"Operation timeout after {timeout_seconds}s")
        
        return wrapper
    return decorator
