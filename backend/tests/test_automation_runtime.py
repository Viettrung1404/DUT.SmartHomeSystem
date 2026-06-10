from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from src.apis.automations import service as automation_service
from src.automation import engine
from src.entities.models import Device, Room
from src.exceptions import ForbiddenError


def test_schedule_context_uses_home_timezone():
    now_utc = datetime(2026, 6, 9, 15, 30, tzinfo=timezone.utc)

    current_time, current_weekday = engine._schedule_context(now_utc, "Asia/Ho_Chi_Minh")

    assert current_time == "22:30"
    assert current_weekday == 2


def test_weekday_time_condition_matches_local_schedule():
    condition = SimpleNamespace(
        id=uuid4(),
        condition_type="weekday_time",
        value='{"time": "22:30", "days_of_week": [2]}',
    )

    assert engine._condition_matches(condition, "22:30", 2)
    assert not engine._condition_matches(condition, "22:31", 2)
    assert not engine._condition_matches(condition, "22:30", 3)


def test_toggle_curtain_uses_kind_and_updates_position():
    device = SimpleNamespace(type="LOCK", config={"kind": "curtain"})
    action = SimpleNamespace(action="toggle", value="true")

    command, value, next_state = engine._resolve_action(device, action, {"power": "OFF"})

    assert command == "open"
    assert value is None
    assert next_state["power"] == "ON"
    assert next_state["position"] == "open"


def test_set_speed_updates_power_and_speed():
    device = SimpleNamespace(type="FAN", config={})
    action = SimpleNamespace(action="set_speed", value="strong")

    command, value, next_state = engine._resolve_action(device, action, {"power": "OFF"})

    assert command == "set_speed"
    assert value == "strong"
    assert next_state["power"] == "ON"
    assert next_state["speed"] == "strong"


def test_open_close_action_updates_lock_state():
    device = SimpleNamespace(type="LOCK", config={})
    action = SimpleNamespace(action="close", value=None)

    command, value, next_state = engine._resolve_action(
        device,
        action,
        {"power": "ON", "door": "open", "isLocked": False},
    )

    assert command == "close"
    assert value is None
    assert next_state["power"] == "OFF"
    assert next_state["door"] == "closed"
    assert next_state["isLocked"] is True


def test_set_position_updates_rain_servo_state():
    device = SimpleNamespace(type="SENSOR", config={"kind": "rain_servo"})
    action = SimpleNamespace(action="set_position", value="wet")

    command, value, next_state = engine._resolve_action(device, action, {"power": "OFF"})

    assert command == "set_position"
    assert value == "wet"
    assert next_state["power"] == "ON"
    assert next_state["position"] == "wet"


def test_set_angle_clamps_and_updates_power():
    device = SimpleNamespace(type="SENSOR", config={"kind": "rain_servo"})
    action = SimpleNamespace(action="set_angle", value="220")

    command, value, next_state = engine._resolve_action(device, action, {"power": "OFF"})

    assert command == "set_angle"
    assert value == "220"
    assert next_state["power"] == "ON"
    assert next_state["angle"] == 180


def test_device_status_condition_reads_device_state():
    device_id = uuid4()
    device = SimpleNamespace(
        id=device_id,
        state=SimpleNamespace(is_online=True, state={"power": "ON"}),
    )
    db = _FakeDb(device=device, room=None)
    condition = SimpleNamespace(
        id=uuid4(),
        condition_type="device_status",
        value=f'{{"device_id": "{device_id}", "field": "status", "operator": "eq", "value": true}}',
    )

    assert engine._condition_matches(condition, "12:00", 1, db)


def test_temperature_condition_compares_numeric_state():
    device_id = uuid4()
    device = SimpleNamespace(
        id=device_id,
        state=SimpleNamespace(is_online=True, state={"temperature": 32}),
    )
    db = _FakeDb(device=device, room=None)
    condition = SimpleNamespace(
        id=uuid4(),
        condition_type="temperature",
        value=f'{{"device_id": "{device_id}", "field": "temperature", "operator": ">", "value": 30}}',
    )

    assert engine._condition_matches(condition, "12:00", 1, db)


class _FakeQuery:
    def __init__(self, result):
        self._result = result

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._result


class _FakeDb:
    def __init__(self, *, device, room):
        self._device = device
        self._room = room

    def query(self, model):
        if model is Device:
            return _FakeQuery(self._device)
        if model is Room:
            return _FakeQuery(self._room)
        return _FakeQuery(None)


def test_action_device_must_belong_to_automation_home():
    home_id = uuid4()
    other_home_id = uuid4()
    room_id = uuid4()
    device_id = uuid4()
    device = SimpleNamespace(id=device_id, room_id=room_id)
    room = SimpleNamespace(id=room_id, home_id=other_home_id, is_active=True)
    db = _FakeDb(device=device, room=room)

    with pytest.raises(ForbiddenError):
        automation_service._check_action_device_access(db, home_id, device_id)
