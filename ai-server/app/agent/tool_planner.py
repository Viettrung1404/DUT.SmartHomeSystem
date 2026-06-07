import json
import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import get_settings


logger = logging.getLogger("ai_server.tool_planner")

ALLOWED_TOOLS = {
    "search_smart_home_records",
    "query_guardian_events",
    "query_suggestion_logs",
    "query_user_patterns",
    "query_activity_logs",
    "query_device_status",
}

ALLOWED_INTENTS = {
    "GUARDIAN_EVENT_QUERY",
    "SUGGESTION_EXPLAIN",
    "DEVICE_HISTORY",
    "FORGOT_OFF_QUERY",
    "DEVICE_STATUS_QUERY",
    "DEVICE_COMMAND",
    "GENERAL_SMART_HOME_QUERY",
}

ALLOWED_TIME_RANGES = {"last_night", "yesterday", "today", "this_week", "last_week"}
ALLOWED_SEARCH_DOMAINS = {"alerts", "suggestions", "activity", "devices", "patterns"}

AGENT_DECISION_SYSTEM_PROMPT = """Bạn là Smart Home AI agent.
Mỗi bước bạn được tự quyết:
1. Gọi đúng một tool để thu thập thêm dữ liệu.
2. Hoặc dừng nếu dữ liệu đã đủ.

Bạn chỉ được dùng tool trong allowed_tools. Không tự tạo tool, home_id, user_id, SQL hay dữ liệu giả.
Tất cả tool đều đã được hệ thống scope theo home_id/user_id hiện tại.

Tool đọc dữ liệu:
- search_smart_home_records: tìm rộng trên DB smart home chuẩn khi không chắc dữ liệu nằm ở bảng nào. Input domains gồm alerts, suggestions, activity, devices, patterns.
- query_guardian_events: cảnh báo/an ninh/bất thường trong security_events.
- query_suggestion_logs: gợi ý/cảnh báo từ suggestion engine.
- query_user_patterns: thói quen, pattern, hay quên tắt.
- query_activity_logs: lịch sử thiết bị, chạy bao lâu, mấy lần.
- query_device_status: trạng thái hiện tại và danh sách thiết bị, bắt buộc trước lệnh điều khiển.

Few-shot examples:
- User: "Tại sao app gợi ý tắt đèn bếp?"
  JSON: {"action":"call_tool","intent":"SUGGESTION_EXPLAIN","tool_call":{"name":"query_suggestion_logs","args":{"time_range":null,"device_hint":"đèn bếp","query":"đèn bếp","domains":null}}}
- User: "Tại sao lại có cảnh báo Dining Room?"
  JSON: {"action":"call_tool","intent":"GUARDIAN_EVENT_QUERY","tool_call":{"name":"search_smart_home_records","args":{"time_range":null,"device_hint":"Dining Room","query":"cảnh báo Dining Room","domains":["alerts","suggestions"]}}}
- User: "Tối qua nhà tôi có gì bất thường không?"
  JSON: {"action":"call_tool","intent":"GUARDIAN_EVENT_QUERY","tool_call":{"name":"query_guardian_events","args":{"time_range":"last_night","device_hint":null,"query":null,"domains":null}}}
- Nếu query_guardian_events trả 0 kết quả cho câu bất thường:
  JSON: {"action":"call_tool","intent":"GUARDIAN_EVENT_QUERY","tool_call":{"name":"search_smart_home_records","args":{"time_range":"last_night","device_hint":null,"query":"bất thường cảnh báo","domains":["alerts","suggestions"]}}}
- User: "Điều hòa phòng ngủ tuần này chạy nhiều không?"
  JSON: {"action":"call_tool","intent":"DEVICE_HISTORY","tool_call":{"name":"query_activity_logs","args":{"time_range":"this_week","device_hint":"điều hòa phòng ngủ","query":"điều hòa phòng ngủ","domains":null}}}
- User: "Tắt điều hòa"
  JSON: {"action":"call_tool","intent":"DEVICE_COMMAND","tool_call":{"name":"query_device_status","args":{"time_range":null,"device_hint":"điều hòa","query":"điều hòa","domains":null}}}

Không tự thêm time_range nếu user không nhắc thời gian. Nếu user không hỏi "tối qua/hôm qua/tuần này/tuần trước/hôm nay", đặt time_range là null.
Nếu tool vừa gọi trả 0 kết quả, đừng gọi lại y hệt. Hãy thử search_smart_home_records với domain liên quan hoặc trả final nếu đã đủ kết luận.
Nếu feedback nói JSON sai hoặc tool/intent bị reject, hãy sửa theo feedback và thử lại.
Nếu câu hỏi là lệnh điều khiển thiết bị, bước đầu tiên phải gọi query_device_status với device_hint tốt nhất.
Output chỉ là JSON theo một trong hai dạng:
{"action":"call_tool","intent":"DEVICE_HISTORY","tool_call":{"name":"search_smart_home_records","args":{"time_range":"this_week","device_hint":"điều hòa","query":"điều hòa chạy nhiều","domains":["activity","devices"]}}}
{"action":"final","intent":"DEVICE_HISTORY","answer":"Đã đủ dữ liệu để trả lời."}"""

REPAIR_SYSTEM_PROMPT = """Bạn là JSON repair assistant.
Nhiệm vụ: sửa output trước đó thành đúng JSON schema của Smart Home agent.
Chỉ trả JSON hợp lệ, không thêm giải thích, không markdown.
Không tự tạo tool hoặc intent ngoài danh sách cho phép."""


@dataclass(frozen=True)
class PlannedToolCall:
    name: str
    time_range: str | None = None
    device_hint: str | None = None
    query: str | None = None
    domains: list[str] | None = None


@dataclass(frozen=True)
class ToolPlan:
    intent: str
    tool_calls: list[PlannedToolCall]
    source: str = "llm"


@dataclass(frozen=True)
class AgentDecision:
    action: str
    intent: str
    tool_call: PlannedToolCall | None = None
    answer: str | None = None
    source: str = "llm"


def _clean_string(value: Any, max_len: int = 120) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if not cleaned or cleaned.lower() in {"null", "none"}:
        return None
    return cleaned[:max_len]


def _clean_domains(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    domains = [item for item in value if isinstance(item, str) and item in ALLOWED_SEARCH_DOMAINS]
    deduped = list(dict.fromkeys(domains))
    return deduped[:5] or None


def _parse_json_object(content: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(content)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(content[start : end + 1])
                return parsed if isinstance(parsed, dict) else None
            except json.JSONDecodeError:
                return None
        return None


def _parse_plan(raw: Any) -> ToolPlan | None:
    if not isinstance(raw, dict):
        return None

    intent = raw.get("intent")
    if intent not in ALLOWED_INTENTS:
        return None

    calls: list[PlannedToolCall] = []
    for item in raw.get("tool_calls", []):
        if not isinstance(item, dict):
            continue
        call = _parse_tool_call(item)
        if call:
            calls.append(call)

    deduped: list[PlannedToolCall] = []
    seen: set[tuple] = set()
    for call in calls:
        key = (call.name, call.time_range, call.device_hint, call.query, tuple(call.domains or []))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(call)

    if not deduped:
        return None
    return ToolPlan(intent=intent, tool_calls=deduped[:4])


def _parse_tool_call(raw: dict[str, Any]) -> PlannedToolCall | None:
    name = raw.get("name")
    if name not in ALLOWED_TOOLS:
        return None
    args = raw.get("args") if isinstance(raw.get("args"), dict) else {}
    time_range = _clean_string(args.get("time_range"))
    if time_range not in ALLOWED_TIME_RANGES:
        time_range = None
    return PlannedToolCall(
        name=name,
        time_range=time_range,
        device_hint=_clean_string(args.get("device_hint")),
        query=_clean_string(args.get("query")),
        domains=_clean_domains(args.get("domains")),
    )


def _parse_agent_decision(raw: Any) -> AgentDecision | None:
    if not isinstance(raw, dict):
        return None

    action = raw.get("action")
    intent = raw.get("intent")
    if action not in {"call_tool", "final"} or intent not in ALLOWED_INTENTS:
        return None

    if action == "final":
        return AgentDecision(action="final", intent=intent, answer=_clean_string(raw.get("answer"), 500))

    tool_data = raw.get("tool_call")
    if not isinstance(tool_data, dict):
        return None
    call = _parse_tool_call(tool_data)
    if not call:
        return None
    return AgentDecision(action="call_tool", intent=intent, tool_call=call)


def _summarize_observations(tool_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observations: list[dict[str, Any]] = []
    for result in tool_results:
        items = result.get("items") if isinstance(result, dict) else []
        if not isinstance(items, list):
            items = []
        observations.append(
            {
                "tool_name": result.get("tool_name"),
                "result_count": result.get("result_count", len(items)),
                "sample_items": items[:3],
            }
        )
    return observations


def _agent_user_prompt(
    message: str,
    memory_context: dict[str, Any] | None,
    tool_results: list[dict[str, Any]],
    used_tool_calls: list[dict[str, Any]],
    max_steps: int,
    suggested_intent: str | None = None,
    feedback: str | None = None,
) -> str:
    return json.dumps(
        {
            "user_message": message,
            "suggested_intent": suggested_intent,
            "feedback": feedback,
            "memory_context": memory_context or {},
            "observations": _summarize_observations(tool_results),
            "used_tool_calls": used_tool_calls,
            "max_steps": max_steps,
            "allowed_tools": sorted(ALLOWED_TOOLS),
            "allowed_intents": sorted(ALLOWED_INTENTS),
            "allowed_time_ranges": sorted(ALLOWED_TIME_RANGES),
            "allowed_search_domains": sorted(ALLOWED_SEARCH_DOMAINS),
        },
        ensure_ascii=False,
        default=str,
    )


def _repair_user_prompt(original_content: str, error: str, original_prompt: str) -> str:
    return json.dumps(
        {
            "error": error,
            "previous_output": original_content[:4000],
            "original_task": original_prompt,
            "valid_schema_call_tool": {
                "action": "call_tool",
                "intent": "one allowed intent",
                "tool_call": {
                    "name": "one allowed tool",
                    "args": {
                        "time_range": "allowed time range or null",
                        "device_hint": "string or null",
                        "query": "string or null",
                        "domains": "array of allowed search domains or null",
                    },
                },
            },
            "valid_schema_final": {
                "action": "final",
                "intent": "one allowed intent",
                "answer": "short reason",
            },
            "allowed_tools": sorted(ALLOWED_TOOLS),
            "allowed_intents": sorted(ALLOWED_INTENTS),
            "allowed_time_ranges": sorted(ALLOWED_TIME_RANGES),
            "allowed_search_domains": sorted(ALLOWED_SEARCH_DOMAINS),
        },
        ensure_ascii=False,
        default=str,
    )


def _decision_from_content(content: str) -> tuple[AgentDecision | None, str]:
    parsed = _parse_json_object(content)
    if parsed is None:
        return None, "invalid_json"
    decision = _parse_agent_decision(parsed)
    if decision is None:
        return None, "invalid_schema"
    return decision, "ok"


def plan_tools_with_llm(message: str, memory_context: dict[str, Any] | None) -> ToolPlan | None:
    return ToolPlan(
        intent="GENERAL_SMART_HOME_QUERY",
        tool_calls=[PlannedToolCall(name="search_smart_home_records", query=message)],
    )


def decide_next_tool_with_llm(
    message: str,
    memory_context: dict[str, Any] | None,
    tool_results: list[dict[str, Any]],
    used_tool_calls: list[dict[str, Any]],
    max_steps: int = 4,
    suggested_intent: str | None = None,
    feedback: str | None = None,
) -> AgentDecision | None:
    settings = get_settings()
    user_prompt = _agent_user_prompt(
        message,
        memory_context,
        tool_results,
        used_tool_calls,
        max_steps,
        suggested_intent=suggested_intent,
        feedback=feedback,
    )
    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": AGENT_DECISION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    }
    try:
        with httpx.Client(timeout=min(settings.request_timeout_seconds, 30)) as client:
            response = client.post(f"{settings.ollama_url.rstrip('/')}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "{}")
            decision, error = _decision_from_content(content)
            if decision is None:
                logger.info("agent_planner.repair_start reason=%s", error)
                repair_payload = {
                    "model": settings.ollama_model,
                    "stream": False,
                    "format": "json",
                    "messages": [
                        {"role": "system", "content": REPAIR_SYSTEM_PROMPT},
                        {"role": "user", "content": _repair_user_prompt(content, error, user_prompt)},
                    ],
                }
                repair_response = client.post(f"{settings.ollama_url.rstrip('/')}/api/chat", json=repair_payload)
                repair_response.raise_for_status()
                repair_content = repair_response.json().get("message", {}).get("content", "{}")
                decision, error = _decision_from_content(repair_content)
                logger.info("agent_planner.repair_done success=%s reason=%s", decision is not None, error)

            logger.info(
                "agent_planner.done success=%s action=%s intent=%s tool=%s feedback=%s",
                decision is not None,
                decision.action if decision else None,
                decision.intent if decision else None,
                decision.tool_call.name if decision and decision.tool_call else None,
                bool(feedback),
            )
            return decision
    except Exception as exc:
        logger.warning("agent_planner.failed error=%s", exc)
        return None


def fallback_plan(intent: str, tools: list[str], time_range: str | None, device_hint: str | None) -> ToolPlan:
    return ToolPlan(
        intent=intent,
        tool_calls=[PlannedToolCall(name=tool, time_range=time_range, device_hint=device_hint) for tool in tools],
        source="rule_fallback",
    )
