from typing import Any
import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.tool_schema import ToolResult
from app.tools.time_utils import resolve_time_range


logger = logging.getLogger("ai_server.tools")


def _normalize_text(value: Any) -> str:
    import re
    import unicodedata

    text_value = unicodedata.normalize("NFD", str(value or "").lower())
    text_value = "".join(ch for ch in text_value if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", text_value).strip()


def _filter_rows_by_device_hint(rows, device_hint: str | None):
    row_dicts = [dict(row) for row in rows]
    if not device_hint:
        return row_dicts

    hint = _normalize_text(device_hint)
    filtered = [
        row
        for row in row_dicts
        if hint in _normalize_text(row.get("device_name"))
        or hint in _normalize_text(row.get("device_slug"))
        or hint in _normalize_text(row.get("room_name"))
    ]
    return filtered or row_dicts


def execute_tool(
    db: Session,
    tool_name: str,
    *,
    intent: str,
    home_id: str,
    user_id: str,
    timezone: str,
    time_range: str | None,
    device_hint: str | None,
) -> ToolResult:
    logger.info(
        "tool.route tool=%s intent=%s home_id=%s user_id=%s time_range=%s device_hint=%s",
        tool_name,
        intent,
        home_id,
        user_id,
        time_range,
        device_hint,
    )
    if tool_name == "query_activity_logs":
        return query_activity_logs(db, home_id, user_id, timezone, time_range, device_hint)
    if tool_name == "query_user_patterns":
        pattern_type = "ANOMALY" if intent in {"GUARDIAN_EVENT_QUERY", "FORGOT_OFF_QUERY"} else None
        return query_user_patterns(db, home_id, user_id, device_hint, pattern_type)
    if tool_name == "query_suggestion_logs":
        action_type = "ALERT" if intent == "GUARDIAN_EVENT_QUERY" else None
        return query_suggestion_logs(db, home_id, user_id, timezone, time_range, action_type)
    if tool_name == "query_guardian_events":
        return query_guardian_events(db, home_id, timezone, time_range)
    if tool_name == "query_device_status":
        return query_device_status(db, home_id, device_hint)
    return ToolResult(tool_name=tool_name, result_count=0, items=[])


def query_activity_logs(
    db: Session,
    home_id: str,
    user_id: str,
    timezone: str,
    time_range: str | None,
    device_hint: str | None,
) -> ToolResult:
    start, end = resolve_time_range(time_range, timezone)
    limit = get_settings().max_tool_rows
    params: dict[str, Any] = {
        "home_id": home_id,
        "user_id": user_id,
        "start": start,
        "end": end,
        "limit": limit,
    }
    rows = db.execute(text("""
        SELECT
            al.id,
            al.timestamp,
            al.session_end,
            al.duration_seconds,
            al.event_type::text AS event_type,
            al.trigger_source::text AS trigger_source,
            al.description,
            d.slug AS device_slug,
            d.name AS device_name,
            d.type::text AS device_type,
            r.name AS room_name
        FROM activity_logs al
        JOIN devices d ON d.id = al.device_id
        LEFT JOIN rooms r ON r.id = d.room_id
        WHERE al.home_id = CAST(:home_id AS uuid)
          AND (al.user_id = CAST(:user_id AS uuid) OR al.user_id IS NULL)
          AND al.timestamp >= :start
          AND al.timestamp < :end
        ORDER BY al.timestamp DESC
        LIMIT :limit
    """), params).mappings().all()
    items = _filter_rows_by_device_hint(rows, device_hint)
    return ToolResult(tool_name="query_activity_logs", result_count=len(items), items=items)


def query_user_patterns(
    db: Session,
    home_id: str,
    user_id: str,
    device_hint: str | None,
    pattern_type: str | None = None,
) -> ToolResult:
    params = {
        "home_id": home_id,
        "user_id": user_id,
        "limit": get_settings().max_tool_rows,
        "pattern_type": pattern_type,
    }
    rows = db.execute(text("""
        SELECT
            up.id,
            up.pattern_type::text AS pattern_type,
            up.pattern_data,
            up.confidence,
            up.computed_at,
            up.is_active,
            d.slug AS device_slug,
            d.name AS device_name,
            r.name AS room_name
        FROM user_patterns up
        LEFT JOIN devices d ON d.id = up.device_id
        LEFT JOIN rooms r ON r.id = d.room_id
        WHERE up.home_id = CAST(:home_id AS uuid)
          AND up.user_id = CAST(:user_id AS uuid)
          AND up.is_active = TRUE
          AND (:pattern_type IS NULL OR up.pattern_type::text = :pattern_type)
        ORDER BY up.computed_at DESC
        LIMIT :limit
    """), params).mappings().all()
    items = _filter_rows_by_device_hint(rows, device_hint)
    return ToolResult(tool_name="query_user_patterns", result_count=len(items), items=items)


def query_suggestion_logs(
    db: Session,
    home_id: str,
    user_id: str,
    timezone: str,
    time_range: str | None,
    action_type: str | None = None,
) -> ToolResult:
    start, end = resolve_time_range(time_range, timezone)
    params = {
        "home_id": home_id,
        "user_id": user_id,
        "limit": get_settings().max_tool_rows,
        "action_type": action_type,
        "start": start,
        "end": end,
        "has_time_range": time_range is not None,
    }
    rows = db.execute(text("""
        SELECT
            sl.id,
            sl.action_type::text AS action_type,
            sl.suggestion_text,
            sl.suggestion_json,
            sl.was_accepted,
            sl.created_at,
            up.pattern_type::text AS pattern_type,
            d.slug AS device_slug,
            d.name AS device_name,
            r.name AS room_name
        FROM suggestion_logs sl
        LEFT JOIN user_patterns up ON up.id = sl.pattern_id
        LEFT JOIN devices d ON d.id = up.device_id
        LEFT JOIN rooms r ON r.id = d.room_id
        WHERE sl.user_id = CAST(:user_id AS uuid)
          AND (up.home_id = CAST(:home_id AS uuid) OR up.home_id IS NULL)
          AND (:action_type IS NULL OR sl.action_type::text = :action_type)
          AND (:has_time_range = FALSE OR (sl.created_at >= :start AND sl.created_at < :end))
        ORDER BY sl.created_at DESC
        LIMIT :limit
    """), params).mappings().all()
    return ToolResult(tool_name="query_suggestion_logs", result_count=len(rows), items=[dict(row) for row in rows])


def query_guardian_events(db: Session, home_id: str, timezone: str, time_range: str | None) -> ToolResult:
    start, end = resolve_time_range(time_range, timezone)
    rows = db.execute(text("""
        SELECT
            id,
            event_type,
            severity,
            description,
            timestamp
        FROM security_events
        WHERE home_id = CAST(:home_id AS uuid)
          AND timestamp >= :start
          AND timestamp < :end
        ORDER BY
            CASE severity
                WHEN 'critical' THEN 4
                WHEN 'high' THEN 3
                WHEN 'medium' THEN 2
                ELSE 1
            END DESC,
            timestamp DESC
        LIMIT :limit
    """), {
        "home_id": home_id,
        "start": start,
        "end": end,
        "limit": get_settings().max_tool_rows,
    }).mappings().all()
    return ToolResult(tool_name="query_guardian_events", result_count=len(rows), items=[dict(row) for row in rows])


def query_device_status(db: Session, home_id: str, device_hint: str | None) -> ToolResult:
    rows = db.execute(text("""
        SELECT
            d.id,
            d.slug AS device_slug,
            d.name AS device_name,
            d.type::text AS device_type,
            r.name AS room_name,
            ds.is_online,
            ds.state,
            ds.last_updated
        FROM devices d
        LEFT JOIN rooms r ON r.id = d.room_id
        LEFT JOIN device_states ds ON ds.device_id = d.id
        WHERE r.home_id = CAST(:home_id AS uuid)
        ORDER BY d.name
        LIMIT :limit
    """), {
        "home_id": home_id,
        "limit": get_settings().max_tool_rows,
    }).mappings().all()
    items = _filter_rows_by_device_hint(rows, device_hint)
    return ToolResult(tool_name="query_device_status", result_count=len(items), items=items)
