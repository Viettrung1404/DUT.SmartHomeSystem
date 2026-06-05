"""
Property-based tests for Entity Extractor.

These tests verify universal properties that should hold for entity extraction:
- Property Test 2: Entity Schema Compliance
- Property Test 3: Entity Extraction Completeness for Control Device
"""

from hypothesis import given, strategies as st, settings, assume
import pytest
from typing import Optional, Dict, Any, List

# Import ENTITY_SCHEMA
from src.models.schemas import ENTITY_SCHEMA


# ============================================================================
# IMPORT REAL IMPLEMENTATION (Task 5.4 completed)
# ============================================================================

from src.entities.entity_extractor import EntityExtractor


# ============================================================================
# HYPOTHESIS STRATEGIES
# ============================================================================

# Valid intents
VALID_INTENTS = [
    "control_device",
    "environmental_comfort",
    "activate_scene",
    "query_sensor",
    "query_device_status",
    "security_mode",
    "security_alert",
    "weather_action",
    "lock_all_doors",
    "turn_off_all_devices",
    "create_automation",
    "unknown"
]


@st.composite
def control_device_text_strategy(draw):
    """
    Generate control device text with device and action.
    
    Examples:
    - "bật đèn phòng khách"
    - "tắt quạt"
    - "mở cửa"
    """
    devices = ["đèn", "quạt", "điều hòa", "ac", "cửa", "mái che"]
    actions = ["bật", "tắt", "mở", "đóng"]
    locations = ["phòng khách", "phòng ngủ", "bếp", "phòng tắm", "ban công"]
    
    action = draw(st.sampled_from(actions))
    device = draw(st.sampled_from(devices))
    
    # Optional location
    include_location = draw(st.booleans())
    
    if include_location:
        location = draw(st.sampled_from(locations))
        text = f"{action} {device} {location}"
    else:
        text = f"{action} {device}"
    
    return text


@st.composite
def environmental_comfort_text_strategy(draw):
    """
    Generate environmental comfort text.
    
    Examples:
    - "Trời nóng quá"
    - "Tối quá"
    - "Ngột ngạt"
    """
    comfort_phrases = [
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
    
    phrase = draw(st.sampled_from(comfort_phrases))
    return phrase


@st.composite
def scene_activation_text_strategy(draw):
    """
    Generate scene activation text.
    
    Examples:
    - "đi ngủ"
    - "thức dậy"
    - "xem phim"
    """
    scene_phrases = [
        "đi ngủ",
        "chúc ngủ ngon",
        "thức dậy",
        "buổi sáng",
        "xem phim",
        "xem tv",
        "đi vắng",
        "rời nhà",
        "về nhà",
        "đã về"
    ]
    
    phrase = draw(st.sampled_from(scene_phrases))
    return phrase


@st.composite
def sensor_query_text_strategy(draw):
    """
    Generate sensor query text.
    
    Examples:
    - "Nhiệt độ phòng ngủ bao nhiêu"
    - "Độ ẩm hiện tại"
    """
    sensor_types = ["nhiệt độ", "độ ẩm", "mưa", "khí gas", "cháy"]
    locations = ["phòng khách", "phòng ngủ", "bếp", "phòng tắm", "ban công"]
    
    sensor = draw(st.sampled_from(sensor_types))
    
    # Optional location
    include_location = draw(st.booleans())
    
    if include_location:
        location = draw(st.sampled_from(locations))
        text = f"{sensor} {location} bao nhiêu"
    else:
        text = f"{sensor} bao nhiêu"
    
    return text


# ============================================================================
# PROPERTY TESTS
# ============================================================================

class TestEntityExtractorProperties:
    """Property-based tests for Entity Extractor."""
    
    @given(text=control_device_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_entity_schema_compliance_control_device(self, text):
        """
        **Validates: Requirements 1.3, 2.2, 2.3, 2.4**
        
        Property 2: Entity Schema Compliance
        
        For any extracted entities, all entity keys and values SHALL belong 
        to ENTITY_SCHEMA defined in the system.
        
        Rationale:
        Entity schema compliance ensures consistency across the system. 
        Backend Decision Engine relies on standardized entity values to 
        make correct decisions. Invalid entities would cause system failures.
        
        Test Strategy:
        1. Generate control device text using Hypothesis
        2. Extract entities using EntityExtractor
        3. Assert: All entity keys are valid (device, action, location, value, unit)
        4. Assert: All entity values belong to ENTITY_SCHEMA
        
        This property ensures that:
        - Entity keys are standardized
        - Entity values are from predefined schema
        - No invalid entities are extracted
        """
        extractor = EntityExtractor()
        intent = "control_device"
        
        # Extract entities
        entities = extractor.extract(text, intent)
        
        # Assert: All entity keys are valid for control_device
        valid_keys = {"device", "action", "location", "value", "unit"}
        for key in entities.keys():
            assert key in valid_keys, (
                f"Invalid entity key for control_device:\n"
                f"  Text: {repr(text)}\n"
                f"  Key: {key}\n"
                f"  Valid keys: {valid_keys}"
            )
        
        # Assert: device value belongs to ENTITY_SCHEMA
        if "device" in entities:
            assert entities["device"] in ENTITY_SCHEMA["device_types"], (
                f"Device value not in ENTITY_SCHEMA:\n"
                f"  Text: {repr(text)}\n"
                f"  Device: {entities['device']}\n"
                f"  Valid devices: {ENTITY_SCHEMA['device_types']}"
            )
        
        # Assert: action value belongs to ENTITY_SCHEMA
        if "action" in entities:
            assert entities["action"] in ENTITY_SCHEMA["actions"], (
                f"Action value not in ENTITY_SCHEMA:\n"
                f"  Text: {repr(text)}\n"
                f"  Action: {entities['action']}\n"
                f"  Valid actions: {ENTITY_SCHEMA['actions']}"
            )
        
        # Assert: location value belongs to ENTITY_SCHEMA
        if "location" in entities:
            assert entities["location"] in ENTITY_SCHEMA["locations"], (
                f"Location value not in ENTITY_SCHEMA:\n"
                f"  Text: {repr(text)}\n"
                f"  Location: {entities['location']}\n"
                f"  Valid locations: {ENTITY_SCHEMA['locations']}"
            )
    
    @given(text=environmental_comfort_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_entity_schema_compliance_environmental_comfort(self, text):
        """
        **Validates: Requirements 1.3, 3.2**
        
        Property 2: Entity Schema Compliance (Environmental Comfort)
        
        For environmental_comfort intent, comfort_type entity SHALL belong 
        to ENTITY_SCHEMA.
        """
        extractor = EntityExtractor()
        intent = "environmental_comfort"
        
        # Extract entities
        entities = extractor.extract(text, intent)
        
        # Assert: All entity keys are valid for environmental_comfort
        valid_keys = {"comfort_type"}
        for key in entities.keys():
            assert key in valid_keys, (
                f"Invalid entity key for environmental_comfort:\n"
                f"  Text: {repr(text)}\n"
                f"  Key: {key}\n"
                f"  Valid keys: {valid_keys}"
            )
        
        # Assert: comfort_type value belongs to ENTITY_SCHEMA
        if "comfort_type" in entities:
            assert entities["comfort_type"] in ENTITY_SCHEMA["comfort_types"], (
                f"Comfort type value not in ENTITY_SCHEMA:\n"
                f"  Text: {repr(text)}\n"
                f"  Comfort type: {entities['comfort_type']}\n"
                f"  Valid comfort types: {ENTITY_SCHEMA['comfort_types']}"
            )
    
    @given(text=scene_activation_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_entity_schema_compliance_activate_scene(self, text):
        """
        **Validates: Requirements 1.3, 6.2**
        
        Property 2: Entity Schema Compliance (Activate Scene)
        
        For activate_scene intent, scene_type entity SHALL belong 
        to ENTITY_SCHEMA.
        """
        extractor = EntityExtractor()
        intent = "activate_scene"
        
        # Extract entities
        entities = extractor.extract(text, intent)
        
        # Assert: All entity keys are valid for activate_scene
        valid_keys = {"scene_type"}
        for key in entities.keys():
            assert key in valid_keys, (
                f"Invalid entity key for activate_scene:\n"
                f"  Text: {repr(text)}\n"
                f"  Key: {key}\n"
                f"  Valid keys: {valid_keys}"
            )
        
        # Assert: scene_type value belongs to ENTITY_SCHEMA
        if "scene_type" in entities:
            assert entities["scene_type"] in ENTITY_SCHEMA["scene_types"], (
                f"Scene type value not in ENTITY_SCHEMA:\n"
                f"  Text: {repr(text)}\n"
                f"  Scene type: {entities['scene_type']}\n"
                f"  Valid scene types: {ENTITY_SCHEMA['scene_types']}"
            )
    
    @given(text=sensor_query_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_2_entity_schema_compliance_query_sensor(self, text):
        """
        **Validates: Requirements 1.3, 4.2**
        
        Property 2: Entity Schema Compliance (Query Sensor)
        
        For query_sensor intent, sensor_type entity SHALL belong 
        to ENTITY_SCHEMA.
        """
        extractor = EntityExtractor()
        intent = "query_sensor"
        
        # Extract entities
        entities = extractor.extract(text, intent)
        
        # Assert: All entity keys are valid for query_sensor
        valid_keys = {"sensor_type", "location"}
        for key in entities.keys():
            assert key in valid_keys, (
                f"Invalid entity key for query_sensor:\n"
                f"  Text: {repr(text)}\n"
                f"  Key: {key}\n"
                f"  Valid keys: {valid_keys}"
            )
        
        # Assert: sensor_type value belongs to ENTITY_SCHEMA
        if "sensor_type" in entities:
            assert entities["sensor_type"] in ENTITY_SCHEMA["sensor_types"], (
                f"Sensor type value not in ENTITY_SCHEMA:\n"
                f"  Text: {repr(text)}\n"
                f"  Sensor type: {entities['sensor_type']}\n"
                f"  Valid sensor types: {ENTITY_SCHEMA['sensor_types']}"
            )
        
        # Assert: location value belongs to ENTITY_SCHEMA
        if "location" in entities:
            assert entities["location"] in ENTITY_SCHEMA["locations"], (
                f"Location value not in ENTITY_SCHEMA:\n"
                f"  Text: {repr(text)}\n"
                f"  Location: {entities['location']}\n"
                f"  Valid locations: {ENTITY_SCHEMA['locations']}"
            )
    
    @given(text=control_device_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_property_3_entity_extraction_completeness_control_device(self, text):
        """
        **Validates: Requirements 2.2, 2.3, 2.4**
        
        Property 3: Entity Extraction Completeness for Control Device
        
        For control_device intent, the EntityExtractor SHALL always extract 
        device and action entities (required), and optionally location entity.
        
        Rationale:
        Control device intent requires device and action to be actionable. 
        Without these entities, Backend cannot execute the command.
        
        Test Strategy:
        1. Generate control device text using Hypothesis
        2. Extract entities using EntityExtractor
        3. Assert: device entity is present
        4. Assert: action entity is present
        5. Assert: location entity is optional
        
        This property ensures that:
        - Required entities are always extracted
        - Control device commands are always actionable
        - System doesn't return incomplete results
        """
        extractor = EntityExtractor()
        intent = "control_device"
        
        # Extract entities
        entities = extractor.extract(text, intent)
        
        # Assert: device entity is present
        assert "device" in entities, (
            f"Device entity missing for control_device:\n"
            f"  Text: {repr(text)}\n"
            f"  Entities: {entities}"
        )
        
        # Assert: action entity is present
        assert "action" in entities, (
            f"Action entity missing for control_device:\n"
            f"  Text: {repr(text)}\n"
            f"  Entities: {entities}"
        )
        
        # Location is optional, no assertion needed


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEntityExtractorEdgeCases:
    """Example-based tests for specific edge cases."""
    
    def test_control_device_with_all_entities(self):
        """Test control device with device, action, and location."""
        extractor = EntityExtractor()
        entities = extractor.extract("bật đèn phòng khách", "control_device")
        
        assert entities["device"] == "light"
        assert entities["action"] == "turn_on"
        assert entities["location"] == "living_room"
    
    def test_control_device_without_location(self):
        """Test control device without location."""
        extractor = EntityExtractor()
        entities = extractor.extract("bật đèn", "control_device")
        
        assert entities["device"] == "light"
        assert entities["action"] == "turn_on"
        assert "location" not in entities
    
    def test_environmental_comfort_cooling(self):
        """Test environmental comfort with cooling."""
        extractor = EntityExtractor()
        entities = extractor.extract("Trời nóng quá", "environmental_comfort")
        
        assert entities["comfort_type"] == "cooling"
    
    def test_activate_scene_sleep(self):
        """Test activate scene with sleep."""
        extractor = EntityExtractor()
        entities = extractor.extract("đi ngủ", "activate_scene")
        
        assert entities["scene_type"] == "sleep"
    
    def test_query_sensor_temperature(self):
        """Test query sensor with temperature."""
        extractor = EntityExtractor()
        entities = extractor.extract("nhiệt độ phòng ngủ bao nhiêu", "query_sensor")
        
        assert entities["sensor_type"] == "temperature"
