import json
import os
from typing import Any, Dict, Tuple
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from flask import Flask, jsonify, render_template, request

WEB_PORT = int(os.getenv("WEB_PORT", "8001"))
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

app = Flask(__name__)

DEFAULT_STATUS: Dict[str, Any] = {
    "device_id": "unknown",
    "den_khach": "unknown",
    "den_ngu": "unknown",
    "quat_khach": "unknown",
    "quat_ngu": "unknown",
    "light": "unknown",
    "fan": "unknown",
    "temperature_c": None,
    "humidity": None,
    "distance_cm": None,
    "distance_alert": None,
    "distance_light": "unknown",
    "gas_detected": None,
    "buzzer": "unknown",
    "rain_detected": None,
    "door": "unknown",
    "timestamp": 0,
}


def _backend_url(path: str) -> str:
    return "{}/{}".format(BACKEND_BASE_URL.rstrip("/"), path.lstrip("/"))


def _backend_get_json(path: str) -> Tuple[int, Dict[str, Any]]:
    req = urllib_request.Request(_backend_url(path), method="GET")
    try:
        with urllib_request.urlopen(req, timeout=8) as resp:
            body = resp.read().decode("utf-8")
            return int(resp.status), json.loads(body)
    except HTTPError as exc:
        body = exc.read().decode("utf-8") if exc.fp else ""
        try:
            data = json.loads(body) if body else {"detail": str(exc)}
        except json.JSONDecodeError:
            data = {"detail": body or str(exc)}
        return int(exc.code), data
    except (URLError, TimeoutError) as exc:
        return 502, {"detail": "Backend unavailable: {}".format(exc)}

def _backend_post_json(path: str, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib_request.Request(
        _backend_url(path),
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib_request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode("utf-8")
            return int(resp.status), json.loads(raw) if raw else {}
    except HTTPError as exc:
        raw = exc.read().decode("utf-8") if exc.fp else ""
        try:
            data = json.loads(raw) if raw else {"detail": str(exc)}
        except json.JSONDecodeError:
            data = {"detail": raw or str(exc)}
        return int(exc.code), data
    except (URLError, TimeoutError) as exc:
        return 502, {"detail": "Backend unavailable: {}".format(exc)}


@app.route("/")
def index():
    return render_template("index.html", backend_base_url=BACKEND_BASE_URL)


@app.route("/api/command", methods=["POST"])
def api_command():
    data = request.get_json(silent=True) or {}
    command = str(data.get("command", "")).strip().lower()
    if command in {"on", "off", "toggle"}:
        command = "light {}".format(command)

    if command not in {
        "den khach on",
        "den khach off",
        "den khach toggle",
        "den ngu on",
        "den ngu off",
        "den ngu toggle",
        "quat khach on",
        "quat khach off",
        "quat khach weak",
        "quat khach strong",
        "quat khach toggle",
        "quat ngu on",
        "quat ngu off",
        "quat ngu weak",
        "quat ngu strong",
        "quat ngu toggle",
        "light on",
        "light off",
        "light toggle",
        "fan on",
        "fan off",
        "fan toggle",
        "buzzer on",
        "buzzer off",
        "buzzer toggle",
        "door open",
        "door close",
        "all on",
        "all off",
        "status",
    }:
        return jsonify({"error": "Invalid command"}), 400

    status_code, payload = _backend_post_json("/iot/command", {"command": command})
    return jsonify(payload), status_code


@app.route("/api/status")
def api_status():
    status_code, payload = _backend_get_json("/iot/status")
    if status_code != 200:
        merged = dict(DEFAULT_STATUS)
        merged["error"] = payload.get("detail", "backend error")
        return jsonify(merged), status_code
    merged = dict(DEFAULT_STATUS)
    merged.update(payload)
    return jsonify(merged)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, use_reloader=False)
