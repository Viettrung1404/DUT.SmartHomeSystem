import logging
import re
import unicodedata
from uuid import uuid4

from app.agent.command_parser import parse_device_command
from app.agent.intent_router import classify_intent
from app.agent.response_formatter import collect_evidence, fallback_answer, max_severity
from app.agent.tool_router import select_tools
from app.db.session import SessionLocal
from app.llm.ollama_client import generate_answer
from app.memory.memory_store import MemoryContext, memory_store
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.tools.smart_home_tools import execute_tool


logger = logging.getLogger("ai_server.agent")


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


def _normalize_text(value) -> str:
    text = unicodedata.normalize("NFD", str(value or "").lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text).strip()


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

        logger.info(
            "chat.intent request_id=%s intent=%s device_hint=%s time_range=%s needs_memory=%s memory_found=%s",
            request_id,
            intent,
            device_hint,
            time_range,
            intent_result.needs_memory,
            memory is not None,
        )

        tool_results = []
        with SessionLocal() as db:
            for tool_name in select_tools(intent):
                logger.info("tool.start request_id=%s tool=%s", request_id, tool_name)
                result = execute_tool(
                    db,
                    tool_name,
                    intent=intent,
                    home_id=request.home_id,
                    user_id=request.user_id,
                    timezone=request.timezone,
                    time_range=time_range,
                    device_hint=device_hint,
                )
                logger.info(
                    "tool.done request_id=%s tool=%s result_count=%s",
                    request_id,
                    result.tool_name,
                    result.result_count,
                )
                tool_results.append(result.model_dump())

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
                suggested_actions = []
                updated = self._update_memory(request, intent, evidence, best.get("device_slug") or device_hint, time_range)
                logger.info(
                    "chat.device_command request_id=%s device_id=%s command=%s",
                    request_id,
                    device_command["device_id"],
                    command,
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

            answer = "Mình chưa xác định được đúng thiết bị để thực hiện lệnh này."
            updated = self._update_memory(request, intent, evidence, device_hint, time_range)
            return ChatResponse(
                answer=answer,
                intent=intent,
                used_tools=used_tools,
                evidence=evidence,
                suggested_actions=[],
                memory_updated=updated,
                severity="none",
                device_command=None,
            )

        llm_response = None
        if evidence:
            logger.info("llm.start request_id=%s model_input_tools=%s", request_id, len(tool_results))
            llm_response = generate_answer(
                request.message,
                memory.to_dict() if memory else None,
                tool_results,
            )
            logger.info("llm.done request_id=%s success=%s", request_id, llm_response is not None)
        else:
            logger.info("llm.skip request_id=%s reason=no_evidence", request_id)

        if llm_response:
            answer = str(llm_response["answer"])
            suggested_actions = _string_list(llm_response.get("suggested_actions"))
            severity = str(llm_response.get("severity") or severity).lower()
        else:
            answer, suggested_actions = fallback_answer(intent, evidence)
            logger.info("chat.fallback request_id=%s reason=%s", request_id, "llm_unavailable_or_no_evidence")

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
