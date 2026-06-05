# Entity Schema Reference

Quick reference guide for all valid entity types and values in the Vietnamese NLP Intent Classification System.

## Core Intent Categories (15 Total)

1. **control_device** - Device control commands
2. **environmental_comfort** - Environmental comfort requests
3. **query_sensor** - Sensor data queries
4. **query_device_status** - Device status queries
5. **security_mode** - Security mode changes
6. **security_alert** - Security alerts
7. **activate_scene** - Scene activation
8. **weather_action** - Weather-responsive actions
9. **lock_all_doors** - Lock all doors
10. **turn_off_all_devices** - Turn off all devices
11. **create_automation** - Create automation rule
12. **unknown** - Fallback intent

## Entity Types and Valid Values

### Device Types
Valid values for `device` entity:
- `light` - Đèn
- `fan` - Quạt
- `ac` - Điều hòa
- `door` - Cửa
- `awning` - Mái che
- `lock` - Khóa
- `curtain` - Rèm cửa
- `camera` - Camera

### Actions
Valid values for `action` entity:
- `turn_on` - Bật/Mở
- `turn_off` - Tắt
- `adjust` - Điều chỉnh
- `open` - Mở
- `close` - Đóng
- `lock` - Khóa
- `unlock` - Mở khóa

### Locations
Valid values for `location` entity:
- `living_room` - Phòng khách
- `bedroom` - Phòng ngủ
- `kitchen` - Nhà bếp
- `bathroom` - Phòng tắm
- `balcony` - Ban công
- `garage` - Nhà để xe

### Scene Types
Valid values for `scene_type` entity:
- `sleep` - Đi ngủ
- `wake_up` - Thức dậy
- `movie` - Xem phim
- `away` - Đi vắng
- `home` - Về nhà

### Sensor Types
Valid values for `sensor_type` entity:
- `temperature` - Nhiệt độ
- `humidity` - Độ ẩm
- `rain` - Mưa
- `gas` - Khí gas
- `fire` - Cháy
- `motion` - Chuyển động

### Comfort Types
Valid values for `comfort_type` entity:
- `cooling` - Làm mát (nóng quá, oi bức)
- `warming` - Làm ấm (lạnh quá, rét)
- `brighten` - Tăng sáng (tối quá)
- `dim` - Giảm sáng (chói quá)
- `ventilate` - Thông gió (ngột ngạt)

### Security Modes
Valid values for `mode` entity:
- `armed` - Kích hoạt an ninh
- `disarmed` - Tắt an ninh

### Alert Types
Valid values for `alert_type` entity:
- `fire` - Cháy
- `gas` - Khí gas
- `intrusion` - Xâm nhập

### Weather Conditions
Valid values for `weather_condition` entity:
- `rain` - Mưa
- `sunny` - Nắng

## Intent-Entity Mapping

### control_device
**Required:** `device`, `action`  
**Optional:** `location`, `value`, `unit`

**Examples:**
```json
{
  "intent": "control_device",
  "entities": {
    "device": "light",
    "action": "turn_on",
    "location": "living_room"
  }
}
```

### environmental_comfort
**Required:** `comfort_type`  
**Optional:** `location`

**Examples:**
```json
{
  "intent": "environmental_comfort",
  "entities": {
    "comfort_type": "cooling"
  }
}
```

### query_sensor
**Required:** `sensor_type`  
**Optional:** `location`

**Examples:**
```json
{
  "intent": "query_sensor",
  "entities": {
    "sensor_type": "temperature",
    "location": "bedroom"
  }
}
```

### query_device_status
**Required:** `device`  
**Optional:** `location`

**Examples:**
```json
{
  "intent": "query_device_status",
  "entities": {
    "device": "light",
    "location": "living_room"
  }
}
```

### security_mode
**Required:** `mode`

**Examples:**
```json
{
  "intent": "security_mode",
  "entities": {
    "mode": "armed"
  }
}
```

### security_alert
**Required:** `alert_type`  
**Auto-added:** `priority` (always "high")

**Examples:**
```json
{
  "intent": "security_alert",
  "entities": {
    "alert_type": "fire",
    "priority": "high"
  }
}
```

### activate_scene
**Required:** `scene_type`

**Examples:**
```json
{
  "intent": "activate_scene",
  "entities": {
    "scene_type": "sleep"
  }
}
```

### weather_action
**Required:** `weather_condition`  
**Optional:** `action`, `device`

**Examples:**
```json
{
  "intent": "weather_action",
  "entities": {
    "weather_condition": "rain",
    "action": "close",
    "device": "awning"
  }
}
```

## Vietnamese Keyword Mappings

### Device Keywords
- "đèn" → `light`
- "quạt" → `fan`
- "điều hòa", "máy lạnh" → `ac`
- "cửa" → `door`
- "mái che" → `awning`
- "khóa" → `lock`
- "rèm" → `curtain`
- "camera" → `camera`

### Action Keywords
- "bật", "mở" → `turn_on`
- "tắt", "đóng" → `turn_off`
- "điều chỉnh", "chỉnh" → `adjust`
- "khóa" → `lock`
- "mở khóa" → `unlock`

### Location Keywords
- "phòng khách" → `living_room`
- "phòng ngủ" → `bedroom`
- "nhà bếp", "bếp" → `kitchen`
- "phòng tắm", "toilet" → `bathroom`
- "ban công" → `balcony`
- "nhà để xe", "garage" → `garage`

### Comfort Keywords
- "nóng", "oi bức", "cần mát" → `cooling`
- "lạnh", "rét", "cần ấm" → `warming`
- "tối", "thiếu sáng" → `brighten`
- "chói", "sáng quá" → `dim`
- "ngột ngạt", "thiếu không khí" → `ventilate`

### Scene Keywords
- "đi ngủ", "ngủ ngon" → `sleep`
- "thức dậy", "buổi sáng" → `wake_up`
- "xem phim", "xem TV" → `movie`
- "đi ra ngoài", "rời nhà" → `away`
- "về nhà", "đã về" → `home`

## Response Format

All intent classification responses follow this structure:

```json
{
  "intent": "string",
  "entities": {
    "key": "value"
  },
  "confidence": 0.95,
  "timestamp": "2024-01-15T10:30:00Z",
  "classifier_type": "rule|ml"
}
```

### Fallback Response (Low Confidence)

When confidence < 0.7:

```json
{
  "intent": "unknown",
  "entities": {},
  "confidence": 0.45,
  "timestamp": "2024-01-15T10:30:00Z",
  "classifier_type": "ml",
  "clarification_needed": true,
  "suggestions": [
    {
      "intent": "control_device",
      "confidence": 0.45
    },
    {
      "intent": "query_device_status",
      "confidence": 0.32
    }
  ]
}
```

## Usage in Code

```python
from src.config.schema import ENTITY_SCHEMA, INTENT_CATEGORIES

# Check if a device type is valid
if device in ENTITY_SCHEMA["device_types"]:
    print(f"Valid device: {device}")

# Get all valid actions
valid_actions = ENTITY_SCHEMA["actions"]

# Check if an intent is valid
if intent in INTENT_CATEGORIES:
    print(f"Valid intent: {intent}")
```

## Notes

- All entity values are in **English** (standardized format)
- Vietnamese keywords are mapped to English entity values
- Entity extraction happens after text preprocessing
- Unknown entity values should be rejected or flagged for review
- The schema is defined in `src/config/schema.py`
