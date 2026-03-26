from fastapi import HTTPException

class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Could not validate user"):
        super().__init__(status_code=401, detail=message)


class ForbiddenError(HTTPException):
    def __init__(self, message: str = "Access denied"):
        super().__init__(status_code=403, detail=message)


# --- Smart Home Errors ---

class HomeNotFoundError(HTTPException):
    def __init__(self, home_id=None):
        msg = "Không tìm thấy nhà" if home_id is None else f"Không tìm thấy nhà với id {home_id}"
        super().__init__(status_code=404, detail=msg)


class RoomNotFoundError(HTTPException):
    def __init__(self, room_id=None):
        msg = "Không tìm thấy phòng" if room_id is None else f"Không tìm thấy phòng với id {room_id}"
        super().__init__(status_code=404, detail=msg)


class DeviceNotFoundError(HTTPException):
    def __init__(self, device_id=None):
        msg = "Không tìm thấy thiết bị" if device_id is None else f"Không tìm thấy thiết bị với id {device_id}"
        super().__init__(status_code=404, detail=msg)


class DeviceOfflineError(HTTPException):
    def __init__(self, device_id=None):
        msg = "Thiết bị đang ngoại tuyến"
        super().__init__(status_code=503, detail=msg)


class AutomationNotFoundError(HTTPException):
    def __init__(self, automation_id=None):
        msg = "Không tìm thấy automation" if automation_id is None else f"Không tìm thấy automation với id {automation_id}"
        super().__init__(status_code=404, detail=msg)


class UserNotFoundError(HTTPException):
    def __init__(self, user_id=None):
        msg = "Không tìm thấy người dùng" if user_id is None else f"Không tìm thấy người dùng với id {user_id}"
        super().__init__(status_code=404, detail=msg)
