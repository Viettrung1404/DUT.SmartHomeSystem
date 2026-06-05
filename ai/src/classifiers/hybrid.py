"""
Hybrid Classifier for Vietnamese NLP Intent Classification.

This classifier combines rule-based and ML-based classifiers to optimize
both speed (<10ms for simple commands) and accuracy (>90% for natural language).

**Validates: Requirements 9.1-9.11**
"""

from typing import Optional, Dict, Any
import logging

from src.classifiers.rule_based import RuleBasedClassifier, ClassificationResult
from src.classifiers.ml_based import MLBasedClassifier

logger = logging.getLogger(__name__)


class HybridClassifier:
    """
    Hybrid Classifier that routes requests to appropriate classifier.
    
    This classifier:
    - Routes simple commands to rule-based classifier (fast path, <10ms)
    - Routes natural language to ML-based classifier (accurate path, <300ms)
    - Compares confidence scores and returns highest
    - Implements fallback strategy: ML failure → rule-based → unknown
    
    Routing Strategy:
    1. Check if text matches simple command patterns (should_use_rule_based)
    2. If yes, try rule-based classifier first
    3. If rule-based returns confidence=1.0, return immediately (fast path)
    4. Otherwise, try ML-based classifier
    5. Compare confidence scores and return highest
    6. If ML fails, fallback to rule-based result or unknown
    """
    
    def __init__(self, 
                 rule_classifier: RuleBasedClassifier,
                 ml_classifier: MLBasedClassifier):
        """
        Initialize hybrid classifier.
        
        Args:
            rule_classifier: RuleBasedClassifier instance
            ml_classifier: MLBasedClassifier instance
        """
        self.rule_classifier = rule_classifier
        self.ml_classifier = ml_classifier
        
        logger.info("Hybrid Classifier initialized successfully")
        logger.info(f"  - Rule-based classifier: {type(rule_classifier).__name__}")
        logger.info(f"  - ML-based classifier: {type(ml_classifier).__name__}")
    
    def should_use_rule_based(self, text: str) -> bool:
        """
        Determine if text should use rule-based classifier.
        
        Simple command indicators:
        - Contains action words: bật, tắt, mở, đóng
        - Contains scene keywords: đi ngủ, thức dậy, xem phim, về nhà, đi vắng
        - Short length (< 10 words)
        - No complex sentence structure
        
        Args:
            text: Preprocessed Vietnamese text
            
        Returns:
            True if should use rule-based, False otherwise
        """
        text_lower = text.lower().strip()
        
        # Check for action words
        action_words = ["bật", "tắt", "mở", "đóng"]
        has_action = any(word in text_lower for word in action_words)
        
        # Check for scene keywords
        scene_keywords = ["đi ngủ", "thức dậy", "xem phim", "về nhà", "đi vắng"]
        has_scene = any(keyword in text_lower for keyword in scene_keywords)
        
        # Check length (simple commands are usually short)
        word_count = len(text_lower.split())
        is_short = word_count <= 10
        
        # Use rule-based if has action/scene and is short
        should_use = (has_action or has_scene) and is_short
        
        if should_use:
            logger.debug(f"Text '{text}' matches simple command pattern (action={has_action}, scene={has_scene}, words={word_count})")
        
        return should_use
    
    def classify(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ClassificationResult:
        """
        Classify intent using hybrid approach.
        
        Decision logic:
        1. Check if text matches simple command patterns (should_use_rule_based)
        2. If yes, try rule-based classifier first
        3. If rule-based returns confidence=1.0, return immediately (fast path)
        4. Otherwise, try ML-based classifier
        5. Compare confidence scores and return highest
        6. If ML fails, fallback to rule-based result or unknown
        
        Args:
            text: Preprocessed Vietnamese text
            context: Optional device context for disambiguation
            
        Returns:
            Classification result with:
            - intent: Predicted intent name
            - entities: Extracted entities dictionary
            - confidence: Confidence score (0.0-1.0)
            - classifier_type: "rule", "ml", or "fallback"
            - (optional) error: Error message if ML failed
            - (optional) top_k_intents: Top-k intents from ML classifier
        """
        logger.info(f"Classifying text: '{text}'")
        
        rule_result = None
        ml_result = None
        
        # Try rule-based first if text looks like simple command
        if self.should_use_rule_based(text):
            logger.debug("Routing to rule-based classifier (simple command detected)")
            rule_result = self.rule_classifier.classify(text)
            
            # If rule-based has perfect confidence, return immediately (fast path)
            if rule_result and rule_result.confidence == 1.0:
                logger.info(f"Rule-based classifier matched with confidence=1.0: intent={rule_result.intent}")
                return rule_result
        
        # Try ML-based classifier
        try:
            logger.debug("Routing to ML-based classifier")
            ml_result = self.ml_classifier.classify(text, context)
            logger.info(
                "ML-based classifier result: intent=%s, confidence=%.3f",
                ml_result["intent"],
                ml_result["confidence"],
            )
        except Exception as e:
            # ML classifier failed, fallback to rule-based or unknown
            logger.error(f"ML classifier failed: {str(e)}")
            
            if rule_result:
                logger.warning(f"Fallback triggered: ML failed, using rule-based result (intent={rule_result.intent}, confidence={rule_result.confidence})")
                return rule_result
            else:
                logger.warning(f"Fallback triggered: Both classifiers failed, returning unknown (error: {str(e)})")
                return ClassificationResult(
                    intent="unknown",
                    entities={"error": str(e)},
                    confidence=0.0,
                    classifier_type="fallback",
                )
        
        # Compare results and return highest confidence
        if rule_result and ml_result:
            # Convert rule_result to dict format if needed
            logger.debug(
                "Comparing confidence scores: rule=%.3f vs ml=%.3f",
                rule_result.confidence,
                ml_result["confidence"],
            )

            if rule_result.confidence >= ml_result["confidence"]:
                logger.info(
                    "Returning rule-based result (confidence=%.3f >= %.3f): intent=%s",
                    rule_result.confidence,
                    ml_result["confidence"],
                    rule_result.intent,
                )
                return rule_result

            logger.info(
                "Returning ML-based result (confidence=%.3f > %.3f): intent=%s",
                ml_result["confidence"],
                rule_result.confidence,
                ml_result["intent"],
            )
            return self._to_result(ml_result)
        elif ml_result:
            logger.info(
                "Returning ML-based result (no rule match): intent=%s, confidence=%.3f",
                ml_result["intent"],
                ml_result["confidence"],
            )
            return self._to_result(ml_result)
        elif rule_result:
            logger.info(f"Returning rule-based result (ML not attempted): intent={rule_result.intent}, confidence={rule_result.confidence}")
            return rule_result
        else:
            # Both failed (shouldn't happen, but handle gracefully)
            logger.warning("No classification result available, returning unknown")
            return ClassificationResult(
                intent="unknown",
                entities={},
                confidence=0.0,
                classifier_type="fallback",
            )

    @staticmethod
    def _to_result(result: Dict[str, Any]) -> ClassificationResult:
        mapped = ClassificationResult(
            intent=str(result.get("intent") or "unknown"),
            entities=dict(result.get("entities") or {}),
            confidence=float(result.get("confidence") or 0.0),
            classifier_type=str(result.get("classifier_type") or "ml"),
        )

        top_k = result.get("top_k_intents")
        if top_k is not None:
            setattr(mapped, "top_k_intents", top_k)

        return mapped
