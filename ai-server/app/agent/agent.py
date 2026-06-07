import logging
import re
import unicodedata
from uuid import uuid4

from app.agent.command_parser import parse_device_command
from app.agent.intent_router import classify_intent
from app.agent.response_formatter import collect_evidence, fallback_answer, max_severity
from app.agent.tool_planner import (
    AgentDecision,
    PlannedToolCall,
    decide_next_tool_with_llm,
    fallback_plan,
)
from app.agent.tool_router import select_tools
from app.db.session import SessionLocal
from app.llm.ollama_client import generate_answer
from app.memory.memory_store import MemoryContext, memory_store
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.tools.smart_home_tools import execute_tool


logger = logging.getLogger("ai_server.agent")

MAX_AGENT_STEPS = 4


def _string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            text = item.get("description") or item.get("action") or item.get("title") or item.get("text")
            if text:
                result.append(str(text))
        elif item is not None:
            result.append(str(item))
    return result


def _format_duration(total_seconds: int) -> str:
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    if hours and minutes:
        return f"{hours} giờ {minutes} phút"
    if hours:
        return f"{hours} giờ"
    if minutes:
        return f"{minutes} phút"
    return f"{total_seconds} giây"


def _normalize_text(value) -> str:
    text = str(value or "").lower().replace("đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


def _answer_longest_activity_question(message: str, evidence: list[dict], time_range: str | None) -> str | None:
    normalized = _normalize_text(message)
    if "lau nhat" not in normalized or "hoat dong" not in normalized:
        return None

    totals: dict[str, dict] = {}
    for item in evidence:
        seconds = int(item.get("duration_seconds") or 0)
        if seconds <= 0:
            continue
        key = str(item.get("device_slug") or item.get("device_name") or "unknown")
        bucket = totals.setdefault(
            key,
            {
                "device_name": item.get("device_name") or item.get("device_slug") or "thiết bị không rõ",
                "room_name": item.get("room_name"),
                "seconds": 0,
            },
        )
        bucket["seconds"] += seconds

    if not totals:
        return None

    winner = max(totals.values(), key=lambda item: item["seconds"])
    device_name = winner["device_name"]
    room_name = winner.get("room_name")
    room_part = f" ở {room_name}" if room_name and room_name not in str(device_name) else ""
    range_part = {
        "yesterday": "hôm qua",
        "last_night": "tối qua",
        "today": "hôm nay",
        "this_week": "tuần này",
        "last_week": "tuần trước",
    }.get(time_range, "trong khoảng dữ liệu đã kiểm tra")
    return f"{device_name}{room_part} hoạt động lâu nhất {range_part}, tổng khoảng {_format_duration(winner['seconds'])}."


def _is_controllable(item: dict) -> bool:
    device_type = _normalize_text(item.get("device_type"))
    return device_type in {"light", "fan", "ac", "lock"}


def _score_device(item: dict, hint: str | None) -> int:
    if not hint:
        return 1 if _is_controllable(item) else 0
    normalized_hint = _normalize_text(hint)
    haystack = " ".join(
        [
            _normalize_text(item.get("device_slug")),
            _normalize_text(item.get("device_name")),
            _normalize_text(item.get("room_name")),
            _normalize_text(item.get("device_type")),
        ]
    )
    score = 0
    for token in normalized_hint.split():
        if token in haystack:
            score += 2
    if normalized_hint in haystack:
        score += 4
    if "bep" in normalized_hint and "bep" in haystack:
        score += 3
    if "den" in normalized_hint and _normalize_text(item.get("device_type")) == "light":
        score += 3
    if "dieu hoa" in normalized_hint and _normalize_text(item.get("device_type")) == "ac":
        score += 3
    if "quat" in normalized_hint and _normalize_text(item.get("device_type")) == "fan":
        score += 3
    if ("khoa" in normalized_hint or "cua" in normalized_hint) and _normalize_text(item.get("device_type")) == "lock":
        score += 3
    return score


def _state_power(item: dict) -> str:
    state = item.get("state")
    if isinstance(state, dict):
        return str(state.get("power") or "").strip().upper()
    return ""


def _candidate_devices_for_command(items: list[dict], command) -> list[dict]:
    controllable = [item for item in items if _is_controllable(item)]
    expected_type = getattr(command, "device_type_hint", None)
    if expected_type:
        typed = [item for item in controllable if _normalize_text(item.get("device_type")) == expected_type]
        if typed:
            controllable = typed

    action = getattr(command, "action", None)
    if action == "turn_off":
        powered = [item for item in controllable if _state_power(item) == "ON"]
        if powered:
            controllable = powered
    elif action == "turn_on":
        powered = [item for item in controllable if _state_power(item) != "ON"]
        if powered:
            controllable = powered

    return controllable


def _resolve_command_for_device(action: str, item: dict) -> str:
    device_type = _normalize_text(item.get("device_type"))
    if device_type == "lock":
        if action in {"turn_on", "open", "unlock"}:
            return "unlock"
        if action in {"turn_off", "close", "lock"}:
            return "lock"
    if action in {"open", "unlock"}:
        return "turn_on"
    if action in {"close", "lock"}:
        return "turn_off"
    return action


def _tool_allowed_for_rule_intent(tool_name: str, rule_intent: str) -> bool:
    if rule_intent == "SUGGESTION_EXPLAIN":
        return tool_name in {"search_smart_home_records", "query_suggestion_logs", "query_user_patterns", "query_activity_logs"}
    if rule_intent == "GUARDIAN_EVENT_QUERY":
        return tool_name in {"search_smart_home_records", "query_guardian_events", "query_suggestion_logs", "query_user_patterns", "query_activity_logs"}
    if rule_intent == "DEVICE_HISTORY":
        return tool_name in {"search_smart_home_records", "query_activity_logs", "query_device_status", "query_user_patterns"}
    if rule_intent == "FORGOT_OFF_QUERY":
        return tool_name in {"search_smart_home_records", "query_user_patterns", "query_suggestion_logs", "query_activity_logs"}
    if rule_intent == "DEVICE_STATUS_QUERY":
        return tool_name in {"search_smart_home_records", "query_device_status"}
    if rule_intent == "DEVICE_COMMAND":
        return tool_name == "query_device_status"
    return True


def _decision_matches_rule_intent(decision: AgentDecision, rule_intent: str) -> bool:
    if rule_intent != "GENERAL_SMART_HOME_QUERY" and decision.intent != rule_intent:
        return False
    if decision.action == "final":
        return True
    if not decision.tool_call:
        return False
    return _tool_allowed_for_rule_intent(decision.tool_call.name, rule_intent)


def _rejection_feedback(decision: AgentDecision, rule_intent: str) -> str:
    tool_name = decision.tool_call.name if decision.tool_call else None
    allowed_tools = {
        "SUGGESTION_EXPLAIN": "query_suggestion_logs, query_user_patterns",
        "GUARDIAN_EVENT_QUERY": "search_smart_home_records, query_guardian_events, query_suggestion_logs, query_user_patterns",
        "DEVICE_HISTORY": "search_smart_home_records, query_activity_logs",
        "FORGOT_OFF_QUERY": "search_smart_home_records, query_user_patterns, query_suggestion_logs",
        "DEVICE_STATUS_QUERY": "search_smart_home_records, query_device_status",
        "DEVICE_COMMAND": "query_device_status",
    }.get(rule_intent, "allowed tools only")
    return (
        f"Rejected previous decision: intent/tool did not match the user question. "
        f"Expected intent {rule_intent}; previous intent was {decision.intent}; previous tool was {tool_name}. "
        f"Choose again using intent {rule_intent} and one of these tools: {allowed_tools}."
    )


def _duplicate_feedback(call: PlannedToolCall, rule_intent: str, tool_results: list[dict]) -> str:
    last_count = next(
        (
            result.get("result_count", 0)
            for result in reversed(tool_results)
            if result.get("tool_name") == call.name
        ),
        0,
    )
    intent_hint = ""
    if rule_intent == "GUARDIAN_EVENT_QUERY" and call.name == "query_guardian_events" and last_count == 0:
        intent_hint = " For an anomaly/security question with zero guardian events, try query_suggestion_logs with the same time_range next."
    elif rule_intent == "SUGGESTION_EXPLAIN" and call.name == "query_suggestion_logs":
        intent_hint = " For a suggestion explanation after suggestion logs, try query_user_patterns next."
    elif rule_intent == "DEVICE_COMMAND" and call.name == "query_device_status":
        intent_hint = " For a device command, do not call another tool after device status; return final."
    return (
        f"Rejected duplicate tool call: {call.name} with the same arguments was already used and returned {last_count} rows. "
        "Choose a different relevant tool, broaden the arguments, or return final; do not repeat the same call."
        f"{intent_hint}"
    )


def _tool_call_key(call: PlannedToolCall) -> tuple[str, str | None, str | None]:
    return (call.name, call.time_range, call.device_hint, call.query, tuple(call.domains or []))


def _sanitize_decision_time_range(decision: AgentDecision, explicit_time_range: str | None) -> AgentDecision:
    call = decision.tool_call
    if (
        explicit_time_range is not None
        and call is not None
        and call.time_range != explicit_time_range
    ):
        return AgentDecision(
            action=decision.action,
            intent=decision.intent,
            tool_call=PlannedToolCall(
                name=call.name,
                time_range=explicit_time_range,
                device_hint=call.device_hint,
                query=call.query,
                domains=call.domains,
            ),
            answer=decision.answer,
            source=decision.source,
        )
    if (
        explicit_time_range is None
        and call is not None
        and call.time_range is not None
    ):
        return AgentDecision(
            action=decision.action,
            intent=decision.intent,
            tool_call=PlannedToolCall(
                name=call.name,
                time_range=None,
                device_hint=call.device_hint,
                query=call.query,
                domains=call.domains,
            ),
            answer=decision.answer,
            source=decision.source,
        )
    return decision


def _should_stop_after_tool(intent: str, tool_name: str, result: dict, used_tool_calls: list[dict]) -> bool:
    result_count = int(result.get("result_count") or 0)
    used_tools = {call.get("name") for call in used_tool_calls}
    if intent == "DEVICE_COMMAND" and tool_name == "query_device_status":
        return True
    if intent == "SUGGESTION_EXPLAIN" and result_count > 0 and tool_name == "query_suggestion_logs":
        return True
    if tool_name == "search_smart_home_records" and result_count > 0:
        return True
    if intent == "DEVICE_HISTORY" and tool_name == "query_activity_logs":
        return True
    if intent == "DEVICE_STATUS_QUERY" and tool_name == "query_device_status":
        return True
    if intent == "FORGOT_OFF_QUERY" and result_count > 0:
        return True
    if intent == "GUARDIAN_EVENT_QUERY":
        if result_count > 0:
            return True
        return {"query_guardian_events", "query_suggestion_logs"}.issubset(used_tools)
    return False


class SmartHomeAgent:
    def handle(self, request: ChatRequest) -> ChatResponse:
        request_id = uuid4().hex[:12]
        intent_result = classify_intent(request.message)
        memory = memory_store.get(request.session_id, request.user_id)
        logger.info(
            "chat.start request_id=%s session_id=%s user_id=%s home_id=%s message_len=%s",
            request_id,
            request.session_id,
            request.user_id,
            request.home_id,
            len(request.message),
        )

        intent = intent_result.intent
        device_hint = intent_result.device_hint
        time_range = intent_result.time_range
        if intent == "FOLLOW_UP" and memory:
            intent = memory.last_intent or "DEVICE_HISTORY"
            device_hint = device_hint or memory.last_device_slug or memory.last_device_name
            time_range = time_range or memory.last_time_range
            logger.info(
                "chat.memory_applied request_id=%s last_intent=%s last_device=%s last_time_range=%s",
                request_id,
                memory.last_intent,
                memory.last_device_slug or memory.last_device_name,
                memory.last_time_range,
            )

        parsed_command_for_intent = parse_device_command(request.message)
        if parsed_command_for_intent:
            intent = "DEVICE_COMMAND"
            device_hint = parsed_command_for_intent.device_hint or device_hint
            time_range = None

        memory_context = memory.to_dict() if memory else None
        tool_results, agent_source, final_hint, intent, device_hint, time_range = self._run_agent_loop(
            request=request,
            request_id=request_id,
            rule_intent=intent,
            memory_context=memory_context,
            device_hint=device_hint,
            time_range=time_range,
        )

        logger.info(
            "chat.intent request_id=%s intent=%s planner_source=%s device_hint=%s time_range=%s needs_memory=%s memory_found=%s",
            request_id,
            intent,
            agent_source,
            device_hint,
            time_range,
            intent_result.needs_memory,
            memory is not None,
        )

        evidence = collect_evidence(tool_results)
        used_tools = [result["tool_name"] for result in tool_results]
        severity = max_severity(evidence)
        device_command = None
        logger.info(
            "chat.evidence request_id=%s evidence_count=%s severity=%s used_tools=%s",
            request_id,
            len(evidence),
            severity,
            ",".join(used_tools),
        )

        if intent == "DEVICE_COMMAND":
            return self._handle_device_command(
                request=request,
                request_id=request_id,
                evidence=evidence,
                used_tools=used_tools,
                severity=severity,
                device_hint=device_hint,
                time_range=time_range,
            )

        deterministic_answer = _answer_longest_activity_question(request.message, evidence, time_range) if intent == "DEVICE_HISTORY" else None
        llm_response = None
        if deterministic_answer:
            logger.info("llm.skip request_id=%s reason=deterministic_activity_answer", request_id)
        elif evidence:
            logger.info("llm.start request_id=%s model_input_tools=%s evidence_count=%s", request_id, len(tool_results), len(evidence))
            llm_response = generate_answer(
                request.message,
                memory.to_dict() if memory else None,
                tool_results,
            )
            logger.info("llm.done request_id=%s success=%s", request_id, llm_response is not None)
        elif tool_results:
            logger.info("llm.skip request_id=%s reason=no_evidence_after_agent", request_id)
        else:
            logger.info("llm.skip request_id=%s reason=no_tools")

        if llm_response:
            answer = str(llm_response["answer"])
            suggested_actions = _string_list(llm_response.get("suggested_actions"))
            severity = str(llm_response.get("severity") or severity).lower()
        elif deterministic_answer:
            answer = deterministic_answer
            suggested_actions = []
        elif final_hint:
            answer = final_hint
            suggested_actions = []
            logger.info("chat.final_hint request_id=%s reason=agent_final_no_llm", request_id)
        else:
            answer, suggested_actions = fallback_answer(intent, evidence)
            logger.info("chat.fallback request_id=%s reason=%s", request_id, "llm_unavailable_or_no_tools")

        updated = self._update_memory(request, intent, evidence, device_hint, time_range)
        logger.info(
            "chat.done request_id=%s intent=%s answer_len=%s memory_updated=%s",
            request_id,
            intent,
            len(answer),
            updated,
        )
        return ChatResponse(
            answer=answer,
            intent=intent,
            used_tools=used_tools,
            evidence=evidence,
            suggested_actions=suggested_actions,
            memory_updated=updated,
            severity=severity,
            device_command=device_command,
        )

    def _run_agent_loop(
        self,
        *,
        request: ChatRequest,
        request_id: str,
        rule_intent: str,
        memory_context: dict | None,
        device_hint: str | None,
        time_range: str | None,
    ) -> tuple[list[dict], str, str | None, str, str | None, str | None]:
        tool_results: list[dict] = []
        used_tool_calls: list[dict] = []
        seen_calls: set[tuple[str, str | None, str | None]] = set()
        agent_source = "llm"
        final_hint: str | None = None
        intent = rule_intent

        with SessionLocal() as db:
            for step in range(1, MAX_AGENT_STEPS + 1):
                decision = decide_next_tool_with_llm(
                    request.message,
                    memory_context,
                    tool_results,
                    used_tool_calls,
                    max_steps=MAX_AGENT_STEPS,
                    suggested_intent=rule_intent,
                )
                if decision is not None:
                    decision = _sanitize_decision_time_range(decision, time_range)
                if decision is not None and not _decision_matches_rule_intent(decision, rule_intent):
                    feedback = _rejection_feedback(decision, rule_intent)
                    logger.info(
                        "agent.step_rejected request_id=%s step=%s rule_intent=%s llm_intent=%s action=%s tool=%s",
                        request_id,
                        step,
                        rule_intent,
                        decision.intent,
                        decision.action,
                        decision.tool_call.name if decision.tool_call else None,
                    )
                    decision = decide_next_tool_with_llm(
                        request.message,
                        memory_context,
                        tool_results,
                        used_tool_calls,
                        max_steps=MAX_AGENT_STEPS,
                        suggested_intent=rule_intent,
                        feedback=feedback,
                    )
                    if decision is not None:
                        decision = _sanitize_decision_time_range(decision, time_range)
                    if decision is not None and not _decision_matches_rule_intent(decision, rule_intent):
                        logger.info(
                            "agent.step_rejected_after_feedback request_id=%s step=%s rule_intent=%s llm_intent=%s action=%s tool=%s",
                            request_id,
                            step,
                            rule_intent,
                            decision.intent,
                            decision.action,
                            decision.tool_call.name if decision.tool_call else None,
                        )
                        decision = None

                if decision is None:
                    if tool_results:
                        logger.info("agent.stop request_id=%s step=%s reason=planner_unavailable_after_observation", request_id, step)
                        break
                    agent_source = "rule_fallback"
                    fallback = fallback_plan(rule_intent, select_tools(rule_intent), time_range, device_hint)
                    logger.info(
                        "agent.fallback_plan request_id=%s tools=%s",
                        request_id,
                        ",".join(call.name for call in fallback.tool_calls),
                    )
                    for fallback_call in fallback.tool_calls:
                        result = self._execute_planned_tool(
                            db,
                            request,
                            request_id,
                            step,
                            fallback_call,
                            rule_intent,
                            agent_source,
                            time_range,
                            device_hint,
                        )
                        tool_results.append(result)
                    break

                intent = decision.intent
                if decision.action == "final":
                    final_hint = decision.answer
                    logger.info("agent.final request_id=%s step=%s intent=%s", request_id, step, intent)
                    break

                call = decision.tool_call
                if call is None:
                    logger.info("agent.stop request_id=%s step=%s reason=missing_tool_call", request_id, step)
                    break
                key = _tool_call_key(call)
                if key in seen_calls:
                    feedback = _duplicate_feedback(call, rule_intent, tool_results)
                    logger.info(
                        "agent.step_duplicate request_id=%s step=%s tool=%s retrying_with_feedback=true",
                        request_id,
                        step,
                        call.name,
                    )
                    decision = decide_next_tool_with_llm(
                        request.message,
                        memory_context,
                        tool_results,
                        used_tool_calls,
                        max_steps=MAX_AGENT_STEPS,
                        suggested_intent=rule_intent,
                        feedback=feedback,
                    )
                    if decision is not None:
                        decision = _sanitize_decision_time_range(decision, time_range)
                    if (
                        decision is None
                        or not _decision_matches_rule_intent(decision, rule_intent)
                        or decision.action != "call_tool"
                        or decision.tool_call is None
                        or _tool_call_key(decision.tool_call) in seen_calls
                    ):
                        logger.info(
                            "agent.stop request_id=%s step=%s reason=duplicate_tool tool=%s",
                            request_id,
                            step,
                            call.name,
                        )
                        break
                    intent = decision.intent
                    call = decision.tool_call
                    key = _tool_call_key(call)
                seen_calls.add(key)
                used_tool_calls.append(
                    {
                        "name": call.name,
                        "args": {
                            "time_range": call.time_range,
                            "device_hint": call.device_hint,
                            "query": call.query,
                            "domains": call.domains,
                        },
                    }
                )
                device_hint = call.device_hint or device_hint
                time_range = call.time_range or time_range
                result = self._execute_planned_tool(
                    db,
                    request,
                    request_id,
                    step,
                    call,
                    intent,
                    decision.source,
                    time_range,
                    device_hint,
                )
                tool_results.append(result)
                used_tool_names = {used_call.get("name") for used_call in used_tool_calls}
                if (
                    intent == "GUARDIAN_EVENT_QUERY"
                    and call.name == "query_guardian_events"
                    and int(result.get("result_count") or 0) == 0
                    and "search_smart_home_records" not in used_tool_names
                ):
                    followup_call = PlannedToolCall(
                        name="search_smart_home_records",
                        time_range=call.time_range or time_range,
                        device_hint=call.device_hint or device_hint,
                        query=call.query or call.device_hint or device_hint or "cảnh báo bất thường",
                        domains=["alerts", "suggestions"],
                    )
                    used_tool_calls.append(
                        {
                            "name": followup_call.name,
                            "args": {
                                "time_range": followup_call.time_range,
                                "device_hint": followup_call.device_hint,
                                "query": followup_call.query,
                                "domains": followup_call.domains,
                            },
                        }
                    )
                    seen_calls.add(_tool_call_key(followup_call))
                    followup_result = self._execute_planned_tool(
                        db,
                        request,
                        request_id,
                        step,
                        followup_call,
                        intent,
                        "agent_followup",
                        time_range,
                        device_hint,
                    )
                    tool_results.append(followup_result)
                    if _should_stop_after_tool(intent, followup_call.name, followup_result, used_tool_calls):
                        logger.info(
                            "agent.stop request_id=%s step=%s reason=guardian_followup_complete tool=%s result_count=%s",
                            request_id,
                            step,
                            followup_call.name,
                            followup_result.get("result_count"),
                        )
                        break
                if _should_stop_after_tool(intent, call.name, result, used_tool_calls):
                    logger.info(
                        "agent.stop request_id=%s step=%s reason=enough_evidence_or_action tool=%s result_count=%s",
                        request_id,
                        step,
                        call.name,
                        result.get("result_count"),
                    )
                    break

        return tool_results, agent_source, final_hint, intent, device_hint, time_range

    def _execute_planned_tool(
        self,
        db,
        request: ChatRequest,
        request_id: str,
        step: int,
        tool_call: PlannedToolCall,
        intent: str,
        source: str,
        time_range: str | None,
        device_hint: str | None,
    ) -> dict:
        logger.info(
            "agent.step request_id=%s step=%s action=call_tool tool=%s source=%s time_range=%s device_hint=%s",
            request_id,
            step,
            tool_call.name,
            source,
            tool_call.time_range or time_range,
            tool_call.device_hint or device_hint,
        )
        logger.info("tool.start request_id=%s tool=%s source=%s", request_id, tool_call.name, source)
        result = execute_tool(
            db,
            tool_call.name,
            intent=intent,
            home_id=request.home_id,
            user_id=request.user_id,
            timezone=request.timezone,
            time_range=tool_call.time_range or time_range,
            device_hint=tool_call.device_hint or device_hint,
            search_query=tool_call.query,
            search_domains=tool_call.domains,
        )
        logger.info(
            "tool.done request_id=%s tool=%s result_count=%s",
            request_id,
            result.tool_name,
            result.result_count,
        )
        return result.model_dump()

    def _handle_device_command(
        self,
        *,
        request: ChatRequest,
        request_id: str,
        evidence: list[dict],
        used_tools: list[str],
        severity: str,
        device_hint: str | None,
        time_range: str | None,
    ) -> ChatResponse:
        parsed_command = parse_device_command(request.message)
        controllable = _candidate_devices_for_command(evidence, parsed_command)
        ranked = sorted(
            controllable,
            key=lambda item: _score_device(item, parsed_command.device_hint if parsed_command else device_hint),
            reverse=True,
        )
        best = ranked[0] if ranked and _score_device(ranked[0], parsed_command.device_hint if parsed_command else device_hint) > 0 else None
        if parsed_command and best:
            command = _resolve_command_for_device(parsed_command.action, best)
            device_command = {
                "device_id": str(best.get("id")),
                "device_slug": best.get("device_slug"),
                "device_name": best.get("device_name"),
                "device_type": best.get("device_type"),
                "command": command,
                "value": None,
            }
            answer = f"Đã xác định thiết bị {best.get('device_name') or best.get('device_slug')} để thực hiện lệnh {command}."
            updated = self._update_memory(request, "DEVICE_COMMAND", evidence, best.get("device_slug") or device_hint, time_range)
            logger.info(
                "chat.device_command request_id=%s device_id=%s command=%s",
                request_id,
                device_command["device_id"],
                command,
            )
            return ChatResponse(
                answer=answer,
                intent="DEVICE_COMMAND",
                used_tools=used_tools,
                evidence=evidence,
                suggested_actions=[],
                memory_updated=updated,
                severity=severity,
                device_command=device_command,
            )

        answer = "Mình chưa xác định được đúng thiết bị để thực hiện lệnh này."
        updated = self._update_memory(request, "DEVICE_COMMAND", evidence, device_hint, time_range)
        return ChatResponse(
            answer=answer,
            intent="DEVICE_COMMAND",
            used_tools=used_tools,
            evidence=evidence,
            suggested_actions=[],
            memory_updated=updated,
            severity="none",
            device_command=None,
        )

    def _update_memory(
        self,
        request: ChatRequest,
        intent: str,
        evidence: list[dict],
        device_hint: str | None,
        time_range: str | None,
    ) -> bool:
        device_item = next((item for item in evidence if item.get("device_slug") or item.get("device_name")), None)
        context = MemoryContext(
            session_id=request.session_id,
            user_id=request.user_id,
            home_id=request.home_id,
            last_intent=intent,
            last_device_slug=(device_item or {}).get("device_slug") or device_hint,
            last_device_name=(device_item or {}).get("device_name") or device_hint,
            last_time_range=time_range,
            conversation_summary=f"Người dùng vừa hỏi intent {intent}.",
        )
        memory_store.upsert(context)
        return True
