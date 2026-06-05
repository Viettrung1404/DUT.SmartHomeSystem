"""
Unit tests for Multi-Intent Handling.

Tests the sentence splitting, multiple intent classification, and response ordering
for multi-intent requests.

**Validates: Requirements 8.1-8.4**
"""

import pytest
from src.preprocessing.pipeline import split_sentences, SENTENCE_SPLIT_KEYWORDS
from src.classifiers.rule_based import RuleBasedClassifier
from src.models.schemas import IntentResponse, MultiIntentResponse


class TestSentenceSplitting:
    """Unit tests for sentence splitting functionality."""
    
    def test_split_with_va(self):
        """Test splitting with 'và' (and)."""
        text = "bật đèn và tắt quạt"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 2
        assert "bật đèn" in sentences[0].lower()
        assert "tắt quạt" in sentences[1].lower()
    
    def test_split_with_roi(self):
        """Test splitting with 'rồi' (then)."""
        text = "đi ngủ rồi tắt đèn"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 2
        assert "đi ngủ" in sentences[0].lower()
        assert "tắt đèn" in sentences[1].lower()
    
    def test_split_with_sau_do(self):
        """Test splitting with 'sau đó' (after that)."""
        text = "bật đèn sau đó xem phim"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 2
        assert "bật đèn" in sentences[0].lower()
        assert "xem phim" in sentences[1].lower()
    
    def test_split_with_xong(self):
        """Test splitting with 'xong' (done/finished)."""
        text = "tắt quạt xong về nhà"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 2
        assert "tắt quạt" in sentences[0].lower()
        assert "về nhà" in sentences[1].lower()
    
    def test_split_three_sentences(self):
        """Test splitting into 3 sentences."""
        text = "bật đèn và tắt quạt rồi đi ngủ"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 3
        assert "bật đèn" in sentences[0].lower()
        assert "tắt quạt" in sentences[1].lower()
        assert "đi ngủ" in sentences[2].lower()
    
    def test_split_four_sentences(self):
        """Test splitting into 4 sentences."""
        text = "bật đèn và tắt quạt rồi đi ngủ xong về nhà"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 4
        assert "bật đèn" in sentences[0].lower()
        assert "tắt quạt" in sentences[1].lower()
        assert "đi ngủ" in sentences[2].lower()
        assert "về nhà" in sentences[3].lower()
    
    def test_no_split_without_keywords(self):
        """Test that text without splitting keywords is not split."""
        text = "bật đèn phòng khách"
        sentences = split_sentences(text)
        
        assert len(sentences) == 1
        assert "bật đèn" in sentences[0].lower()
    
    def test_split_with_multiple_va(self):
        """Test splitting with multiple 'và' keywords."""
        text = "bật đèn và tắt quạt và đi ngủ"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 3
        assert "bật đèn" in sentences[0].lower()
        assert "tắt quạt" in sentences[1].lower()
        assert "đi ngủ" in sentences[2].lower()
    
    def test_split_with_mixed_keywords(self):
        """Test splitting with mixed keywords."""
        text = "bật đèn và tắt quạt sau đó đi ngủ"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 3
        assert "bật đèn" in sentences[0].lower()
        assert "tắt quạt" in sentences[1].lower()
        assert "đi ngủ" in sentences[2].lower()
    
    def test_split_preserves_order(self):
        """Test that splitting preserves sentence order."""
        text = "đi ngủ và về nhà"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 2
        # First sentence should be "đi ngủ"
        assert sentences[0].lower().startswith("đi ngủ") or "đi ngủ" in sentences[0].lower()
        # Second sentence should be "về nhà"
        assert "về nhà" in sentences[1].lower()
    
    def test_split_handles_whitespace(self):
        """Test that splitting handles extra whitespace."""
        text = "bật đèn   và   tắt quạt"
        sentences = split_sentences(text)
        
        assert len(sentences) >= 2
        # Each sentence should be trimmed
        for sentence in sentences:
            assert sentence == sentence.strip()
    
    def test_split_with_punctuation(self):
        """Test splitting with punctuation."""
        text = "bật đèn, và tắt quạt."
        sentences = split_sentences(text)
        
        assert len(sentences) >= 2
    
    def test_sentence_split_keywords_constant(self):
        """Test that SENTENCE_SPLIT_KEYWORDS constant is defined."""
        assert SENTENCE_SPLIT_KEYWORDS is not None
        assert isinstance(SENTENCE_SPLIT_KEYWORDS, list)
        assert len(SENTENCE_SPLIT_KEYWORDS) > 0
        
        # Check that expected keywords are present
        expected_keywords = ["và", "rồi", "sau đó", "xong"]
        for keyword in expected_keywords:
            assert keyword in SENTENCE_SPLIT_KEYWORDS, \
                f"Expected keyword '{keyword}' in SENTENCE_SPLIT_KEYWORDS"


class TestMultiIntentClassification:
    """Unit tests for multi-intent classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = RuleBasedClassifier()
    
    def test_classify_two_intents(self):
        """Test classifying text with 2 intents."""
        text = "bật đèn và tắt quạt"
        sentences = split_sentences(text)
        
        # Classify each sentence
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Should have 2 results
        assert len(results) >= 2
        
        # First should be control_device with turn_on + light
        assert results[0].intent == "control_device"
        assert results[0].entities["action"] == "turn_on"
        assert results[0].entities["device"] == "light"
        
        # Second should be control_device with turn_off + fan
        assert results[1].intent == "control_device"
        assert results[1].entities["action"] == "turn_off"
        assert results[1].entities["device"] == "fan"
    
    def test_classify_three_intents(self):
        """Test classifying text with 3 intents."""
        text = "bật đèn và tắt quạt rồi đi ngủ"
        sentences = split_sentences(text)
        
        # Classify each sentence
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Should have 3 results
        assert len(results) >= 3
        
        # First: control_device
        assert results[0].intent == "control_device"
        
        # Second: control_device
        assert results[1].intent == "control_device"
        
        # Third: activate_scene
        assert results[2].intent == "activate_scene"
        assert results[2].entities["scene_type"] == "sleep"
    
    def test_classify_mixed_intents(self):
        """Test classifying text with different intent types."""
        text = "bật đèn và đi ngủ"
        sentences = split_sentences(text)
        
        # Classify each sentence
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Should have 2 results
        assert len(results) >= 2
        
        # First: control_device
        assert results[0].intent == "control_device"
        
        # Second: activate_scene
        assert results[1].intent == "activate_scene"
    
    def test_order_preservation(self):
        """Test that intent order is preserved."""
        text = "đi ngủ và về nhà"
        sentences = split_sentences(text)
        
        # Classify each sentence
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Should have 2 results
        assert len(results) >= 2
        
        # First should be sleep scene
        assert results[0].intent == "activate_scene"
        assert results[0].entities["scene_type"] == "sleep"
        
        # Second should be home scene
        assert results[1].intent == "activate_scene"
        assert results[1].entities["scene_type"] == "home"
    
    def test_confidence_scores(self):
        """Test that each intent has confidence score."""
        text = "bật đèn và tắt quạt"
        sentences = split_sentences(text)
        
        # Classify each sentence
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Each result should have confidence
        for result in results:
            assert hasattr(result, 'confidence')
            assert 0.0 <= result.confidence <= 1.0
    
    def test_classifier_type(self):
        """Test that each intent has classifier_type."""
        text = "bật đèn và tắt quạt"
        sentences = split_sentences(text)
        
        # Classify each sentence
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Each result should have classifier_type
        for result in results:
            assert hasattr(result, 'classifier_type')
            assert result.classifier_type in ["rule", "ml"]


class TestMultiIntentResponseOrdering:
    """Unit tests for multi-intent response ordering."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = RuleBasedClassifier()
    
    def test_response_order_matches_text_order(self):
        """Test that response order matches text order."""
        text = "bật đèn và tắt quạt rồi đi ngủ"
        sentences = split_sentences(text)
        
        # Classify each sentence in order
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Verify order
        assert len(results) >= 3
        
        # Order should be: control_device (turn_on light), control_device (turn_off fan), activate_scene (sleep)
        assert results[0].intent == "control_device"
        assert results[0].entities["action"] == "turn_on"
        
        assert results[1].intent == "control_device"
        assert results[1].entities["action"] == "turn_off"
        
        assert results[2].intent == "activate_scene"
        assert results[2].entities["scene_type"] == "sleep"
    
    def test_reverse_order(self):
        """Test that reverse order is preserved."""
        text = "đi ngủ rồi tắt đèn"
        sentences = split_sentences(text)
        
        # Classify each sentence in order
        results = []
        for sentence in sentences:
            result = self.classifier.classify(sentence.strip())
            if result:
                results.append(result)
        
        # Verify order
        assert len(results) >= 2
        
        # Order should be: activate_scene (sleep), control_device (turn_off light)
        assert results[0].intent == "activate_scene"
        assert results[0].entities["scene_type"] == "sleep"
        
        assert results[1].intent == "control_device"
        assert results[1].entities["action"] == "turn_off"


class TestMultiIntentEdgeCases:
    """Unit tests for multi-intent edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = RuleBasedClassifier()
    
    def test_empty_sentence_after_split(self):
        """Test handling of empty sentences after splitting."""
        text = "bật đèn và "
        sentences = split_sentences(text)
        
        # Should handle gracefully
        results = []
        for sentence in sentences:
            if sentence.strip():  # Skip empty sentences
                result = self.classifier.classify(sentence.strip())
                if result:
                    results.append(result)
        
        # Should have at least 1 result
        assert len(results) >= 1
    
    def test_single_intent_not_split(self):
        """Test that single intent is not split."""
        text = "bật đèn phòng khách"
        sentences = split_sentences(text)
        
        # Should return single sentence
        assert len(sentences) == 1
        
        # Classify
        result = self.classifier.classify(sentences[0].strip())
        assert result is not None
        assert result.intent == "control_device"
    
    def test_splitting_keyword_at_start(self):
        """Test handling of splitting keyword at start."""
        text = "và bật đèn"
        sentences = split_sentences(text)
        
        # Should handle gracefully
        results = []
        for sentence in sentences:
            if sentence.strip():
                result = self.classifier.classify(sentence.strip())
                if result:
                    results.append(result)
        
        # Should have at least 1 result
        assert len(results) >= 1
    
    def test_splitting_keyword_at_end(self):
        """Test handling of splitting keyword at end."""
        text = "bật đèn và"
        sentences = split_sentences(text)
        
        # Should handle gracefully
        results = []
        for sentence in sentences:
            if sentence.strip():
                result = self.classifier.classify(sentence.strip())
                if result:
                    results.append(result)
        
        # Should have at least 1 result
        assert len(results) >= 1
    
    def test_consecutive_splitting_keywords(self):
        """Test handling of consecutive splitting keywords."""
        text = "bật đèn và rồi tắt quạt"
        sentences = split_sentences(text)
        
        # Should handle gracefully
        results = []
        for sentence in sentences:
            if sentence.strip():
                result = self.classifier.classify(sentence.strip())
                if result:
                    results.append(result)
        
        # Should have at least 2 results
        assert len(results) >= 2
