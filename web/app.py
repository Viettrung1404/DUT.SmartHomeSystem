import json
import os
import logging
from functools import wraps
from typing import Any, Dict, Tuple
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from urllib.parse import quote

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

WEB_PORT = int(os.getenv("WEB_PORT", "8001"))
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")

app = Flask(__name__)
app.secret_key = os.getenv("WEB_SECRET_KEY", "dev-web-secret-change-me")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("WEB_SECURE_COOKIE", "false").lower() == "true"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SESSION_ACCESS_TOKEN = "access_token"
SESSION_REFRESH_TOKEN = "refresh_token"
SESSION_USER = "user"
SESSION_HOME_ID = "active_home_id"

DEFAULT_STATUS: Dict[str, Any] = {
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


def _backend_get_json(path: str, access_token: str | None = None) -> Tuple[int, Any]:
    headers: Dict[str, str] = {}
    if access_token:
        headers["Authorization"] = "Bearer {}".format(access_token)
    req = urllib_request.Request(_backend_url(path), method="GET", headers=headers)
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


def _backend_post_json(
    path: str,
    payload: Dict[str, Any],
    access_token: str | None = None,
) -> Tuple[int, Any]:
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if access_token:
        headers["Authorization"] = "Bearer {}".format(access_token)
    req = urllib_request.Request(
        _backend_url(path),
        data=body,
        method="POST",
        headers=headers,
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


def _is_authenticated() -> bool:
    return bool(session.get(SESSION_ACCESS_TOKEN) and session.get(SESSION_REFRESH_TOKEN))


def _current_user() -> Dict[str, Any] | None:
    user = session.get(SESSION_USER)
    if isinstance(user, dict):
        return user
    return None


def _is_admin() -> bool:
    """Check if current user is an admin."""
    user = _current_user()
    return user and isinstance(user, dict) and user.get("is_admin", False)


def _set_auth_session(access_token: str, refresh_token: str, user: Dict[str, Any]) -> None:
    session[SESSION_ACCESS_TOKEN] = access_token
    session[SESSION_REFRESH_TOKEN] = refresh_token
    session[SESSION_USER] = user


def _clear_auth_session() -> None:
    session.pop(SESSION_ACCESS_TOKEN, None)
    session.pop(SESSION_REFRESH_TOKEN, None)
    session.pop(SESSION_USER, None)
    session.pop(SESSION_HOME_ID, None)


def _refresh_access_token() -> bool:
    refresh_token = session.get(SESSION_REFRESH_TOKEN)
    if not refresh_token:
        return False
    status_code, payload = _backend_post_json("/auth/refresh", {"refresh_token": refresh_token})
    if status_code != 200:
        return False

    new_access = payload.get("access_token")
    new_refresh = payload.get("refresh_token")
    if not new_access or not new_refresh:
        return False

    session[SESSION_ACCESS_TOKEN] = new_access
    session[SESSION_REFRESH_TOKEN] = new_refresh
    return True


def _authed_backend_get(path: str) -> Tuple[int, Any]:
    access_token = session.get(SESSION_ACCESS_TOKEN)
    if not access_token:
        return 401, {"detail": "Not authenticated"}

    status_code, payload = _backend_get_json(path, access_token=access_token)
    if status_code != 401:
        return status_code, payload

    if not _refresh_access_token():
        _clear_auth_session()
        return status_code, payload

    return _backend_get_json(path, access_token=session.get(SESSION_ACCESS_TOKEN))


def _authed_backend_post(path: str, payload: Dict[str, Any]) -> Tuple[int, Any]:
    access_token = session.get(SESSION_ACCESS_TOKEN)
    if not access_token:
        return 401, {"detail": "Not authenticated"}

    status_code, data = _backend_post_json(path, payload, access_token=access_token)
    if status_code != 401:
        return status_code, data

    if not _refresh_access_token():
        _clear_auth_session()
        return status_code, data

    return _backend_post_json(path, payload, access_token=session.get(SESSION_ACCESS_TOKEN))


def _extract_error(payload: Dict[str, Any], fallback: str) -> str:
    detail = payload.get("detail") if isinstance(payload, dict) else None
    if isinstance(detail, list):
        return "; ".join(str(item) for item in detail)
    if detail:
        return str(detail)
    message = payload.get("error") if isinstance(payload, dict) else None
    if message:
        return str(message)
    return fallback


def _get_user_homes() -> list[Dict[str, Any]]:
    status_code, payload = _authed_backend_get("/homes/")
    if status_code != 200 or not isinstance(payload, list):
        return []
    return [home for home in payload if isinstance(home, dict)]


def _resolve_home_id() -> str | None:
    homes = _get_user_homes()
    if not homes:
        session.pop(SESSION_HOME_ID, None)
        return None

    saved_home_id = session.get(SESSION_HOME_ID)
    if isinstance(saved_home_id, str):
        for home in homes:
            if isinstance(home, dict) and home.get("id") == saved_home_id:
                return saved_home_id
    session.pop(SESSION_HOME_ID, None)
    return None


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not _is_authenticated():
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


def api_login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not _is_authenticated():
            return jsonify({"detail": "Authentication required"}), 401
        return view_func(*args, **kwargs)

    return wrapped


def admin_required(view_func):
    """Require user to be logged in and be an admin."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not _is_authenticated():
            return redirect(url_for("login"))
        if not _is_admin():
            return render_template("error.html", error="Access Denied", message="You do not have permission to access this page."), 403
        return view_func(*args, **kwargs)

    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if _is_authenticated():
        return redirect(url_for("select_home"))

    error = None
    email = ""
    if request.method == "POST":
        email = str(request.form.get("email", "")).strip()
        password = str(request.form.get("password", "")).strip()

        if not email or not password:
            error = "Vui long nhap day du email va mat khau"
        else:
            status_code, token_payload = _backend_post_json(
                "/auth/login",
                {"email": email, "password": password},
            )
            if status_code != 200:
                error = _extract_error(token_payload, "Dang nhap that bai")
            else:
                access_token = token_payload.get("access_token")
                refresh_token = token_payload.get("refresh_token")
                if not access_token or not refresh_token:
                    error = "Phan hoi token khong hop le"
                else:
                    user_status, user_payload = _backend_get_json(
                        "/auth/me",
                        access_token=access_token,
                    )
                    if user_status != 200:
                        error = _extract_error(user_payload, "Khong the tai thong tin nguoi dung")
                    else:
                        _set_auth_session(access_token, refresh_token, user_payload)
                        session.pop(SESSION_HOME_ID, None)
                        return redirect(url_for("select_home"))

    return render_template("login.html", error=error, email=email)


@app.route("/register", methods=["GET", "POST"])
def register():
    if _is_authenticated():
        return redirect(url_for("select_home"))

    error = None
    form_data = {"full_name": "", "email": ""}
    if request.method == "POST":
        full_name = str(request.form.get("full_name", "")).strip()
        email = str(request.form.get("email", "")).strip()
        password = str(request.form.get("password", "")).strip()
        form_data = {"full_name": full_name, "email": email}

        if not full_name or not email or not password:
            error = "Vui long nhap day du ho ten, email va mat khau"
        else:
            register_code, register_payload = _backend_post_json(
                "/auth/register",
                {"full_name": full_name, "email": email, "password": password},
            )
            if register_code not in (200, 201):
                error = _extract_error(register_payload, "Dang ky that bai")
            else:
                login_code, token_payload = _backend_post_json(
                    "/auth/login",
                    {"email": email, "password": password},
                )
                if login_code != 200:
                    error = _extract_error(token_payload, "Dang ky thanh cong nhung dang nhap tu dong that bai")
                else:
                    access_token = token_payload.get("access_token")
                    refresh_token = token_payload.get("refresh_token")
                    if not access_token or not refresh_token:
                        error = "Phan hoi token khong hop le"
                    else:
                        user_code, user_payload = _backend_get_json(
                            "/auth/me",
                            access_token=access_token,
                        )
                        if user_code != 200:
                            error = _extract_error(user_payload, "Khong the tai thong tin nguoi dung")
                        else:
                            _set_auth_session(access_token, refresh_token, user_payload)
                            session.pop(SESSION_HOME_ID, None)
                            return redirect(url_for("select_home"))

    return render_template("register.html", error=error, form_data=form_data)


@app.route("/logout", methods=["POST"])
def logout():
    _clear_auth_session()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    user = _current_user() or {}
    homes = _get_user_homes()
    home_id = _resolve_home_id()
    if not home_id:
        return redirect(url_for("select_home", next="/"))

    active_home = next((home for home in homes if home.get("id") == home_id), None)
    return render_template(
        "index.html",
        backend_base_url=BACKEND_BASE_URL,
        home_id=home_id,
        current_user=user,
        home_missing=False,
        active_home=active_home,
    )


@app.route("/homes/select", methods=["GET"])
@login_required
def select_home():
    user = _current_user() or {}
    homes = _get_user_homes()
    selected_home_id = _resolve_home_id()
    return render_template(
        "home_select.html",
        current_user=user,
        homes=homes,
        selected_home_id=selected_home_id,
        error=None,
        next_url=request.args.get("next", "/"),
    )


@app.route("/homes/select", methods=["POST"])
@login_required
def set_active_home():
    selected_home_id = str(request.form.get("home_id", "")).strip()
    homes = _get_user_homes()
    valid_home_ids = {str(home.get("id")) for home in homes if home.get("id")}
    next_url = str(request.form.get("next", "/")).strip() or "/"

    if not selected_home_id or selected_home_id not in valid_home_ids:
        return render_template(
            "home_select.html",
            current_user=_current_user() or {},
            homes=homes,
            selected_home_id=_resolve_home_id(),
            error="Nha duoc chon khong hop le.",
            next_url=next_url,
        ), 400

    session[SESSION_HOME_ID] = selected_home_id
    if not next_url.startswith("/"):
        next_url = "/"
    return redirect(next_url)


@app.route("/api/command", methods=["POST"])
@api_login_required
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

    home_id = _resolve_home_id()
    if not home_id:
        return jsonify({"detail": "No home found for current user. Please create a home first."}), 400

    logger.debug("/api/command request: home_id=%s command=%s", home_id, command)
    status_code, payload = _authed_backend_post(
        "/iot/command",
        {"command": command, "home_id": home_id},
    )
    logger.debug("/api/command response: status=%s payload=%s", status_code, payload)
    if status_code == 401:
        _clear_auth_session()
    return jsonify(payload), status_code


@app.route("/api/status")
@api_login_required
def api_status():
    home_id = _resolve_home_id()
    if not home_id:
        merged = dict(DEFAULT_STATUS)
        merged["error"] = "No home found for current user. Please create a home first."
        return jsonify(merged), 400

    q = "home_id={}".format(quote(home_id, safe=""))
    logger.debug("/api/status request: home_id=%s", home_id)
    status_code, payload = _authed_backend_get("/iot/status?{}".format(q))
    logger.debug("/api/status response: status=%s payload=%s", status_code, payload)
    if status_code == 401:
        _clear_auth_session()
        return jsonify({"detail": "Authentication required"}), 401
    if status_code != 200:
        merged = dict(DEFAULT_STATUS)
        merged["error"] = payload.get("detail", "backend error")
        return jsonify(merged), status_code
    merged = dict(DEFAULT_STATUS)
    merged.update(payload)
    return jsonify(merged)


@app.route("/api/face/enroll-batch", methods=["POST"])
@api_login_required
def api_face_enroll_batch():
    data = request.get_json(silent=True) or {}
    person_id = str(data.get("person_id", "")).strip()
    incoming_home_id = str(data.get("home_id", "")).strip()
    images_base64 = data.get("images_base64")

    if not person_id:
        return jsonify({"detail": "person_id is required"}), 400
    if not isinstance(images_base64, list):
        return jsonify({"detail": "images_base64 must be an array of base64 strings"}), 400
    if len(images_base64) != 5:
        return jsonify({"detail": "Please upload exactly 5 images"}), 400
    if not all(isinstance(item, str) and item.strip() for item in images_base64):
        return jsonify({"detail": "Each image in images_base64 must be a non-empty string"}), 400

    home_id = incoming_home_id or _resolve_home_id()
    if not home_id:
        return jsonify({"detail": "No home found for current user. Please create a home first."}), 400

    payload = {
        "home_id": home_id,
        "person_id": person_id,
        "images_base64": images_base64,
    }
    status_code, response_payload = _authed_backend_post("/face/enroll-batch", payload)
    if status_code == 401:
        _clear_auth_session()
    return jsonify(response_payload), status_code


# ==================== ADMIN ROUTES ====================

@app.route("/admin")
@admin_required
def admin_dashboard():
    """Admin dashboard - show stats and links."""
    user = _current_user() or {}
    
    # Get stats
    homes_status, homes_data = _authed_backend_get("/homes/")
    homes = homes_data if homes_status == 200 and isinstance(homes_data, list) else []
    
    stats = {
        "total_homes": len(homes),
        "total_devices": sum(h.get("device_count", 0) for h in homes if isinstance(h, dict)),
        "total_active_devices": sum(h.get("active_devices", 0) for h in homes if isinstance(h, dict)),
    }
    
    return render_template(
        "admin_dashboard.html",
        current_user=user,
        stats=stats,
        backend_base_url=BACKEND_BASE_URL,
    )


@app.route("/admin/homes")
@admin_required
def admin_homes():
    """Admin homes list - view all homes and create new ones."""
    user = _current_user() or {}
    error = None
    
    # Get all homes
    homes_status, homes_data = _authed_backend_get("/homes/")
    homes = homes_data if homes_status == 200 and isinstance(homes_data, list) else []
    
    return render_template(
        "admin_homes.html",
        current_user=user,
        homes=homes,
        error=error,
        backend_base_url=BACKEND_BASE_URL,
    )


@app.route("/admin/homes", methods=["POST"])
@admin_required
def admin_create_home():
    """Create a new home."""
    user = _current_user() or {}
    name = str(request.form.get("name", "")).strip()
    address = str(request.form.get("address", "")).strip()
    
    error = None
    if not name:
        error = "Home name is required"
    else:
        status_code, payload = _authed_backend_post("/homes/", {
            "name": name,
            "address": address or None,
        })
        
        if status_code not in (200, 201):
            error = _extract_error(payload, "Failed to create home")
        else:
            return redirect(url_for("admin_homes"))
    
    homes_status, homes_data = _authed_backend_get("/homes/")
    homes = homes_data if homes_status == 200 and isinstance(homes_data, list) else []
    
    return render_template(
        "admin_homes.html",
        current_user=user,
        homes=homes,
        error=error,
        backend_base_url=BACKEND_BASE_URL,
    )


@app.route("/admin/homes/<home_id>")
@admin_required
def admin_home_detail(home_id: str):
    """View home details and manage devices."""
    user = _current_user() or {}
    
    # Get home details
    home_status, home_data = _authed_backend_get(f"/homes/{home_id}")
    if home_status != 200:
        error = _extract_error(home_data, "Home not found")
        return render_template("error.html", error="Error", message=error), 404
    
    home = home_data if isinstance(home_data, dict) else {}
    devices_status, devices_data = _authed_backend_get(f"/devices/?home_id={quote(home_id, safe='')}")
    devices = devices_data if devices_status == 200 and isinstance(devices_data, list) else []
    
    return render_template(
        "admin_home_detail.html",
        current_user=user,
        home=home,
        devices=devices,
        backend_base_url=BACKEND_BASE_URL,
    )


@app.route("/admin/devices", methods=["POST"])
@admin_required
def admin_create_device():
    """Create a new device in a home."""
    user = _current_user() or {}
    data = request.get_json(silent=True) or {}
    
    home_id = str(data.get("home_id", "")).strip()
    name = str(data.get("name", "")).strip()
    device_type = str(data.get("type", "")).strip()
    location = str(data.get("location", "")).strip() or None
    mqtt_home_key = str(data.get("mqtt_home_key", "")).strip() or None
    mqtt_device_key = str(data.get("mqtt_device_key", "")).strip() or None
    
    if not all([home_id, name, device_type]):
        return jsonify({"detail": "home_id, name, and type are required"}), 400

    metadata = {}
    if mqtt_home_key:
        metadata["mqtt_home_key"] = mqtt_home_key
    if mqtt_device_key:
        metadata["mqtt_device_key"] = mqtt_device_key
    
    status_code, payload = _authed_backend_post("/devices/", {
        "home_id": home_id,
        "name": name,
        "type": device_type,
        "location": location,
        "metadata": metadata
    })
    
    if status_code not in (200, 201):
        error = _extract_error(payload, "Failed to create device")
        return jsonify({"detail": error}), status_code
    
    return jsonify(payload), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=WEB_PORT, debug=False, use_reloader=False)
