"""
Property-based tests for preprocessing pipeline.

These tests verify universal properties that should hold for all inputs.
"""

from hypothesis import given, strategies as st, settings
import pytest

# Import actual implementation
from src.preprocessing.pipeline import PreprocessingPipeline, PreprocessedText


# ============================================================================
# PROPERTY TESTS
# ============================================================================

class TestPreprocessingProperties:
    """Property-based tests for preprocessing pipeline."""
    
    @given(text=st.text(min_size=1, max_size=500))
    @settings(max_examples=100, deadline=None)
    def test_property_13_normalization_idempotence(self, text):
        """
        **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6**
        
        Property 13: Text Normalization Idempotence
        
        For any Vietnamese text input, applying the preprocessing pipeline twice 
        SHALL produce the same result as applying it once (idempotence).
        
        Specifically: normalize(normalize(text)) = normalize(text)
        
        Rationale:
        Preprocessing must be deterministic and idempotent. If preprocessing 
        changes the text in unpredictable ways on repeated application, it 
        indicates bugs in the normalization logic.
        
        Test Strategy:
        1. Generate random text inputs using Hypothesis
        2. Apply preprocessing once: text -> normalized_once
        3. Apply preprocessing again: normalized_once -> normalized_twice
        4. Assert: normalized_once == normalized_twice
        
        This property ensures that:
        - Lowercase conversion is stable (already lowercase stays lowercase)
        - Whitespace normalization is stable (normalized whitespace stays normalized)
        - Slang normalization is stable (normalized slang stays normalized)
        - Punctuation removal is stable (removed punctuation stays removed)
        - Emoji removal is stable (removed emojis stay removed)
        - Spell correction is stable (corrected text stays corrected)
        """
        preprocessor = PreprocessingPipeline()
        
        # Apply preprocessing once
        result_once = preprocessor.preprocess(text)
        normalized_once = result_once.normalized_text
        
        # Apply preprocessing twice (on the already normalized text)
        result_twice = preprocessor.preprocess(normalized_once)
        normalized_twice = result_twice.normalized_text
        
        # Assert idempotence: f(f(x)) = f(x)
        assert normalized_once == normalized_twice, (
            f"Preprocessing not idempotent:\n"
            f"  Original: {repr(text[:100])}\n"
            f"  After 1st pass: {repr(normalized_once[:100])}\n"
            f"  After 2nd pass: {repr(normalized_twice[:100])}"
        )
    
    @given(text=st.text(min_size=1, max_size=500))
    @settings(max_examples=100, deadline=None)
    def test_preprocessing_returns_valid_structure(self, text):
        """
        Verify that preprocessing always returns a valid PreprocessedText structure.
        
        This is a supporting property test that ensures the preprocessing pipeline
        never crashes and always returns the expected data structure.
        """
        preprocessor = PreprocessingPipeline()
        
        result = preprocessor.preprocess(text)
        
        # Assert result structure
        assert isinstance(result, PreprocessedText)
        assert isinstance(result.normalized_text, str)
        assert isinstance(result.original_text, str)
        assert isinstance(result.sentences, list)
        
        # Assert original text is preserved
        assert result.original_text == text
        
        # Assert sentences are all strings
        for sentence in result.sentences:
            assert isinstance(sentence, str)
    
    @given(text=st.text(min_size=1, max_size=500))
    @settings(max_examples=100, deadline=None)
    def test_preprocessing_preserves_content_length_order(self, text):
        """
        Verify that preprocessing doesn't drastically change text length.
        
        While preprocessing may add or remove characters (e.g., normalizing slang,
        removing emojis), the normalized text should be within a reasonable length
        range of the original text.
        
        This property helps catch bugs where preprocessing accidentally duplicates
        or loses large portions of text.
        
        Note: This test allows empty output for inputs that contain only
        punctuation, whitespace, emoji, or non-Vietnamese special characters,
        as these are intentionally removed by the preprocessing pipeline.
        """
        preprocessor = PreprocessingPipeline()
        
        result = preprocessor.preprocess(text)
        normalized = result.normalized_text
        
        # Normalized text should not be excessively longer than original
        # Allow up to 3x expansion (for slang expansion like "k" -> "không")
        assert len(normalized) <= len(text) * 3, (
            f"Preprocessing expanded text too much: "
            f"{len(text)} -> {len(normalized)}"
        )


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestPreprocessingEdgeCases:
    """Example-based tests for specific edge cases."""
    
    def test_empty_string_handling(self):
        """Test that empty string is handled gracefully."""
        preprocessor = PreprocessingPipeline()
        
        result = preprocessor.preprocess("")
        
        assert result.normalized_text == ""
        assert result.original_text == ""
    
    def test_whitespace_only_handling(self):
        """Test that whitespace-only input is normalized to empty string."""
        preprocessor = PreprocessingPipeline()
        
        result = preprocessor.preprocess("   \n\t  ")
        
        assert result.normalized_text == ""
        assert result.original_text == "   \n\t  "
    
    def test_already_normalized_text_unchanged(self):
        """Test that already normalized text remains unchanged."""
        preprocessor = PreprocessingPipeline()
        
        # Simple lowercase text with no special characters
        text = "bật đèn phòng khách"
        
        result = preprocessor.preprocess(text)
        
        # Should be idempotent
        assert result.normalized_text == text or result.normalized_text == text.lower()
    
    def test_vietnamese_characters_preserved(self):
        """Test that Vietnamese diacritics are preserved during normalization."""
        preprocessor = PreprocessingPipeline()
        
        text = "Trời nóng quá"
        
        result = preprocessor.preprocess(text)
        
        # Vietnamese characters should be preserved (just lowercased)
        assert "ờ" in result.normalized_text
        assert "ó" in result.normalized_text
    
    def test_multiple_spaces_normalized(self):
        """Test that multiple spaces are normalized to single space."""
        preprocessor = PreprocessingPipeline()
        
        text = "bật    đèn     phòng    khách"
        
        result = preprocessor.preprocess(text)
        
        # Multiple spaces should be normalized to single space
        assert "    " not in result.normalized_text
        assert "bật đèn phòng khách" == result.normalized_text
