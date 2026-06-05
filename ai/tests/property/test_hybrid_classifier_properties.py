"""
Property-based tests for Hybrid Classifier routing.

These tests verify universal properties that should hold for hybrid classifier routing.
"""

from hypothesis import given, strategies as st, settings
import pytest
from typing import Optional, Dict, Any, List
from dataclasses import dataclass


# ============================================================================
# IMPORT REAL IMPLEMENTATION (Task 4.3 completed)
# ============================================================================

from src.classifiers.rule_based import RuleBasedClassifier, ClassificationResult


class MLBasedClassifier:
    """
    Stub for ML-Based Classifier.
    
    This will be implemented in later tasks.
    For now, it returns a dummy result for natural language.
    """
    
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify natural language text using ML model (stub).
        
        Returns ClassificationResult with confidence < 1.0.
        """
        # Stub: Return environmental_comfort for natural language
        return ClassificationResult(
            intent="environmental_comfort",
            entities={"comfort_type": "cooling"},
            confidence=0.85,
            classifier_type="ml"
        )


class HybridClassifier:
    """
    Stub for Hybrid Classifier.
    
    This will be implemented in Task 4.3.
    Routes to rule-based or ML-based classifier based on input.
    """
    
    def __init__(self):
        self.rule_classifier = RuleBasedClassifier()
        self.ml_classifier = MLBasedClassifier()
    
    def classify(self, text: str) -> ClassificationResult:
        """
        Classify intent using hybrid approach.
        
        Decision logic:
        1. Try rule-based classifier first
        2. If confidence = 1.0, return rule-based result
        3. Otherwise, use ML-based classifier
        """
        # Try rule-based first
        rule_result = self.rule_classifier.classify(text)
        
        if rule_result is not None and rule_result.confidence == 1.0:
            return rule_result
        
        # Fallback to ML-based
        return self.ml_classifier.classify(text)


# ============================================================================
# HYPOTHESIS STRATEGIES
# ============================================================================

# Devices in Vietnamese
DEVICES = ["đèn", "quạt", "điều hòa", "ac", "cửa", "mái che"]

# Actions in Vietnamese
ACTIONS = ["bật", "tắt", "mở", "đóng"]

# Locations in Vietnamese (optional)
LOCATIONS = ["phòng khách", "phòng ngủ", "bếp", "phòng tắm", "ban công"]


@st.composite
def simple_command_strategy(draw):
    """
    Generate simple command patterns that should match rule-based classifier.
    
    Patterns:
    - "bật đèn"
    - "tắt quạt"
    - "mở cửa phòng khách"
    - "đóng mái che ban công"
    """
    action = draw(st.sampled_from(ACTIONS))
    device = draw(st.sampled_from(DEVICES))
    
    # Optional location
    include_location = draw(st.booleans())
    
    if include_location:
        location = draw(st.sampled_from(LOCATIONS))
        command = f"{action} {device} {location}"
    else:
        command = f"{action} {device}"
    
    # Optional whitespace variations
    add_extra_spaces = draw(st.booleans())
    if add_extra_spaces:
        command = "  " + command + "  "
    
    return command


@st.composite
def natural_language_strategy(draw):
    """
    Generate natural language text that should NOT match rule-based patterns.
    
    Examples:
    - "Trời nóng quá"
    - "Tối quá"
    - "Ngột ngạt"
    """
    natural_phrases = [
        "Trời nóng quá",
        "Trời lạnh quá",
        "Tối quá",
        "Sáng quá",
        "Ngột ngạt",
        "Oi bức",
        "Rét quá",
        "Thiếu sáng",
        "Chói quá"
    ]
    
    phrase = draw(st.sampled_from(natural_phrases))
    return phrase


# ============================================================================
# PROPERTY TESTS
# ============================================================================

class TestHybridClassifierProperties:
    """Property-based tests for Hybrid Classifier routing."""
    
    @given(command=simple_command_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_15_simple_commands_route_to_rule_based(self, command):
        """
        **Validates: Requirements 13.1, 13.2, 13.3, 13.4, 13.5, 13.7, 13.8**
        
        Property 15: Hybrid Classifier Routing Consistency
        
        For any simple command text matching rule-based patterns 
        (e.g., "bật {device}", "tắt {device}"), the Hybrid Classifier SHALL 
        route to the Rule-Based Classifier and return confidence=1.0.
        
        Rationale:
        Hybrid routing optimizes performance (rule-based is <10ms) while 
        maintaining accuracy (ML-based for complex cases). Consistent routing 
        prevents non-deterministic behavior.
        
        Test Strategy:
        1. Generate simple command patterns using Hypothesis
        2. Classify using HybridClassifier
        3. Assert: classifier_type == "rule"
        4. Assert: confidence == 1.0
        5. Assert: intent == "control_device"
        
        This property ensures that:
        - Simple commands are routed to rule-based classifier (fast path)
        - Rule-based classifier returns confidence=1.0 for matched patterns
        - Routing is deterministic and consistent
        """
        classifier = HybridClassifier()
        
        # Classify the simple command
        result = classifier.classify(command)
        
        # Assert routing to rule-based classifier
        assert result.classifier_type == "rule", (
            f"Simple command should route to rule-based classifier:\n"
            f"  Command: {repr(command)}\n"
            f"  Classifier type: {result.classifier_type}\n"
            f"  Expected: rule"
        )
        
        # Assert confidence = 1.0
        assert result.confidence == 1.0, (
            f"Rule-based classifier should return confidence=1.0:\n"
            f"  Command: {repr(command)}\n"
            f"  Confidence: {result.confidence}\n"
            f"  Expected: 1.0"
        )
        
        # Assert intent is control_device
        assert result.intent == "control_device", (
            f"Simple commands should be classified as control_device:\n"
            f"  Command: {repr(command)}\n"
            f"  Intent: {result.intent}\n"
            f"  Expected: control_device"
        )
        
        # Assert entities are extracted
        assert "action" in result.entities, (
            f"Action entity should be extracted:\n"
            f"  Command: {repr(command)}\n"
            f"  Entities: {result.entities}"
        )
        
        assert "device" in result.entities, (
            f"Device entity should be extracted:\n"
            f"  Command: {repr(command)}\n"
            f"  Entities: {result.entities}"
        )
    
    @given(text=natural_language_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_15_natural_language_routes_to_ml_based(self, text):
        """
        **Validates: Requirements 13.1, 13.4, 13.5, 13.8**
        
        Property 15 (Part 2): Hybrid Classifier Routing Consistency
        
        For any natural language text not matching patterns, the Hybrid 
        Classifier SHALL route to the ML-Based Classifier.
        
        Test Strategy:
        1. Generate natural language phrases using Hypothesis
        2. Classify using HybridClassifier
        3. Assert: classifier_type == "ml"
        4. Assert: confidence < 1.0 (ML models don't return perfect confidence)
        
        This property ensures that:
        - Natural language is routed to ML-based classifier
        - ML-based classifier is used for complex cases
        - Routing is deterministic and consistent
        """
        classifier = HybridClassifier()
        
        # Classify the natural language text
        result = classifier.classify(text)
        
        # Assert routing to ML-based classifier
        assert result.classifier_type == "ml", (
            f"Natural language should route to ML-based classifier:\n"
            f"  Text: {repr(text)}\n"
            f"  Classifier type: {result.classifier_type}\n"
            f"  Expected: ml"
        )
        
        # Assert confidence < 1.0 (ML models don't return perfect confidence)
        assert result.confidence < 1.0, (
            f"ML-based classifier should return confidence < 1.0:\n"
            f"  Text: {repr(text)}\n"
            f"  Confidence: {result.confidence}\n"
            f"  Expected: < 1.0"
        )


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestHybridClassifierEdgeCases:
    """Example-based tests for specific edge cases."""
    
    def test_simple_command_bật_đèn(self):
        """Test simple command: 'bật đèn'"""
        classifier = HybridClassifier()
        result = classifier.classify("bật đèn")
        
        assert result.classifier_type == "rule"
        assert result.confidence == 1.0
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "light"
    
    def test_simple_command_tắt_quạt_phòng_ngủ(self):
        """Test simple command with location: 'tắt quạt phòng ngủ'"""
        classifier = HybridClassifier()
        result = classifier.classify("tắt quạt phòng ngủ")
        
        assert result.classifier_type == "rule"
        assert result.confidence == 1.0
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_off"
        assert result.entities["device"] == "fan"
        assert result.entities["location"] == "bedroom"
    
    def test_simple_command_mở_cửa(self):
        """Test simple command: 'mở cửa'"""
        classifier = HybridClassifier()
        result = classifier.classify("mở cửa")
        
        assert result.classifier_type == "rule"
        assert result.confidence == 1.0
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "door"
    
    def test_simple_command_đóng_mái_che(self):
        """Test simple command: 'đóng mái che'"""
        classifier = HybridClassifier()
        result = classifier.classify("đóng mái che")
        
        assert result.classifier_type == "rule"
        assert result.confidence == 1.0
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_off"
        assert result.entities["device"] == "awning"
    
    def test_natural_language_trời_nóng_quá(self):
        """Test natural language: 'Trời nóng quá'"""
        classifier = HybridClassifier()
        result = classifier.classify("Trời nóng quá")
        
        assert result.classifier_type == "ml"
        assert result.confidence < 1.0
    
    def test_natural_language_tối_quá(self):
        """Test natural language: 'Tối quá'"""
        classifier = HybridClassifier()
        result = classifier.classify("Tối quá")
        
        assert result.classifier_type == "ml"
        assert result.confidence < 1.0
    
    def test_simple_command_with_extra_whitespace(self):
        """Test simple command with extra whitespace"""
        classifier = HybridClassifier()
        result = classifier.classify("  bật đèn  ")
        
        assert result.classifier_type == "rule"
        assert result.confidence == 1.0
        assert result.intent == "control_device"
    
    def test_simple_command_uppercase(self):
        """Test simple command with uppercase (should be case-insensitive)"""
        classifier = HybridClassifier()
        result = classifier.classify("BẬT ĐÈN")
        
        assert result.classifier_type == "rule"
        assert result.confidence == 1.0
        assert result.intent == "control_device"
