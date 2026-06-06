"""
scripts/run_llm_formatter.py
============================
Đọc user_patterns active → gọi Ollama → lưu suggestion_logs.

Chạy thủ công:
    python scripts/run_llm_formatter.py

Trong production: Celery task gọi format_suggestions_for_home() sau khi
run_full_pipeline() xong.

LLM_PROVIDER: ollama (default) | claude
OLLAMA_URL:   http://localhost:11434 (default)
OLLAMA_MODEL: qwen2.5:3b (default — tiếng Việt tốt nhất nhóm nhỏ)
"""

import json
import os
import sys
import httpx
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.entities.models import SuggestionLog, ActionType

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

DB_URL        = os.getenv("DATABASE_URL", "postgresql://postgres:123456@localhost:5432/smarthome")
LLM_PROVIDER  = os.getenv("LLM_PROVIDER",  "ollama")   # "ollama" | "claude"
OLLAMA_URL    = os.getenv("OLLAMA_URL",     "http://localhost:11434")
OLLAMA_MODEL  = os.getenv("OLLAMA_MODEL",   "qwen2.5:3b")
CLAUDE_KEY    = os.getenv("ANTHROPIC_API_KEY", "")
TZ            = ZoneInfo("Asia/Ho_Chi_Minh")

# Tên thiết bị tiếng Việt để LLM dùng trong câu gợi ý
DEVICE_NAMES_VN = {
    "light_bedroom":  "đèn phòng ngủ",
    "fan_bedroom":    "quạt phòng ngủ",
    "ac_bedroom":     "điều hoà phòng ngủ",
    "light_living":   "đèn phòng khách",
    "fan_living":     "quạt phòng khách",
    "ac_living":      "điều hoà phòng khách",
    "light_kitchen":  "đèn bếp",
}

DOW_VN = {0:"Chủ nhật",1:"Thứ 2",2:"Thứ 3",3:"Thứ 4",4:"Thứ 5",5:"Thứ 6",6:"Thứ 7"}


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDER
#
# Nguyên tắc quan trọng: LLM KHÔNG tự query DB.
# Ta chuẩn bị JSON context đầy đủ, LLM chỉ diễn đạt thành tiếng Việt.
# ═══════════════════════════════════════════════════════════════════════════════

def build_prompt(pattern: dict, user_name: str) -> str:
    ptype = pattern["pattern_type"]
    data  = pattern["pattern_data"]
    dev   = DEVICE_NAMES_VN.get(pattern.get("device_id", ""), pattern.get("device_id", "thiết bị"))

    if ptype == "TIME_HABIT":
        days_str = ", ".join(DOW_VN.get(d, str(d)) for d in data.get("days_of_week", []))
        prompt = f"""Bạn là trợ lý smart home. Viết 1 gợi ý ngắn gọn bằng tiếng Việt cho người dùng tên {user_name}.

Dữ liệu phân tích:
- Thiết bị: {dev}
- Thói quen: thường bật lúc {data.get('hour', '?')}h các ngày: {days_str}
- Thời gian bật trung bình: {data.get('avg_dur_min', '?')} phút
- Độ tin cậy: {int(pattern.get('confidence', 0.8) * 100)}%

Hãy trả về JSON với định dạng sau (CHỈ JSON, không thêm gì khác):
{{
  "title": "Tiêu đề ngắn (max 8 từ)",
  "description": "Mô tả thói quen + đề xuất tạo lịch (1-2 câu, thân thiện)",
  "action_type": "SCHEDULE",
  "schedule_payload": {{
    "time": "{data.get('hour', 22):02d}:00",
    "days_of_week": {data.get('days_of_week', [])},
    "action_payload": {{"power": "ON"}}
  }}
}}"""

    elif ptype == "ANOMALY":
        prompt = f"""Bạn là trợ lý smart home. Viết 1 cảnh báo ngắn gọn bằng tiếng Việt cho {user_name}.

Dữ liệu:
- Thiết bị: {dev}
- Phân tích: {data.get('label_vn', 'phát hiện bất thường')}
- Xảy ra: {data.get('occurrences', '?')} lần trong 30 ngày

Trả về JSON (CHỈ JSON):
{{
  "title": "Tiêu đề cảnh báo (max 8 từ)",
  "description": "Mô tả vấn đề + lời khuyên (1-2 câu, nhẹ nhàng)",
  "action_type": "ALERT",
  "schedule_payload": null
}}"""

    elif ptype == "CLUSTER":
        prompt = f"""Bạn là trợ lý smart home. Tóm tắt thói quen sử dụng thiết bị của {user_name}.

Phân tích:
- Nhóm thói quen: {data.get('label_vn', data.get('cluster_name', '?'))}
- Giờ hoạt động nhiều nhất: {data.get('peak_hour', '?')}h
- Tỷ lệ cuối tuần: {int(data.get('weekend_ratio', 0) * 100)}%

Trả về JSON (CHỈ JSON):
{{
  "title": "Mô tả phong cách sinh hoạt (max 8 từ)",
  "description": "Nhận xét thói quen + 1 gợi ý tối ưu hoá điện năng (2 câu)",
  "action_type": "AUTOMATION",
  "schedule_payload": null
}}"""

    else:
        return None

    return prompt


# ═══════════════════════════════════════════════════════════════════════════════
# LLM CALLER
# Abstraction layer: switch provider bằng LLM_PROVIDER env var.
# ═══════════════════════════════════════════════════════════════════════════════

def call_llm(prompt: str) -> str | None:
    """Gọi LLM, trả về raw text. None nếu lỗi."""
    if LLM_PROVIDER == "claude":
        return _call_claude(prompt)
    return _call_ollama(prompt)


def _call_ollama(prompt: str) -> str | None:
    try:
        resp = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model":  OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,   # thấp để output ổn định / ít hallucinate
                    "num_predict": 300,
                },
            },
            timeout=90.0,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")
    except Exception as e:
        print(f"    [Ollama error] {e}")
        return None


def _call_claude(prompt: str) -> str | None:
    try:
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key":         CLAUDE_KEY,
                "anthropic-version": "2023-06-01",
                "content-type":      "application/json",
            },
            json={
                "model":      "claude-haiku-4-5-20251001",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
    except Exception as e:
        print(f"    [Claude API error] {e}")
        return None


def parse_llm_output(raw: str) -> dict | None:
    """Trích xuất JSON từ output LLM (đề phòng model thêm markdown)."""
    if not raw:
        return None
    # Strip markdown code fences nếu có
    cleaned = raw.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                cleaned = part
                break
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Thử tìm { ... } đầu tiên
        start = cleaned.find("{")
        end   = cleaned.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except Exception:
                pass
    print(f"    [Parse error] Không parse được JSON từ LLM output")
    return None


def build_fallback_suggestion(pattern: dict, display_name: str | None = None) -> dict:
    """Create a deterministic suggestion when the LLM service is unavailable."""
    ptype = pattern["pattern_type"]
    data = pattern["pattern_data"] or {}
    device_name = display_name or DEVICE_NAMES_VN.get(
        pattern.get("device_id", ""),
        pattern.get("device_id", "thiết bị"),
    )

    if ptype == "TIME_HABIT":
        hour = int(data.get("hour", 22))
        days = data.get("days_of_week", [])
        days_str = ", ".join(DOW_VN.get(int(d), str(d)) for d in days) or "các ngày gần đây"
        return {
            "title": f"Tạo lịch cho {device_name}",
            "description": (
                f"Hệ thống nhận thấy bạn thường bật {device_name} lúc {hour:02d}:00 vào {days_str}. "
                "Bạn có thể tạo lịch tự động để thao tác thuận tiện hơn."
            ),
            "action_type": "SCHEDULE",
            "schedule_payload": {
                "time": f"{hour:02d}:00",
                "days_of_week": days,
                "action_payload": {"power": "ON"},
            },
        }

    if ptype == "ANOMALY":
        occurrences = data.get("occurrences", "?")
        label = data.get("label_vn") or f"{device_name} có dấu hiệu sử dụng bất thường"
        return {
            "title": f"Cảnh báo {device_name}",
            "description": (
                f"{label}. Mẫu này xuất hiện {occurrences} lần trong dữ liệu gần đây; "
                "bạn nên kiểm tra trạng thái thiết bị để tránh lãng phí điện hoặc rủi ro vận hành."
            ),
            "action_type": "ALERT",
            "schedule_payload": None,
        }

    if ptype == "CLUSTER":
        label = data.get("label_vn") or data.get("cluster_name") or "thói quen sử dụng thiết bị"
        return {
            "title": "Tối ưu thói quen sử dụng",
            "description": (
                f"Hệ thống ghi nhận {label}. Bạn có thể xem lại lịch tự động và thiết bị thường dùng "
                "để tối ưu tiện nghi và điện năng."
            ),
            "action_type": "AUTOMATION",
            "schedule_payload": None,
        }

    return {
        "title": "Gợi ý nhà thông minh",
        "description": "Hệ thống phát hiện một mẫu sử dụng thiết bị đáng chú ý và đề xuất bạn kiểm tra lại.",
        "action_type": "ALERT",
        "schedule_payload": None,
    }


def load_latest_decision_candidates_for_home(session: Session, home_id, limit: int = 0) -> list[dict]:
    sql = """
        WITH latest_decision AS (
            SELECT DISTINCT ON (sdl.pattern_id)
                sdl.pattern_id,
                sdl.decision_score,
                sdl.should_suggest,
                sdl.blocked_by,
                sdl.cooldown_signature,
                sdl.metadata_json,
                sdl.created_at AS decision_created_at
            FROM suggestion_decision_logs sdl
            JOIN user_patterns up ON up.id = sdl.pattern_id
            WHERE up.home_id = :hid
            ORDER BY sdl.pattern_id, sdl.created_at DESC, sdl.id DESC
        )
        SELECT
            up.id,
            up.user_id,
            up.device_id,
            d.slug AS device_slug,
            d.name AS device_name,
            up.pattern_type,
            up.pattern_data,
            up.confidence,
            u.full_name,
            u.email,
            ld.decision_score,
            ld.should_suggest,
            ld.blocked_by,
            ld.cooldown_signature,
            ld.metadata_json,
            ld.decision_created_at
        FROM latest_decision ld
        JOIN user_patterns up ON up.id = ld.pattern_id
        JOIN users u ON u.id = up.user_id
        LEFT JOIN devices d ON d.id = up.device_id
        WHERE up.home_id = :hid
          AND up.is_active = true
          AND ld.should_suggest = true
        ORDER BY ld.decision_score DESC, ld.decision_created_at DESC, up.id DESC
    """
    params = {"hid": str(home_id)}
    if limit and limit > 0:
        sql += " LIMIT :limit"
        params["limit"] = int(limit)

    rows = session.execute(text(sql), params).fetchall()
    ordered: list[dict] = []

    for row in rows:
        meta = row.metadata_json or {}
        score = round(float(row.decision_score or 0.0), 4)
        ordered.append({
            "row": row,
            "candidate": {
                "pattern_id": int(row.id),
                "home_id": str(home_id),
                "user_id": str(row.user_id),
                "user_email": row.email,
                "user_name": row.full_name,
                "device_id": str(row.device_id) if row.device_id else None,
                "pattern_type": row.pattern_type,
                "threshold": meta.get("threshold"),
                "score": score,
                "usefulness": bool(meta.get("usefulness", True)),
                "usefulness_reasons": list(meta.get("usefulness_reasons", [])),
                "cooldown_pass": True,
                "cooldown_reasons": list(meta.get("cooldown_reasons", [])),
                "cooldown_signature": row.cooldown_signature,
                "priority_score": meta.get("priority_score"),
                "priority_reason": list(meta.get("priority_reason", [])),
                "priority_hard_override": bool(meta.get("priority_hard_override", False)),
                "priority_rank": None,
                "score_breakdown": meta.get("score_breakdown", {}),
                "decision_score": score,
                "decision_created_at": row.decision_created_at,
                "blocked_by": row.blocked_by,
            },
            "sort_key": (
                score,
                row.decision_created_at,
                int(row.id),
            ),
        })

    ordered.sort(key=lambda item: item["sort_key"], reverse=True)
    return ordered


def build_explanation_json(candidate: dict) -> dict:
    return {
        "decision_score": candidate.get("score"),
        "threshold": candidate.get("threshold"),
        "priority_score": candidate.get("priority_score"),
        "priority_rank": candidate.get("priority_rank"),
        "priority_reason": candidate.get("priority_reason", []),
        "cooldown_pass": candidate.get("cooldown_pass", False),
        "cooldown_reasons": candidate.get("cooldown_reasons", []),
        "cooldown_signature": candidate.get("cooldown_signature"),
        "usefulness": candidate.get("usefulness", False),
        "usefulness_reasons": candidate.get("usefulness_reasons", []),
        "priority_hard_override": candidate.get("priority_hard_override", False),
    }


def load_patterns_for_candidates(session: Session, home_id, candidates: list[dict]) -> list[dict]:
    if not candidates:
        return []

    normalized_candidates = [
        c.get("candidate", c)
        for c in candidates
        if isinstance(c, dict)
    ]
    candidate_ids = [
        int(c["pattern_id"])
        for c in normalized_candidates
        if c.get("pattern_id") is not None
    ]
    if not candidate_ids:
        return []

    stmt = text("""
        SELECT
            up.id, up.user_id, up.device_id, d.slug AS device_slug, d.name AS device_name, up.pattern_type,
            up.pattern_data, up.confidence,
            u.full_name
        FROM user_patterns up
        JOIN users u ON u.id = up.user_id
        LEFT JOIN devices d ON d.id = up.device_id
        WHERE up.home_id = :hid
          AND up.id IN :pattern_ids
    """).bindparams(bindparam("pattern_ids", expanding=True))
    rows = session.execute(stmt, {"hid": str(home_id), "pattern_ids": candidate_ids}).fetchall()

    row_map = {int(row.id): row for row in rows}
    ordered = []
    candidate_order = {int(c["pattern_id"]): idx for idx, c in enumerate(normalized_candidates)}

    for candidate in normalized_candidates:
        pid = int(candidate["pattern_id"])
        row = row_map.get(pid)
        if not row:
            continue
        ordered.append({
            "row": row,
            "candidate": candidate,
            "sort_key": (
                int(candidate.get("priority_rank") or 9999),
                candidate_order.get(pid, 9999),
            ),
        })

    ordered.sort(key=lambda item: item["sort_key"])
    return ordered


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

def format_suggestions_for_home(session: Session, home_id, decision_candidates: list[dict] | None = None):
    """Xử lý tất cả active patterns của home → sinh suggestion_logs."""

    if decision_candidates is not None:
        patterns = load_patterns_for_candidates(session, home_id, decision_candidates)
    else:
        patterns = session.execute(text("""
            SELECT
                up.id, up.user_id, up.device_id, d.slug AS device_slug, d.name AS device_name, up.pattern_type,
                up.pattern_data, up.confidence,
                u.full_name
            FROM user_patterns up
            JOIN users u ON u.id = up.user_id
            LEFT JOIN devices d ON d.id = up.device_id
            WHERE up.home_id  = :hid
              AND up.is_active = true
              AND up.confidence >= 0.5
            ORDER BY up.user_id, up.pattern_type
        """), {"hid": str(home_id)}).fetchall()

    print(f"  Xử lý {len(patterns)} patterns...")
    created = 0

    for item in patterns:
        if isinstance(item, dict):
            p = item["row"]
            candidate = item.get("candidate", {})
        else:
            p = item
            candidate = {}

        pattern_dict = {
            "pattern_type": p.pattern_type,
            "device_id":    p.device_slug or str(p.device_id or ""),
            "pattern_data": p.pattern_data,
            "confidence":   p.confidence,
        }

        prompt = build_prompt(pattern_dict, p.full_name or "bạn")
        if not prompt:
            continue

        print(f"    [{p.pattern_type}] {p.device_id or 'cluster'} → calling {LLM_PROVIDER}...")
        raw    = call_llm(prompt)
        parsed = parse_llm_output(raw)

        if not parsed:
            print("      [Fallback] LLM unavailable or invalid output, using rule-based formatter")
            parsed = build_fallback_suggestion(
                pattern_dict,
                p.device_name or p.device_slug or str(p.device_id or ""),
            )

        # Map action_type string → Enum
        action_map = {"SCHEDULE": ActionType.SCHEDULE, "ALERT": ActionType.ALERT,
                      "AUTOMATION": ActionType.AUTOMATION}
        action_type = action_map.get(parsed.get("action_type", ""), ActionType.ALERT)

        # Kiểm tra không tạo gợi ý trùng trong 7 ngày
        existing = session.execute(text("""
            SELECT id FROM suggestion_logs
            WHERE user_id    = :uid
              AND pattern_id = :pid
              AND created_at > NOW() - INTERVAL '7 days'
            LIMIT 1
        """), {"uid": str(p.user_id), "pid": p.id}).fetchone()

        if existing:
            print(f"      [SKIP] Gợi ý đã tồn tại trong 7 ngày")
            continue

        explanation_json = build_explanation_json(candidate) if candidate else {}

        session.add(SuggestionLog(
            user_id=p.user_id,
            pattern_id=p.id,
            action_type=action_type,
            suggestion_text=f"{parsed.get('title','')}: {parsed.get('description','')}",
            suggestion_json={
                "title":            parsed.get("title"),
                "description":      parsed.get("description"),
                "device_id":        str(p.device_id) if p.device_id else None,
                "device_slug":      p.device_slug,
                "device_name":      p.device_name,
                "action_type":      parsed.get("action_type"),
                "schedule_payload": parsed.get("schedule_payload"),
                "explanation":      explanation_json,
                "source": {
                    "pattern_id": int(p.id),
                    "pattern_type": p.pattern_type,
                    "user_name": p.full_name,
                },
            },
            was_accepted=None,
        ))
        created += 1

    session.flush()
    print(f"  → Tạo {created} suggestion_logs mới")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Format suggestions from latest decision logs or active patterns")
    parser.add_argument("--limit", type=int, default=0, help="Max passed decision candidates to format (0 = all)")
    args = parser.parse_args()

    engine = create_engine(DB_URL, echo=False)
    with Session(engine) as session:
        with session.begin():
            homes = session.execute(
                text("SELECT id FROM homes WHERE is_active = true")
            ).fetchall()

            candidate_index: dict[str, list[dict]] = {}
            for home_row in homes:
                home_key = str(home_row[0])
                candidate_index[home_key] = load_latest_decision_candidates_for_home(
                    session,
                    home_key,
                )

            limit_enabled = args.limit and args.limit > 0
            remaining = args.limit if limit_enabled else 0
            for home_key in sorted(candidate_index):
                home_candidates = candidate_index[home_key]
                if limit_enabled:
                    if remaining <= 0:
                        candidate_index[home_key] = []
                        continue
                    candidate_index[home_key] = home_candidates[:remaining]
                    remaining -= len(candidate_index[home_key])

            for home_row in homes:
                home_id = str(home_row[0])
                print(f"\n── Home {home_id} ──")
                home_candidates = candidate_index.get(home_id)
                if not home_candidates:
                    print("  [SKIP] Không có candidate đã pass cooldown cho home này")
                    continue
                format_suggestions_for_home(session, home_id, decision_candidates=home_candidates)

    print("\n✓ Done! Kiểm tra bảng suggestion_logs.")
    print("Bước tiếp theo:")
    print("  Khởi động FastAPI → GET /suggestions/me để xem kết quả trên mobile")


if __name__ == "__main__":
    print(f"LLM provider: {LLM_PROVIDER} / model: {OLLAMA_MODEL if LLM_PROVIDER=='ollama' else 'claude-haiku'}")
    main()
