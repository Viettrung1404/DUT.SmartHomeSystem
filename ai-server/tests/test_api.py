from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


client = TestClient(app)


def _sample_context() -> dict:
    return {
        "rooms": [
            {"id": "room-living", "name": "Phòng khách", "aliases": ["pk", "living room"]},
            {"id": "room-bedroom", "name": "Phòng ngủ", "aliases": ["pn", "bedroom"]},
        ],
        "devices": [
            {
                "id": "dev-light-living",
                "room_id": "room-living",
                "name": "Đèn phòng khách",
                "type": "light",
                "aliases": ["đèn khách"],
                "metadata": {"state": "off"},
                "status": False,
                "online_status": True,
            },
            {
                "id": "dev-fan-living",
                "room_id": "room-living",
                "name": "Quạt phòng khách",
                "type": "fan",
                "aliases": ["quat khach"],
                "metadata": {"speed": "off"},
                "status": False,
                "online_status": True,
            },
            {
                "id": "dev-sensor-living",
                "room_id": "room-living",
                "name": "Cảm biến nhiệt độ phòng khách",
                "type": "temperature_humidity",
                "aliases": ["cảm biến pk"],
                "metadata": {"temperature": 29.1, "humidity": 71.0},
                "status": True,
                "online_status": True,
            },
        ],
    }


def _sample_history() -> list[dict]:
    start = datetime(2026, 6, 5, 18, 0, 0)
    history = []
    for idx in range(12):
        history.append(
            {
                "timestamp": (start + timedelta(minutes=5 * idx)).isoformat(),
                "temperature": 27.0 + (idx * 0.15),
                "humidity": 61.0 + (idx * 0.45),
                "occupancy_ratio": 0.7 if idx > 6 else 0.2,
                "fan_on": False if idx < 10 else True,
                "rain_detected": False,
                "outdoor_temp": 31.5,
            }
        )
    return history


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert len(payload["models"]) >= 2


def test_parse_control_device() -> None:
    response = client.post(
        "/api/v1/nlp/parse",
        json={"text": "Bật đèn phòng khách", "context": _sample_context()},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "control_device"
    assert payload["action_draft"]["action"] == "turn_on"
    assert payload["action_draft"]["room_id"] == "room-living"


def test_parse_no_diacritic_uses_hybrid_path() -> None:
    response = client.post(
        "/api/v1/nlp/parse",
        json={"text": "bat den phong khach", "context": _sample_context()},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "control_device"
    assert any(
        marker.startswith("intent_model=baseline_tfidf_lr") or marker.startswith("slot_model=")
        for marker in payload["explanation"]
    )


def test_parse_missing_slot() -> None:
    response = client.post("/api/v1/nlp/parse", json={"text": "Bật đèn đi", "context": _sample_context()})
    assert response.status_code == 200
    payload = response.json()
    assert "room" in payload["missing_slots"] or "device" in payload["missing_slots"]


def test_assistant_query_sensor() -> None:
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "Nhiệt độ phòng khách bao nhiêu", "home_context": _sample_context()},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["nlu"]["intent"] == "query_sensor"
    assert "sensor_summary" in payload["grounding"]


def test_environment_prediction() -> None:
    response = client.post(
        "/api/v1/predict/environment",
        json={"inline_history": _sample_history()},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["temperature_interval"]["lower"] <= payload["temperature_next_30min"] <= payload["temperature_interval"]["upper"]
    assert payload["humidity_interval"]["lower"] <= payload["humidity_next_30min"] <= payload["humidity_interval"]["upper"]
    assert payload["top_signals"]


def test_environment_prediction_batch() -> None:
    response = client.post(
        "/api/v1/predict/environment/batch",
        json={
            "items": [
                {"request_id": "living", "request": {"inline_history": _sample_history()}},
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["request_id"] == "living"
