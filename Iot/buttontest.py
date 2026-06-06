# -*- coding: utf-8 -*-
import os
import time

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None


BUTTON_PIN = int(os.getenv("BUTTON_PIN", "11"))
RELAY_PIN = int(os.getenv("RELAY_PIN", "20"))
BUTTON_ACTIVE_LOW = os.getenv("BUTTON_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
RELAY_ACTIVE_LOW = os.getenv("RELAY_ACTIVE_LOW", "1").strip().lower() in {"1", "true", "yes", "on"}
DEBOUNCE_SECONDS = float(os.getenv("BUTTON_DEBOUNCE_SECONDS", "0.2"))
POLL_INTERVAL_SECONDS = float(os.getenv("BUTTON_POLL_INTERVAL_SECONDS", "0.05"))


def log(message):
    print("[BUTTON-TEST] {}".format(message))


def button_pressed(value):
    return value == GPIO.LOW if BUTTON_ACTIVE_LOW else value == GPIO.HIGH


def set_relay(is_on):
    if GPIO is None:
        log("relay -> {}".format("ON" if is_on else "OFF"))
        return

    output_level = GPIO.LOW if (is_on and RELAY_ACTIVE_LOW) or (not is_on and not RELAY_ACTIVE_LOW) else GPIO.HIGH
    GPIO.output(RELAY_PIN, output_level)


def main():
    if GPIO is None:
        raise SystemExit("RPi.GPIO is not installed; run this on the Raspberry Pi")

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP if BUTTON_ACTIVE_LOW else GPIO.PUD_DOWN)
    GPIO.setup(RELAY_PIN, GPIO.OUT)

    # Start with the relay off so the first press is easy to observe.
    set_relay(False)

    last_button_value = GPIO.input(BUTTON_PIN)
    last_press_ts = 0.0
    light_on = False

    log(
        "start button_pin={} relay_pin={} button_active_low={} relay_active_low={}".format(
            BUTTON_PIN,
            RELAY_PIN,
            BUTTON_ACTIVE_LOW,
            RELAY_ACTIVE_LOW,
        )
    )
    log("initial button state={}".format("PRESSED" if button_pressed(last_button_value) else "RELEASED"))

    try:
        while True:
            current_value = GPIO.input(BUTTON_PIN)
            current_pressed = button_pressed(current_value)
            previous_pressed = button_pressed(last_button_value)
            now = time.monotonic()

            if current_pressed and not previous_pressed:
                if (now - last_press_ts) >= DEBOUNCE_SECONDS:
                    light_on = not light_on
                    set_relay(light_on)
                    log("nut duoc bam -> den phong khach {}".format("SANG" if light_on else "TAT"))
                    last_press_ts = now

            last_button_value = current_value
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        log("stopping")
    finally:
        set_relay(False)
        GPIO.cleanup()


if __name__ == "__main__":
    main()