"""
Unit tests for Hybrid Classifier routing logic.

These tests verify the HybridClassifier's ability to:
- Route simple commands to rule-based classifier
- Route natural language to ML-based classifier
- Compare confidence scores and return highest
- Implement fallback strategy (ML failure → rule-based → unknown)
- Determine routing decisions via should_use_rule_based()

**Validates: Requirements 9.1-9.11**
"""

import pytest
from typing import Optional, Dict, Any
from unittest.mock import Mock, MagicMock, patch


# ============================================================================
# MOCK CLASSIFIERS FOR TESTING
# ============================================================================

class MockRuleBasedClassifier:
    """Mock rule-based classifier for testing."""
    
    def classify(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Mock classify method.
        
        Returns confidence=1.0 for simple commands, None for natural language.
        """
        # Simple command patterns
        simple_patterns = [
            "bật đèn", "tắt quạt", "mở cửa", "đóng mái che",
            "bật điều hòa", "tắt ac", "đi ngủ", "thức dậy",
            "xem phim", "về nhà", "đi vắng"
        ]
        
        text_lower = text.lower().strip()
        
        # Check if text matches any simple pattern
        for pattern in simple_patterns:
            if pattern in text_lower:
                return {
                    "intent": "control_device" if any(word in pattern for word in ["bật", "tắt", "mở", "đóng"]) else "activate_scene",
                    "entities": {"device": "light"} if "đèn" in pattern else {},
                    "confidence": 1.0,
                    "classifier_type": "rule"
                }
        
        # No match
        return None


class MockMLBasedClassifier:
    """Mock ML-based classifier for testing."""
    
    def __init__(self, should_fail=False):
        """
        Initialize mock ML classifier.
        
        Args:
            should_fail: If True, classify() will raise an exception
        """
        self.should_fail = should_fail
    
    def classify(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mock classify method.
        
        Returns varying confidence scores based on text complexity.
        """
        if self.should_fail:
            raise RuntimeError("ML model inference failed")
        
        text_lower = text.lower().strip()
        
        # Natural language patterns (high confidence)
        if any(phrase in text_lower for phrase in ["nóng quá", "lạnh quá", "tối quá", "ngột ngạt"]):
            return {
                "intent": "environmental_comfort",
                "entities": {"comfort_type": "cooling"},
                "confidence": 0.95,
                "classifier_type": "ml",
                "top_k_intents": [
                    ("environmental_comfort", 0.95),
                    ("control_device", 0.03),
                    ("query_sensor", 0.02)
                ]
            }
        
        # Ambiguous patterns (medium confidence)
        elif any(phrase in text_lower for phrase in ["nhiệt độ", "độ ẩm", "thời tiết"]):
            return {
                "intent": "query_sensor",
                "entities": {"sensor_type": "temperature"},
                "confidence": 0.65,
                "classifier_type": "ml",
                "top_k_intents": [
                    ("query_sensor", 0.65),
                    ("environmental_comfort", 0.25),
                    ("weather_action", 0.10)
                ]
            }
        
        # Simple commands (low confidence - should defer to rule-based)
        elif any(word in text_lower for word in ["bật", "tắt", "mở", "đóng"]):
            return {
                "intent": "control_device",
                "entities": {},
                "confidence": 0.50,
                "classifier_type": "ml",
                "top_k_intents": [
                    ("control_device", 0.50),
                    ("activate_scene", 0.30),
                    ("unknown", 0.20)
                ]
            }
        
        # Unknown patterns (very low confidence)
        else:
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.30,
                "classifier_type": "ml",
                "top_k_intents": [
                    ("unknown", 0.30),
                    ("control_device", 0.25),
                    ("query_sensor", 0.20)
                ]
            }


# ============================================================================
# HYBRID CLASSIFIER (STUB FOR TESTING)
# ============================================================================

class HybridClassifier:
    """
    Hybrid Classifier that routes requests to appropriate classifier.
    
    This is a stub implementation for testing purposes.
    The actual implementation will be done in Task 9.2.
    """
    
    def __init__(self, rule_classifier, ml_classifier):
        """
        Initialize hybrid classifier.
        
        Args:
            rule_classifier: RuleBasedClassifier instance
            ml_classifier: MLBasedClassifier instance
        """
        self.rule_classifier = rule_classifier
        self.ml_classifier = ml_classifier
    
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
        return (has_action or has_scene) and is_short
    
    def classify(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify intent using hybrid approach.
        
        Decision logic:
        1. Check if text matches simple command patterns (should_use_rule_based)
        2. If yes, try rule-based classifier first
        3. If rule-based returns confidence=1.0, return immediately
        4. Otherwise, try ML-based classifier
        5. Compare confidence scores and return highest
        6. If ML fails, fallback to rule-based result or unknown
        
        Args:
            text: Preprocessed Vietnamese text
            context: Optional device context for disambiguation
            
        Returns:
            Classification result with intent, entities, confidence, classifier_type
        """
        rule_result = None
        ml_result = None
        
        # Try rule-based first if text looks like simple command
        if self.should_use_rule_based(text):
            rule_result = self.rule_classifier.classify(text)
            
            # If rule-based has perfect confidence, return immediately
            if rule_result and rule_result.get("confidence") == 1.0:
                return rule_result
        
        # Try ML-based classifier
        try:
            ml_result = self.ml_classifier.classify(text, context)
        except Exception as e:
            # ML classifier failed, fallback to rule-based or unknown
            if rule_result:
                return rule_result
            else:
                return {
                    "intent": "unknown",
                    "entities": {},
                    "confidence": 0.0,
                    "classifier_type": "fallback",
                    "error": str(e)
                }
        
        # Compare results and return highest confidence
        if rule_result and ml_result:
            if rule_result["confidence"] >= ml_result["confidence"]:
                return rule_result
            else:
                return ml_result
        elif ml_result:
            return ml_result
        elif rule_result:
            return rule_result
        else:
            # Both failed
            return {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.0,
                "classifier_type": "fallback"
            }


# ============================================================================
# UNIT TESTS: ROUTING LOGIC
# ============================================================================

class TestHybridClassifierRouting:
    """Unit tests for hybrid classifier routing logic."""
    
    def test_simple_command_routes_to_rule_based(self):
        """Test that simple commands route to rule-based classifier."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Simple command: "bật đèn"
        result = hybrid.classify("bật đèn")
        
        assert result is not None
        assert result["classifier_type"] == "rule"
        assert result["confidence"] == 1.0
    
    def test_natural_language_routes_to_ml_based(self):
        """Test that natural language routes to ML-based classifier."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Natural language: "nóng quá"
        result = hybrid.classify("nóng quá")
        
        assert result is not None
        assert result["classifier_type"] == "ml"
        assert result["intent"] == "environmental_comfort"
        assert result["confidence"] == 0.95
    
    def test_tat_quat_routes_to_rule_based(self):
        """Test that 'tắt quạt' routes to rule-based classifier."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("tắt quạt")
        
        assert result["classifier_type"] == "rule"
        assert result["confidence"] == 1.0
    
    def test_mo_cua_routes_to_rule_based(self):
        """Test that 'mở cửa' routes to rule-based classifier."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("mở cửa")
        
        assert result["classifier_type"] == "rule"
        assert result["confidence"] == 1.0
    
    def test_toi_qua_routes_to_ml_based(self):
        """Test that 'tối quá' routes to ML-based classifier."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("tối quá")
        
        assert result["classifier_type"] == "ml"
        assert result["confidence"] == 0.95
    
    def test_ngot_ngat_routes_to_ml_based(self):
        """Test that 'ngột ngạt' routes to ML-based classifier."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("ngột ngạt")
        
        assert result["classifier_type"] == "ml"
        assert result["confidence"] == 0.95


# ============================================================================
# UNIT TESTS: CONFIDENCE COMPARISON
# ============================================================================

class TestHybridClassifierConfidenceComparison:
    """Unit tests for confidence comparison logic."""
    
    def test_returns_highest_confidence_result(self):
        """Test that hybrid classifier returns result with highest confidence."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Rule-based returns 1.0, ML returns 0.50
        result = hybrid.classify("bật đèn")
        
        assert result["confidence"] == 1.0
        assert result["classifier_type"] == "rule"
    
    def test_ml_wins_when_higher_confidence(self):
        """Test that ML result is returned when it has higher confidence."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Natural language: ML returns 0.95, rule-based returns None
        result = hybrid.classify("nóng quá")
        
        assert result["confidence"] == 0.95
        assert result["classifier_type"] == "ml"
    
    def test_rule_based_perfect_confidence_returns_immediately(self):
        """Test that rule-based with confidence=1.0 returns immediately."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Simple command with perfect match
        result = hybrid.classify("tắt quạt")
        
        # Should return immediately without calling ML classifier
        assert result["confidence"] == 1.0
        assert result["classifier_type"] == "rule"
    
    def test_ambiguous_input_uses_ml_confidence(self):
        """Test that ambiguous input uses ML classifier's confidence."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Ambiguous: "nhiệt độ" - rule-based returns None, ML returns 0.65
        result = hybrid.classify("nhiệt độ bao nhiêu")
        
        assert result["classifier_type"] == "ml"
        assert result["confidence"] == 0.65


# ============================================================================
# UNIT TESTS: FALLBACK STRATEGY
# ============================================================================

class TestHybridClassifierFallbackStrategy:
    """Unit tests for fallback strategy when ML fails."""
    
    def test_ml_failure_fallback_to_rule_based(self):
        """Test that ML failure falls back to rule-based result."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier(should_fail=True)
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Simple command: rule-based should work, ML will fail
        result = hybrid.classify("bật đèn")
        
        # Should fallback to rule-based result
        assert result["classifier_type"] == "rule"
        assert result["confidence"] == 1.0
    
    def test_ml_failure_with_no_rule_match_returns_unknown(self):
        """Test that ML failure with no rule match returns unknown."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier(should_fail=True)
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Natural language: rule-based returns None, ML fails
        result = hybrid.classify("nóng quá")
        
        # Should return unknown with fallback classifier_type
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["classifier_type"] == "fallback"
        assert "error" in result
    
    def test_both_classifiers_fail_returns_unknown(self):
        """Test that both classifiers failing returns unknown."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier(should_fail=True)
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Text that doesn't match any pattern
        result = hybrid.classify("xyz abc 123")
        
        assert result["intent"] == "unknown"
        assert result["confidence"] == 0.0
        assert result["classifier_type"] == "fallback"
    
    def test_ml_failure_preserves_rule_based_entities(self):
        """Test that ML failure preserves rule-based entities."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier(should_fail=True)
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("bật đèn")
        
        # Should have entities from rule-based classifier
        assert "entities" in result
        assert result["classifier_type"] == "rule"


# ============================================================================
# UNIT TESTS: should_use_rule_based() METHOD
# ============================================================================

class TestShouldUseRuleBased:
    """Unit tests for should_use_rule_based() method."""
    
    def test_bat_den_should_use_rule_based(self):
        """Test that 'bật đèn' should use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("bật đèn") is True
    
    def test_tat_quat_should_use_rule_based(self):
        """Test that 'tắt quạt' should use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("tắt quạt") is True
    
    def test_mo_cua_should_use_rule_based(self):
        """Test that 'mở cửa' should use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("mở cửa") is True
    
    def test_dong_mai_che_should_use_rule_based(self):
        """Test that 'đóng mái che' should use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("đóng mái che") is True
    
    def test_di_ngu_should_use_rule_based(self):
        """Test that 'đi ngủ' should use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("đi ngủ") is True
    
    def test_thuc_day_should_use_rule_based(self):
        """Test that 'thức dậy' should use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("thức dậy") is True
    
    def test_xem_phim_should_use_rule_based(self):
        """Test that 'xem phim' should use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("xem phim") is True
    
    def test_nong_qua_should_not_use_rule_based(self):
        """Test that 'nóng quá' should NOT use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("nóng quá") is False
    
    def test_toi_qua_should_not_use_rule_based(self):
        """Test that 'tối quá' should NOT use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("tối quá") is False
    
    def test_ngot_ngat_should_not_use_rule_based(self):
        """Test that 'ngột ngạt' should NOT use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        assert hybrid.should_use_rule_based("ngột ngạt") is False
    
    def test_long_sentence_should_not_use_rule_based(self):
        """Test that long sentences should NOT use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        long_text = "bật đèn phòng khách và tắt quạt phòng ngủ rồi đóng cửa ban công"
        
        # Even though it has action words, it's too long (>10 words)
        assert hybrid.should_use_rule_based(long_text) is False
    
    def test_short_natural_language_should_not_use_rule_based(self):
        """Test that short natural language without actions should NOT use rule-based."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        # Short but no action words or scene keywords
        assert hybrid.should_use_rule_based("nhiệt độ") is False
        assert hybrid.should_use_rule_based("độ ẩm") is False


# ============================================================================
# UNIT TESTS: EDGE CASES
# ============================================================================

class TestHybridClassifierEdgeCases:
    """Unit tests for edge cases."""
    
    def test_empty_text(self):
        """Test classification with empty text."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("")
        
        # Should return unknown
        assert result["intent"] == "unknown"
        assert result["confidence"] <= 0.30
    
    def test_very_long_text(self):
        """Test classification with very long text."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        long_text = " ".join(["bật đèn"] * 50)
        result = hybrid.classify(long_text)
        
        # Should not use rule-based due to length
        assert result is not None
    
    def test_special_characters(self):
        """Test classification with special characters."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("bật đèn!!!")
        
        # Should still work
        assert result is not None
    
    def test_case_insensitive(self):
        """Test that classification is case-insensitive."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result1 = hybrid.classify("BẬT ĐÈN")
        result2 = hybrid.classify("bật đèn")
        
        # Both should return same intent
        assert result1["intent"] == result2["intent"]
    
    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("  bật đèn  ")
        
        assert result is not None
        assert result["classifier_type"] == "rule"
    
    def test_context_passed_to_ml_classifier(self):
        """Test that device context is passed to ML classifier."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = Mock()
        ml_classifier.classify = Mock(return_value={
            "intent": "control_device",
            "entities": {},
            "confidence": 0.85,
            "classifier_type": "ml"
        })
        
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        context = {
            "current_room": "living_room",
            "devices": [{"id": "light_1", "type": "light", "state": "off"}]
        }
        
        result = hybrid.classify("nóng quá", context=context)
        
        # Verify ML classifier was called with context
        ml_classifier.classify.assert_called_once_with("nóng quá", context)


# ============================================================================
# UNIT TESTS: INTEGRATION SCENARIOS
# ============================================================================

class TestHybridClassifierIntegration:
    """Integration tests for realistic scenarios."""
    
    def test_simple_command_with_location(self):
        """Test simple command with location."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("bật đèn phòng khách")
        
        assert result["classifier_type"] == "rule"
        assert result["confidence"] == 1.0
    
    def test_natural_language_comfort_request(self):
        """Test natural language comfort request."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("trời nóng quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["classifier_type"] == "ml"
        assert result["confidence"] >= 0.90
    
    def test_query_sensor_request(self):
        """Test query sensor request."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("nhiệt độ phòng khách bao nhiêu")
        
        assert result["intent"] == "query_sensor"
        assert result["classifier_type"] == "ml"
    
    def test_scene_activation(self):
        """Test scene activation."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        result = hybrid.classify("đi ngủ")
        
        assert result["intent"] == "activate_scene"
        assert result["classifier_type"] == "rule"
        assert result["confidence"] == 1.0
    
    def test_multiple_simple_commands(self):
        """Test multiple simple commands return consistent results."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        commands = ["bật đèn", "tắt quạt", "mở cửa", "đóng mái che"]
        
        for command in commands:
            result = hybrid.classify(command)
            assert result["classifier_type"] == "rule"
            assert result["confidence"] == 1.0
    
    def test_multiple_natural_language_requests(self):
        """Test multiple natural language requests."""
        rule_classifier = MockRuleBasedClassifier()
        ml_classifier = MockMLBasedClassifier()
        hybrid = HybridClassifier(rule_classifier, ml_classifier)
        
        requests = ["nóng quá", "lạnh quá", "tối quá", "ngột ngạt"]
        
        for request in requests:
            result = hybrid.classify(request)
            assert result["classifier_type"] == "ml"
            assert result["confidence"] >= 0.90
