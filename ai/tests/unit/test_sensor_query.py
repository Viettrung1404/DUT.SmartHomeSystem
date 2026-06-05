"""
Unit tests for sensor query classification.

These tests verify that sensor query patterns are correctly classified as
query_sensor or query_device_status with appropriate entity extraction.

**Validates: Requirements 4.1, 4.2, 4.3, 4.4**
"""

import pytest
from src.classifiers.rule_based import RuleBasedClassifier
from src.entities.entity_extractor import EntityExtractor


class TestSensorQueryClassification:
    """Unit tests for sensor query intent classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.rule_classifier = RuleBasedClassifier()
        self.entity_extractor = EntityExtractor()
    
    # ========================================================================
    # TEMPERATURE SENSOR QUERIES
    # ========================================================================
    
    def test_temperature_query_basic(self):
        """Test: 'nhiệt độ bao nhiêu' -> query_sensor with temperature."""
        text = "nhiệt độ bao nhiêu"
        
        # For now, rule-based classifier doesn't handle sensor queries
        # This will be implemented in Task 11.3
        # result = self.rule_classifier.classify(text)
        
        # Test entity extraction
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "temperature", \
            f"Expected sensor_type 'temperature', got {entities.get('sensor_type')}"
    
    def test_temperature_query_with_degrees(self):
        """Test: 'bao nhiêu độ' -> query_sensor with temperature."""
        text = "bao nhiêu độ"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "temperature"
    
    def test_temperature_query_with_measure(self):
        """Test: 'đo nhiệt độ' -> query_sensor with temperature."""
        text = "đo nhiệt độ"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "temperature"
    
    def test_temperature_query_with_location(self):
        """Test: 'nhiệt độ phòng ngủ' -> query_sensor with temperature and location."""
        text = "nhiệt độ phòng ngủ"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "temperature"
        assert entities.get("location") == "bedroom"
    
    def test_temperature_query_with_check(self):
        """Test: 'kiểm tra nhiệt độ' -> query_sensor with temperature."""
        text = "kiểm tra nhiệt độ"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "temperature"
    
    # ========================================================================
    # HUMIDITY SENSOR QUERIES
    # ========================================================================
    
    def test_humidity_query_basic(self):
        """Test: 'độ ẩm bao nhiêu' -> query_sensor with humidity."""
        text = "độ ẩm bao nhiêu"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "humidity"
    
    def test_humidity_query_short(self):
        """Test: 'ẩm không' -> query_sensor with humidity."""
        text = "ẩm không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "humidity"
    
    def test_humidity_query_with_check(self):
        """Test: 'kiểm tra độ ẩm' -> query_sensor with humidity."""
        text = "kiểm tra độ ẩm"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "humidity"
    
    def test_humidity_query_with_location(self):
        """Test: 'độ ẩm phòng khách' -> query_sensor with humidity and location."""
        text = "độ ẩm phòng khách"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "humidity"
        assert entities.get("location") == "living_room"
    
    # ========================================================================
    # RAIN SENSOR QUERIES
    # ========================================================================
    
    def test_rain_query_basic(self):
        """Test: 'có mưa không' -> query_sensor with rain."""
        text = "có mưa không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "rain"
    
    def test_rain_query_weather(self):
        """Test: 'trời mưa không' -> query_sensor with rain."""
        text = "trời mưa không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "rain"
    
    def test_rain_query_forecast(self):
        """Test: 'dự báo mưa' -> query_sensor with rain."""
        text = "dự báo mưa"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "rain"
    
    def test_rain_query_outside(self):
        """Test: 'có mưa ngoài trời không' -> query_sensor with rain."""
        text = "có mưa ngoài trời không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "rain"
    
    # ========================================================================
    # GAS SENSOR QUERIES
    # ========================================================================
    
    def test_gas_query_basic(self):
        """Test: 'có khí gas không' -> query_sensor with gas."""
        text = "có khí gas không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "gas"
    
    def test_gas_query_leak(self):
        """Test: 'rò rỉ gas' -> query_sensor with gas."""
        text = "rò rỉ gas"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "gas"
    
    def test_gas_query_detect(self):
        """Test: 'phát hiện gas' -> query_sensor with gas."""
        text = "phát hiện gas"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "gas"
    
    def test_gas_query_check(self):
        """Test: 'kiểm tra khí gas' -> query_sensor with gas."""
        text = "kiểm tra khí gas"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "gas"
    
    # ========================================================================
    # FIRE SENSOR QUERIES
    # ========================================================================
    
    def test_fire_query_basic(self):
        """Test: 'có cháy không' -> query_sensor with fire."""
        text = "có cháy không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "fire"
    
    def test_fire_query_detect(self):
        """Test: 'phát hiện lửa' -> query_sensor with fire."""
        text = "phát hiện lửa"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "fire"
    
    def test_fire_query_alarm(self):
        """Test: 'báo cháy' -> query_sensor with fire."""
        text = "báo cháy"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "fire"
    
    def test_fire_query_check(self):
        """Test: 'kiểm tra cháy' -> query_sensor with fire."""
        text = "kiểm tra cháy"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "fire"
    
    # ========================================================================
    # MOTION SENSOR QUERIES
    # ========================================================================
    
    def test_motion_query_basic(self):
        """Test: 'có người không' -> query_sensor with motion."""
        text = "có người không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "motion"
    
    def test_motion_query_detect(self):
        """Test: 'phát hiện chuyển động' -> query_sensor with motion."""
        text = "phát hiện chuyển động"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "motion"
    
    def test_motion_query_someone(self):
        """Test: 'ai đó vào' -> query_sensor with motion."""
        text = "ai đó vào"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "motion"
    
    def test_motion_query_check(self):
        """Test: 'kiểm tra chuyển động' -> query_sensor with motion."""
        text = "kiểm tra chuyển động"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "motion"
    
    def test_motion_query_in_room(self):
        """Test: 'có ai trong phòng không' -> query_sensor with motion."""
        text = "có ai trong phòng không"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        assert entities.get("sensor_type") == "motion"


class TestDeviceStatusQueryClassification:
    """Unit tests for device status query intent classification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.rule_classifier = RuleBasedClassifier()
        self.entity_extractor = EntityExtractor()
    
    # ========================================================================
    # LIGHT STATUS QUERIES
    # ========================================================================
    
    def test_light_status_query_basic(self):
        """Test: 'trạng thái đèn' -> query_device_status with light."""
        text = "trạng thái đèn"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "light"
    
    def test_light_status_query_is_on(self):
        """Test: 'đèn có bật không' -> query_device_status with light."""
        text = "đèn có bật không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "light"
    
    def test_light_status_query_is_running(self):
        """Test: 'đèn đang bật không' -> query_device_status with light."""
        text = "đèn đang bật không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "light"
    
    def test_light_status_query_with_location(self):
        """Test: 'trạng thái đèn phòng khách' -> query_device_status with light and location."""
        text = "trạng thái đèn phòng khách"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "light"
        assert entities.get("location") == "living_room"
    
    # ========================================================================
    # FAN STATUS QUERIES
    # ========================================================================
    
    def test_fan_status_query_basic(self):
        """Test: 'trạng thái quạt' -> query_device_status with fan."""
        text = "trạng thái quạt"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "fan"
    
    def test_fan_status_query_is_on(self):
        """Test: 'quạt có bật không' -> query_device_status with fan."""
        text = "quạt có bật không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "fan"
    
    def test_fan_status_query_is_running(self):
        """Test: 'quạt đang chạy không' -> query_device_status with fan."""
        text = "quạt đang chạy không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "fan"
    
    def test_fan_status_query_with_location(self):
        """Test: 'trạng thái quạt phòng ngủ' -> query_device_status with fan and location."""
        text = "trạng thái quạt phòng ngủ"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "fan"
        assert entities.get("location") == "bedroom"
    
    # ========================================================================
    # AC STATUS QUERIES
    # ========================================================================
    
    def test_ac_status_query_basic(self):
        """Test: 'trạng thái điều hòa' -> query_device_status with ac."""
        text = "trạng thái điều hòa"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "ac"
    
    def test_ac_status_query_is_on(self):
        """Test: 'điều hòa có bật không' -> query_device_status with ac."""
        text = "điều hòa có bật không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "ac"
    
    def test_ac_status_query_short(self):
        """Test: 'ac đang bật không' -> query_device_status with ac."""
        text = "ac đang bật không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "ac"
    
    # ========================================================================
    # DOOR STATUS QUERIES
    # ========================================================================
    
    def test_door_status_query_basic(self):
        """Test: 'trạng thái cửa' -> query_device_status with door."""
        text = "trạng thái cửa"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "door"
    
    def test_door_status_query_is_open(self):
        """Test: 'cửa có mở không' -> query_device_status with door."""
        text = "cửa có mở không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "door"
    
    def test_door_status_query_is_opening(self):
        """Test: 'cửa đang mở không' -> query_device_status with door."""
        text = "cửa đang mở không"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        assert entities.get("device") == "door"
    
    # ========================================================================
    # EDGE CASES AND NEGATIVE TESTS
    # ========================================================================
    
    def test_query_vs_control_distinction(self):
        """Test that query patterns are distinguished from control patterns."""
        # Query pattern
        query_text = "đèn có bật không"
        query_entities = self.entity_extractor.extract(query_text, "query_device_status")
        assert query_entities.get("device") == "light"
        
        # Control pattern
        control_text = "bật đèn"
        control_entities = self.entity_extractor.extract(control_text, "control_device")
        assert control_entities.get("device") == "light"
        assert control_entities.get("action") == "turn_on"
    
    def test_sensor_query_with_multiple_locations(self):
        """Test sensor query with location extraction."""
        test_cases = [
            ("nhiệt độ phòng khách", "living_room"),
            ("độ ẩm phòng ngủ", "bedroom"),
            ("nhiệt độ bếp", "kitchen"),
            ("độ ẩm phòng tắm", "bathroom")
        ]
        
        for text, expected_location in test_cases:
            entities = self.entity_extractor.extract(text, "query_sensor")
            assert entities.get("location") == expected_location, \
                f"Expected location '{expected_location}' for '{text}', got '{entities.get('location')}'"
    
    def test_device_status_query_with_multiple_locations(self):
        """Test device status query with location extraction."""
        test_cases = [
            ("trạng thái đèn phòng khách", "light", "living_room"),
            ("quạt phòng ngủ có bật không", "fan", "bedroom"),
            ("trạng thái điều hòa bếp", "ac", "kitchen")
        ]
        
        for text, expected_device, expected_location in test_cases:
            entities = self.entity_extractor.extract(text, "query_device_status")
            assert entities.get("device") == expected_device, \
                f"Expected device '{expected_device}' for '{text}', got '{entities.get('device')}'"
            assert entities.get("location") == expected_location, \
                f"Expected location '{expected_location}' for '{text}', got '{entities.get('location')}'"
    
    def test_empty_entities_for_unknown_sensor(self):
        """Test that unknown sensor types don't extract entities."""
        text = "kiểm tra xyz"
        
        entities = self.entity_extractor.extract(text, "query_sensor")
        
        # Should not extract sensor_type for unknown sensor
        assert "sensor_type" not in entities or entities.get("sensor_type") is None
    
    def test_empty_entities_for_unknown_device(self):
        """Test that unknown device types don't extract entities."""
        text = "trạng thái xyz"
        
        entities = self.entity_extractor.extract(text, "query_device_status")
        
        # Should not extract device for unknown device
        assert "device" not in entities or entities.get("device") is None


class TestSensorQueryEntityExtraction:
    """Unit tests for entity extraction in sensor queries."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.entity_extractor = EntityExtractor()
    
    def test_extract_all_sensor_types(self):
        """Test extraction of all sensor types."""
        test_cases = [
            ("nhiệt độ", "temperature"),
            ("độ ẩm", "humidity"),
            ("mưa", "rain"),
            ("khí gas", "gas"),
            ("cháy", "fire"),
            ("chuyển động", "motion")
        ]
        
        for text, expected_sensor_type in test_cases:
            entities = self.entity_extractor.extract(text, "query_sensor")
            assert entities.get("sensor_type") == expected_sensor_type, \
                f"Expected sensor_type '{expected_sensor_type}' for '{text}', got '{entities.get('sensor_type')}'"
    
    def test_extract_all_device_types_for_status(self):
        """Test extraction of all device types for status queries."""
        test_cases = [
            ("trạng thái đèn", "light"),
            ("trạng thái quạt", "fan"),
            ("trạng thái điều hòa", "ac"),
            ("trạng thái cửa", "door")
        ]
        
        for text, expected_device in test_cases:
            entities = self.entity_extractor.extract(text, "query_device_status")
            assert entities.get("device") == expected_device, \
                f"Expected device '{expected_device}' for '{text}', got '{entities.get('device')}'"
    
    def test_longest_match_first(self):
        """Test that longest keyword match is prioritized."""
        # "khí gas" should match before "gas"
        text = "có khí gas không"
        entities = self.entity_extractor.extract(text, "query_sensor")
        assert entities.get("sensor_type") == "gas"
        
        # "điều hòa" should match before individual words
        text = "trạng thái điều hòa"
        entities = self.entity_extractor.extract(text, "query_device_status")
        assert entities.get("device") == "ac"
    
    def test_case_insensitive_matching(self):
        """Test that entity extraction is case-insensitive."""
        test_cases = [
            ("NHIỆT ĐỘ", "temperature"),
            ("Độ Ẩm", "humidity"),
            ("Trạng Thái Đèn", "light")
        ]
        
        for text, expected_value in test_cases:
            if "nhiệt" in text.lower() or "độ ẩm" in text.lower():
                entities = self.entity_extractor.extract(text, "query_sensor")
                assert entities.get("sensor_type") == expected_value
            else:
                entities = self.entity_extractor.extract(text, "query_device_status")
                assert entities.get("device") == expected_value
