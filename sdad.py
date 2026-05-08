# -*- coding: utf-8 -*-
import os
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

DOOR_PIN = int(os.getenv("DOOR_PIN", "17"))
DOOR_OPEN_SECONDS = float(os.getenv("DOOR_OPEN_SECONDS", "3"))
DOOR_OPEN_ANGLE = float(os.getenv("DOOR_OPEN_ANGLE", "130"))
DOOR_CLOSE_ANGLE = float(os.getenv("DOOR_CLOSE_ANGLE", "0"))
LIGHT_PIN = int(os.getenv("LIGHT_PIN", "20"))
LIGHT_PIN2 = int(os.getenv("LIGHT_PIN2", "25"))
FAN_PIN = int(os.getenv("FAN_PIN", "21"))
FAN_PIN2 = int(os.getenv("FAN_PIN2", "26"))
TOGGLE_SECONDS = float(os.getenv("TOGGLE_SECONDS", "3"))
SERVO_MIN_DUTY = float(os.getenv("SERVO_MIN_DUTY", "2.5"))
SERVO_MAX_DUTY = float(os.getenv("SERVO_MAX_DUTY", "12.5"))
SERVO_FREQUENCY = float(os.getenv("SERVO_FREQUENCY", "50"))

def angle_to_duty(angle: float) -> float:
    safe_angle = max(0.0, min(180.0, angle))
    span = SERVO_MAX_DUTY - SERVO_MIN_DUTY
    return SERVO_MIN_DUTY + (safe_angle / 180.0) * span

def open_then_close() -> None:
    if GPIO is None:
        print("RPi.GPIO not available; simulation mode.")
        print("[SIM] Door open to {} deg on pin {} for {}s".format(DOOR_OPEN_ANGLE, DOOR_PIN, DOOR_OPEN_SECONDS))
        time.sleep(DOOR_OPEN_SECONDS)
        print("[SIM] Door close to {} deg".format(DOOR_CLOSE_ANGLE))
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DOOR_PIN, GPIO.OUT)
    pwm = GPIO.PWM(DOOR_PIN, SERVO_FREQUENCY)

    try:
        pwm.start(0)
        open_duty = angle_to_duty(DOOR_OPEN_ANGLE)
        close_duty = angle_to_duty(DOOR_CLOSE_ANGLE)

        pwm.ChangeDutyCycle(open_duty)
        print("Door opened to {} deg on pin {} for {}s".format(DOOR_OPEN_ANGLE, DOOR_PIN, DOOR_OPEN_SECONDS))
        time.sleep(0.5)
        pwm.ChangeDutyCycle(0)

        time.sleep(DOOR_OPEN_SECONDS)

        pwm.ChangeDutyCycle(close_duty)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(0)
        print("Door closed to {} deg".format(DOOR_CLOSE_ANGLE))
    finally:
        pwm.stop()
        GPIO.cleanup(DOOR_PIN)

def run_light_fan_loop() -> None:
    if GPIO is None:
        print("RPi.GPIO not available; simulation mode.")
        while True:
            print("[SIM] LIGHT/FAN ON for {}s".format(TOGGLE_SECONDS))
            time.sleep(TOGGLE_SECONDS)
            print("[SIM] LIGHT/FAN OFF for {}s".format(TOGGLE_SECONDS))
            time.sleep(TOGGLE_SECONDS)

    GPIO.setmode(GPIO.BCM)
    output_pins = [LIGHT_PIN, LIGHT_PIN2, FAN_PIN, FAN_PIN2]
    for pin in output_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

    try:
        while True:
            for pin in output_pins:
                GPIO.output(pin, GPIO.HIGH)
            print("LIGHT/FAN ON for {}s".format(TOGGLE_SECONDS))
            time.sleep(TOGGLE_SECONDS)

            for pin in output_pins:
                GPIO.output(pin, GPIO.LOW)
            print("LIGHT/FAN OFF for {}s".format(TOGGLE_SECONDS))
            time.sleep(TOGGLE_SECONDS)
    finally:
        for pin in output_pins:
            GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup(output_pins)

if __name__ == "__main__":
    try:
        open_then_close()
        run_light_fan_loop()
    except KeyboardInterrupt:
        print("\nStopped by user")