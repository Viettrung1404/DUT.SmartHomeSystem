from app.agent.command_parser import parse_device_command


def test_activity_duration_question_is_not_command():
    assert parse_device_command("Thiết bị nào hoạt động lâu nhất hôm qua?") is None


def test_turn_off_ac_command_still_parses():
    command = parse_device_command("Tắt điều hòa")

    assert command is not None
    assert command.action == "turn_off"
    assert command.device_type_hint == "ac"


def test_close_door_command_still_parses():
    command = parse_device_command("Đóng cửa chính")

    assert command is not None
    assert command.action == "close"
    assert command.device_type_hint == "lock"
