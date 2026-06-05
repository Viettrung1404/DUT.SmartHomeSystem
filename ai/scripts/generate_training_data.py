"""
Training Data Generation Script for Vietnamese NLP Intent Classification.

This script generates a JSON dataset with Vietnamese text samples for each intent,
including entities and metadata. The dataset follows the format required for
PhoBERT fine-tuning.

**Validates: Requirements 9.1, 9.2, 9.3**

Usage:
    python scripts/generate_training_data.py --output data/raw/training_data.json --samples 150
"""

import json
import random
import argparse
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


# ============================================================================
# INTENT TEMPLATES WITH VIETNAMESE EXAMPLES
# ============================================================================

INTENT_TEMPLATES = {
    "control_device": {
        "description": "Control smart home devices (lights, fans, AC, doors, etc.)",
        "templates": [
            # Lights
            ("Bật đèn {location}", {"device": "light", "action": "turn_on", "location": "{location}"}),
            ("Tắt đèn {location}", {"device": "light", "action": "turn_off", "location": "{location}"}),
            ("Mở đèn {location}", {"device": "light", "action": "turn_on", "location": "{location}"}),
            ("Tắt ánh sáng {location}", {"device": "light", "action": "turn_off", "location": "{location}"}),
            ("Bật bóng đèn {location}", {"device": "light", "action": "turn_on", "location": "{location}"}),
            ("Chỉnh độ sáng {location} {value}%", {"device": "light", "action": "adjust", "location": "{location}", "value": "{value}", "unit": "%"}),
            ("Đặt độ sáng {value}%", {"device": "light", "action": "adjust", "value": "{value}", "unit": "%"}),
            
            # Fans
            ("Bật quạt {location}", {"device": "fan", "action": "turn_on", "location": "{location}"}),
            ("Tắt quạt {location}", {"device": "fan", "action": "turn_off", "location": "{location}"}),
            ("Khởi động quạt trần {location}", {"device": "fan", "action": "turn_on", "location": "{location}"}),
            ("Dừng quạt {location}", {"device": "fan", "action": "turn_off", "location": "{location}"}),
            ("Chạy quạt máy", {"device": "fan", "action": "turn_on"}),
            
            # AC
            ("Bật điều hòa {location}", {"device": "ac", "action": "turn_on", "location": "{location}"}),
            ("Tắt máy lạnh {location}", {"device": "ac", "action": "turn_off", "location": "{location}"}),
            ("Đặt nhiệt độ {value} độ", {"device": "ac", "action": "adjust", "value": "{value}", "unit": "C"}),
            ("Chỉnh AC {value} độ C", {"device": "ac", "action": "adjust", "value": "{value}", "unit": "C"}),
            ("Bật air conditioner", {"device": "ac", "action": "turn_on"}),
            
            # Doors
            ("Mở cửa {location}", {"device": "door", "action": "turn_on", "location": "{location}"}),
            ("Đóng cửa {location}", {"device": "door", "action": "turn_off", "location": "{location}"}),
            ("Mở cửa ra vào", {"device": "door", "action": "turn_on"}),
            ("Đóng cửa chính", {"device": "door", "action": "turn_off"}),
            
            # Awnings
            ("Mở mái che {location}", {"device": "awning", "action": "turn_on", "location": "{location}"}),
            ("Đóng mái che {location}", {"device": "awning", "action": "turn_off", "location": "{location}"}),
            ("Mở mái hiên", {"device": "awning", "action": "turn_on"}),
            ("Đóng mái bạt", {"device": "awning", "action": "turn_off"}),
            
            # Locks
            ("Khóa cửa {location}", {"device": "lock", "action": "lock", "location": "{location}"}),
            ("Mở khóa cửa {location}", {"device": "lock", "action": "unlock", "location": "{location}"}),
            ("Khóa ổ khóa", {"device": "lock", "action": "lock"}),
            
            # Curtains
            ("Mở rèm {location}", {"device": "curtain", "action": "turn_on", "location": "{location}"}),
            ("Đóng rèm cửa {location}", {"device": "curtain", "action": "turn_off", "location": "{location}"}),
            
            # Cameras
            ("Bật camera {location}", {"device": "camera", "action": "turn_on", "location": "{location}"}),
            ("Tắt cam", {"device": "camera", "action": "turn_off"}),
        ]
    },
    
    "environmental_comfort": {
        "description": "Express environmental comfort needs (hot, cold, dark, bright, stuffy)",
        "templates": [
            # Cooling
            ("Trời nóng quá", {"comfort_type": "cooling"}),
            ("Oi bức quá", {"comfort_type": "cooling"}),
            ("Cần làm mát", {"comfort_type": "cooling"}),
            ("Nóng quá đi", {"comfort_type": "cooling"}),
            ("Cần mát hơn", {"comfort_type": "cooling"}),
            ("Làm mát phòng này", {"comfort_type": "cooling"}),
            
            # Warming
            ("Trời lạnh quá", {"comfort_type": "warming"}),
            ("Rét quá", {"comfort_type": "warming"}),
            ("Cần ấm hơn", {"comfort_type": "warming"}),
            ("Lạnh quá đi", {"comfort_type": "warming"}),
            ("Cần sưởi ấm", {"comfort_type": "warming"}),
            
            # Brighten
            ("Tối quá", {"comfort_type": "brighten"}),
            ("Thiếu sáng", {"comfort_type": "brighten"}),
            ("Cần sáng hơn", {"comfort_type": "brighten"}),
            ("Tối quá đi", {"comfort_type": "brighten"}),
            ("Sáng lên", {"comfort_type": "brighten"}),
            
            # Dim
            ("Sáng quá", {"comfort_type": "dim"}),
            ("Chói quá", {"comfort_type": "dim"}),
            ("Giảm sáng", {"comfort_type": "dim"}),
            ("Sáng quá đi", {"comfort_type": "dim"}),
            ("Tối hơn", {"comfort_type": "dim"}),
            
            # Ventilate
            ("Ngột ngạt", {"comfort_type": "ventilate"}),
            ("Thiếu không khí", {"comfort_type": "ventilate"}),
            ("Cần thông gió", {"comfort_type": "ventilate"}),
            ("Ngột ngạt quá", {"comfort_type": "ventilate"}),
            ("Thoáng hơn", {"comfort_type": "ventilate"}),
        ]
    },
    
    "activate_scene": {
        "description": "Activate predefined scenes (sleep, wake_up, movie, away, home)",
        "templates": [
            # Sleep
            ("Đi ngủ", {"scene_type": "sleep"}),
            ("Chúc ngủ ngon", {"scene_type": "sleep"}),
            ("Chuẩn bị ngủ", {"scene_type": "sleep"}),
            ("Tôi đi ngủ", {"scene_type": "sleep"}),
            ("Ngủ thôi", {"scene_type": "sleep"}),
            
            # Wake up
            ("Thức dậy", {"scene_type": "wake_up"}),
            ("Buổi sáng", {"scene_type": "wake_up"}),
            ("Chào buổi sáng", {"scene_type": "wake_up"}),
            ("Dậy rồi", {"scene_type": "wake_up"}),
            ("Tôi dậy rồi", {"scene_type": "wake_up"}),
            
            # Movie
            ("Xem phim", {"scene_type": "movie"}),
            ("Xem TV", {"scene_type": "movie"}),
            ("Rạp chiếu phim", {"scene_type": "movie"}),
            ("Coi phim", {"scene_type": "movie"}),
            ("Xem tivi", {"scene_type": "movie"}),
            
            # Away
            ("Đi ra ngoài", {"scene_type": "away"}),
            ("Rời nhà", {"scene_type": "away"}),
            ("Đi vắng", {"scene_type": "away"}),
            ("Ra ngoài", {"scene_type": "away"}),
            ("Tôi đi ra ngoài", {"scene_type": "away"}),
            
            # Home
            ("Về nhà", {"scene_type": "home"}),
            ("Đã về", {"scene_type": "home"}),
            ("Tôi về rồi", {"scene_type": "home"}),
            ("Về rồi", {"scene_type": "home"}),
            ("Tôi đã về", {"scene_type": "home"}),
        ]
    },
    
    "query_sensor": {
        "description": "Query sensor data (temperature, humidity, rain, gas, fire, motion)",
        "templates": [
            # Temperature
            ("Nhiệt độ {location} bao nhiêu", {"sensor_type": "temperature", "location": "{location}"}),
            ("Nhiệt độ hiện tại", {"sensor_type": "temperature"}),
            ("Bao nhiêu độ", {"sensor_type": "temperature"}),
            ("Kiểm tra nhiệt độ {location}", {"sensor_type": "temperature", "location": "{location}"}),
            
            # Humidity
            ("Độ ẩm {location} bao nhiêu", {"sensor_type": "humidity", "location": "{location}"}),
            ("Độ ẩm hiện tại", {"sensor_type": "humidity"}),
            ("Kiểm tra độ ẩm", {"sensor_type": "humidity"}),
            
            # Rain
            ("Trời có mưa không", {"sensor_type": "rain"}),
            ("Đang mưa không", {"sensor_type": "rain"}),
            ("Có mưa không", {"sensor_type": "rain"}),
            
            # Gas
            ("Có khí gas không", {"sensor_type": "gas"}),
            ("Phát hiện gas", {"sensor_type": "gas"}),
            ("Kiểm tra gas", {"sensor_type": "gas"}),
            
            # Fire
            ("Có cháy không", {"sensor_type": "fire"}),
            ("Phát hiện lửa", {"sensor_type": "fire"}),
            ("Kiểm tra cháy", {"sensor_type": "fire"}),
            
            # Motion
            ("Có chuyển động không", {"sensor_type": "motion"}),
            ("Phát hiện chuyển động", {"sensor_type": "motion"}),
            ("Kiểm tra chuyển động", {"sensor_type": "motion"}),
        ]
    },
    
    "query_device_status": {
        "description": "Query device status",
        "templates": [
            ("Đèn {location} đang bật không", {"device": "light", "location": "{location}"}),
            ("Quạt {location} đang chạy không", {"device": "fan", "location": "{location}"}),
            ("Điều hòa có bật không", {"device": "ac"}),
            ("Cửa {location} đóng chưa", {"device": "door", "location": "{location}"}),
            ("Trạng thái đèn", {"device": "light"}),
            ("Kiểm tra quạt", {"device": "fan"}),
            ("Camera có bật không", {"device": "camera"}),
        ]
    },
    
    "security_mode": {
        "description": "Activate or deactivate security mode",
        "templates": [
            ("Kích hoạt chế độ an ninh", {"mode": "armed"}),
            ("Bật an ninh", {"mode": "armed"}),
            ("Tắt chế độ an ninh", {"mode": "disarmed"}),
            ("Vô hiệu hóa an ninh", {"mode": "disarmed"}),
            ("Bật chế độ bảo vệ", {"mode": "armed"}),
            ("Tắt bảo vệ", {"mode": "disarmed"}),
        ]
    },
    
    "security_alert": {
        "description": "Security alerts (fire, gas, intrusion) - with false positive prevention",
        "templates": [
            # Fire alerts (real danger)
            ("Có cháy", {"alert_type": "fire"}),
            ("Phát hiện lửa", {"alert_type": "fire"}),
            ("Báo cháy", {"alert_type": "fire"}),
            ("Cháy rồi", {"alert_type": "fire"}),
            
            # Gas alerts
            ("Rò rỉ khí gas", {"alert_type": "gas"}),
            ("Phát hiện gas", {"alert_type": "gas"}),
            ("Có mùi gas", {"alert_type": "gas"}),
            
            # Intrusion alerts
            ("Có người lạ", {"alert_type": "intrusion"}),
            ("Phát hiện xâm nhập", {"alert_type": "intrusion"}),
            ("Có kẻ trộm", {"alert_type": "intrusion"}),
        ]
    },
    
    "weather_action": {
        "description": "Weather-responsive actions",
        "templates": [
            ("Trời mưa đóng mái che", {"weather_condition": "rain", "action": "turn_off", "device": "awning"}),
            ("Đang mưa đóng cửa", {"weather_condition": "rain", "action": "turn_off", "device": "door"}),
            ("Trời nắng mở mái che", {"weather_condition": "sunny", "action": "turn_on", "device": "awning"}),
            ("Có mưa", {"weather_condition": "rain"}),
            ("Trời nắng", {"weather_condition": "sunny"}),
        ]
    },
    
    "lock_all_doors": {
        "description": "Lock all doors at once",
        "templates": [
            ("Khóa tất cả cửa", {}),
            ("Khóa toàn bộ cửa", {}),
            ("Khóa hết cửa", {}),
            ("Khóa tất cả các cửa", {}),
        ]
    },
    
    "turn_off_all_devices": {
        "description": "Turn off all devices",
        "templates": [
            ("Tắt tất cả thiết bị", {}),
            ("Tắt toàn bộ", {}),
            ("Tắt hết", {}),
            ("Tắt tất cả", {}),
        ]
    },
    
    "create_automation": {
        "description": "Create automation rules",
        "templates": [
            ("Tạo quy tắc tự động", {}),
            ("Tạo tự động hóa", {}),
            ("Thiết lập tự động hóa", {}),
            ("Tạo quy tắc mới", {}),
            ("Lập quy tắc tự động", {}),
        ]
    },
    
    "unknown": {
        "description": "Unknown or unclear intent",
        "templates": [
            ("Hello", {}),
            ("Xin chào", {}),
            ("Cảm ơn", {}),
            ("Tạm biệt", {}),
            ("Hôm nay thế nào", {}),
            ("Bạn khỏe không", {}),
        ]
    }
}


# ============================================================================
# ENTITY VALUE POOLS
# ============================================================================

# Vietnamese to English location mapping
LOCATION_MAPPING = {
    "phòng khách": "living_room",
    "phòng ngủ": "bedroom",
    "bếp": "kitchen",
    "phòng tắm": "bathroom",
    "ban công": "balcony",
    "garage": "garage"
}

LOCATIONS = ["phòng khách", "phòng ngủ", "bếp", "phòng tắm", "ban công", "garage"]
VALUES_TEMP = [18, 20, 22, 24, 25, 26, 28, 30]
VALUES_PERCENT = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


# ============================================================================
# DATA GENERATION FUNCTIONS
# ============================================================================

def generate_samples(intent: str, templates: List[tuple], num_samples: int) -> List[Dict[str, Any]]:
    """
    Generate training samples for a given intent.
    
    Args:
        intent: Intent name
        templates: List of (text_template, entities_template) tuples
        num_samples: Number of samples to generate
        
    Returns:
        List of training samples with text, intent, entities, and metadata
    """
    samples = []
    
    # Calculate how many times to repeat each template
    repeats_per_template = max(1, num_samples // len(templates))
    
    for text_template, entities_template in templates:
        for _ in range(repeats_per_template):
            # Fill in placeholders
            text = text_template
            entities = entities_template.copy()
            
            # Replace location placeholder
            if "{location}" in text:
                location_vn = random.choice(LOCATIONS)
                location_en = LOCATION_MAPPING.get(location_vn, location_vn)
                text = text.replace("{location}", location_vn)
                if "location" in entities and entities["location"] == "{location}":
                    entities["location"] = location_en
            
            # Replace value placeholder (temperature)
            if "{value}" in text and "unit" in entities and entities.get("unit") == "C":
                value = random.choice(VALUES_TEMP)
                text = text.replace("{value}", str(value))
                if "value" in entities and entities["value"] == "{value}":
                    entities["value"] = value
            
            # Replace value placeholder (percentage)
            elif "{value}" in text and "unit" in entities and entities.get("unit") == "%":
                value = random.choice(VALUES_PERCENT)
                text = text.replace("{value}", str(value))
                if "value" in entities and entities["value"] == "{value}":
                    entities["value"] = value
            
            # Create sample
            sample = {
                "text": text,
                "intent": intent,
                "entities": entities,
                "metadata": {
                    "source": "generated",
                    "timestamp": datetime.now().isoformat(),
                    "language": "vi"
                }
            }
            
            samples.append(sample)
            
            # Stop if we have enough samples
            if len(samples) >= num_samples:
                break
        
        if len(samples) >= num_samples:
            break
    
    return samples[:num_samples]


def generate_training_dataset(samples_per_intent: int = 150) -> List[Dict[str, Any]]:
    """
    Generate complete training dataset for all intents.
    
    Args:
        samples_per_intent: Number of samples to generate per intent
        
    Returns:
        List of all training samples
    """
    all_samples = []
    
    for intent, config in INTENT_TEMPLATES.items():
        print(f"Generating {samples_per_intent} samples for intent: {intent}")
        templates = config["templates"]
        samples = generate_samples(intent, templates, samples_per_intent)
        all_samples.extend(samples)
        print(f"  → Generated {len(samples)} samples")
    
    # Shuffle samples
    random.shuffle(all_samples)
    
    return all_samples


def save_dataset(samples: List[Dict[str, Any]], output_path: str):
    """
    Save dataset to JSON file.
    
    Args:
        samples: List of training samples
        output_path: Path to output JSON file
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, ensure_ascii=False, indent=2)
    
    print(f"\nDataset saved to: {output_path}")
    print(f"Total samples: {len(samples)}")
    
    # Print intent distribution
    intent_counts = {}
    for sample in samples:
        intent = sample["intent"]
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    print("\nIntent distribution:")
    for intent, count in sorted(intent_counts.items()):
        print(f"  {intent}: {count} samples")


# ============================================================================
# MAIN SCRIPT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Generate training dataset for Vietnamese NLP Intent Classification")
    parser.add_argument("--output", type=str, default="data/raw/training_data.json", help="Output JSON file path")
    parser.add_argument("--samples", type=int, default=150, help="Number of samples per intent")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    # Set random seed
    random.seed(args.seed)
    
    print(f"Generating training dataset with {args.samples} samples per intent...")
    print(f"Random seed: {args.seed}")
    print()
    
    # Generate dataset
    samples = generate_training_dataset(samples_per_intent=args.samples)
    
    # Save dataset
    save_dataset(samples, args.output)
    
    print("\n✓ Training dataset generation completed!")


if __name__ == "__main__":
    main()
