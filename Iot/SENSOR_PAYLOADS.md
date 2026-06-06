# Payload cảm biến -> BE (thư mục IoT)

Tài liệu này liệt kê các cảm biến gửi dữ liệu lên backend và định dạng payload MQTT.

## MQTT topics

Ưu tiên (per-device):
- device/{device_id}/status

Legacy (vẫn được iot_client.py publish):
- smarthome/{HOME_ID}/status
- smarthome/{HOME_ID}/sensors

Backend nhận status theo từng thiết bị và lưu giá trị cảm biến vào device.metadata.

## Danh sách cảm biến và payload

1) DHT11 / DHT22 (nhiệt độ + độ ẩm)
- Device kind trong device_map.json: temperature_humidity
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "temperature": 28.5,
      "humidity": 60.0
    }
  }
- Nguồn: read_dht()

2) Cảm biến mưa
- Device kind trong device_map.json: rain_sensor
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "rain_detected": true
    }
  }
- Nguồn: read_rain()

3) Cảm biến gas
- Device kind trong device_map.json: gas_sensor
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "gas_detected": true
    }
  }
- Nguồn: read_gas()

4) Cảm biến khoảng cách siêu âm
- Device kind trong device_map.json: distance_sensor
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "distance_cm": 123.4,
      "distance_alert": false
    }
  }
- Nguồn: read_distance()

## Danh sách thiết bị điều khiển và payload

1) Đèn
- Device kind trong device_map.json: light
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "state": "on"
    }
  }

2) Quạt
- Device kind trong device_map.json: fan
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "speed": "strong"
    }
  }

3) Cửa (servo cửa)
- Device kind trong device_map.json: door
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": false,
    "metadata": {
      "door": "closed"
    }
  }

4) Còi (buzzer)
- Device kind trong device_map.json: buzzer
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "buzzer": "on"
    }
  }

5) Đèn khoảng cách
- Device kind trong device_map.json: distance_light
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
      "distance_light": "on"
    }
  }

6) Servo che mưa
- Device kind trong device_map.json: rain_servo
- Payload (device/{id}/status):
  {
    "online": true,
    "timestamp": 1710000000,
    "status": true,
    "metadata": {
        "position": "wet",
        "angle": 120
    }
  }

## Payload cảm biến legacy (smarthome/{HOME_ID}/sensors)

Topic legacy gửi payload gộp:
{
  "distance_cm": 123.4,
  "distance_alert": false,
  "distance_light": "off",
  "gas_detected": false,
  "buzzer": "off",
  "rain_detected": false,
  "timestamp": 1710000000
}

## Cách map cảm biến

Để gửi dữ liệu cảm biến lên backend, thêm UUID thiết bị vào device_map.json với kind đúng:
- temperature_humidity
- rain_sensor
- gas_sensor
- distance_sensor
