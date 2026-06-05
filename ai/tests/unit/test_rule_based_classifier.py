"""
Unit tests for Rule-Based Classifier pattern matching.

These tests verify specific rule-based pattern matching scenarios for:
- Control device patterns (bật/tắt/mở/đóng + device + optional location)
- Activate scene patterns (đi ngủ, thức dậy, xem phim, đi vắng, về nhà)
- Entity extraction from matched patterns

**Validates: Requirements 2.1-2.6, 6.1-6.7, 13.1-13.3**
"""

import pytest
from typing import Optional, Dict, Any
from dataclasses import dataclass


# ============================================================================
# IMPORT REAL IMPLEMENTATION (Task 4.3 completed)
# ============================================================================

from src.classifiers.rule_based import RuleBasedClassifier, ClassificationResult


# ============================================================================
# UNIT TESTS: Control Device Patterns
# ============================================================================

class TestControlDevicePatterns:
    """Unit tests for control device pattern matching."""
    
    def test_bat_den_pattern(self):
        """Test pattern: 'bật đèn' → control_device with turn_on + light."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật đèn")
        
        assert result is not None, "Should match 'bật đèn' pattern"
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "light"
        assert result.confidence == 1.0
        assert result.classifier_type == "rule"
    
    def test_tat_quat_pattern(self):
        """Test pattern: 'tắt quạt' → control_device with turn_off + fan."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("tắt quạt")
        
        assert result is not None, "Should match 'tắt quạt' pattern"
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_off"
        assert result.entities["device"] == "fan"
        assert result.confidence == 1.0
    
    def test_mo_cua_pattern(self):
        """Test pattern: 'mở cửa' → control_device with turn_on + door."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("mở cửa")
        
        assert result is not None, "Should match 'mở cửa' pattern"
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "door"
        assert result.confidence == 1.0
    
    def test_dong_mai_che_pattern(self):
        """Test pattern: 'đóng mái che' → control_device with turn_off + awning."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đóng mái che")
        
        assert result is not None, "Should match 'đóng mái che' pattern"
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_off"
        assert result.entities["device"] == "awning"
        assert result.confidence == 1.0
    
    def test_bat_dieu_hoa_pattern(self):
        """Test pattern: 'bật điều hòa' → control_device with turn_on + ac."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật điều hòa")
        
        assert result is not None, "Should match 'bật điều hòa' pattern"
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "ac"
        assert result.confidence == 1.0
    
    def test_tat_ac_pattern(self):
        """Test pattern: 'tắt ac' → control_device with turn_off + ac."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("tắt ac")
        
        assert result is not None, "Should match 'tắt ac' pattern"
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_off"
        assert result.entities["device"] == "ac"
        assert result.confidence == 1.0


# ============================================================================
# UNIT TESTS: Control Device Patterns with Location
# ============================================================================

class TestControlDeviceWithLocationPatterns:
    """Unit tests for control device patterns with location extraction."""
    
    def test_bat_den_phong_khach(self):
        """Test pattern: 'bật đèn phòng khách' → extracts living_room location."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật đèn phòng khách")
        
        assert result is not None
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "light"
        assert result.entities["location"] == "living_room"
        assert result.confidence == 1.0
    
    def test_tat_quat_phong_ngu(self):
        """Test pattern: 'tắt quạt phòng ngủ' → extracts bedroom location."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("tắt quạt phòng ngủ")
        
        assert result is not None
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_off"
        assert result.entities["device"] == "fan"
        assert result.entities["location"] == "bedroom"
        assert result.confidence == 1.0
    
    def test_mo_cua_phong_tam(self):
        """Test pattern: 'mở cửa phòng tắm' → extracts bathroom location."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("mở cửa phòng tắm")
        
        assert result is not None
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "door"
        assert result.entities["location"] == "bathroom"
        assert result.confidence == 1.0
    
    def test_dong_mai_che_ban_cong(self):
        """Test pattern: 'đóng mái che ban công' → extracts balcony location."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đóng mái che ban công")
        
        assert result is not None
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_off"
        assert result.entities["device"] == "awning"
        assert result.entities["location"] == "balcony"
        assert result.confidence == 1.0
    
    def test_bat_dieu_hoa_bep(self):
        """Test pattern: 'bật điều hòa bếp' → extracts kitchen location."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật điều hòa bếp")
        
        assert result is not None
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "ac"
        assert result.entities["location"] == "kitchen"
        assert result.confidence == 1.0


# ============================================================================
# UNIT TESTS: Activate Scene Patterns
# ============================================================================

class TestActivateScenePatterns:
    """Unit tests for activate scene pattern matching."""
    
    def test_di_ngu_scene(self):
        """Test pattern: 'đi ngủ' → activate_scene with sleep."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đi ngủ")
        
        assert result is not None, "Should match 'đi ngủ' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
        assert result.classifier_type == "rule"
    
    def test_chuc_ngu_ngon_scene(self):
        """Test pattern: 'chúc ngủ ngon' → activate_scene with sleep."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("chúc ngủ ngon")
        
        assert result is not None, "Should match 'chúc ngủ ngon' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
    
    def test_chuan_bi_ngu_scene(self):
        """Test pattern: 'chuẩn bị ngủ' → activate_scene with sleep."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("chuẩn bị ngủ")
        
        assert result is not None, "Should match 'chuẩn bị ngủ' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "sleep"
        assert result.confidence == 1.0
    
    def test_thuc_day_scene(self):
        """Test pattern: 'thức dậy' → activate_scene with wake_up."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("thức dậy")
        
        assert result is not None, "Should match 'thức dậy' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
    
    def test_buoi_sang_scene(self):
        """Test pattern: 'buổi sáng' → activate_scene with wake_up."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("buổi sáng")
        
        assert result is not None, "Should match 'buổi sáng' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
    
    def test_chao_buoi_sang_scene(self):
        """Test pattern: 'chào buổi sáng' → activate_scene with wake_up."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("chào buổi sáng")
        
        assert result is not None, "Should match 'chào buổi sáng' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "wake_up"
        assert result.confidence == 1.0
    
    def test_xem_phim_scene(self):
        """Test pattern: 'xem phim' → activate_scene with movie."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("xem phim")
        
        assert result is not None, "Should match 'xem phim' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    def test_xem_tv_scene(self):
        """Test pattern: 'xem tv' → activate_scene with movie."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("xem tv")
        
        assert result is not None, "Should match 'xem tv' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    def test_rap_chieu_phim_scene(self):
        """Test pattern: 'rạp chiếu phim' → activate_scene with movie."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("rạp chiếu phim")
        
        assert result is not None, "Should match 'rạp chiếu phim' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
        assert result.confidence == 1.0
    
    def test_di_ra_ngoai_scene(self):
        """Test pattern: 'đi ra ngoài' → activate_scene with away."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đi ra ngoài")
        
        assert result is not None, "Should match 'đi ra ngoài' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
    
    def test_roi_nha_scene(self):
        """Test pattern: 'rời nhà' → activate_scene with away."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("rời nhà")
        
        assert result is not None, "Should match 'rời nhà' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
    
    def test_di_vang_scene(self):
        """Test pattern: 'đi vắng' → activate_scene with away."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đi vắng")
        
        assert result is not None, "Should match 'đi vắng' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "away"
        assert result.confidence == 1.0
    
    def test_ve_nha_scene(self):
        """Test pattern: 'về nhà' → activate_scene with home."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("về nhà")
        
        assert result is not None, "Should match 'về nhà' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0
    
    def test_da_ve_scene(self):
        """Test pattern: 'đã về' → activate_scene with home."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đã về")
        
        assert result is not None, "Should match 'đã về' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0
    
    def test_toi_ve_roi_scene(self):
        """Test pattern: 'tôi về rồi' → activate_scene with home."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("tôi về rồi")
        
        assert result is not None, "Should match 'tôi về rồi' pattern"
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "home"
        assert result.confidence == 1.0


# ============================================================================
# UNIT TESTS: Entity Extraction
# ============================================================================

class TestEntityExtraction:
    """Unit tests for entity extraction from matched patterns."""
    
    def test_extract_action_bat_maps_to_turn_on(self):
        """Test that 'bật' action maps to 'turn_on'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật đèn")
        
        assert result.entities["action"] == "turn_on"
    
    def test_extract_action_mo_maps_to_turn_on(self):
        """Test that 'mở' action maps to 'turn_on'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("mở cửa")
        
        assert result.entities["action"] == "turn_on"
    
    def test_extract_action_tat_maps_to_turn_off(self):
        """Test that 'tắt' action maps to 'turn_off'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("tắt quạt")
        
        assert result.entities["action"] == "turn_off"
    
    def test_extract_action_dong_maps_to_turn_off(self):
        """Test that 'đóng' action maps to 'turn_off'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đóng mái che")
        
        assert result.entities["action"] == "turn_off"
    
    def test_extract_device_den_maps_to_light(self):
        """Test that 'đèn' device maps to 'light'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật đèn")
        
        assert result.entities["device"] == "light"
    
    def test_extract_device_quat_maps_to_fan(self):
        """Test that 'quạt' device maps to 'fan'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("tắt quạt")
        
        assert result.entities["device"] == "fan"
    
    def test_extract_device_dieu_hoa_maps_to_ac(self):
        """Test that 'điều hòa' device maps to 'ac'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật điều hòa")
        
        assert result.entities["device"] == "ac"
    
    def test_extract_device_cua_maps_to_door(self):
        """Test that 'cửa' device maps to 'door'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("mở cửa")
        
        assert result.entities["device"] == "door"
    
    def test_extract_device_mai_che_maps_to_awning(self):
        """Test that 'mái che' device maps to 'awning'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đóng mái che")
        
        assert result.entities["device"] == "awning"
    
    def test_extract_location_phong_khach_maps_to_living_room(self):
        """Test that 'phòng khách' location maps to 'living_room'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật đèn phòng khách")
        
        assert result.entities["location"] == "living_room"
    
    def test_extract_location_phong_ngu_maps_to_bedroom(self):
        """Test that 'phòng ngủ' location maps to 'bedroom'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("tắt quạt phòng ngủ")
        
        assert result.entities["location"] == "bedroom"
    
    def test_extract_location_bep_maps_to_kitchen(self):
        """Test that 'bếp' location maps to 'kitchen'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật điều hòa bếp")
        
        assert result.entities["location"] == "kitchen"
    
    def test_extract_location_phong_tam_maps_to_bathroom(self):
        """Test that 'phòng tắm' location maps to 'bathroom'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("mở cửa phòng tắm")
        
        assert result.entities["location"] == "bathroom"
    
    def test_extract_location_ban_cong_maps_to_balcony(self):
        """Test that 'ban công' location maps to 'balcony'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đóng mái che ban công")
        
        assert result.entities["location"] == "balcony"
    
    def test_extract_scene_type_sleep(self):
        """Test that sleep scene keywords extract scene_type='sleep'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đi ngủ")
        
        assert result.entities["scene_type"] == "sleep"
    
    def test_extract_scene_type_wake_up(self):
        """Test that wake_up scene keywords extract scene_type='wake_up'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("thức dậy")
        
        assert result.entities["scene_type"] == "wake_up"
    
    def test_extract_scene_type_movie(self):
        """Test that movie scene keywords extract scene_type='movie'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("xem phim")
        
        assert result.entities["scene_type"] == "movie"
    
    def test_extract_scene_type_away(self):
        """Test that away scene keywords extract scene_type='away'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("đi vắng")
        
        assert result.entities["scene_type"] == "away"
    
    def test_extract_scene_type_home(self):
        """Test that home scene keywords extract scene_type='home'."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("về nhà")
        
        assert result.entities["scene_type"] == "home"


# ============================================================================
# UNIT TESTS: Edge Cases and Negative Cases
# ============================================================================

class TestEdgeCasesAndNegativeCases:
    """Unit tests for edge cases and negative cases."""
    
    def test_no_match_returns_none(self):
        """Test that non-matching text returns None."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("xyz abc")
        
        assert result is None, "Should not match query text without specific patterns"
    
    def test_case_insensitive_matching(self):
        """Test that pattern matching is case-insensitive."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("BẬT ĐÈN")
        
        assert result is not None
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "light"
    
    def test_whitespace_handling(self):
        """Test that extra whitespace is handled correctly."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("  bật đèn  ")
        
        assert result is not None
        assert result.intent == "control_device"
        assert result.entities["action"] == "turn_on"
        assert result.entities["device"] == "light"
    
    def test_location_optional_not_present(self):
        """Test that location entity is not present when not specified."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("bật đèn")
        
        assert result is not None
        assert "location" not in result.entities
    
    def test_scene_takes_precedence_over_device(self):
        """Test that scene patterns are checked before device patterns."""
        classifier = RuleBasedClassifier()
        result = classifier.classify("xem phim")
        
        # Should match scene pattern, not device pattern
        assert result is not None
        assert result.intent == "activate_scene"
        assert result.entities["scene_type"] == "movie"
    
    def test_partial_match_not_sufficient(self):
        """Test that partial matches don't trigger false positives."""
        classifier = RuleBasedClassifier()
        
        # "bật" without device should not match
        result = classifier.classify("bật")
        assert result is None
        
        # "đèn" without action should not match
        result = classifier.classify("đèn")
        assert result is None
