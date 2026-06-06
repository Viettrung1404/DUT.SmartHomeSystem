from __future__ import annotations

INTENTS = [
    "control_device",
    "query_sensor",
    "query_device_status",
    "environmental_comfort",
    "greeting",
    "out_of_scope",
]

ROOM_ALIASES = {
    "living_room": ["phong khach", "pk", "living room", "phong tiep khach", "khach"],
    "bedroom": ["phong ngu", "pn", "bedroom", "ngu"],
    "kitchen": ["phong bep", "bep", "kitchen", "nha bep"],
    "bathroom": ["phong tam", "nha ve sinh", "wc", "bathroom", "tam"],
    "roof_zone": ["mai che", "san thuong", "ngoai troi", "roof zone", "khu mai"],
    "main_door": ["cua chinh", "cua truoc", "main door"],
}

DEVICE_TYPE_ALIASES = {
    "light": ["den", "light", "lamp", "den khach", "den ngu"],
    "fan": ["quat", "fan"],
    "door_servo": ["cua", "cua chinh", "servo cua", "door", "cong"],
    "roof_servo": ["tran servo", "mai che", "che mua", "rain servo", "servo mai"],
    "dht11_sensor": ["nhiet do", "do am", "cam bien nhiet do", "cam bien do am", "dht11"],
    "gas_sensor": ["gas", "khi gas", "cam bien gas"],
    "rain_sensor": ["mua", "cam bien mua"],
    "fire_sensor": ["chay", "bao chay", "cam bien chay", "khoi"],
    "bathroom_ultrasonic_sensor": ["khoang cach", "sieu am", "distance sensor", "co nguoi"],
}

SENSOR_TYPE_ALIASES = {
    "temperature": ["nhiet do", "nong", "lanh", "do c"],
    "humidity": ["do am", "am"],
    "gas_detected": ["gas", "khi gas"],
    "fire_detected": ["chay", "lua", "khoi", "bao chay"],
    "rain_detected": ["mua"],
    "occupancy": ["co nguoi", "co ai", "dang su dung", "nha ve sinh co nguoi"],
}

ACTION_ALIASES = {
    "turn_on": ["bat", "mo", "switch on"],
    "turn_off": ["tat", "switch off"],
    "open": ["mo"],
    "close": ["dong"],
    "lock": ["khoa"],
    "unlock": ["mo khoa", "unlock"],
    "set_speed": ["chinh toc do", "toc do", "set speed"],
}

CAPABILITY_NOTE = (
    "Comfort output la comfort proxy tu sensor va forecast, khong phai PMV exact vi V1 "
    "khong su dung day du bien nhu air speed, clothing va metabolic rate."
)
