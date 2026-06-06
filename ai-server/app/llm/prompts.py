import json
from typing import Any


SYSTEM_PROMPT = """Bạn là AI Smart Home Guardian Assistant.
Chỉ trả lời dựa trên TOOL_RESULTS và MEMORY_CONTEXT.
Không được tự bịa thời gian, tên thiết bị, số lần, nguyên nhân hoặc trạng thái.
Nếu dữ liệu không đủ, nói rõ là chưa đủ dữ liệu.
Trả lời bằng tiếng Việt, ngắn gọn, dễ hiểu.
Output phải là JSON hợp lệ với các key: answer, severity, suggested_actions, evidence_summary."""


def build_user_prompt(message: str, memory_context: dict[str, Any] | None, tool_results: list[dict[str, Any]]) -> str:
    return "\n".join([
        "USER_QUESTION:",
        message,
        "",
        "MEMORY_CONTEXT:",
        json.dumps(memory_context or {}, ensure_ascii=False, default=str),
        "",
        "TOOL_RESULTS:",
        json.dumps(tool_results, ensure_ascii=False, default=str),
    ])

