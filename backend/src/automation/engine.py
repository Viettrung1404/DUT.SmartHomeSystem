"""
Automation engine checks time-based conditions and executes device actions via MQTT.
"""

import json
import logging
from datetime import datetime, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm.attributes import flag_modified

scheduler = BackgroundScheduler()
_db_session_factory = None


def _schedule_context(now_utc: datetime, timezone_name: str | None) -> tuple[str, int]:
    try:
        tz = ZoneInfo(timezone_name or "Asia/Ho_Chi_Minh")
    except ZoneInfoNotFoundError:
        logging.warning("Invalid home timezone %s; falling back to UTC", timezone_name)
        tz = timezone.utc

    local_now = now_utc.astimezone(tz)
    # Match the existing schedule convention: Sunday=0, Monday=1, ..., Saturday=6.
    return local_now.strftime("%H:%M"), (local_now.weekday() + 1) % 7


def _condition_matches(condition, current_time: str, current_weekday: int) -> bool:
    if condition.condition_type == "time":
        return condition.value == current_time

    if condition.condition_type == "weekday_time":
        try:
            payload = json.loads(condition.value)
        except (TypeError, ValueError, json.JSONDecodeError):
            logging.warning(
                "Invalid weekday_time payload on automation condition %s",
                condition.id,
            )
            return False

        expected_time = str(payload.get("time", "")).strip()
        days_of_week = payload.get("days_of_week") or []
        try:
            normalized_days = {int(day) for day in days_of_week}
        except (TypeError, ValueError):
            logging.warning(
                "Invalid days_of_week payload on automation condition %s",
                condition.id,
            )
            return False

        return expected_time == current_time and current_weekday in normalized_days

    return False


def _device_type_value(device) -> str:
    return str(getattr(getattr(device, "type", ""), "value", getattr(device, "type", ""))).strip().lower()


def _device_kind(device) -> str:
    config = getattr(device, "config", None)
    if isinstance(config, dict):
        kind = str(config.get("kind") or "").strip().lower()
        if kind:
            return kind
    return _device_type_value(device)


def _is_truthy_action_value(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"on", "true", "1", "open", "unlock"}
    return bool(value)


def _apply_power_state(state: dict, *, is_on: bool) -> None:
    state["power"] = "ON" if is_on else "OFF"


def _apply_door_like_state(kind: str, state: dict, *, is_open: bool) -> None:
    if kind in {"door", "lock"}:
        state["door"] = "open" if is_open else "closed"
    if kind == "lock":
        state["isLocked"] = not is_open
    if kind == "curtain":
        state["position"] = "open" if is_open else "closed"


def _resolve_action(device, action, old_state: dict) -> tuple[str, object | None, dict]:
    command = str(action.action or "").strip().lower()
    value = action.value
    kind = _device_kind(device)
    next_state = dict(old_state or {})

    if command == "toggle":
        is_on = _is_truthy_action_value(value)
        if kind in {"lock", "door", "curtain"}:
            command = "open" if is_on else "close"
            value = None
            _apply_power_state(next_state, is_on=is_on)
            _apply_door_like_state(kind, next_state, is_open=is_on)
        else:
            command = "turn_on" if is_on else "turn_off"
            value = None
            _apply_power_state(next_state, is_on=is_on)
        return command, value, next_state

    if command == "set_brightness":
        next_state["brightness"] = value
    elif command == "set_temperature":
        next_state["targetTemp"] = value
    elif command == "set_mode":
        next_state["mode"] = value
    elif command == "set_speed":
        next_state["speed"] = str(value) if value is not None else "off"
        _apply_power_state(next_state, is_on=str(next_state["speed"]).lower() != "off")
    elif command in {"lock", "unlock"}:
        is_open = command == "unlock"
        next_state["isLocked"] = not is_open
        next_state["door"] = "open" if is_open else "closed"
        _apply_power_state(next_state, is_on=is_open)
    elif command == "set_position":
        next_state["position"] = value
    elif command == "set_angle":
        next_state["angle"] = value
    elif command in {"turn_on", "on"}:
        command = "turn_on"
        _apply_power_state(next_state, is_on=True)
    elif command in {"turn_off", "off"}:
        command = "turn_off"
        _apply_power_state(next_state, is_on=False)
    elif command == "open":
        _apply_power_state(next_state, is_on=True)
        _apply_door_like_state(kind, next_state, is_open=True)
    elif command == "close":
        _apply_power_state(next_state, is_on=False)
        _apply_door_like_state(kind, next_state, is_open=False)

    return command, value, next_state


def init_automation_engine(session_factory):
    global _db_session_factory
    _db_session_factory = session_factory

    scheduler.add_job(check_time_automations, "interval", minutes=1, id="time_check")
    scheduler.start()
    logging.info("Automation engine started")


def check_time_automations(now: datetime | None = None):
    """Check all enabled automations with time-based conditions."""
    if not _db_session_factory:
        return

    from src.entities.models import Automation, Device, DeviceLog, DeviceState, TriggerSource
    from src.mqtt_client import publish_device_command
    from src.services.activity_logger import record_device_power_transition

    db = _db_session_factory()
    try:
        now_utc = now or datetime.now(timezone.utc)
        if now_utc.tzinfo is None:
            now_utc = now_utc.replace(tzinfo=timezone.utc)
        else:
            now_utc = now_utc.astimezone(timezone.utc)

        automations = db.query(Automation).filter(Automation.enabled == True).all()

        for automation in automations:
            current_time, current_weekday = _schedule_context(
                now_utc,
                getattr(getattr(automation, "home", None), "timezone", None),
            )
            conditions_met = True
            for condition in automation.conditions:
                if not _condition_matches(condition, current_time, current_weekday):
                    conditions_met = False
                    break

            if conditions_met and automation.conditions:
                logging.info("Automation triggered: %s", automation.name)
                for action in automation.actions:
                    try:
                        if action.device_id:
                            device = db.query(Device).filter(Device.id == action.device_id).first()
                            if device and device.state and device.state.is_online:
                                old_state = dict(device.state.state or {})
                                command, value, next_state = _resolve_action(device, action, old_state)

                                publish_device_command(str(device.id), command, value)

                                if not device.state:
                                    device.state = DeviceState(
                                        device_id=device.id,
                                        state={},
                                        is_online=True,
                                    )

                                device.state.state = next_state
                                flag_modified(device.state, "state")
                                device.state.last_updated = now_utc
                                record_device_power_transition(
                                    db,
                                    device=device,
                                    old_state=old_state,
                                    new_state=next_state,
                                    trigger_source=TriggerSource.AUTOMATION,
                                    home_id=automation.home_id,
                                )
                                db.add(
                                    DeviceLog(
                                        id=uuid4(),
                                        device_id=device.id,
                                        action=command,
                                        value=str(value) if value is not None else None,
                                    )
                                )
                    except Exception as e:
                        logging.error("Automation action failed: %s", e)

                db.commit()
    except Exception as e:
        logging.error("Automation check error: %s", e)
    finally:
        db.close()


def stop_automation_engine():
    scheduler.shutdown(wait=False)
    logging.info("Automation engine stopped")
