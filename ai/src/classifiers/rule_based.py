"""
Rule-Based Classifier for Vietnamese Smart Home Intent Classification.

This classifier uses pattern matching for simple commands to provide fast (<10ms)
classification with confidence=1.0 for matched patterns.

**Validates: Requirements 2.1-2.6, 6.1-6.7, 13.1-13.8**
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ClassificationResult:
    """Result from classifier."""
    intent: str
    entities: Dict[str, Any]
    confidence: float
    classifier_type: str  # "rule" or "ml"

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)


class RuleBasedClassifier:
    """
    Rule-Based Classifier for simple command pattern matching.
    
    This classifier matches Vietnamese text against predefined patterns for:
    - Control device commands (bật/tắt/mở/đóng + device + optional location)
    - Activate scene commands (đi ngủ, thức dậy, xem phim, đi vắng, về nhà)
    
    Returns confidence=1.0 for matched patterns, None for no match.
    """
    
    def __init__(self):
        """Initialize classifier with pattern dictionaries."""
        # Device keywords (Vietnamese → English mapping)
        self.device_map = {
            "đèn": "light",
            "quạt": "fan",
            "điều hòa": "ac",
            "ac": "ac",
            "cửa": "door",
            "mái che": "awning"
        }
        
        # Action keywords (Vietnamese → English mapping)
        self.action_map = {
            "bật": "turn_on",
            "mở": "turn_on",
            "tắt": "turn_off",
            "đóng": "turn_off"
        }
        
        # Location keywords (Vietnamese → English mapping)
        self.location_map = {
            "phòng khách": "living_room",
            "phòng ngủ": "bedroom",
            "bếp": "kitchen",
            "phòng tắm": "bathroom",
            "ban công": "balcony"
        }
        
        # Scene keywords (scene_type → Vietnamese keywords)
        self.scene_keywords = {
            "sleep": ["đi ngủ", "chúc ngủ ngon", "chuẩn bị ngủ"],
            "wake_up": ["thức dậy", "buổi sáng", "chào buổi sáng"],
            "movie": ["xem phim", "xem tv", "rạp chiếu phim"],
            "away": ["đi ra ngoài", "rời nhà", "đi vắng"],
            "home": ["về nhà", "đã về", "tôi về rồi"]
        }
        
        # Environmental comfort keywords (comfort_type → Vietnamese keywords)
        self.comfort_keywords = {
            "cooling": ["nóng quá", "oi bức", "nóng nực"],
            "warming": ["lạnh quá", "rét quá", "lạnh lẽo"],
            "brighten": ["tối quá", "thiếu sáng", "tối om"],
            "dim": ["sáng quá", "chói mắt", "sáng lóa"],
            "ventilate": ["ngột ngạt", "thiếu không khí"]
        }
        
        # Sensor query keywords (sensor_type → Vietnamese keywords)
        self.sensor_query_keywords = {
            "temperature": ["nhiệt độ bao nhiêu", "bao nhiêu độ", "đo nhiệt độ", "kiểm tra nhiệt độ", "nhiệt độ"],
            "humidity": ["độ ẩm bao nhiêu", "ẩm không", "kiểm tra độ ẩm", "đo độ ẩm", "độ ẩm"],
            "rain": ["có mưa không", "trời mưa không", "dự báo mưa", "kiểm tra mưa"],
            "gas": ["có khí gas không", "rò rỉ gas", "phát hiện gas", "kiểm tra khí gas", "có gas không"],
            "fire": ["có cháy không", "phát hiện lửa", "báo cháy", "kiểm tra cháy", "có lửa không"],
            "motion": ["có người không", "phát hiện chuyển động", "ai đó vào", "kiểm tra chuyển động", "có ai trong phòng không"]
        }
        
        # Device status query keywords (device → Vietnamese keywords)
        self.device_status_keywords = {
            "light": ["trạng thái đèn", "đèn có bật không", "đèn đang bật không"],
            "fan": ["trạng thái quạt", "quạt có bật không", "quạt đang chạy không"],
            "ac": ["trạng thái điều hòa", "điều hòa có bật không", "ac đang bật không"],
            "door": ["trạng thái cửa", "cửa có mở không", "cửa đang mở không"]
        }
        
        # Security mode keywords (mode → Vietnamese keywords)
        self.security_mode_keywords = {
            "armed": ["bật báo động", "kích hoạt an ninh", "bật chế độ an ninh", "bật bảo vệ", "armed"],
            "disarmed": ["tắt báo động", "vô hiệu hóa an ninh", "tắt chế độ an ninh", "tắt bảo vệ", "disarmed"]
        }
        
        # Security alert keywords (alert_type → Vietnamese keywords)
        self.security_alert_keywords = {
            "fire": ["cháy", "fire", "có lửa", "hỏa hoạn", "cháy rồi", "cháy kìa", "cảnh báo cháy", "phát hiện cháy"],
            "gas": ["gas", "khí gas", "có mùi gas", "rò rỉ gas", "gas leak", "cảnh báo gas", "phát hiện gas", "phát hiện khí gas", "khí gas rò rỉ"],
            "intrusion": ["trộm", "đột nhập", "có người lạ", "kẻ xâm nhập", "cảnh báo trộm", "intruder"]
        }
        
        # Entertainment context keywords (for false positive prevention)
        self.entertainment_keywords = ["phim", "game", "bài hát", "trận đấu", "video", "nhạc", "truyện"]
    
    def classify(self, text: str) -> Optional[ClassificationResult]:
        """
        Match text against predefined patterns.
        
        Pattern matching order:
        1. Scene activation patterns (higher priority)
        2. Environmental comfort patterns
        3. Sensor query patterns
        4. Device status query patterns
        5. Control device patterns
        
        Args:
            text: Preprocessed Vietnamese text (should be lowercase and trimmed)
            
        Returns:
            ClassificationResult with confidence=1.0 if matched, None otherwise
        """
        # Normalize text: lowercase and strip whitespace
        text_lower = text.lower().strip()
        
        # Check for scene activation patterns (higher priority)
        scene_result = self._match_scene_pattern(text_lower)
        if scene_result:
            return scene_result
        
        # Check for environmental comfort patterns
        comfort_result = self._match_environmental_comfort_pattern(text_lower)
        if comfort_result:
            return comfort_result

        # Check for sensor query patterns
        sensor_result = self._match_sensor_query_pattern(text_lower)
        if sensor_result:
            return sensor_result

        # Check for device status query patterns
        device_status_result = self._match_device_status_query_pattern(text_lower)
        if device_status_result:
            return device_status_result

        # Check for control device patterns
        device_result = self._match_control_device_pattern(text_lower)
        if device_result:
            return device_result
        
        # No match found
        return None
    
    def _match_control_device_pattern(self, text: str) -> Optional[ClassificationResult]:
        """
        Match control device patterns: action + device + optional location.
        
        Pattern examples:
        - "bật đèn" → control_device with turn_on + light
        - "tắt quạt phòng ngủ" → control_device with turn_off + fan + bedroom
        - "mở cửa" → control_device with turn_on + door
        - "đóng mái che ban công" → control_device with turn_off + awning + balcony
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            ClassificationResult if pattern matched, None otherwise
        """
        # Check for action + device pattern
        for vn_action, en_action in self.action_map.items():
            for vn_device, en_device in self.device_map.items():
                # Both action and device must be present
                if vn_action in text and vn_device in text:
                    # Extract entities
                    entities = {
                        "action": en_action,
                        "device": en_device
                    }
                    
                    # Extract location if present (optional)
                    location = self._extract_location(text)
                    if location:
                        entities["location"] = location
                    
                    return ClassificationResult(
                        intent="control_device",
                        entities=entities,
                        confidence=1.0,
                        classifier_type="rule"
                    )
        
        return None
    
    def _match_scene_pattern(self, text: str) -> Optional[ClassificationResult]:
        """
        Match scene activation patterns.
        
        Pattern examples:
        - "đi ngủ" → activate_scene with sleep
        - "thức dậy" → activate_scene with wake_up
        - "xem phim" → activate_scene with movie
        - "đi vắng" → activate_scene with away
        - "về nhà" → activate_scene with home
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            ClassificationResult if pattern matched, None otherwise
        """
        for scene_type, keywords in self.scene_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return ClassificationResult(
                        intent="activate_scene",
                        entities={"scene_type": scene_type},
                        confidence=1.0,
                        classifier_type="rule"
                    )
        
        return None
    
    def _match_environmental_comfort_pattern(self, text: str) -> Optional[ClassificationResult]:
        """
        Match environmental comfort patterns.
        
        Pattern examples:
        - "nóng quá" → environmental_comfort with cooling
        - "lạnh quá" → environmental_comfort with warming
        - "tối quá" → environmental_comfort with brighten
        - "sáng quá" → environmental_comfort with dim
        - "ngột ngạt" → environmental_comfort with ventilate
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            ClassificationResult if pattern matched, None otherwise
        """
        for comfort_type, keywords in self.comfort_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return ClassificationResult(
                        intent="environmental_comfort",
                        entities={"comfort_type": comfort_type},
                        confidence=0.85,
                        classifier_type="rule"
                    )
        
        return None
    
    def _match_sensor_query_pattern(self, text: str) -> Optional[ClassificationResult]:
        """
        Match sensor query patterns.
        
        Pattern examples:
        - "nhiệt độ bao nhiêu" → query_sensor with temperature
        - "độ ẩm bao nhiêu" → query_sensor with humidity
        - "có mưa không" → query_sensor with rain
        - "có khí gas không" → query_sensor with gas
        - "có cháy không" → query_sensor with fire
        - "có người không" → query_sensor with motion
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            ClassificationResult if pattern matched, None otherwise
        """
        # Check longest match first to handle multi-word patterns
        for sensor_type, keywords in self.sensor_query_keywords.items():
            # Sort keywords by length (longest first)
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            for keyword in sorted_keywords:
                if keyword in text:
                    entities = {"sensor_type": sensor_type}
                    
                    # Extract location if present (optional)
                    location = self._extract_location(text)
                    if location:
                        entities["location"] = location
                    
                    return ClassificationResult(
                        intent="query_sensor",
                        entities=entities,
                        confidence=0.85,
                        classifier_type="rule"
                    )
        
        return None
    
    def _match_device_status_query_pattern(self, text: str) -> Optional[ClassificationResult]:
        """
        Match device status query patterns.
        
        Pattern examples:
        - "trạng thái đèn" → query_device_status with light
        - "đèn có bật không" → query_device_status with light
        - "quạt đang chạy không" → query_device_status with fan
        - "cửa có mở không" → query_device_status with door
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            ClassificationResult if pattern matched, None otherwise
        """
        # Check longest match first to handle multi-word patterns
        for device, keywords in self.device_status_keywords.items():
            # Sort keywords by length (longest first)
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            for keyword in sorted_keywords:
                if keyword in text:
                    entities = {"device": device}
                    
                    # Extract location if present (optional)
                    location = self._extract_location(text)
                    if location:
                        entities["location"] = location
                    
                    return ClassificationResult(
                        intent="query_device_status",
                        entities=entities,
                        confidence=0.85,
                        classifier_type="rule"
                    )
        
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """
        Extract location from text.
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            Standardized location string (e.g., "living_room") or None
        """
        for vn_location, en_location in self.location_map.items():
            if vn_location in text:
                return en_location
        
        return None
    
    def extract_entities_from_pattern(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities from matched pattern.
        
        This method is called after classify() to extract additional entities
        or re-extract entities with more sophisticated logic if needed.
        
        Args:
            text: Preprocessed text
            intent: Predicted intent from classify()
            
        Returns:
            Dictionary of extracted entities
        """
        text_lower = text.lower().strip()
        entities = {}
        
        if intent == "control_device":
            # Extract action
            for vn_action, en_action in self.action_map.items():
                if vn_action in text_lower:
                    entities["action"] = en_action
                    break
            
            # Extract device
            for vn_device, en_device in self.device_map.items():
                if vn_device in text_lower:
                    entities["device"] = en_device
                    break
            
            # Extract location (optional)
            location = self._extract_location(text_lower)
            if location:
                entities["location"] = location
        
        elif intent == "activate_scene":
            # Extract scene_type
            for scene_type, keywords in self.scene_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        entities["scene_type"] = scene_type
                        return entities
        
        elif intent == "environmental_comfort":
            # Extract comfort_type
            for comfort_type, keywords in self.comfort_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        entities["comfort_type"] = comfort_type
                        return entities
        
        elif intent == "query_sensor":
            # Extract sensor_type
            for sensor_type, keywords in self.sensor_query_keywords.items():
                # Sort keywords by length (longest first)
                sorted_keywords = sorted(keywords, key=len, reverse=True)
                for keyword in sorted_keywords:
                    if keyword in text_lower:
                        entities["sensor_type"] = sensor_type
                        # Extract location (optional)
                        location = self._extract_location(text_lower)
                        if location:
                            entities["location"] = location
                        return entities
        
        elif intent == "query_device_status":
            # Extract device
            for device, keywords in self.device_status_keywords.items():
                # Sort keywords by length (longest first)
                sorted_keywords = sorted(keywords, key=len, reverse=True)
                for keyword in sorted_keywords:
                    if keyword in text_lower:
                        entities["device"] = device
                        # Extract location (optional)
                        location = self._extract_location(text_lower)
                        if location:
                            entities["location"] = location
                        return entities
        
        return entities
    
    def _match_security_mode_pattern(self, text: str) -> Optional[ClassificationResult]:
        """
        Match security mode patterns.
        
        Pattern examples:
        - "bật báo động" → security_mode with armed
        - "tắt báo động" → security_mode with disarmed
        - "kích hoạt an ninh" → security_mode with armed
        - "vô hiệu hóa an ninh" → security_mode with disarmed
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            ClassificationResult if pattern matched, None otherwise
        """
        # Check disarmed BEFORE armed (because "disarmed" contains "armed")
        for mode, keywords in [("disarmed", self.security_mode_keywords["disarmed"]), 
                               ("armed", self.security_mode_keywords["armed"])]:
            # Sort keywords by length (longest first)
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            for keyword in sorted_keywords:
                if keyword in text:
                    return ClassificationResult(
                        intent="security_mode",
                        entities={"mode": mode},
                        confidence=1.0,
                        classifier_type="rule"
                    )
        
        return None
    
    def _match_security_alert_pattern(self, text: str) -> Optional[ClassificationResult]:
        """
        Match security alert patterns with false positive prevention.
        
        Pattern examples:
        - "cháy rồi" → security_alert with fire + priority=high
        - "rò rỉ gas" → security_alert with gas + priority=high
        - "có trộm" → security_alert with intrusion + priority=high
        
        False positive prevention:
        - "phim này cháy quá" → NOT security_alert (entertainment context)
        - "game này nổ tung" → NOT security_alert (entertainment context)
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            ClassificationResult if pattern matched, None otherwise
        """
        # Check for entertainment context (false positive prevention)
        has_entertainment_context = any(ent_kw in text for ent_kw in self.entertainment_keywords)
        
        # If entertainment context detected, don't classify as security_alert
        if has_entertainment_context:
            return None
        
        # Check for security alert keywords
        for alert_type, keywords in self.security_alert_keywords.items():
            # Sort keywords by length (longest first)
            sorted_keywords = sorted(keywords, key=len, reverse=True)
            for keyword in sorted_keywords:
                if keyword in text:
                    return ClassificationResult(
                        intent="security_alert",
                        entities={"alert_type": alert_type, "priority": "high"},
                        confidence=1.0,
                        classifier_type="rule"
                    )
        
        return None
