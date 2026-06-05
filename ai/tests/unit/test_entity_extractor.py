"""
Unit tests for Entity Extractor.

These tests verify specific entity extraction scenarios for:
- Device extraction (đèn → light, quạt → fan, etc.)
- Action extraction (bật → turn_on, tắt → turn_off, etc.)
- Location extraction (phòng khách → living_room, etc.)
- Numeric value extraction (30 độ → (30, 'C'), 50% → (50, '%'))
- Comfort type extraction (nóng → cooling, lạnh → warming, etc.)
- Scene type extraction (đi ngủ → sleep, etc.)
- Sensor type extraction (nhiệt độ → temperature, etc.)

**Validates: Requirements 1.3, 2.2-2.6, 3.2, 4.2, 6.2**
"""

import pytest
from typing import Optional, Dict, Any


# ============================================================================
# IMPORT REAL IMPLEMENTATION (Task 5.4 completed)
# ============================================================================

from src.entities.entity_extractor import EntityExtractor


# ============================================================================
# UNIT TESTS: Device Extraction
# ============================================================================

class TestDeviceExtraction:
    """Unit tests for device extraction."""
    
    def test_extract_device_den_to_light(self):
        """Test that 'đèn' extracts to 'light'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("bật đèn phòng khách")
        assert device == "light"
    
    def test_extract_device_anh_sang_to_light(self):
        """Test that 'ánh sáng' extracts to 'light'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("bật ánh sáng")
        assert device == "light"
    
    def test_extract_device_quat_to_fan(self):
        """Test that 'quạt' extracts to 'fan'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("tắt quạt")
        assert device == "fan"
    
    def test_extract_device_quat_tran_to_fan(self):
        """Test that 'quạt trần' extracts to 'fan'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("bật quạt trần")
        assert device == "fan"
    
    def test_extract_device_dieu_hoa_to_ac(self):
        """Test that 'điều hòa' extracts to 'ac'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("bật điều hòa")
        assert device == "ac"
    
    def test_extract_device_may_lanh_to_ac(self):
        """Test that 'máy lạnh' extracts to 'ac'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("tắt máy lạnh")
        assert device == "ac"
    
    def test_extract_device_ac_to_ac(self):
        """Test that 'ac' extracts to 'ac'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("bật ac")
        assert device == "ac"
    
    def test_extract_device_cua_to_door(self):
        """Test that 'cửa' extracts to 'door'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("mở cửa")
        assert device == "door"
    
    def test_extract_device_mai_che_to_awning(self):
        """Test that 'mái che' extracts to 'awning'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("đóng mái che")
        assert device == "awning"
    
    def test_extract_device_khoa_to_lock(self):
        """Test that 'khóa' extracts to 'lock'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("khóa cửa")
        assert device == "lock"
    
    def test_extract_device_rem_to_curtain(self):
        """Test that 'rèm' extracts to 'curtain'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("mở rèm")
        assert device == "curtain"
    
    def test_extract_device_camera_to_camera(self):
        """Test that 'camera' extracts to 'camera'."""
        extractor = EntityExtractor()
        device = extractor.extract_device("bật camera")
        assert device == "camera"
    
    def test_extract_device_no_match_returns_none(self):
        """Test that no device match returns None."""
        extractor = EntityExtractor()
        device = extractor.extract_device("trời nóng quá")
        assert device is None


# ============================================================================
# UNIT TESTS: Action Extraction
# ============================================================================

class TestActionExtraction:
    """Unit tests for action extraction."""
    
    def test_extract_action_bat_to_turn_on(self):
        """Test that 'bật' extracts to 'turn_on'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("bật đèn")
        assert action == "turn_on"
    
    def test_extract_action_mo_to_turn_on(self):
        """Test that 'mở' extracts to 'turn_on'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("mở cửa")
        assert action == "turn_on"
    
    def test_extract_action_khoi_dong_to_turn_on(self):
        """Test that 'khởi động' extracts to 'turn_on'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("khởi động quạt")
        assert action == "turn_on"
    
    def test_extract_action_tat_to_turn_off(self):
        """Test that 'tắt' extracts to 'turn_off'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("tắt đèn")
        assert action == "turn_off"
    
    def test_extract_action_dong_to_turn_off(self):
        """Test that 'đóng' extracts to 'turn_off'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("đóng cửa")
        assert action == "turn_off"
    
    def test_extract_action_dung_to_turn_off(self):
        """Test that 'dừng' extracts to 'turn_off'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("dừng quạt")
        assert action == "turn_off"
    
    def test_extract_action_dieu_chinh_to_adjust(self):
        """Test that 'điều chỉnh' extracts to 'adjust'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("điều chỉnh nhiệt độ")
        assert action == "adjust"
    
    def test_extract_action_chinh_to_adjust(self):
        """Test that 'chỉnh' extracts to 'adjust'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("chỉnh độ sáng")
        assert action == "adjust"
    
    def test_extract_action_dat_to_adjust(self):
        """Test that 'đặt' extracts to 'adjust'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("đặt nhiệt độ 25 độ")
        assert action == "adjust"
    
    def test_extract_action_khoa_to_lock(self):
        """Test that 'khóa' extracts to 'lock'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("khóa cửa")
        assert action == "lock"
    
    def test_extract_action_mo_khoa_to_unlock(self):
        """Test that 'mở khóa' extracts to 'unlock'."""
        extractor = EntityExtractor()
        action = extractor.extract_action("mở khóa cửa")
        assert action == "unlock"
    
    def test_extract_action_no_match_returns_none(self):
        """Test that no action match returns None."""
        extractor = EntityExtractor()
        action = extractor.extract_action("trời nóng quá")
        assert action is None


# ============================================================================
# UNIT TESTS: Location Extraction
# ============================================================================

class TestLocationExtraction:
    """Unit tests for location extraction."""
    
    def test_extract_location_phong_khach_to_living_room(self):
        """Test that 'phòng khách' extracts to 'living_room'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("bật đèn phòng khách")
        assert location == "living_room"
    
    def test_extract_location_phong_ngu_to_bedroom(self):
        """Test that 'phòng ngủ' extracts to 'bedroom'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("tắt quạt phòng ngủ")
        assert location == "bedroom"
    
    def test_extract_location_bep_to_kitchen(self):
        """Test that 'bếp' extracts to 'kitchen'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("bật đèn bếp")
        assert location == "kitchen"
    
    def test_extract_location_nha_bep_to_kitchen(self):
        """Test that 'nhà bếp' extracts to 'kitchen'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("tắt đèn nhà bếp")
        assert location == "kitchen"
    
    def test_extract_location_phong_tam_to_bathroom(self):
        """Test that 'phòng tắm' extracts to 'bathroom'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("mở cửa phòng tắm")
        assert location == "bathroom"
    
    def test_extract_location_nha_ve_sinh_to_bathroom(self):
        """Test that 'nhà vệ sinh' extracts to 'bathroom'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("bật đèn nhà vệ sinh")
        assert location == "bathroom"
    
    def test_extract_location_ban_cong_to_balcony(self):
        """Test that 'ban công' extracts to 'balcony'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("đóng mái che ban công")
        assert location == "balcony"
    
    def test_extract_location_garage_to_garage(self):
        """Test that 'garage' extracts to 'garage'."""
        extractor = EntityExtractor()
        location = extractor.extract_location("mở cửa garage")
        assert location == "garage"
    
    def test_extract_location_no_match_returns_none(self):
        """Test that no location match returns None."""
        extractor = EntityExtractor()
        location = extractor.extract_location("bật đèn")
        assert location is None


# ============================================================================
# UNIT TESTS: Numeric Value Extraction
# ============================================================================

class TestNumericValueExtraction:
    """Unit tests for numeric value extraction."""
    
    def test_extract_numeric_30_do_returns_30_C(self):
        """Test that '30 độ' extracts to (30, 'C')."""
        extractor = EntityExtractor()
        numeric = extractor.extract_numeric_value("đặt nhiệt độ 30 độ")
        assert numeric == (30, 'C')
    
    def test_extract_numeric_25_do_c_returns_25_C(self):
        """Test that '25 độ C' extracts to (25, 'C')."""
        extractor = EntityExtractor()
        numeric = extractor.extract_numeric_value("chỉnh 25 độ c")
        assert numeric == (25, 'C')
    
    def test_extract_numeric_50_percent_returns_50_percent(self):
        """Test that '50%' extracts to (50, '%')."""
        extractor = EntityExtractor()
        numeric = extractor.extract_numeric_value("chỉnh độ sáng 50%")
        assert numeric == (50, '%')
    
    def test_extract_numeric_80_percent_returns_80_percent(self):
        """Test that '80 %' extracts to (80, '%')."""
        extractor = EntityExtractor()
        numeric = extractor.extract_numeric_value("đặt 80 %")
        assert numeric == (80, '%')
    
    def test_extract_numeric_just_number_returns_number_empty_unit(self):
        """Test that just '25' extracts to (25, '')."""
        extractor = EntityExtractor()
        numeric = extractor.extract_numeric_value("đặt 25")
        assert numeric == (25, '')
    
    def test_extract_numeric_no_number_returns_none(self):
        """Test that no number returns None."""
        extractor = EntityExtractor()
        numeric = extractor.extract_numeric_value("bật đèn")
        assert numeric is None


# ============================================================================
# UNIT TESTS: Full Entity Extraction
# ============================================================================

class TestFullEntityExtraction:
    """Unit tests for full entity extraction based on intent."""
    
    def test_extract_control_device_all_entities(self):
        """Test control_device with all entities."""
        extractor = EntityExtractor()
        entities = extractor.extract("bật đèn phòng khách", "control_device")
        
        assert entities["device"] == "light"
        assert entities["action"] == "turn_on"
        assert entities["location"] == "living_room"
    
    def test_extract_control_device_with_numeric(self):
        """Test control_device with numeric value."""
        extractor = EntityExtractor()
        entities = extractor.extract("đặt nhiệt độ 25 độ", "control_device")
        
        assert entities["action"] == "adjust"
        assert entities["value"] == 25
        assert entities["unit"] == "C"
    
    def test_extract_environmental_comfort_cooling(self):
        """Test environmental_comfort with cooling."""
        extractor = EntityExtractor()
        entities = extractor.extract("Trời nóng quá", "environmental_comfort")
        
        assert entities["comfort_type"] == "cooling"
    
    def test_extract_environmental_comfort_warming(self):
        """Test environmental_comfort with warming."""
        extractor = EntityExtractor()
        entities = extractor.extract("Trời lạnh quá", "environmental_comfort")
        
        assert entities["comfort_type"] == "warming"
    
    def test_extract_environmental_comfort_brighten(self):
        """Test environmental_comfort with brighten."""
        extractor = EntityExtractor()
        entities = extractor.extract("Tối quá", "environmental_comfort")
        
        assert entities["comfort_type"] == "brighten"
    
    def test_extract_environmental_comfort_dim(self):
        """Test environmental_comfort with dim."""
        extractor = EntityExtractor()
        entities = extractor.extract("Sáng quá", "environmental_comfort")
        
        assert entities["comfort_type"] == "dim"
    
    def test_extract_environmental_comfort_ventilate(self):
        """Test environmental_comfort with ventilate."""
        extractor = EntityExtractor()
        entities = extractor.extract("Ngột ngạt", "environmental_comfort")
        
        assert entities["comfort_type"] == "ventilate"
    
    def test_extract_activate_scene_sleep(self):
        """Test activate_scene with sleep."""
        extractor = EntityExtractor()
        entities = extractor.extract("đi ngủ", "activate_scene")
        
        assert entities["scene_type"] == "sleep"
    
    def test_extract_activate_scene_wake_up(self):
        """Test activate_scene with wake_up."""
        extractor = EntityExtractor()
        entities = extractor.extract("thức dậy", "activate_scene")
        
        assert entities["scene_type"] == "wake_up"
    
    def test_extract_activate_scene_movie(self):
        """Test activate_scene with movie."""
        extractor = EntityExtractor()
        entities = extractor.extract("xem phim", "activate_scene")
        
        assert entities["scene_type"] == "movie"
    
    def test_extract_activate_scene_away(self):
        """Test activate_scene with away."""
        extractor = EntityExtractor()
        entities = extractor.extract("đi vắng", "activate_scene")
        
        assert entities["scene_type"] == "away"
    
    def test_extract_activate_scene_home(self):
        """Test activate_scene with home."""
        extractor = EntityExtractor()
        entities = extractor.extract("về nhà", "activate_scene")
        
        assert entities["scene_type"] == "home"
    
    def test_extract_query_sensor_temperature(self):
        """Test query_sensor with temperature."""
        extractor = EntityExtractor()
        entities = extractor.extract("nhiệt độ phòng ngủ bao nhiêu", "query_sensor")
        
        assert entities["sensor_type"] == "temperature"
        assert entities["location"] == "bedroom"
    
    def test_extract_query_sensor_humidity(self):
        """Test query_sensor with humidity."""
        extractor = EntityExtractor()
        entities = extractor.extract("độ ẩm hiện tại", "query_sensor")
        
        assert entities["sensor_type"] == "humidity"
    
    def test_extract_query_device_status(self):
        """Test query_device_status with device and location."""
        extractor = EntityExtractor()
        entities = extractor.extract("đèn phòng khách đang bật không", "query_device_status")
        
        assert entities["device"] == "light"
        assert entities["location"] == "living_room"
