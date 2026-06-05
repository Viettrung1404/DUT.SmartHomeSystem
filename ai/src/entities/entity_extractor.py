"""
Entity Extractor for Vietnamese Smart Home Intent Classification.

This extractor uses keyword matching and regex patterns to extract structured
entities from Vietnamese text based on the predicted intent.

**Validates: Requirements 1.3, 2.2-2.6, 3.2, 4.2, 6.2**
"""

from typing import Optional, Dict, Any
import re


class EntityExtractor:
    """
    Entity Extractor for Vietnamese text.
    
    This extractor matches Vietnamese keywords to standardized entity values
    defined in ENTITY_SCHEMA. It supports:
    - Device extraction (đèn → light, quạt → fan, etc.)
    - Action extraction (bật → turn_on, tắt → turn_off, etc.)
    - Location extraction (phòng khách → living_room, etc.)
    - Numeric value extraction (30 độ → (30, 'C'), 50% → (50, '%'))
    - Comfort type extraction (nóng → cooling, lạnh → warming, etc.)
    - Scene type extraction (đi ngủ → sleep, etc.)
    - Sensor type extraction (nhiệt độ → temperature, etc.)
    """
    
    def __init__(self):
        """Initialize entity extractor with keyword mappings."""
        # Device keywords (Vietnamese → English mapping)
        # Sorted by length (longest first) to match longer phrases first
        self.device_keywords = {
            "quạt trần": "fan",
            "quạt máy": "fan",
            "bóng đèn": "light",
            "ánh sáng": "light",
            "điều hòa": "ac",
            "máy lạnh": "ac",
            "air conditioner": "ac",
            "cửa ra vào": "door",
            "cửa chính": "door",
            "mái hiên": "awning",
            "mái bạt": "awning",
            "mái che": "awning",
            "rèm cửa": "curtain",
            "ổ khóa": "lock",
            "nhà để xe": "garage",
            "đèn": "light",
            "quạt": "fan",
            "ac": "ac",
            "cửa": "door",
            "khóa": "lock",
            "rèm": "curtain",
            "camera": "camera",
            "cam": "camera"
        }
        
        # Action keywords (Vietnamese → English mapping)
        self.action_keywords = {
            "mở khóa": "unlock",
            "khởi động": "turn_on",
            "điều chỉnh": "adjust",
            "bật": "turn_on",
            "mở": "turn_on",
            "chạy": "turn_on",
            "tắt": "turn_off",
            "đóng": "turn_off",
            "dừng": "turn_off",
            "ngừng": "turn_off",
            "chỉnh": "adjust",
            "đặt": "adjust",
            "set": "adjust",
            "khóa": "lock"
        }
        
        # Location keywords (Vietnamese → English mapping)
        self.location_keywords = {
            "phòng ngủ chính": "bedroom",
            "phòng khách": "living_room",
            "living room": "living_room",
            "phòng ngủ": "bedroom",
            "bedroom": "bedroom",
            "nhà bếp": "kitchen",
            "kitchen": "kitchen",
            "phòng tắm": "bathroom",
            "nhà vệ sinh": "bathroom",
            "toilet": "bathroom",
            "bathroom": "bathroom",
            "ban công": "balcony",
            "balcony": "balcony",
            "sân thượng": "balcony",
            "nhà để xe": "garage",
            "garage": "garage",
            "bếp": "kitchen"
        }
        
        # Comfort type keywords
        self.comfort_keywords = {
            "thiếu không khí": "ventilate",
            "thiếu sáng": "brighten",
            "sáng hơn": "brighten",
            "cần sáng": "brighten",
            "sáng quá": "dim",
            "giảm sáng": "dim",
            "tối hơn": "dim",
            "thông gió": "ventilate",
            "oi bức": "cooling",
            "làm mát": "cooling",
            "cần mát": "cooling",
            "sưởi ấm": "warming",
            "cần ấm": "warming",
            "ngột ngạt": "ventilate",
            "nóng": "cooling",
            "mát": "cooling",
            "lạnh": "warming",
            "rét": "warming",
            "ấm": "warming",
            "tối": "brighten",
            "chói": "dim",
            "thoáng": "ventilate"
        }
        
        # Scene type keywords
        self.scene_keywords = {
            "chúc ngủ ngon": "sleep",
            "chuẩn bị ngủ": "sleep",
            "chào buổi sáng": "wake_up",
            "buổi sáng": "wake_up",
            "rạp chiếu phim": "movie",
            "xem phim": "movie",
            "xem tv": "movie",
            "đi ra ngoài": "away",
            "rời nhà": "away",
            "đi vắng": "away",
            "tôi về rồi": "home",
            "đã về": "home",
            "về nhà": "home",
            "đi ngủ": "sleep",
            "thức dậy": "wake_up"
        }
        
        # Sensor type keywords
        self.sensor_keywords = {
            "chuyển động": "motion",
            "di chuyển": "motion",
            "có người không": "motion",
            "ai đó vào": "motion",
            "có ai trong phòng không": "motion",
            "nhiệt độ": "temperature",
            "bao nhiêu độ": "temperature",
            "temperature": "temperature",
            "độ ẩm": "humidity",
            "ẩm không": "humidity",
            "humidity": "humidity",
            "khí gas": "gas",
            "mưa": "rain",
            "rain": "rain",
            "gas": "gas",
            "cháy": "fire",
            "fire": "fire",
            "lửa": "fire",
            "motion": "motion"
        }
        
        # Security mode keywords
        self.security_mode_keywords = {
            "bật báo động": "armed",
            "kích hoạt an ninh": "armed",
            "bật chế độ an ninh": "armed",
            "bật bảo vệ": "armed",
            "tắt báo động": "disarmed",
            "vô hiệu hóa an ninh": "disarmed",
            "tắt chế độ an ninh": "disarmed",
            "tắt bảo vệ": "disarmed",
            "armed": "armed",
            "disarmed": "disarmed"
        }
        
        # Security alert keywords
        self.security_alert_keywords = {
            "cháy rồi": "fire",
            "cháy kìa": "fire",
            "cảnh báo cháy": "fire",
            "phát hiện cháy": "fire",
            "hỏa hoạn": "fire",
            "có lửa": "fire",
            "khí gas rò rỉ": "gas",
            "rò rỉ gas": "gas",
            "gas leak": "gas",
            "cảnh báo gas": "gas",
            "phát hiện gas": "gas",
            "phát hiện khí gas": "gas",
            "có mùi gas": "gas",
            "cảnh báo trộm": "intrusion",
            "có người lạ": "intrusion",
            "kẻ xâm nhập": "intrusion",
            "đột nhập": "intrusion",
            "intruder": "intrusion",
            "cháy": "fire",
            "fire": "fire",
            "khí gas": "gas",
            "trộm": "intrusion"
        }
    
    def extract(self, text: str, intent: str, context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Extract entities based on intent type.
        
        Extraction strategies:
        - Keyword matching for device, action, location
        - Regex for numeric values (temperature, percentage)
        - Context inference for missing location
        
        Args:
            text: Preprocessed Vietnamese text (should be lowercase and trimmed)
            intent: Predicted intent
            context: Optional device context for inference
            
        Returns:
            Dictionary of extracted entities
        """
        text_lower = text.lower().strip()
        entities = {}
        
        if intent == "control_device":
            # Extract device
            device = self.extract_device(text_lower)
            if device:
                entities["device"] = device
            
            # Extract action
            action = self.extract_action(text_lower)
            if action:
                entities["action"] = action
            
            # Extract location (optional)
            location = self.extract_location(text_lower, context)
            if location:
                entities["location"] = location
            
            # Extract numeric value (optional)
            numeric = self.extract_numeric_value(text_lower)
            if numeric:
                entities["value"] = numeric[0]
                entities["unit"] = numeric[1]
        
        elif intent == "environmental_comfort":
            # Extract comfort_type
            # Check longest match first
            sorted_keywords = sorted(self.comfort_keywords.items(), key=lambda x: len(x[0]), reverse=True)
            for keyword, comfort_type in sorted_keywords:
                if keyword in text_lower:
                    entities["comfort_type"] = comfort_type
                    break
        
        elif intent == "activate_scene":
            # Extract scene_type
            # Check longest match first
            sorted_keywords = sorted(self.scene_keywords.items(), key=lambda x: len(x[0]), reverse=True)
            for keyword, scene_type in sorted_keywords:
                if keyword in text_lower:
                    entities["scene_type"] = scene_type
                    break
        
        elif intent == "query_sensor":
            # Extract sensor_type
            # Check longest match first
            sorted_keywords = sorted(self.sensor_keywords.items(), key=lambda x: len(x[0]), reverse=True)
            for keyword, sensor_type in sorted_keywords:
                if keyword in text_lower:
                    entities["sensor_type"] = sensor_type
                    break
            
            # Extract location (optional)
            location = self.extract_location(text_lower, context)
            if location:
                entities["location"] = location
        
        elif intent == "query_device_status":
            # Extract device
            device = self.extract_device(text_lower)
            if device:
                entities["device"] = device
            
            # Extract location (optional)
            location = self.extract_location(text_lower, context)
            if location:
                entities["location"] = location
        
        elif intent == "security_mode":
            # Extract mode (armed/disarmed)
            # Check longest match first (disarmed before armed)
            sorted_keywords = sorted(self.security_mode_keywords.items(), key=lambda x: len(x[0]), reverse=True)
            for keyword, mode in sorted_keywords:
                if keyword in text_lower:
                    entities["mode"] = mode
                    break
        
        elif intent == "security_alert":
            # Extract alert_type (fire/gas/intrusion)
            # Check longest match first
            sorted_keywords = sorted(self.security_alert_keywords.items(), key=lambda x: len(x[0]), reverse=True)
            for keyword, alert_type in sorted_keywords:
                if keyword in text_lower:
                    entities["alert_type"] = alert_type
                    entities["priority"] = "high"  # All security alerts have high priority
                    break
        
        return entities
    
    def extract_device(self, text: str) -> Optional[str]:
        """
        Extract device type from text.
        
        Uses longest match first to handle multi-word device names
        (e.g., "quạt trần" before "quạt").
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            Standardized device string (e.g., "light") or None
        """
        # Sort by length (longest first) to match longer phrases first
        sorted_keywords = sorted(self.device_keywords.items(), key=lambda x: len(x[0]), reverse=True)
        
        for vn_device, en_device in sorted_keywords:
            if vn_device in text:
                return en_device
        
        return None
    
    def extract_action(self, text: str) -> Optional[str]:
        """
        Extract action from text.
        
        Uses longest match first to handle multi-word actions
        (e.g., "mở khóa" before "mở").
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            Standardized action string (e.g., "turn_on") or None
        """
        # Sort by length (longest first) to match longer phrases first
        sorted_keywords = sorted(self.action_keywords.items(), key=lambda x: len(x[0]), reverse=True)
        
        for vn_action, en_action in sorted_keywords:
            if vn_action in text:
                return en_action
        
        return None
    
    def extract_location(self, text: str, context: Optional[Any] = None) -> Optional[str]:
        """
        Extract or infer location from text or context.
        
        Priority:
        1. Explicit location in text (longest match first)
        2. Infer from device context (current_room)
        
        Args:
            text: Normalized text (lowercase, trimmed)
            context: Optional device context for inference
            
        Returns:
            Standardized location string (e.g., "living_room") or None
        """
        # Sort by length (longest first) to match longer phrases first
        sorted_keywords = sorted(self.location_keywords.items(), key=lambda x: len(x[0]), reverse=True)
        
        for vn_location, en_location in sorted_keywords:
            if vn_location in text:
                return en_location
        
        # If no location in text, try to infer from context
        if context:
            if hasattr(context, "current_room") and context.current_room:
                return context.current_room
            if isinstance(context, dict):
                current_room = context.get("current_room")
                if current_room:
                    return current_room
        
        return None
    
    def extract_numeric_value(self, text: str) -> Optional[tuple]:
        """
        Extract numeric value and unit from text.
        
        Supported patterns:
        - "30 độ" or "30 độ C" → (30, 'C')
        - "50%" or "50 %" → (50, '%')
        - "25" → (25, '')
        
        Args:
            text: Normalized text (lowercase, trimmed)
            
        Returns:
            Tuple of (value, unit) or None
            Examples: (30, 'C'), (50, '%'), (25, '')
        """
        # Pattern for "30 độ" or "30 độ C"
        pattern_degrees = r'(\d+)\s*độ\s*c?'
        match = re.search(pattern_degrees, text)
        if match:
            value = int(match.group(1))
            return (value, 'C')
        
        # Pattern for "50%"
        pattern_percent = r'(\d+)\s*%'
        match = re.search(pattern_percent, text)
        if match:
            value = int(match.group(1))
            return (value, '%')
        
        # Pattern for just numbers (e.g., "25")
        pattern_number = r'(\d+)'
        match = re.search(pattern_number, text)
        if match:
            value = int(match.group(1))
            return (value, '')
        
        return None
