TOOL_MAP = {
    "GUARDIAN_EVENT_QUERY": ["query_guardian_events", "query_suggestion_logs", "query_user_patterns"],
    "SUGGESTION_EXPLAIN": ["query_suggestion_logs", "query_user_patterns"],
    "DEVICE_HISTORY": ["query_activity_logs"],
    "FORGOT_OFF_QUERY": ["query_user_patterns", "query_activity_logs"],
    "DEVICE_STATUS_QUERY": ["query_device_status"],
    "DEVICE_COMMAND": ["query_device_status"],
    "FOLLOW_UP": ["query_activity_logs"],
    "GENERAL_SMART_HOME_QUERY": ["query_device_status"],
}


def select_tools(intent: str) -> list[str]:
    return TOOL_MAP.get(intent, ["query_device_status"])
