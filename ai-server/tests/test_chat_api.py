from fastapi.testclient import TestClient

from app.main import app
from app.memory.memory_store import memory_store


def _payload(message="Tối qua nhà tôi có gì bất thường không?"):
    return {
        "session_id": "test-session",
        "user_id": "11111111-1111-1111-1111-111111111111",
        "home_id": "22222222-2222-2222-2222-222222222222",
        "message": message,
        "timezone": "Asia/Ho_Chi_Minh",
    }


class DummySession:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_chat_no_evidence_uses_fallback(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(tool_name=args[1], result_count=0, items=[]),
    )
    monkeypatch.setattr(agent_module, "generate_answer", lambda *args, **kwargs: None)

    response = TestClient(app).post("/v1/chat", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "GUARDIAN_EVENT_QUERY"
    assert body["evidence"] == []
    assert body["severity"] == "none"
    assert "chưa tìm thấy dữ liệu" in body["answer"].lower()


def test_chat_with_evidence_calls_llm(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name=args[1],
            result_count=1,
            items=[{"severity": "high", "description": "Door opened"}],
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "generate_answer",
        lambda *args, **kwargs: {
            "answer": "Có cảnh báo cửa mở.",
            "severity": "high",
            "suggested_actions": ["Kiểm tra cửa"],
        },
    )

    response = TestClient(app).post("/v1/chat", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Có cảnh báo cửa mở."
    assert body["severity"] == "high"
    assert body["suggested_actions"] == ["Kiểm tra cửa"]
    assert body["evidence"]


def test_chat_sanitizes_llm_action_objects(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name=args[1],
            result_count=1,
            items=[{"suggestion_text": "Tắt đèn bếp sau 30 phút"}],
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "generate_answer",
        lambda *args, **kwargs: {
            "answer": "Có gợi ý dựa trên lịch sử.",
            "severity": "none",
            "suggested_actions": [{"description": "Xem lại automation đèn bếp"}],
        },
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Tại sao app gợi ý tắt đèn bếp?"))

    assert response.status_code == 200
    assert response.json()["suggested_actions"] == ["Xem lại automation đèn bếp"]


def test_chat_device_command_returns_command(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name="query_device_status",
            result_count=1,
            items=[
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "device_slug": "en_bep",
                    "device_name": "Den bep",
                    "device_type": "LIGHT",
                    "room_name": "Bep",
                    "is_online": True,
                    "state": {"power": "ON"},
                }
            ],
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Tat den bep"))

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "DEVICE_COMMAND"
    assert body["device_command"]["device_id"] == "33333333-3333-3333-3333-333333333333"
    assert body["device_command"]["command"] == "turn_off"


def test_chat_light_command_locks_parser_hint_when_llm_suggests_ac(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    tool_hints = []

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        agent_module,
        "decide_next_tool_with_llm",
        lambda *args, **kwargs: AgentDecision(
            action="call_tool",
            intent="DEVICE_COMMAND",
            tool_call=PlannedToolCall(
                name="query_device_status",
                device_hint="dieu hoa phong khach",
                query="dieu hoa phong khach",
            ),
        ),
    )

    def fake_execute_tool(*args, **kwargs):
        tool_hints.append(kwargs.get("device_hint"))
        return ToolResult(
            tool_name="query_device_status",
            result_count=2,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "dieu_hoa_lg_dual_cool",
                    "device_name": "Dieu hoa LG Dual Cool",
                    "device_type": "AC",
                    "room_name": "Phong khach",
                    "state": {"power": "OFF"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "den_tran_phong_khach",
                    "device_name": "Den tran phong khach",
                    "device_type": "LIGHT",
                    "room_name": "Phong khach",
                    "state": {"power": "OFF"},
                },
            ],
        )

    monkeypatch.setattr(agent_module, "execute_tool", fake_execute_tool)

    response = TestClient(app).post("/v1/chat", json=_payload("Bat den phong khach"))

    assert response.status_code == 200
    body = response.json()
    assert tool_hints == ["den phong khach"]
    assert body["device_command"]["device_id"] == "22222222-2222-2222-2222-222222222222"
    assert body["device_command"]["device_type"] == "LIGHT"


def test_chat_short_command_uses_last_device_from_memory(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    calls: list[str | None] = []

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())

    def fake_decide(message, *args, **kwargs):
        if message == "Tat di":
            return AgentDecision(
                action="call_tool",
                intent="DEVICE_COMMAND",
                tool_call=PlannedToolCall(name="query_device_status", device_hint="dieu hoa", query="dieu hoa"),
            )
        return None

    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", fake_decide)

    def fake_execute_tool(*args, **kwargs):
        calls.append(kwargs.get("device_hint"))
        return ToolResult(
            tool_name="query_device_status",
            result_count=2,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "ieu_hoa_panasonic",
                    "device_name": "Dieu hoa Panasonic",
                    "device_type": "AC",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "en_tran_phong_khach",
                    "device_name": "Den tran phong khach",
                    "device_type": "LIGHT",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
            ],
        )

    monkeypatch.setattr(agent_module, "execute_tool", fake_execute_tool)

    client = TestClient(app)
    session_payload = _payload("Bat den phong khach")
    session_payload["session_id"] = "short-command-memory"

    first = client.post("/v1/chat", json=session_payload)
    assert first.status_code == 200
    assert first.json()["device_command"]["device_id"] == "22222222-2222-2222-2222-222222222222"

    session_payload["message"] = "Tat di"
    second = client.post("/v1/chat", json=session_payload)

    assert second.status_code == 200
    body = second.json()
    assert body["intent"] == "DEVICE_COMMAND"
    assert body["device_command"]["device_id"] == "22222222-2222-2222-2222-222222222222"
    assert body["device_command"]["command"] == "turn_off"
    assert calls == ["den phong khach", "en_tran_phong_khach"]


def test_chat_multi_device_command_returns_multiple_commands(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    tool_hints: list[str | None] = []

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        agent_module,
        "decide_next_tool_with_llm",
        lambda *args, **kwargs: AgentDecision(
            action="call_tool",
            intent="DEVICE_COMMAND",
            tool_call=PlannedToolCall(name="query_device_status", device_hint="khoa cua", query="khoa cua"),
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: (
            tool_hints.append(kwargs.get("device_hint"))
            or ToolResult(
                tool_name="query_device_status",
                result_count=3,
                items=[
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "device_slug": "khoa_cua_smart_lock",
                        "device_name": "Khoa cua Smart Lock",
                        "device_type": "LOCK",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "OFF"},
                    },
                    {
                        "id": "22222222-2222-2222-2222-222222222222",
                        "device_slug": "quat_phong_khach",
                        "device_name": "Quat phong khach",
                        "device_type": "FAN",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "OFF"},
                    },
                    {
                        "id": "33333333-3333-3333-3333-333333333333",
                        "device_slug": "den_phong_khach",
                        "device_name": "Den phong khach",
                        "device_type": "LIGHT",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "OFF"},
                    },
                ],
            )
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Bat quat phong khach va bat den phong khach"))

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "DEVICE_COMMAND"
    assert body["device_command"] is None
    assert [command["device_id"] for command in body["device_commands"]] == [
        "22222222-2222-2222-2222-222222222222",
        "33333333-3333-3333-3333-333333333333",
    ]
    assert [command["command"] for command in body["device_commands"]] == ["turn_on", "turn_on"]
    assert tool_hints == [None]


def test_chat_multi_device_command_uses_full_tool_rows_not_compact_evidence(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    filler = [
        {
            "id": f"00000000-0000-0000-0000-00000000000{i}",
            "device_slug": f"other_lock_{i}",
            "device_name": f"Other Lock {i}",
            "device_type": "LOCK",
            "room_name": "Phong khach",
            "is_online": True,
            "state": {"power": "OFF"},
        }
        for i in range(8)
    ]

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        agent_module,
        "decide_next_tool_with_llm",
        lambda *args, **kwargs: AgentDecision(
            action="call_tool",
            intent="DEVICE_COMMAND",
            tool_call=PlannedToolCall(name="query_device_status"),
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name="query_device_status",
            result_count=12,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "khoa_cua_smart_lock",
                    "device_name": "Khoa cua Smart Lock",
                    "device_type": "LOCK",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "quat_phong_khach",
                    "device_name": "Quat phong khach",
                    "device_type": "FAN",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
                *filler,
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "device_slug": "den_phong_khach",
                    "device_name": "Den phong khach",
                    "device_type": "LIGHT",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
            ],
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Bat quat phong khach va bat den phong khach"))

    assert response.status_code == 200
    body = response.json()
    assert [command["device_id"] for command in body["device_commands"]] == [
        "22222222-2222-2222-2222-222222222222",
        "33333333-3333-3333-3333-333333333333",
    ]


def test_chat_generic_multi_light_command_uses_previous_multi_device_memory(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name="query_device_status",
            result_count=3,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "den_tran_phong_khach",
                    "device_name": "Den tran phong khach",
                    "device_type": "LIGHT",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "den_led_phong_ngu",
                    "device_name": "Den LED phong ngu",
                    "device_type": "LIGHT",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "device_slug": "quat_phong_khach",
                    "device_name": "Quat phong khach",
                    "device_type": "FAN",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
            ],
        ),
    )

    client = TestClient(app)
    payload = _payload("Bat 2 den phong khach va phong ngu")
    payload["session_id"] = "multi-light-memory"

    first = client.post("/v1/chat", json=payload)
    assert first.status_code == 200
    assert [command["device_id"] for command in first.json()["device_commands"]] == [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]

    payload["message"] = "Tat 2 den"
    second = client.post("/v1/chat", json=payload)

    assert second.status_code == 200
    body = second.json()
    assert [command["device_id"] for command in body["device_commands"]] == [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]
    assert [command["command"] for command in body["device_commands"]] == ["turn_off", "turn_off"]


def test_chat_all_devices_command_expands_safe_controllable_devices(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    tool_hints: list[str | None] = []

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        agent_module,
        "decide_next_tool_with_llm",
        lambda *args, **kwargs: AgentDecision(
            action="call_tool",
            intent="DEVICE_COMMAND",
            tool_call=PlannedToolCall(name="query_device_status", device_hint="khoa cua"),
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: (
            tool_hints.append(kwargs.get("device_hint"))
            or ToolResult(
                tool_name="query_device_status",
                result_count=5,
                items=[
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "device_slug": "den_phong_khach",
                        "device_name": "Den phong khach",
                        "device_type": "LIGHT",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "OFF"},
                    },
                    {
                        "id": "22222222-2222-2222-2222-222222222222",
                        "device_slug": "quat_phong_khach",
                        "device_name": "Quat phong khach",
                        "device_type": "FAN",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "OFF"},
                    },
                    {
                        "id": "33333333-3333-3333-3333-333333333333",
                        "device_slug": "ac_phong_khach",
                        "device_name": "Dieu hoa phong khach",
                        "device_type": "AC",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "OFF"},
                    },
                    {
                        "id": "44444444-4444-4444-4444-444444444444",
                        "device_slug": "khoa_cua",
                        "device_name": "Khoa cua",
                        "device_type": "LOCK",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "OFF"},
                    },
                    {
                        "id": "55555555-5555-5555-5555-555555555555",
                        "device_slug": "cam_bien",
                        "device_name": "Cam bien",
                        "device_type": "SENSOR",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {},
                    },
                ],
            )
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Bat het tat ca cac thiet bi"))

    assert response.status_code == 200
    body = response.json()
    assert [command["device_id"] for command in body["device_commands"]] == [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
        "33333333-3333-3333-3333-333333333333",
    ]
    assert [command["command"] for command in body["device_commands"]] == ["turn_on", "turn_on", "turn_on"]
    assert tool_hints == [None]


def test_chat_all_devices_in_room_command_filters_room(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name="query_device_status",
            result_count=4,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "den_phong_ngu",
                    "device_name": "Den phong ngu",
                    "device_type": "LIGHT",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "quat_phong_ngu",
                    "device_name": "Quat phong ngu",
                    "device_type": "FAN",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "device_slug": "ac_phong_ngu",
                    "device_name": "Dieu hoa phong ngu",
                    "device_type": "AC",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
                {
                    "id": "44444444-4444-4444-4444-444444444444",
                    "device_slug": "den_phong_khach",
                    "device_name": "Den phong khach",
                    "device_type": "LIGHT",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
            ],
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Tat het tat ca thiet bi trong phong ngu"))

    assert response.status_code == 200
    body = response.json()
    assert [command["device_id"] for command in body["device_commands"]] == [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
        "33333333-3333-3333-3333-333333333333",
    ]
    assert [command["command"] for command in body["device_commands"]] == ["turn_off", "turn_off", "turn_off"]


def test_chat_all_devices_outside_room_command_excludes_room(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    tool_hints: list[str | None] = []

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        agent_module,
        "decide_next_tool_with_llm",
        lambda *args, **kwargs: AgentDecision(
            action="call_tool",
            intent="DEVICE_COMMAND",
            tool_call=PlannedToolCall(name="query_device_status", device_hint="phong ngu"),
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: (
            tool_hints.append(kwargs.get("device_hint"))
            or ToolResult(
                tool_name="query_device_status",
                result_count=6,
                items=[
                    {
                        "id": "11111111-1111-1111-1111-111111111111",
                        "device_slug": "den_phong_ngu",
                        "device_name": "Den phong ngu",
                        "device_type": "LIGHT",
                        "room_name": "Phong ngu",
                        "is_online": True,
                        "state": {"power": "ON"},
                    },
                    {
                        "id": "22222222-2222-2222-2222-222222222222",
                        "device_slug": "quat_phong_ngu",
                        "device_name": "Quat phong ngu",
                        "device_type": "FAN",
                        "room_name": "Phong ngu",
                        "is_online": True,
                        "state": {"power": "ON"},
                    },
                    {
                        "id": "33333333-3333-3333-3333-333333333333",
                        "device_slug": "den_phong_khach",
                        "device_name": "Den phong khach",
                        "device_type": "LIGHT",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "ON"},
                    },
                    {
                        "id": "44444444-4444-4444-4444-444444444444",
                        "device_slug": "quat_bep",
                        "device_name": "Quat bep",
                        "device_type": "FAN",
                        "room_name": "Bep",
                        "is_online": True,
                        "state": {"power": "ON"},
                    },
                    {
                        "id": "55555555-5555-5555-5555-555555555555",
                        "device_slug": "khoa_cua",
                        "device_name": "Khoa cua",
                        "device_type": "LOCK",
                        "room_name": "Phong khach",
                        "is_online": True,
                        "state": {"power": "ON"},
                    },
                    {
                        "id": "66666666-6666-6666-6666-666666666666",
                        "device_slug": "cam_bien",
                        "device_name": "Cam bien",
                        "device_type": "SENSOR",
                        "room_name": "Bep",
                        "is_online": True,
                        "state": {},
                    },
                ],
            )
        ),
    )

    response = TestClient(app).post(
        "/v1/chat",
        json=_payload("Tat nhung thiet bi ngoai nhung thiet bi trong phong ngu"),
    )

    assert response.status_code == 200
    body = response.json()
    assert [command["device_id"] for command in body["device_commands"]] == [
        "33333333-3333-3333-3333-333333333333",
        "44444444-4444-4444-4444-444444444444",
    ]
    assert [command["command"] for command in body["device_commands"]] == ["turn_off", "turn_off"]
    assert tool_hints == [None]


def test_chat_ac_command_does_not_pick_light(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name="query_device_status",
            result_count=2,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "en_led_phong_ngu",
                    "device_name": "Den LED phong ngu",
                    "device_type": "LIGHT",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "ieu_hoa_panasonic",
                    "device_name": "Dieu hoa Panasonic",
                    "device_type": "AC",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
            ],
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Tat dieu hoa"))

    assert response.status_code == 200
    body = response.json()
    assert body["device_command"]["device_id"] == "22222222-2222-2222-2222-222222222222"
    assert body["device_command"]["device_type"] == "AC"


def test_chat_accented_ac_command_does_not_pick_light(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name="query_device_status",
            result_count=2,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "en_led_phong_ngu",
                    "device_name": "Den LED phong ngu",
                    "device_type": "LIGHT",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "ieu_hoa_panasonic",
                    "device_name": "Dieu hoa Panasonic",
                    "device_type": "AC",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "ON"},
                },
            ],
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Tắt điều hòa"))

    assert response.status_code == 200
    body = response.json()
    assert body["device_command"]["device_id"] == "22222222-2222-2222-2222-222222222222"
    assert body["device_command"]["device_type"] == "AC"


def test_chat_activity_duration_question_does_not_execute_command(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    executed_tools: list[str] = []
    tool_time_ranges: list[str | None] = []

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        agent_module,
        "decide_next_tool_with_llm",
        lambda *args, **kwargs: AgentDecision(
            action="call_tool",
            intent="DEVICE_HISTORY",
            tool_call=PlannedToolCall(name="query_activity_logs", time_range="last_night"),
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: (
            executed_tools.append(args[1])
            or tool_time_ranges.append(kwargs.get("time_range"))
            or ToolResult(
                tool_name="query_activity_logs",
                result_count=1,
                items=[
                    {
                        "device_slug": "fan_living",
                        "device_name": "Quạt phòng khách",
                        "device_type": "FAN",
                        "room_name": "Phòng khách",
                        "duration_seconds": 10800,
                    }
                ],
            )
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "generate_answer",
        lambda *args, **kwargs: {
            "answer": "Hôm qua quạt phòng khách hoạt động lâu nhất.",
            "severity": "none",
            "suggested_actions": [],
        },
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Thiết bị nào hoạt động lâu nhất hôm qua?"))

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "DEVICE_HISTORY"
    assert body["device_command"] is None
    assert executed_tools == ["query_activity_logs"]
    assert tool_time_ranges == ["yesterday"]
    assert "3 giờ" in body["answer"]


def test_chat_uses_llm_agent_tool_call(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    executed_tools: list[str] = []
    calls = 0

    def decide(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            return AgentDecision(
                action="call_tool",
                intent="DEVICE_STATUS_QUERY",
                tool_call=PlannedToolCall(name="query_device_status", device_hint="den bep"),
            )
        return AgentDecision(action="final", intent="DEVICE_STATUS_QUERY", answer="Đã đủ dữ liệu.")

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", decide)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: (
            executed_tools.append(args[1])
            or ToolResult(tool_name=args[1], result_count=0, items=[])
        ),
    )
    monkeypatch.setattr(agent_module, "generate_answer", lambda *args, **kwargs: None)

    response = TestClient(app).post("/v1/chat", json=_payload("Kiểm tra đèn bếp"))

    assert response.status_code == 200
    assert response.json()["intent"] == "DEVICE_STATUS_QUERY"
    assert executed_tools == ["query_device_status"]


def test_chat_rejects_bad_llm_tool_for_suggestion(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    executed_tools: list[str] = []
    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(
        agent_module,
        "decide_next_tool_with_llm",
        lambda *args, **kwargs: AgentDecision(
            action="call_tool",
            intent="GENERAL_SMART_HOME_QUERY",
            tool_call=PlannedToolCall(name="query_device_status"),
        ),
    )
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: (
            executed_tools.append(args[1])
            or ToolResult(tool_name=args[1], result_count=0, items=[])
        ),
    )
    monkeypatch.setattr(agent_module, "generate_answer", lambda *args, **kwargs: None)

    response = TestClient(app).post("/v1/chat", json=_payload("Tại sao app gợi ý tắt đèn bếp?"))

    assert response.status_code == 200
    assert response.json()["intent"] == "SUGGESTION_EXPLAIN"
    assert executed_tools == ["query_suggestion_logs", "query_user_patterns"]


def test_chat_repairs_rejected_llm_tool_with_feedback(monkeypatch):
    from app.agent import agent as agent_module
    from app.agent.tool_planner import AgentDecision, PlannedToolCall
    from app.schemas.tool_schema import ToolResult

    executed_tools: list[str] = []
    feedback_values: list[str | None] = []

    def decide(*args, **kwargs):
        feedback_values.append(kwargs.get("feedback"))
        if len(feedback_values) == 1:
            return AgentDecision(
                action="call_tool",
                intent="DEVICE_HISTORY",
                tool_call=PlannedToolCall(name="query_activity_logs"),
            )
        return AgentDecision(
            action="call_tool",
            intent="SUGGESTION_EXPLAIN",
            tool_call=PlannedToolCall(name="query_suggestion_logs", device_hint="den bep"),
        )

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", decide)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: (
            executed_tools.append(args[1])
            or ToolResult(tool_name=args[1], result_count=0, items=[])
        ),
    )
    monkeypatch.setattr(agent_module, "generate_answer", lambda *args, **kwargs: None)

    response = TestClient(app).post("/v1/chat", json=_payload("Tại sao app gợi ý tắt đèn bếp?"))

    assert response.status_code == 200
    assert response.json()["intent"] == "SUGGESTION_EXPLAIN"
    assert executed_tools == ["query_suggestion_logs"]
    assert feedback_values[0] is None
    assert "Expected intent SUGGESTION_EXPLAIN" in feedback_values[1]


def test_reset_memory_endpoint():
    memory_store.reset("reset-session", "u1")
    response = TestClient(app).post("/v1/chat/reset", json={"session_id": "reset-session", "user_id": "u1"})
    assert response.status_code == 200
    assert response.json() == {"success": True}


def test_missing_message_returns_422():
    payload = _payload()
    payload.pop("message")
    response = TestClient(app).post("/v1/chat", json=payload)
    assert response.status_code == 422


def test_chat_target_count_returns_multiple_commands(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
    monkeypatch.setattr(agent_module, "decide_next_tool_with_llm", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name="query_device_status",
            result_count=3,
            items=[
                {
                    "id": "11111111-1111-1111-1111-111111111111",
                    "device_slug": "quat_tran_assa",
                    "device_name": "Quat tran ASSA",
                    "device_type": "FAN",
                    "room_name": "Phong khach",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
                {
                    "id": "22222222-2222-2222-2222-222222222222",
                    "device_slug": "quat_thong_gio",
                    "device_name": "Quat thong gio",
                    "device_type": "FAN",
                    "room_name": "Nha tam",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
                {
                    "id": "33333333-3333-3333-3333-333333333333",
                    "device_slug": "quat_ung_xiaomi",
                    "device_name": "Quat dung Xiaomi",
                    "device_type": "FAN",
                    "room_name": "Phong ngu",
                    "is_online": True,
                    "state": {"power": "OFF"},
                },
            ],
        ),
    )

    response = TestClient(app).post("/v1/chat", json=_payload("Bat 2 cai quat"))

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "DEVICE_COMMAND"
    assert body["device_command"] is None
    assert len(body["device_commands"]) == 2
    assert [command["device_id"] for command in body["device_commands"]] == [
        "11111111-1111-1111-1111-111111111111",
        "22222222-2222-2222-2222-222222222222",
    ]
