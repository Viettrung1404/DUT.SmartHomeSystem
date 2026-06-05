"""
Entity schema definitions for Vietnamese NLP Intent Classification.
Defines all valid entity types and their allowed values.
"""

from typing import Dict, List

# Entity Schema - Standardized Parameters
ENTITY_SCHEMA: Dict[str, List[str]] = {
    "device_types": [
        "light",
        "fan",
        "ac",
        "door",
        "awning",
        "lock",
        "curtain",
        "camera",
    ],
    "actions": [
        "turn_on",
        "turn_off",
        "adjust",
        "open",
        "close",
        "lock",
        "unlock",
    ],
    "locations": [
        "living_room",
        "bedroom",
        "kitchen",
        "bathroom",
        "balcony",
        "garage",
    ],
    "scene_types": [
        "sleep",
        "wake_up",
        "movie",
        "away",
        "home",
    ],
    "sensor_types": [
        "temperature",
        "humidity",
        "rain",
        "gas",
        "fire",
        "motion",
    ],
    "comfort_types": [
        "cooling",
        "warming",
        "brighten",
        "dim",
        "ventilate",
    ],
    "security_modes": [
        "armed",
        "disarmed",
    ],
    "alert_types": [
        "fire",
        "gas",
        "intrusion",
    ],
    "weather_conditions": [
        "rain",
        "sunny",
    ],
}

# Intent Categories (15 core intents)
INTENT_CATEGORIES: List[str] = [
    "control_device",
    "environmental_comfort",
    "query_sensor",
    "query_device_status",
    "security_mode",
    "security_alert",
    "activate_scene",
    "weather_action",
    "lock_all_doors",
    "turn_off_all_devices",
    "create_automation",
    "unknown",
]

# Intent to Entity Mapping (which entities are expected for each intent)
INTENT_ENTITY_MAPPING: Dict[str, List[str]] = {
    "control_device": ["device", "action", "location", "value", "unit"],
    "environmental_comfort": ["comfort_type", "location"],
    "query_sensor": ["sensor_type", "location"],
    "query_device_status": ["device", "location"],
    "security_mode": ["mode"],
    "security_alert": ["alert_type", "priority"],
    "activate_scene": ["scene_type"],
    "weather_action": ["weather_condition", "action", "device"],
    "lock_all_doors": [],
    "turn_off_all_devices": [],
    "create_automation": ["trigger", "action", "condition"],
    "unknown": [],
}

# Required entities for each intent (must be present)
REQUIRED_ENTITIES: Dict[str, List[str]] = {
    "control_device": ["device", "action"],
    "environmental_comfort": ["comfort_type"],
    "query_sensor": ["sensor_type"],
    "query_device_status": ["device"],
    "security_mode": ["mode"],
    "security_alert": ["alert_type"],
    "activate_scene": ["scene_type"],
    "weather_action": ["weather_condition"],
    "lock_all_doors": [],
    "turn_off_all_devices": [],
    "create_automation": [],
    "unknown": [],
}
