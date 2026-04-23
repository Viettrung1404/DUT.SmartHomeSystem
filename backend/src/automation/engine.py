"""
Automation engine — checks time-based conditions on a schedule
and executes device actions via MQTT.
"""

import logging
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

scheduler = BackgroundScheduler()
_db_session_factory = None


def init_automation_engine(session_factory):
    global _db_session_factory
    _db_session_factory = session_factory

    # Check time-based automations every minute
    scheduler.add_job(check_time_automations, 'interval', minutes=1, id='time_check')
    scheduler.start()
    logging.info("Automation engine started")


def check_time_automations():
    """Check all enabled automations with time-based conditions."""
    if not _db_session_factory:
        return

    from src.entities.automation import Automation, AutomationCondition, AutomationAction
    from src.entities.device import Device
    from src.mqtt_client import publish_command

    db = _db_session_factory()
    try:
        now = datetime.now(timezone.utc)
        current_time = now.strftime("%H:%M")

        automations = db.query(Automation).filter(Automation.enabled == True).all()

        for automation in automations:
            conditions_met = True
            for condition in automation.conditions:
                if condition.condition_type == 'time':
                    if condition.value != current_time:
                        conditions_met = False
                        break
                # Other condition types can be added here

            if conditions_met and automation.conditions:
                logging.info(f"Automation triggered: {automation.name}")
                for action in automation.actions:
                    try:
                        if action.device_id:
                            device = db.query(Device).filter(Device.id == action.device_id).first()
                            if device and device.online_status:
                                command = action.action
                                if action.value is not None and action.action == 'toggle':
                                    command = 'on' if str(action.value).lower() in {'1', 'true', 'on'} else 'off'
                                elif action.value is not None and action.action in {'set_brightness', 'set_temperature', 'set_mode'}:
                                    command = f"{action.action}:{action.value}"

                                publish_command(command, str(device.home_id), str(device.id))

                                # Update device in DB
                                if action.action == 'toggle':
                                    device.status = action.value == 'on' or action.value == 'True'
                                elif action.action in ('set_brightness', 'set_temperature', 'set_mode'):
                                    metadata = device.metadata_json or {}
                                    key_map = {
                                        'set_brightness': 'brightness',
                                        'set_temperature': 'targetTemp',
                                        'set_mode': 'mode',
                                    }
                                    metadata[key_map[action.action]] = action.value
                                    device.metadata_json = metadata
                                device.last_seen = now
                    except Exception as e:
                        logging.error(f"Automation action failed: {e}")

                db.commit()
    except Exception as e:
        logging.error(f"Automation check error: {e}")
    finally:
        db.close()


def stop_automation_engine():
    scheduler.shutdown(wait=False)
    logging.info("Automation engine stopped")
