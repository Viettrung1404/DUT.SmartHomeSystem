from app.agent.command_parser import parse_device_command, parse_device_commands


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


def test_multi_device_command_parses_each_segment():
    commands = parse_device_commands("Bật quạt phòng khách và bật đèn phòng khách")

    assert len(commands) == 2
    assert [command.action for command in commands] == ["turn_on", "turn_on"]
    assert [command.device_type_hint for command in commands] == ["fan", "light"]
    assert [command.device_hint for command in commands] == ["quat phong khach", "den phong khach"]


def test_multi_room_light_command_inherits_action_and_device_type():
    commands = parse_device_commands("Bat 2 den phong khach va phong ngu")

    assert len(commands) == 2
    assert [command.action for command in commands] == ["turn_on", "turn_on"]
    assert [command.device_type_hint for command in commands] == ["light", "light"]
    assert [command.device_hint for command in commands] == ["den phong khach", "den phong ngu"]


def test_all_devices_command_parses_group_scope():
    commands = parse_device_commands("Bat het tat ca cac thiet bi")

    assert len(commands) == 1
    assert commands[0].action == "turn_on"
    assert commands[0].target_all is True
    assert commands[0].device_hint is None
    assert commands[0].room_hint is None


def test_all_devices_in_room_command_parses_room_scope():
    commands = parse_device_commands("Tat het tat ca thiet bi trong phong ngu")

    assert len(commands) == 1
    assert commands[0].action == "turn_off"
    assert commands[0].target_all is True
    assert commands[0].room_hint == "phong ngu"


def test_all_devices_outside_room_command_parses_exclusion_scope():
    commands = parse_device_commands("Tat nhung thiet bi ngoai nhung thiet bi trong phong ngu")

    assert len(commands) == 1
    assert commands[0].action == "turn_off"
    assert commands[0].target_all is True
    assert commands[0].room_hint is None
    assert commands[0].exclude_room_hint == "phong ngu"
