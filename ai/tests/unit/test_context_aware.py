"""
Unit tests for Context-Aware Classification.

Tests location inference from device context and device prioritization
for context-aware intent classification.

**Validates: Requirements 9.1-9.3**
"""

import pytest
from src.models.schemas import DeviceContext
from src.entities.entity_extractor import EntityExtractor
from src.classifiers.rule_based import RuleBasedClassifier


class TestLocationInference:
    """Unit tests for location inference from device context."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = EntityExtractor()
    
    # ========================================================================
    # CONTROL DEVICE INTENT
    # ========================================================================
    
    def test_control_device_infers_location_from_context(self):
        """Test that control_device infers location from context."""
        context = DeviceContext(current_room="living_room")
        
        entities = self.extractor.extract("bật đèn", "control_device", context)
        
        assert "location" in entities
        assert entities["location"] == "living_room"
    
    def test_control_device_all_rooms(self):
        """Test location inference for all valid rooms."""
        rooms = ["living_room", "bedroom", "kitchen", "bathroom", "balcony"]
        
        for room in rooms:
            context = DeviceContext(current_room=room)
            entities = self.extractor.extract("bật đèn", "control_device", context)
            
            assert "location" in entities
            assert entities["location"] == room
    
    def test_control_device_explicit_location_overrides_context(self):
        """Test that explicit location overrides context."""
        context = DeviceContext(current_room="living_room")
        
        entities = self.extractor.extract("bật đèn phòng ngủ", "control_device", context)
        
        assert "location" in entities
        assert entities["location"] == "bedroom"
    
    def test_control_device_no_context_no_location(self):
        """Test that without context, no location is inferred."""
        entities = self.extractor.extract("bật đèn", "control_device", None)
        
        assert "location" not in entities
    
    def test_control_device_empty_context_no_location(self):
        """Test that empty context doesn't infer location."""
        context = DeviceContext(current_room=None)
        
        entities = self.extractor.extract("bật đèn", "control_device", context)
        
        assert "location" not in entities
    
    # ========================================================================
    # QUERY SENSOR INTENT
    # ========================================================================
    
    def test_query_sensor_infers_location_from_context(self):
        """Test that query_sensor infers location from context."""
        context = DeviceContext(current_room="bedroom")
        
        entities = self.extractor.extract("nhiệt độ bao nhiêu", "query_sensor", context)
        
        assert "location" in entities
        assert entities["location"] == "bedroom"
    
    def test_query_sensor_explicit_location_overrides_context(self):
        """Test that explicit location overrides context for query_sensor."""
        context = DeviceContext(current_room="living_room")
        
        entities = self.extractor.extract("nhiệt độ phòng ngủ bao nhiêu", "query_sensor", context)
        
        assert "location" in entities
        assert entities["location"] == "bedroom"
    
    def test_query_sensor_no_context_no_location(self):
        """Test that without context, no location is inferred for query_sensor."""
        entities = self.extractor.extract("nhiệt độ bao nhiêu", "query_sensor", None)
        
        assert "location" not in entities
    
    # ========================================================================
    # QUERY DEVICE STATUS INTENT
    # ========================================================================
    
    def test_query_device_status_infers_location_from_context(self):
        """Test that query_device_status infers location from context."""
        context = DeviceContext(current_room="kitchen")
        
        entities = self.extractor.extract("trạng thái đèn", "query_device_status", context)
        
        assert "location" in entities
        assert entities["location"] == "kitchen"
    
    def test_query_device_status_explicit_location_overrides_context(self):
        """Test that explicit location overrides context for query_device_status."""
        context = DeviceContext(current_room="living_room")
        
        entities = self.extractor.extract("trạng thái đèn phòng ngủ", "query_device_status", context)
        
        assert "location" in entities
        assert entities["location"] == "bedroom"
    
    def test_query_device_status_no_context_no_location(self):
        """Test that without context, no location is inferred for query_device_status."""
        entities = self.extractor.extract("trạng thái đèn", "query_device_status", None)
        
        assert "location" not in entities
    
    # ========================================================================
    # LOCATION PRIORITY TESTS
    # ========================================================================
    
    def test_location_priority_explicit_over_context(self):
        """Test that explicit location has priority over context."""
        context = DeviceContext(current_room="living_room")
        
        # Explicit location should win
        entities = self.extractor.extract("bật đèn phòng ngủ", "control_device", context)
        assert entities["location"] == "bedroom"
        
        entities = self.extractor.extract("bật đèn bếp", "control_device", context)
        assert entities["location"] == "kitchen"
    
    def test_location_priority_context_over_none(self):
        """Test that context location has priority over no location."""
        context = DeviceContext(current_room="bedroom")
        
        # Context location should be used
        entities = self.extractor.extract("bật đèn", "control_device", context)
        assert entities["location"] == "bedroom"
        
        # Without context, no location
        entities = self.extractor.extract("bật đèn", "control_device", None)
        assert "location" not in entities
    
    # ========================================================================
    # MULTIPLE DEVICES WITH SAME CONTEXT
    # ========================================================================
    
    def test_multiple_devices_same_context(self):
        """Test that context applies to multiple device commands."""
        context = DeviceContext(current_room="bedroom")
        
        commands = [
            ("bật đèn", "control_device"),
            ("tắt quạt", "control_device"),
            ("bật điều hòa", "control_device")
        ]
        
        for command, intent in commands:
            entities = self.extractor.extract(command, intent, context)
            assert "location" in entities
            assert entities["location"] == "bedroom"
    
    def test_multiple_queries_same_context(self):
        """Test that context applies to multiple query commands."""
        context = DeviceContext(current_room="living_room")
        
        commands = [
            ("nhiệt độ bao nhiêu", "query_sensor"),
            ("độ ẩm bao nhiêu", "query_sensor"),
            ("trạng thái đèn", "query_device_status"),
            ("trạng thái quạt", "query_device_status")
        ]
        
        for command, intent in commands:
            entities = self.extractor.extract(command, intent, context)
            assert "location" in entities
            assert entities["location"] == "living_room"


class TestContextAwareClassification:
    """Unit tests for context-aware classification with rule-based classifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = RuleBasedClassifier()
        self.extractor = EntityExtractor()
    
    def test_full_flow_with_context(self):
        """Test full classification flow with context."""
        context = DeviceContext(current_room="bedroom")
        
        # Classify
        result = self.classifier.classify("bật đèn")
        assert result is not None
        assert result.intent == "control_device"
        
        # Extract entities with context
        entities = self.extractor.extract("bật đèn", result.intent, context)
        
        # Should have device, action, and location
        assert entities["device"] == "light"
        assert entities["action"] == "turn_on"
        assert entities["location"] == "bedroom"
    
    def test_full_flow_without_context(self):
        """Test full classification flow without context."""
        # Classify
        result = self.classifier.classify("bật đèn")
        assert result is not None
        assert result.intent == "control_device"
        
        # Extract entities without context
        entities = self.extractor.extract("bật đèn", result.intent, None)
        
        # Should have device and action, but no location
        assert entities["device"] == "light"
        assert entities["action"] == "turn_on"
        assert "location" not in entities
    
    def test_context_with_explicit_location(self):
        """Test that explicit location is preserved even with context."""
        context = DeviceContext(current_room="living_room")
        
        # Classify
        result = self.classifier.classify("bật đèn phòng ngủ")
        assert result is not None
        
        # Extract entities with context
        entities = self.extractor.extract("bật đèn phòng ngủ", result.intent, context)
        
        # Should use explicit location, not context
        assert entities["location"] == "bedroom"


class TestContextEdgeCases:
    """Unit tests for context-aware edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = EntityExtractor()
    
    def test_invalid_room_in_context(self):
        """Test handling of invalid room in context."""
        # Note: DeviceContext doesn't validate room names, so any string is accepted
        context = DeviceContext(current_room="invalid_room")
        
        entities = self.extractor.extract("bật đèn", "control_device", context)
        
        # Should still infer location from context (even if invalid)
        assert "location" in entities
        assert entities["location"] == "invalid_room"
    
    def test_whitespace_in_context_room(self):
        """Test handling of whitespace in context room."""
        context = DeviceContext(current_room="  living_room  ")
        
        entities = self.extractor.extract("bật đèn", "control_device", context)
        
        # Should preserve whitespace (no trimming in entity extractor)
        assert "location" in entities
        assert entities["location"] == "  living_room  "
    
    def test_context_with_non_location_intent(self):
        """Test that context doesn't affect non-location intents."""
        context = DeviceContext(current_room="bedroom")
        
        # Scene activation doesn't use location
        entities = self.extractor.extract("đi ngủ", "activate_scene", context)
        
        # Should not have location
        assert "location" not in entities
        assert "scene_type" in entities
    
    def test_context_with_environmental_comfort(self):
        """Test that context doesn't affect environmental comfort."""
        context = DeviceContext(current_room="bedroom")
        
        # Environmental comfort doesn't use location
        entities = self.extractor.extract("nóng quá", "environmental_comfort", context)
        
        # Should not have location
        assert "location" not in entities
        assert "comfort_type" in entities


class TestDeviceContextSchema:
    """Unit tests for DeviceContext schema."""
    
    def test_device_context_creation(self):
        """Test creating DeviceContext."""
        context = DeviceContext(current_room="living_room")
        
        assert context.current_room == "living_room"
    
    def test_device_context_optional_room(self):
        """Test that current_room is optional."""
        context = DeviceContext()
        
        assert context.current_room is None
    
    def test_device_context_none_room(self):
        """Test DeviceContext with None room."""
        context = DeviceContext(current_room=None)
        
        assert context.current_room is None
    
    def test_device_context_all_valid_rooms(self):
        """Test DeviceContext with all valid rooms."""
        rooms = ["living_room", "bedroom", "kitchen", "bathroom", "balcony"]
        
        for room in rooms:
            context = DeviceContext(current_room=room)
            assert context.current_room == room
