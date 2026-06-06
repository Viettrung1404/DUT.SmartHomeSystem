from app.agent.intent_router import classify_intent


def test_guardian_intent_with_time_range():
    result = classify_intent("Toi qua nha toi co gi bat thuong khong?")
    assert result.intent == "GUARDIAN_EVENT_QUERY"
    assert result.time_range == "last_night"


def test_suggestion_explain_intent():
    result = classify_intent("Tai sao app goi y tat den bep?")
    assert result.intent == "SUGGESTION_EXPLAIN"
    assert result.device_hint == "den bep"


def test_device_history_intent():
    result = classify_intent("Dieu hoa phong ngu tuan nay chay may lan?")
    assert result.intent == "DEVICE_HISTORY"
    assert result.device_hint == "dieu hoa phong ngu"
    assert result.time_range == "this_week"


def test_forgot_off_intent():
    result = classify_intent("Thiet bi nao hay bi quen tat nhat?")
    assert result.intent == "FORGOT_OFF_QUERY"


def test_follow_up_needs_memory():
    result = classify_intent("The tuan nay thi sao?")
    assert result.intent == "FOLLOW_UP"
    assert result.needs_memory is True
    assert result.time_range == "this_week"


def test_device_command_intent():
    result = classify_intent("Tat den bep")
    assert result.intent == "DEVICE_COMMAND"
