# IoT Tools

## mqtt_command_test.py

Send MQTT commands to a device topic.

Syntax:

python tools/mqtt_command_test.py <device_id> <command> [--value <value>] [--raw]

Notes:
- Default payload is JSON: {"command": "...", "value": ...}
- Use --raw to send raw string without JSON wrapper.
- MQTT config is read from environment variables.

Examples

Light (on/off/toggle):
- python tools/mqtt_command_test.py fee0abdc-ba55-4593-89e4-0bb127a14659 on
- python tools/mqtt_command_test.py 11111111-1111-1111-1111-111111111111 off
- python tools/mqtt_command_test.py 11111111-1111-1111-1111-111111111111 toggle

Fan (room device id):
- python tools/mqtt_command_test.py 33333333-3333-3333-3333-333333333333 strong
- python tools/mqtt_command_test.py 33333333-3333-3333-3333-333333333333 weak
- python tools/mqtt_command_test.py 33333333-3333-3333-3333-333333333333 off
- python tools/mqtt_command_test.py 33333333-3333-3333-3333-333333333333 set_speed --value strong

Door:
- python tools/mqtt_command_test.py 55555555-5555-5555-5555-555555555555 open
- python tools/mqtt_command_test.py 55555555-5555-5555-5555-555555555555 close

Buzzer:
- python tools/mqtt_command_test.py 66666666-6666-6666-6666-666666666666 on
- python tools/mqtt_command_test.py 66666666-6666-6666-6666-666666666666 off
- python tools/mqtt_command_test.py 66666666-6666-6666-6666-666666666666 toggle

Distance light:
- python tools/mqtt_command_test.py 77777777-7777-7777-7777-777777777777 on
- python tools/mqtt_command_test.py 77777777-7777-7777-7777-777777777777 off
- python tools/mqtt_command_test.py 77777777-7777-7777-7777-777777777777 toggle

Rain servo:
- python tools/mqtt_command_test.py cccccccc-cccc-cccc-cccc-cccccccccccc open
- python tools/mqtt_command_test.py cccccccc-cccc-cccc-cccc-cccccccccccc close
- python tools/mqtt_command_test.py cccccccc-cccc-cccc-cccc-cccccccccccc set_position --value wet
- python tools/mqtt_command_test.py cccccccc-cccc-cccc-cccc-cccccccccccc set_position --value dry
- python tools/mqtt_command_test.py cccccccc-cccc-cccc-cccc-cccccccccccc set_angle --value 120

Raw payload (legacy style):
- python tools/mqtt_command_test.py 55555555-5555-5555-5555-555555555555 "door open" --raw
