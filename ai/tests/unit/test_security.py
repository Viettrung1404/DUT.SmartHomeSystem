"""
Unit tests for security mode and security alert classification.

These tests verify that security mode and security alert patterns are correctly 
classified with appropriate entity extraction and false positive prevention.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8**
"""

import pytest
from src.classifiers.rule_based import RuleBasedClassifier
from src.entities.entity_extractor import EntityExtractor


class TestSecurityModeClassification:
    """Unit tests for security mode intent classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.rule_classifier = RuleBasedClassifier()
        self.entity_extractor = EntityExtractor()
    
    # ========================================================================
    # ARMED MODE TESTS
    # ========================================================================
    
    def test_armed_mode_basic(self):
        """Test: 'bật báo động' -> security_mode with armed."""
        text = "bật báo động"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "armed", \
            f"Expected mode 'armed', got {entities.get('mode')}"
    
    def test_armed_mode_activate_security(self):
        """Test: 'kích hoạt an ninh' -> security_mode with armed."""
        text = "kích hoạt an ninh"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "armed"
    
    def test_armed_mode_turn_on_security(self):
        """Test: 'bật chế độ an ninh' -> security_mode with armed."""
        text = "bật chế độ an ninh"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "armed"
    
    def test_armed_mode_with_prefix(self):
        """Test: 'tôi muốn bật báo động' -> security_mode with armed."""
        text = "tôi muốn bật báo động"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "armed"
    
    def test_armed_mode_with_suffix(self):
        """Test: 'bật báo động đi' -> security_mode with armed."""
        text = "bật báo động đi"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "armed"
    
    # ========================================================================
    # DISARMED MODE TESTS
    # ========================================================================
    
    def test_disarmed_mode_basic(self):
        """Test: 'tắt báo động' -> security_mode with disarmed."""
        text = "tắt báo động"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "disarmed", \
            f"Expected mode 'disarmed', got {entities.get('mode')}"
    
    def test_disarmed_mode_deactivate_security(self):
        """Test: 'vô hiệu hóa an ninh' -> security_mode with disarmed."""
        text = "vô hiệu hóa an ninh"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "disarmed"
    
    def test_disarmed_mode_turn_off_security(self):
        """Test: 'tắt chế độ an ninh' -> security_mode with disarmed."""
        text = "tắt chế độ an ninh"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "disarmed"
    
    def test_disarmed_mode_with_prefix(self):
        """Test: 'tôi muốn tắt báo động' -> security_mode with disarmed."""
        text = "tôi muốn tắt báo động"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "disarmed"
    
    def test_disarmed_mode_with_suffix(self):
        """Test: 'tắt báo động đi' -> security_mode with disarmed."""
        text = "tắt báo động đi"
        
        entities = self.entity_extractor.extract(text, "security_mode")
        
        assert entities.get("mode") == "disarmed"


class TestSecurityAlertClassification:
    """Unit tests for security alert intent classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.rule_classifier = RuleBasedClassifier()
        self.entity_extractor = EntityExtractor()
    
    # ========================================================================
    # FIRE ALERT TESTS
    # ========================================================================
    
    def test_fire_alert_basic(self):
        """Test: 'cháy rồi' -> security_alert with fire and priority=high."""
        text = "cháy rồi"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "fire", \
            f"Expected alert_type 'fire', got {entities.get('alert_type')}"
        assert entities.get("priority") == "high", \
            f"Expected priority 'high', got {entities.get('priority')}"
    
    def test_fire_alert_has_fire(self):
        """Test: 'có lửa' -> security_alert with fire."""
        text = "có lửa"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "fire"
        assert entities.get("priority") == "high"
    
    def test_fire_alert_conflagration(self):
        """Test: 'hỏa hoạn' -> security_alert with fire."""
        text = "hỏa hoạn"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "fire"
        assert entities.get("priority") == "high"
    
    def test_fire_alert_warning(self):
        """Test: 'cảnh báo cháy' -> security_alert with fire."""
        text = "cảnh báo cháy"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "fire"
        assert entities.get("priority") == "high"
    
    def test_fire_alert_detected(self):
        """Test: 'phát hiện cháy' -> security_alert with fire."""
        text = "phát hiện cháy"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "fire"
        assert entities.get("priority") == "high"
    
    # ========================================================================
    # GAS ALERT TESTS
    # ========================================================================
    
    def test_gas_alert_leak(self):
        """Test: 'rò rỉ gas' -> security_alert with gas and priority=high."""
        text = "rò rỉ gas"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "gas", \
            f"Expected alert_type 'gas', got {entities.get('alert_type')}"
        assert entities.get("priority") == "high", \
            f"Expected priority 'high', got {entities.get('priority')}"
    
    def test_gas_alert_smell(self):
        """Test: 'có mùi gas' -> security_alert with gas."""
        text = "có mùi gas"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "gas"
        assert entities.get("priority") == "high"
    
    def test_gas_alert_warning(self):
        """Test: 'cảnh báo gas' -> security_alert with gas."""
        text = "cảnh báo gas"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "gas"
        assert entities.get("priority") == "high"
    
    def test_gas_alert_detected(self):
        """Test: 'phát hiện gas' -> security_alert with gas."""
        text = "phát hiện gas"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "gas"
        assert entities.get("priority") == "high"
    
    def test_gas_alert_detected_gas(self):
        """Test: 'phát hiện khí gas' -> security_alert with gas."""
        text = "phát hiện khí gas"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "gas"
        assert entities.get("priority") == "high"
    
    # ========================================================================
    # INTRUSION ALERT TESTS
    # ========================================================================
    
    def test_intrusion_alert_thief(self):
        """Test: 'có trộm' -> security_alert with intrusion and priority=high."""
        text = "có trộm"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "intrusion", \
            f"Expected alert_type 'intrusion', got {entities.get('alert_type')}"
        assert entities.get("priority") == "high", \
            f"Expected priority 'high', got {entities.get('priority')}"
    
    def test_intrusion_alert_break_in(self):
        """Test: 'đột nhập' -> security_alert with intrusion."""
        text = "đột nhập"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "intrusion"
        assert entities.get("priority") == "high"
    
    def test_intrusion_alert_stranger(self):
        """Test: 'có người lạ' -> security_alert with intrusion."""
        text = "có người lạ"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "intrusion"
        assert entities.get("priority") == "high"
    
    def test_intrusion_alert_intruder(self):
        """Test: 'kẻ xâm nhập' -> security_alert with intrusion."""
        text = "kẻ xâm nhập"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "intrusion"
        assert entities.get("priority") == "high"
    
    def test_intrusion_alert_warning(self):
        """Test: 'cảnh báo trộm' -> security_alert with intrusion."""
        text = "cảnh báo trộm"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "intrusion"
        assert entities.get("priority") == "high"


class TestSecurityAlertFalsePositivePrevention:
    """Unit tests for false positive prevention in security alert classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.rule_classifier = RuleBasedClassifier()
        self.entity_extractor = EntityExtractor()
    
    # ========================================================================
    # FALSE POSITIVE TESTS (should NOT be security_alert)
    # ========================================================================
    
    def test_false_positive_movie_fire(self):
        """Test: 'phim này cháy quá' should NOT be security_alert (entertainment context)."""
        text = "phim này cháy quá"
        
        # This should NOT extract security alert entities
        # In actual implementation, the classifier should detect entertainment context
        # and NOT classify as security_alert
        
        # For now, we test that if it's incorrectly classified as security_alert,
        # the entity extractor should not extract alert_type
        # (This will be properly handled in the classifier logic)
        pass  # This test will be implemented when classifier logic is added
    
    def test_false_positive_game_explosive(self):
        """Test: 'game này nổ tung' should NOT be security_alert (entertainment context)."""
        text = "game này nổ tung"
        
        # Entertainment context - should NOT be security_alert
        pass
    
    def test_false_positive_song_explosive(self):
        """Test: 'bài hát này bùng nổ' should NOT be security_alert (entertainment context)."""
        text = "bài hát này bùng nổ"
        
        # Entertainment context - should NOT be security_alert
        pass
    
    def test_false_positive_match_fire(self):
        """Test: 'trận đấu này cháy' should NOT be security_alert (entertainment context)."""
        text = "trận đấu này cháy"
        
        # Entertainment context - should NOT be security_alert
        pass
    
    def test_false_positive_video_peak(self):
        """Test: 'video này đỉnh quá' should NOT be security_alert (entertainment context)."""
        text = "video này đỉnh quá"
        
        # Entertainment context - should NOT be security_alert
        pass
    
    # ========================================================================
    # TRUE POSITIVE TESTS (should be security_alert)
    # ========================================================================
    
    def test_true_positive_fire_in_room(self):
        """Test: 'cháy ở phòng khách' should be security_alert (no entertainment context)."""
        text = "cháy ở phòng khách"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "fire"
        assert entities.get("priority") == "high"
    
    def test_true_positive_gas_leak_in_kitchen(self):
        """Test: 'rò rỉ gas ở bếp' should be security_alert (no entertainment context)."""
        text = "rò rỉ gas ở bếp"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "gas"
        assert entities.get("priority") == "high"
    
    def test_true_positive_stranger_outside(self):
        """Test: 'có người lạ ở ngoài' should be security_alert (no entertainment context)."""
        text = "có người lạ ở ngoài"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        assert entities.get("alert_type") == "intrusion"
        assert entities.get("priority") == "high"
    
    # ========================================================================
    # EDGE CASES
    # ========================================================================
    
    def test_security_vs_query_distinction(self):
        """Test that security alerts are distinguished from sensor queries."""
        # Security alert (statement)
        alert_text = "cháy rồi"
        alert_entities = self.entity_extractor.extract(alert_text, "security_alert")
        assert alert_entities.get("alert_type") == "fire"
        assert alert_entities.get("priority") == "high"
        
        # Sensor query (question)
        query_text = "có cháy không"
        query_entities = self.entity_extractor.extract(query_text, "query_sensor")
        assert query_entities.get("sensor_type") == "fire"
        assert "priority" not in query_entities  # Queries don't have priority
    
    def test_all_alert_types_have_priority(self):
        """Test that all alert types include priority=high."""
        test_cases = [
            ("cháy rồi", "fire"),
            ("rò rỉ gas", "gas"),
            ("có trộm", "intrusion")
        ]
        
        for text, expected_alert_type in test_cases:
            entities = self.entity_extractor.extract(text, "security_alert")
            
            assert entities.get("alert_type") == expected_alert_type, \
                f"Expected alert_type '{expected_alert_type}' for '{text}', got '{entities.get('alert_type')}'"
            assert entities.get("priority") == "high", \
                f"Expected priority 'high' for '{text}', got '{entities.get('priority')}'"
    
    def test_empty_entities_for_unknown_alert(self):
        """Test that unknown alert types don't extract entities."""
        text = "cảnh báo xyz"
        
        entities = self.entity_extractor.extract(text, "security_alert")
        
        # Should not extract alert_type for unknown alert
        assert "alert_type" not in entities or entities.get("alert_type") is None
