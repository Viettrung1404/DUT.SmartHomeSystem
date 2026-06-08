TOOL_MAP = {
    "GUARDIAN_EVENT_QUERY": ["search_smart_home_records"],
    "SUGGESTION_EXPLAIN": ["query_suggestion_logs", "query_user_patterns"],
    "DEVICE_HISTORY": ["query_activity_logs"],
    "FORGOT_OFF_QUERY": ["search_smart_home_records"],
    "DEVICE_STATUS_QUERY": ["query_device_status"],
    "DEVICE_COMMAND": ["query_device_status"],
    "FOLLOW_UP": ["search_smart_home_records"],
    "GENERAL_SMART_HOME_QUERY": ["search_smart_home_records"],
}


def select_tools(intent: str) -> list[str]:
    return TOOL_MAP.get(intent, ["search_smart_home_records"])
