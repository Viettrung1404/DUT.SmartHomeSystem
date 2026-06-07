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
