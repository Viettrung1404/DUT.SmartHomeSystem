"""
Pydantic data models for Vietnamese NLP Intent Classification API.

This module defines all request and response models with validation rules:
- DeviceState: Individual device state in context
- DeviceContext: Device context for context-aware classification
- IntentClassificationRequest: Request model for intent classification endpoint
- IntentResponse: Successful intent classification response
- FallbackResponse: Fallback response when classification confidence is low
- MultiIntentResponse: Response for multi-intent requests
- ErrorResponse: Error response model

Also includes ENTITY_SCHEMA constant with entity value constraints.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Entity Schema Constants
ENTITY_SCHEMA = {
    "device_types": ["light", "fan", "ac", "door", "awning", "lock", "curtain", "camera"],
    "actions": ["turn_on", "turn_off", "adjust", "open", "close", "lock", "unlock"],
    "locations": ["living_room", "bedroom", "kitchen", "bathroom", "balcony", "garage"],
    "scene_types": ["sleep", "wake_up", "movie", "away", "home"],
    "sensor_types": ["temperature", "humidity", "rain", "gas", "fire", "motion"],
    "comfort_types": ["cooling", "warming", "brighten", "dim", "ventilate"],
    "security_modes": ["armed", "disarmed"],
    "alert_types": ["fire", "gas", "intrusion"],
    "weather_conditions": ["rain", "sunny"]
}


class DeviceState(BaseModel):
    """Individual device state in context."""
    id: str = Field(..., min_length=1, description="Unique device identifier")
    type: str = Field(..., description="Device type (light, fan, ac, etc.)")
    state: str = Field(..., description="Current state (on, off, etc.)")
    location: Optional[str] = Field(None, description="Device location")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Additional attributes (brightness, temperature, etc.)")

    class Config:
        schema_extra = {
            "example": {
                "id": "light_1",
                "type": "light",
                "state": "off",
                "location": "living_room",
                "attributes": {"brightness": 80, "color": "warm_white"}
            }
        }


class DeviceContext(BaseModel):
    """Device context for context-aware classification."""
    current_room: Optional[str] = Field(None, description="User's current room")
    devices: List[DeviceState] = Field(default_factory=list, description="List of available devices")
    time_of_day: Optional[str] = Field(None, description="Time context (morning, afternoon, evening, night)")

    class Config:
        schema_extra = {
            "example": {
                "current_room": "living_room",
                "devices": [
                    {"id": "light_1", "type": "light", "state": "off", "location": "living_room"},
                    {"id": "fan_1", "type": "fan", "state": "on", "location": "living_room"}
                ],
                "time_of_day": "evening"
            }
        }


class IntentClassificationRequest(BaseModel):
    """Request model for intent classification endpoint."""
    text: str = Field(..., min_length=1, max_length=500, description="Vietnamese text input")
    user_id: Optional[str] = Field(None, description="User identifier for logging and rate limiting")
    home_id: Optional[str] = Field(None, description="Home identifier for context")
    device_context: Optional[DeviceContext] = Field(None, description="Device context for disambiguation")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Bật đèn phòng khách",
                "user_id": "user_123",
                "home_id": "home_456",
                "device_context": {
                    "current_room": "living_room",
                    "devices": [
                        {"id": "light_1", "type": "light", "state": "off", "location": "living_room"},
                        {"id": "fan_1", "type": "fan", "state": "on", "location": "living_room"}
                    ]
                }
            }
        }


class IntentResponse(BaseModel):
    """Successful intent classification response."""
    intent: str = Field(..., description="Classified intent name")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    classifier_type: str = Field(..., description="Classifier used (rule, ml)")
    priority: Optional[str] = Field(None, description="Priority level (high for security alerts)")
    
    class Config:
        schema_extra = {
            "example": {
                "intent": "control_device",
                "entities": {
                    "device": "light",
                    "action": "turn_on",
                    "location": "living_room"
                },
                "confidence": 1.0,
                "timestamp": "2024-01-15T10:30:00Z",
                "classifier_type": "rule",
                "priority": None
            }
        }


class FallbackResponse(BaseModel):
    """Fallback response when classification confidence is low."""
    intent: str = Field(default="unknown", description="Fallback intent")
    entities: Dict[str, Any] = Field(default_factory=dict, description="Partial entities if any")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    clarification_needed: bool = Field(default=True, description="Whether clarification is needed")
    suggestions: List[str] = Field(default_factory=list, description="Suggested intents or clarification questions")
    top_intents: List[Dict[str, Any]] = Field(default_factory=list, description="Top 3 possible intents with scores")
    
    class Config:
        schema_extra = {
            "example": {
                "intent": "unknown",
                "entities": {},
                "confidence": 0.45,
                "timestamp": "2024-01-15T10:30:00Z",
                "clarification_needed": True,
                "suggestions": [
                    "Bạn muốn bật thiết bị nào?",
                    "Bạn muốn kiểm tra cảm biến nào?"
                ],
                "top_intents": [
                    {"intent": "control_device", "confidence": 0.45},
                    {"intent": "query_sensor", "confidence": 0.32},
                    {"intent": "environmental_comfort", "confidence": 0.23}
                ]
            }
        }


class MultiIntentResponse(BaseModel):
    """Response for multi-intent requests (sentence splitting)."""
    intents: List[IntentResponse] = Field(..., min_length=1, description="List of classified intents")
    total_intents: int = Field(..., description="Total number of intents detected")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "intents": [
                    {
                        "intent": "control_device",
                        "entities": {"device": "light", "action": "turn_on", "location": "living_room"},
                        "confidence": 1.0,
                        "classifier_type": "rule"
                    },
                    {
                        "intent": "control_device",
                        "entities": {"device": "fan", "action": "turn_off", "location": "bedroom"},
                        "confidence": 1.0,
                        "classifier_type": "rule"
                    }
                ],
                "total_intents": 2,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error_type: str = Field(..., description="Error type (validation, authentication, server)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error_type": "validation",
                "message": "Input không hợp lệ",
                "details": {"field": "text", "reason": "Text cannot be empty"},
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
