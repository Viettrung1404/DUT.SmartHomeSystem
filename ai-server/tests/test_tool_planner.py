from app.agent.tool_planner import _parse_agent_decision, _parse_json_object, _parse_plan, fallback_plan


def test_parse_valid_llm_tool_plan():
    plan = _parse_plan({
        "intent": "SUGGESTION_EXPLAIN",
        "tool_calls": [
            {"name": "query_suggestion_logs", "args": {"device_hint": "den bep"}},
            {"name": "query_user_patterns", "args": {"device_hint": "den bep"}},
        ],
    })

    assert plan is not None
    assert plan.intent == "SUGGESTION_EXPLAIN"
    assert [call.name for call in plan.tool_calls] == ["query_suggestion_logs", "query_user_patterns"]
    assert plan.tool_calls[0].device_hint == "den bep"


def test_parse_rejects_unknown_tools():
    plan = _parse_plan({
        "intent": "DEVICE_HISTORY",
        "tool_calls": [
            {"name": "run_sql", "args": {"query": "select * from users"}},
        ],
    })

    assert plan is None


def test_parse_rejects_unknown_intent():
    plan = _parse_plan({
        "intent": "DROP_DATABASE",
        "tool_calls": [{"name": "query_device_status", "args": {}}],
    })

    assert plan is None


def test_fallback_plan_marks_source():
    plan = fallback_plan("DEVICE_STATUS_QUERY", ["query_device_status"], None, "den")
    assert plan.source == "rule_fallback"
    assert plan.tool_calls[0].name == "query_device_status"
    assert plan.tool_calls[0].device_hint == "den"


def test_parse_agent_tool_decision():
    decision = _parse_agent_decision({
        "action": "call_tool",
        "intent": "DEVICE_HISTORY",
        "tool_call": {
            "name": "query_activity_logs",
            "args": {"time_range": "this_week", "device_hint": "điều hòa phòng ngủ"},
        },
    })

    assert decision is not None
    assert decision.action == "call_tool"
    assert decision.intent == "DEVICE_HISTORY"
    assert decision.tool_call.name == "query_activity_logs"
    assert decision.tool_call.time_range == "this_week"
    assert decision.tool_call.device_hint == "điều hòa phòng ngủ"


def test_parse_agent_final_decision():
    decision = _parse_agent_decision({
        "action": "final",
        "intent": "GUARDIAN_EVENT_QUERY",
        "answer": "Đã đủ dữ liệu.",
    })

    assert decision is not None
    assert decision.action == "final"
    assert decision.answer == "Đã đủ dữ liệu."


def test_parse_agent_rejects_unknown_tool():
    decision = _parse_agent_decision({
        "action": "call_tool",
        "intent": "DEVICE_HISTORY",
        "tool_call": {"name": "run_sql", "args": {}},
    })

    assert decision is None


def test_parse_json_object_extracts_wrapped_json():
    parsed = _parse_json_object(
        'Here is JSON:\n{"action":"final","intent":"DEVICE_HISTORY","answer":"ok"}\n'
    )

    assert parsed == {"action": "final", "intent": "DEVICE_HISTORY", "answer": "ok"}
