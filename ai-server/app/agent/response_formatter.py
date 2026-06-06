from typing import Any


SEVERITY_ORDER = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def collect_evidence(tool_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for result in tool_results:
        tool_name = result["tool_name"]
        for item in result["items"][:10]:
            compact = {"type": tool_name}
            for key in [
                "id",
                "event_type",
                "severity",
                "description",
                "timestamp",
                "created_at",
                "device_slug",
                "device_name",
                "device_type",
                "room_name",
                "event_type",
                "duration_seconds",
                "suggestion_text",
                "pattern_type",
                "confidence",
                "is_online",
                "state",
                "last_updated",
            ]:
                if key in item:
                    compact[key] = item[key]
            evidence.append(compact)
    return evidence


def max_severity(evidence: list[dict[str, Any]]) -> str:
    current = "none"
    for item in evidence:
        severity = str(item.get("severity", "none")).lower()
        if SEVERITY_ORDER.get(severity, 0) > SEVERITY_ORDER[current]:
            current = severity
    return current


def fallback_answer(intent: str, evidence: list[dict[str, Any]]) -> tuple[str, list[str]]:
    if not evidence:
        return "Mình chưa tìm thấy dữ liệu phù hợp trong hệ thống để trả lời câu này.", []

    if intent == "GUARDIAN_EVENT_QUERY":
        first = evidence[0]
        severity = first.get("severity", "không rõ")
        description = first.get("description") or first.get("event_type", "sự kiện an ninh")
        timestamp = first.get("timestamp", "không rõ thời gian")
        return (
            f"Mình tìm thấy {len(evidence)} bằng chứng liên quan. Đáng chú ý nhất: {description}, "
            f"mức {severity}, thời điểm {timestamp}.",
            ["Kiểm tra lịch sử thiết bị", "Kiểm tra camera hoặc trạng thái khóa nếu có"],
        )

    if intent == "SUGGESTION_EXPLAIN":
        suggestion = next((item for item in evidence if item.get("suggestion_text")), evidence[0])
        text = suggestion.get("suggestion_text", "gợi ý gần đây")
        device = suggestion.get("device_name")
        device_part = f" cho {device}" if device else ""
        return f"Hệ thống tạo gợi ý{device_part} dựa trên dữ liệu đã ghi nhận: {text}", []

    if intent in {"DEVICE_HISTORY", "FOLLOW_UP"}:
        logs = [item for item in evidence if item.get("type") == "query_activity_logs"]
        total_seconds = sum(int(item.get("duration_seconds") or 0) for item in logs)
        if total_seconds:
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"Mình tìm thấy {len(logs)} log hoạt động, tổng thời gian khoảng {hours} giờ {minutes} phút.", []
        return f"Mình tìm thấy {len(logs)} log hoạt động liên quan trong khoảng thời gian này.", []

    if intent == "FORGOT_OFF_QUERY":
        return f"Mình tìm thấy {len(evidence)} bằng chứng liên quan tới thói quen hoặc sự kiện quên tắt thiết bị.", []

    if intent == "DEVICE_STATUS_QUERY":
        online = sum(1 for item in evidence if item.get("is_online"))
        return f"Mình tìm thấy {len(evidence)} thiết bị phù hợp, trong đó {online} thiết bị đang online.", []

    return "Mình đã tìm thấy một số dữ liệu liên quan trong hệ thống, bạn có thể hỏi cụ thể hơn theo thiết bị hoặc thời gian.", []
