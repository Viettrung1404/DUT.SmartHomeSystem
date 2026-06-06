from app.agent.tool_router import select_tools


def test_guardian_tools():
    assert select_tools("GUARDIAN_EVENT_QUERY") == [
        "query_guardian_events",
        "query_suggestion_logs",
        "query_user_patterns",
    ]


def test_device_history_tools():
    assert select_tools("DEVICE_HISTORY") == ["query_activity_logs"]


def test_unknown_intent_defaults_to_status():
    assert select_tools("UNKNOWN") == ["query_device_status"]

