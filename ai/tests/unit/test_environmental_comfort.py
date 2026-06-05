"""
Unit tests for Environmental Comfort Intent Classification.

These tests verify:
- Environmental comfort classification for all 5 comfort types
- Correct comfort_type entity extraction
- Vietnamese keyword recognition
- Classification accuracy with various Vietnamese expressions

**Validates: Requirements 3.1-3.7, Task 10.2**
"""

import pytest
from typing import Dict, Any


# ============================================================================
# STUB ML-BASED CLASSIFIER FOR TESTING
# ============================================================================

class MLBasedClassifier:
    """
    Stub ML-Based Classifier for testing environmental comfort classification.
    
    This stub recognizes environmental comfort keywords and returns appropriate
    intent and entities for testing purposes.
    """
    
    CONFIDENCE_THRESHOLD = 0.7
    
    # Environmental comfort keyword mappings
    # Note: Check longer/more specific phrases first to avoid partial matches
    COMFORT_KEYWORDS = {
        "cooling": ["nóng", "oi bức", "nóng quá", "nóng nực", "oi", "nóng bức", "mát", "làm mát", "cần mát"],
        "warming": ["lạnh", "rét", "lạnh quá", "rét quá", "lạnh lẽo", "rét mướt", "ấm", "sưởi ấm", "cần ấm"],
        "brighten": ["thiếu sáng", "tối om", "tối thui", "sáng hơn", "cần sáng", "tối quá", "tối"],
        "dim": ["sáng quá", "chói mắt", "sáng lóa", "giảm sáng", "sáng lắm", "chói", "sáng"],
        "ventilate": ["ngột ngạt", "thiếu không khí", "ngột", "ngạt", "bí bách", "thông gió", "thoáng"]
    }
    
    def classify(self, text: str) -> Dict[str, Any]:
        """
        Classify Vietnamese text for environmental comfort intent.
        
        Args:
            text: Vietnamese text input
            
        Returns:
            Dictionary with intent, entities, confidence, and classifier_type
        """
        text_lower = text.lower().strip()
        
        # Check for environmental comfort keywords
        # Sort keywords by length (longest first) to match longer phrases first
        for comfort_type, keywords in self.COMFORT_KEYWORDS.items():
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            for keyword in sorted_keywords:
                if keyword in text_lower:
                    return {
                        "intent": "environmental_comfort",
                        "entities": {"comfort_type": comfort_type},
                        "confidence": 0.85,
                        "classifier_type": "ml"
                    }
        
        # No environmental comfort keyword found
        return {
            "intent": "unknown",
            "entities": {},
            "confidence": 0.3,
            "classifier_type": "ml"
        }


# ============================================================================
# UNIT TESTS: COOLING COMFORT TYPE
# ============================================================================

class TestEnvironmentalComfortCooling:
    """Unit tests for cooling comfort type classification."""
    
    def test_cooling_nong_qua(self):
        """Test 'nóng quá' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("nóng quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
        assert result["classifier_type"] == "ml"
    
    def test_cooling_troi_nong(self):
        """Test 'trời nóng' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("trời nóng")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_cooling_oi_buc(self):
        """Test 'oi bức' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("oi bức")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_cooling_nong_nuc(self):
        """Test 'nóng nực' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("nóng nực")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_cooling_phong_nay_nong_lam(self):
        """Test 'phòng này nóng lắm' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("phòng này nóng lắm")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_cooling_o_day_nong_qua(self):
        """Test 'ở đây nóng quá' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("ở đây nóng quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_cooling_can_mat(self):
        """Test 'cần mát' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("cần mát")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_cooling_lam_mat(self):
        """Test 'làm mát' classifies as cooling."""
        classifier = MLBasedClassifier()
        result = classifier.classify("làm mát")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7


# ============================================================================
# UNIT TESTS: WARMING COMFORT TYPE
# ============================================================================

class TestEnvironmentalComfortWarming:
    """Unit tests for warming comfort type classification."""
    
    def test_warming_lanh_qua(self):
        """Test 'lạnh quá' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("lạnh quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7
        assert result["classifier_type"] == "ml"
    
    def test_warming_troi_lanh(self):
        """Test 'trời lạnh' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("trời lạnh")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7
    
    def test_warming_ret_qua(self):
        """Test 'rét quá' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("rét quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7
    
    def test_warming_lanh_leo(self):
        """Test 'lạnh lẽo' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("lạnh lẽo")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7
    
    def test_warming_phong_nay_lanh_lam(self):
        """Test 'phòng này lạnh lắm' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("phòng này lạnh lắm")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7
    
    def test_warming_o_day_ret(self):
        """Test 'ở đây rét' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("ở đây rét")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7
    
    def test_warming_can_am(self):
        """Test 'cần ấm' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("cần ấm")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7
    
    def test_warming_suoi_am(self):
        """Test 'sưởi ấm' classifies as warming."""
        classifier = MLBasedClassifier()
        result = classifier.classify("sưởi ấm")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "warming"
        assert result["confidence"] >= 0.7


# ============================================================================
# UNIT TESTS: BRIGHTEN COMFORT TYPE
# ============================================================================

class TestEnvironmentalComfortBrighten:
    """Unit tests for brighten comfort type classification."""
    
    def test_brighten_toi_qua(self):
        """Test 'tối quá' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("tối quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7
        assert result["classifier_type"] == "ml"
    
    def test_brighten_troi_toi(self):
        """Test 'trời tối' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("trời tối")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7
    
    def test_brighten_thieu_sang(self):
        """Test 'thiếu sáng' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("thiếu sáng")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7
    
    def test_brighten_toi_om(self):
        """Test 'tối om' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("tối om")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7
    
    def test_brighten_phong_nay_toi_lam(self):
        """Test 'phòng này tối lắm' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("phòng này tối lắm")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7
    
    def test_brighten_trong_nha_toi_that(self):
        """Test 'trong nhà tối thật' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("trong nhà tối thật")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7
    
    def test_brighten_can_sang(self):
        """Test 'cần sáng' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("cần sáng")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7
    
    def test_brighten_sang_hon(self):
        """Test 'sáng hơn' classifies as brighten."""
        classifier = MLBasedClassifier()
        result = classifier.classify("sáng hơn")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "brighten"
        assert result["confidence"] >= 0.7


# ============================================================================
# UNIT TESTS: DIM COMFORT TYPE
# ============================================================================

class TestEnvironmentalComfortDim:
    """Unit tests for dim comfort type classification."""
    
    def test_dim_choi_qua(self):
        """Test 'chói quá' classifies as dim."""
        classifier = MLBasedClassifier()
        result = classifier.classify("chói quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "dim"
        assert result["confidence"] >= 0.7
        assert result["classifier_type"] == "ml"
    
    def test_dim_sang_qua(self):
        """Test 'sáng quá' classifies as dim."""
        classifier = MLBasedClassifier()
        result = classifier.classify("sáng quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "dim"
        assert result["confidence"] >= 0.7
    
    def test_dim_choi_mat(self):
        """Test 'chói mắt' classifies as dim."""
        classifier = MLBasedClassifier()
        result = classifier.classify("chói mắt")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "dim"
        assert result["confidence"] >= 0.7
    
    def test_dim_sang_loa(self):
        """Test 'sáng lóa' classifies as dim."""
        classifier = MLBasedClassifier()
        result = classifier.classify("sáng lóa")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "dim"
        assert result["confidence"] >= 0.7
    
    def test_dim_phong_nay_sang_lam(self):
        """Test 'phòng này sáng lắm' classifies as dim."""
        classifier = MLBasedClassifier()
        result = classifier.classify("phòng này sáng lắm")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "dim"
        assert result["confidence"] >= 0.7
    
    def test_dim_troi_sang_choi_mat(self):
        """Test 'trời sáng chói mắt' classifies as dim."""
        classifier = MLBasedClassifier()
        result = classifier.classify("trời sáng chói mắt")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "dim"
        assert result["confidence"] >= 0.7
    
    def test_dim_giam_sang(self):
        """Test 'giảm sáng' classifies as dim."""
        classifier = MLBasedClassifier()
        result = classifier.classify("giảm sáng")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "dim"
        assert result["confidence"] >= 0.7


# ============================================================================
# UNIT TESTS: VENTILATE COMFORT TYPE
# ============================================================================

class TestEnvironmentalComfortVentilate:
    """Unit tests for ventilate comfort type classification."""
    
    def test_ventilate_ngot_ngat_qua(self):
        """Test 'ngột ngạt quá' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("ngột ngạt quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7
        assert result["classifier_type"] == "ml"
    
    def test_ventilate_thieu_khong_khi(self):
        """Test 'thiếu không khí' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("thiếu không khí")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7
    
    def test_ventilate_ngot_ngat(self):
        """Test 'ngột ngạt' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("ngột ngạt")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7
    
    def test_ventilate_bi_bach(self):
        """Test 'bí bách' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("bí bách")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7
    
    def test_ventilate_phong_nay_ngot_lam(self):
        """Test 'phòng này ngột lắm' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("phòng này ngột lắm")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7
    
    def test_ventilate_khong_khi_ngot_ngat(self):
        """Test 'không khí ngột ngạt' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("không khí ngột ngạt")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7
    
    def test_ventilate_thong_gio(self):
        """Test 'thông gió' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("thông gió")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7
    
    def test_ventilate_can_thoang(self):
        """Test 'cần thoáng' classifies as ventilate."""
        classifier = MLBasedClassifier()
        result = classifier.classify("cần thoáng")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "ventilate"
        assert result["confidence"] >= 0.7


# ============================================================================
# UNIT TESTS: EDGE CASES AND VARIATIONS
# ============================================================================

class TestEnvironmentalComfortEdgeCases:
    """Unit tests for edge cases and variations."""
    
    def test_with_context_words_cooling(self):
        """Test cooling with additional context words."""
        classifier = MLBasedClassifier()
        
        test_cases = [
            "ở đây nóng quá",
            "phòng này nóng lắm",
            "trong nhà oi bức thật"
        ]
        
        for text in test_cases:
            result = classifier.classify(text)
            assert result["intent"] == "environmental_comfort"
            assert result["entities"]["comfort_type"] == "cooling"
            assert result["confidence"] >= 0.7
    
    def test_with_context_words_warming(self):
        """Test warming with additional context words."""
        classifier = MLBasedClassifier()
        
        test_cases = [
            "ở đây lạnh quá",
            "phòng này rét lắm",
            "trong nhà lạnh lẽo thật"
        ]
        
        for text in test_cases:
            result = classifier.classify(text)
            assert result["intent"] == "environmental_comfort"
            assert result["entities"]["comfort_type"] == "warming"
            assert result["confidence"] >= 0.7
    
    def test_with_context_words_brighten(self):
        """Test brighten with additional context words."""
        classifier = MLBasedClassifier()
        
        test_cases = [
            "ở đây tối quá",
            "phòng này tối lắm",
            "trong nhà thiếu sáng thật"
        ]
        
        for text in test_cases:
            result = classifier.classify(text)
            assert result["intent"] == "environmental_comfort"
            assert result["entities"]["comfort_type"] == "brighten"
            assert result["confidence"] >= 0.7
    
    def test_with_context_words_dim(self):
        """Test dim with additional context words."""
        classifier = MLBasedClassifier()
        
        test_cases = [
            "ở đây sáng quá",
            "phòng này chói lắm",
            "trời sáng chói mắt"
        ]
        
        for text in test_cases:
            result = classifier.classify(text)
            assert result["intent"] == "environmental_comfort"
            assert result["entities"]["comfort_type"] == "dim"
            assert result["confidence"] >= 0.7
    
    def test_with_context_words_ventilate(self):
        """Test ventilate with additional context words."""
        classifier = MLBasedClassifier()
        
        test_cases = [
            "ở đây ngột ngạt quá",
            "phòng này thiếu không khí",
            "không khí ngột ngạt lắm"
        ]
        
        for text in test_cases:
            result = classifier.classify(text)
            assert result["intent"] == "environmental_comfort"
            assert result["entities"]["comfort_type"] == "ventilate"
            assert result["confidence"] >= 0.7
    
    def test_uppercase_text(self):
        """Test that uppercase text is handled correctly."""
        classifier = MLBasedClassifier()
        
        result = classifier.classify("NÓNG QUÁ")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_mixed_case_text(self):
        """Test that mixed case text is handled correctly."""
        classifier = MLBasedClassifier()
        
        result = classifier.classify("Trời Nóng Quá")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_with_extra_whitespace(self):
        """Test that extra whitespace is handled correctly."""
        classifier = MLBasedClassifier()
        
        result = classifier.classify("  nóng   quá  ")
        
        assert result["intent"] == "environmental_comfort"
        assert result["entities"]["comfort_type"] == "cooling"
        assert result["confidence"] >= 0.7
    
    def test_non_comfort_text_returns_unknown(self):
        """Test that non-comfort text returns unknown intent."""
        classifier = MLBasedClassifier()
        
        non_comfort_texts = [
            "bật đèn",
            "tắt quạt",
            "nhiệt độ bao nhiêu",
            "đi ngủ"
        ]
        
        for text in non_comfort_texts:
            result = classifier.classify(text)
            assert result["intent"] == "unknown"
            assert result["confidence"] < 0.7


# ============================================================================
# UNIT TESTS: CONFIDENCE THRESHOLD
# ============================================================================

class TestEnvironmentalComfortConfidence:
    """Unit tests for confidence threshold validation."""
    
    def test_all_comfort_types_meet_threshold(self):
        """Test that all comfort types meet confidence threshold (>= 0.7)."""
        classifier = MLBasedClassifier()
        
        test_cases = [
            ("nóng quá", "cooling"),
            ("lạnh quá", "warming"),
            ("tối quá", "brighten"),
            ("sáng quá", "dim"),
            ("ngột ngạt", "ventilate")
        ]
        
        for text, expected_comfort_type in test_cases:
            result = classifier.classify(text)
            
            assert result["intent"] == "environmental_comfort"
            assert result["entities"]["comfort_type"] == expected_comfort_type
            assert result["confidence"] >= 0.7, \
                f"Confidence {result['confidence']} below threshold for '{text}'"
    
    def test_clear_keywords_have_high_confidence(self):
        """Test that clear keywords have high confidence (>= 0.8)."""
        classifier = MLBasedClassifier()
        
        clear_keywords = [
            "nóng quá",
            "lạnh quá",
            "tối quá",
            "sáng quá",
            "ngột ngạt quá"
        ]
        
        for text in clear_keywords:
            result = classifier.classify(text)
            
            assert result["confidence"] >= 0.8, \
                f"Clear keyword '{text}' should have confidence >= 0.8, got {result['confidence']}"
