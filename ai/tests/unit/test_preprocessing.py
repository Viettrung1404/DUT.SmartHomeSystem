"""
Unit tests for preprocessing functions.

**Validates: Requirements 14.1-14.7**

These tests verify specific Vietnamese examples for each preprocessing function:
- Lowercase conversion (14.1)
- Slang normalization (14.3)
- Punctuation removal (14.2)
- Emoji and special character removal (14.4)
- Spell correction (14.6)
- Sentence splitting (14.7)

Following TDD approach: tests are written before implementation.
"""

import pytest

# Import actual implementation
from src.preprocessing.pipeline import (
    lowercase_text,
    normalize_slang,
    remove_punctuation,
    remove_emoji,
    correct_spelling,
    split_sentences
)


# ============================================================================
# UNIT TESTS
# ============================================================================

class TestLowercaseConversion:
    """
    **Validates: Requirement 14.1**
    
    Test lowercase conversion for Vietnamese text.
    """
    
    def test_uppercase_to_lowercase(self):
        """Test converting uppercase Vietnamese text to lowercase."""
        text = "BẬT ĐÈN PHÒNG KHÁCH"
        result = lowercase_text(text)
        assert result == "bật đèn phòng khách"
    
    def test_mixed_case_to_lowercase(self):
        """Test converting mixed case text to lowercase."""
        text = "Trời Nóng Quá"
        result = lowercase_text(text)
        assert result == "trời nóng quá"
    
    def test_already_lowercase_unchanged(self):
        """Test that already lowercase text remains unchanged."""
        text = "tắt quạt phòng ngủ"
        result = lowercase_text(text)
        assert result == "tắt quạt phòng ngủ"
    
    def test_vietnamese_diacritics_preserved(self):
        """Test that Vietnamese diacritics are preserved during lowercase."""
        text = "ĐIỀU HÒA"
        result = lowercase_text(text)
        assert result == "điều hòa"
        # Verify diacritics are still present
        assert "ề" in result
        assert "ò" in result


class TestSlangNormalization:
    """
    **Validates: Requirement 14.3**
    
    Test slang normalization for Vietnamese text.
    Slang mappings from design.md:
    - k/ko/hok → không
    - đc/dc → được
    - vs → với
    - j → gì
    - tks/thanks → cảm ơn
    - ok/oke → được
    """
    
    def test_normalize_k_to_khong(self):
        """Test normalizing 'k' to 'không'."""
        text = "k bật đèn"
        result = normalize_slang(text)
        assert result == "không bật đèn"
    
    def test_normalize_ko_to_khong(self):
        """Test normalizing 'ko' to 'không'."""
        text = "ko cần quạt"
        result = normalize_slang(text)
        assert result == "không cần quạt"
    
    def test_normalize_hok_to_khong(self):
        """Test normalizing 'hok' to 'không'."""
        text = "hok biết"
        result = normalize_slang(text)
        assert result == "không biết"
    
    def test_normalize_dc_to_duoc(self):
        """Test normalizing 'đc' to 'được'."""
        text = "đc rồi"
        result = normalize_slang(text)
        assert result == "được rồi"
    
    def test_normalize_dc_ascii_to_duoc(self):
        """Test normalizing 'dc' (ASCII) to 'được'."""
        text = "dc không"
        result = normalize_slang(text)
        assert result == "được không"
    
    def test_normalize_vs_to_voi(self):
        """Test normalizing 'vs' to 'với'."""
        text = "bật đèn vs quạt"
        result = normalize_slang(text)
        assert result == "bật đèn với quạt"
    
    def test_normalize_j_to_gi(self):
        """Test normalizing 'j' to 'gì'."""
        text = "làm j"
        result = normalize_slang(text)
        assert result == "làm gì"
    
    def test_normalize_tks_to_cam_on(self):
        """Test normalizing 'tks' to 'cảm ơn'."""
        text = "tks bạn"
        result = normalize_slang(text)
        assert result == "cảm ơn bạn"
    
    def test_normalize_thanks_to_cam_on(self):
        """Test normalizing 'thanks' to 'cảm ơn'."""
        text = "thanks nhiều"
        result = normalize_slang(text)
        assert result == "cảm ơn nhiều"
    
    def test_normalize_ok_to_duoc(self):
        """Test normalizing 'ok' to 'được'."""
        text = "ok luôn"
        result = normalize_slang(text)
        assert result == "được luôn"
    
    def test_normalize_oke_to_duoc(self):
        """Test normalizing 'oke' to 'được'."""
        text = "oke nha"
        result = normalize_slang(text)
        assert result == "được nha"
    
    def test_normalize_multiple_slang(self):
        """Test normalizing multiple slang words in one sentence."""
        text = "k đc vs j"
        result = normalize_slang(text)
        assert result == "không được với gì"
    
    def test_no_slang_unchanged(self):
        """Test that text without slang remains unchanged."""
        text = "bật đèn phòng khách"
        result = normalize_slang(text)
        assert result == "bật đèn phòng khách"


class TestPunctuationRemoval:
    """
    **Validates: Requirement 14.2**
    
    Test punctuation removal while keeping semantic meaning.
    """
    
    def test_remove_exclamation_mark(self):
        """Test removing exclamation mark."""
        text = "Nóng quá!"
        result = remove_punctuation(text)
        assert result == "Nóng quá"
        assert "!" not in result
    
    def test_remove_question_mark(self):
        """Test removing question mark."""
        text = "Nhiệt độ bao nhiêu?"
        result = remove_punctuation(text)
        assert result == "Nhiệt độ bao nhiêu"
        assert "?" not in result
    
    def test_remove_comma(self):
        """Test removing comma."""
        text = "Bật đèn, tắt quạt"
        result = remove_punctuation(text)
        assert "," not in result
    
    def test_remove_period(self):
        """Test removing period."""
        text = "Bật đèn phòng khách."
        result = remove_punctuation(text)
        assert result == "Bật đèn phòng khách"
        assert "." not in result
    
    def test_remove_multiple_punctuation(self):
        """Test removing multiple punctuation marks."""
        text = "Nóng quá! Bật điều hòa đi?"
        result = remove_punctuation(text)
        assert "!" not in result
        assert "?" not in result
    
    def test_keep_numbers_and_units(self):
        """Test that numbers and units are preserved (semantic meaning)."""
        text = "Điều chỉnh 25 độ"
        result = remove_punctuation(text)
        assert "25" in result
        assert "độ" in result
    
    def test_normalize_whitespace_after_removal(self):
        """Test that whitespace is normalized after punctuation removal."""
        text = "Bật đèn,,,   tắt quạt"
        result = remove_punctuation(text)
        # Should not have multiple spaces
        assert "  " not in result


class TestEmojiRemoval:
    """
    **Validates: Requirement 14.4**
    
    Test emoji and special character removal.
    """
    
    def test_remove_emoji_fire(self):
        """Test removing fire emoji."""
        text = "Nóng quá 🔥"
        result = remove_emoji(text)
        assert "🔥" not in result
        assert "Nóng quá" in result
    
    def test_remove_emoji_sun(self):
        """Test removing sun emoji."""
        text = "Trời nắng ☀️"
        result = remove_emoji(text)
        assert "☀️" not in result
        assert "Trời nắng" in result
    
    def test_remove_emoji_snowflake(self):
        """Test removing snowflake emoji."""
        text = "Lạnh quá ❄️"
        result = remove_emoji(text)
        assert "❄️" not in result
        assert "Lạnh quá" in result
    
    def test_remove_multiple_emoji(self):
        """Test removing multiple emoji."""
        text = "Nóng quá 🔥🔥🔥"
        result = remove_emoji(text)
        assert "🔥" not in result
        assert "Nóng quá" in result
    
    def test_remove_emoji_with_text(self):
        """Test removing emoji mixed with text."""
        text = "Bật đèn 💡 phòng khách"
        result = remove_emoji(text)
        assert "💡" not in result
        assert "Bật đèn" in result
        assert "phòng khách" in result
    
    def test_keep_vietnamese_characters(self):
        """Test that Vietnamese characters are not removed."""
        text = "Điều hòa"
        result = remove_emoji(text)
        assert result == "Điều hòa"
        # Verify Vietnamese diacritics are preserved
        assert "ề" in result
        assert "ò" in result
    
    def test_text_without_emoji_unchanged(self):
        """Test that text without emoji remains unchanged."""
        text = "Bật đèn phòng khách"
        result = remove_emoji(text)
        assert result == "Bật đèn phòng khách"


class TestSpellCorrection:
    """
    **Validates: Requirement 14.6**
    
    Test spell correction for common Vietnamese typos.
    """
    
    def test_correct_khong_typo(self):
        """Test correcting 'khong' to 'không'."""
        text = "khong biet"
        result = correct_spelling(text)
        assert result == "không biet"
    
    def test_correct_duoc_typo(self):
        """Test correcting 'duoc' to 'được'."""
        text = "duoc roi"
        result = correct_spelling(text)
        assert result == "được roi"
    
    def test_correct_voi_typo(self):
        """Test correcting 'voi' to 'với'."""
        text = "bat den voi quat"
        result = correct_spelling(text)
        assert result == "bat den với quat"
    
    def test_correct_gi_typo(self):
        """Test correcting 'gi' to 'gì'."""
        text = "lam gi"
        result = correct_spelling(text)
        assert result == "lam gì"
    
    def test_correct_nha_typo(self):
        """Test correcting 'nha' to 'nhà'."""
        text = "ve nha"
        result = correct_spelling(text)
        assert result == "ve nhà"
    
    def test_correct_toi_typo(self):
        """Test correcting 'toi' to 'tôi'."""
        text = "toi muon"
        result = correct_spelling(text)
        assert result == "tôi muon"
    
    def test_correct_multiple_typos(self):
        """Test correcting multiple typos in one sentence."""
        text = "toi khong duoc"
        result = correct_spelling(text)
        assert result == "tôi không được"
    
    def test_correct_text_unchanged(self):
        """Test that correctly spelled text remains unchanged."""
        text = "bật đèn phòng khách"
        result = correct_spelling(text)
        assert result == "bật đèn phòng khách"


class TestSentenceSplitting:
    """
    **Validates: Requirement 14.7**
    
    Test sentence splitting for multi-intent detection.
    Keywords: và, rồi, sau đó, xong, tiếp theo, kế tiếp
    """
    
    def test_split_by_va(self):
        """Test splitting by 'và' keyword."""
        text = "bật đèn phòng khách và tắt quạt phòng ngủ"
        result = split_sentences(text)
        assert len(result) == 2
        assert "bật đèn phòng khách" in result
        assert "tắt quạt phòng ngủ" in result
    
    def test_split_by_roi(self):
        """Test splitting by 'rồi' keyword."""
        text = "bật đèn rồi tắt quạt"
        result = split_sentences(text)
        assert len(result) == 2
        assert "bật đèn" in result
        assert "tắt quạt" in result
    
    def test_split_by_sau_do(self):
        """Test splitting by 'sau đó' keyword."""
        text = "mở cửa sau đó bật điều hòa"
        result = split_sentences(text)
        assert len(result) == 2
        assert "mở cửa" in result
        assert "bật điều hòa" in result
    
    def test_split_by_xong(self):
        """Test splitting by 'xong' keyword."""
        text = "tắt đèn xong khóa cửa"
        result = split_sentences(text)
        assert len(result) == 2
        assert "tắt đèn" in result
        assert "khóa cửa" in result
    
    def test_split_by_tiep_theo(self):
        """Test splitting by 'tiếp theo' keyword."""
        text = "bật quạt tiếp theo mở mái che"
        result = split_sentences(text)
        assert len(result) == 2
        assert "bật quạt" in result
        assert "mở mái che" in result
    
    def test_split_by_ke_tiep(self):
        """Test splitting by 'kế tiếp' keyword."""
        text = "tắt điều hòa kế tiếp đóng cửa"
        result = split_sentences(text)
        assert len(result) == 2
        assert "tắt điều hòa" in result
        assert "đóng cửa" in result
    
    def test_split_multiple_keywords(self):
        """Test splitting by multiple keywords in one sentence."""
        text = "bật đèn và tắt quạt rồi khóa cửa"
        result = split_sentences(text)
        assert len(result) == 3
        assert "bật đèn" in result
        assert "tắt quạt" in result
        assert "khóa cửa" in result
    
    def test_no_split_single_intent(self):
        """Test that single intent text is not split."""
        text = "bật đèn phòng khách"
        result = split_sentences(text)
        assert len(result) == 1
        assert result[0] == "bật đèn phòng khách"
    
    def test_split_complex_example(self):
        """Test splitting complex multi-intent example from requirements."""
        text = "bật đèn phòng khách và tắt quạt phòng ngủ rồi khóa cửa"
        result = split_sentences(text)
        assert len(result) == 3
        # Verify all three intents are captured
        assert any("bật đèn" in s for s in result)
        assert any("tắt quạt" in s for s in result)
        assert any("khóa cửa" in s for s in result)


# ============================================================================
# INTEGRATION TESTS (Testing Multiple Functions Together)
# ============================================================================

class TestPreprocessingIntegration:
    """
    Integration tests for combining multiple preprocessing functions.
    
    These tests verify that preprocessing functions work correctly together.
    """
    
    def test_full_preprocessing_pipeline(self):
        """Test full preprocessing pipeline with all functions."""
        # Input with uppercase, slang, punctuation, and emoji
        text = "K BẬT ĐÈN! 💡 vs TẮT QUẠT?"
        
        # Apply preprocessing steps
        result = lowercase_text(text)
        result = normalize_slang(result)
        result = remove_punctuation(result)
        result = remove_emoji(result)
        
        # Expected: "không bật đèn với tắt quạt"
        assert "không" in result
        assert "bật đèn" in result
        assert "với" in result
        assert "tắt quạt" in result
        assert "!" not in result
        assert "?" not in result
        assert "💡" not in result
    
    def test_preprocessing_with_sentence_splitting(self):
        """Test preprocessing with sentence splitting for multi-intent."""
        text = "Bật đèn phòng khách và tắt quạt phòng ngủ"
        
        # Apply preprocessing
        result = lowercase_text(text)
        sentences = split_sentences(result)
        
        assert len(sentences) == 2
        assert "bật đèn phòng khách" in sentences
        assert "tắt quạt phòng ngủ" in sentences
    
    def test_preprocessing_with_typos_and_slang(self):
        """Test preprocessing with both typos and slang."""
        text = "toi k duoc bat den"
        
        # Apply spell correction and slang normalization
        result = correct_spelling(text)
        result = normalize_slang(result)
        
        # Expected: "tôi không được bat den"
        assert "tôi" in result
        assert "không" in result
        assert "được" in result
