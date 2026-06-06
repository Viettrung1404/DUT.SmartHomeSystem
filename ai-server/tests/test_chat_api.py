from fastapi.testclient import TestClient

from app.main import app
from app.memory.memory_store import memory_store


def _payload(message="Toi qua nha toi co gi bat thuong khong?"):
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
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(tool_name=kwargs.get("tool_name", args[1]), result_count=0, items=[]),
    )
    monkeypatch.setattr(agent_module, "generate_answer", lambda *args, **kwargs: {"answer": "should not be used"})

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
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name=kwargs.get("tool_name", args[1]),
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
    monkeypatch.setattr(
        agent_module,
        "execute_tool",
        lambda *args, **kwargs: ToolResult(
            tool_name=kwargs.get("tool_name", args[1]),
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

    response = TestClient(app).post("/v1/chat", json=_payload("Tai sao app goi y tat den bep?"))

    assert response.status_code == 200
    assert response.json()["suggested_actions"] == ["Xem lại automation đèn bếp"]


def test_chat_device_command_returns_command(monkeypatch):
    from app.agent import agent as agent_module
    from app.schemas.tool_schema import ToolResult

    monkeypatch.setattr(agent_module, "SessionLocal", lambda: DummySession())
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
