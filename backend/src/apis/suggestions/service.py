import json
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

LATEST_FEEDBACK_JOIN = """
    LEFT JOIN LATERAL (
        SELECT
            sfl.feedback_type::text AS feedback_type,
            sfl.feedback_reason,
            sfl.feedback_time
        FROM suggestion_feedback_logs sfl
        WHERE sfl.suggestion_id = sl.id
        ORDER BY sfl.feedback_time DESC, sfl.id DESC
        LIMIT 1
    ) fb ON true
"""


class SuggestionService:
    @staticmethod
    def _suggestion_belongs_to_user(session: Session, suggestion_id: int, user_id: str) -> bool:
        row = session.execute(
            text(
                """
                SELECT 1
                FROM suggestion_logs
                WHERE id = :suggestion_id
                  AND user_id = CAST(:user_id AS uuid)
                """
            ),
            {"suggestion_id": suggestion_id, "user_id": user_id},
        ).first()
        return row is not None

    @staticmethod
    def get_user_suggestions(
        session: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_old: bool = False,
    ) -> tuple[int, list[dict]]:
        total_sql = """
            SELECT COUNT(*)
            FROM suggestion_logs
            WHERE user_id = CAST(:user_id AS uuid)
        """
        list_sql = """
             SELECT sl.id, sl.user_id, sl.pattern_id, sl.action_type::text AS action_type,
                 sl.suggestion_text, sl.suggestion_json, sl.was_accepted,
                 fb.feedback_type AS latest_feedback_type,
                 fb.feedback_reason AS latest_feedback_reason,
                 fb.feedback_time,
                 sl.created_at
             FROM suggestion_logs sl
             """ + LATEST_FEEDBACK_JOIN + """
            WHERE sl.user_id = CAST(:user_id AS uuid)
        """
        params = {"user_id": user_id, "limit": limit, "offset": offset}

        if not include_old:
            total_sql += " AND created_at >= NOW() - INTERVAL '30 days'"
            list_sql += " AND created_at >= NOW() - INTERVAL '30 days'"

        list_sql += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

        total = int(session.execute(text(total_sql), params).scalar() or 0)
        rows = session.execute(text(list_sql), params).mappings().all()
        return total, [dict(row) for row in rows]

    @staticmethod
    def get_user_suggestions_by_action_type(
        session: Session,
        user_id: str,
        action_type: str,
        limit: int = 20,
    ) -> list[dict]:
        rows = session.execute(
            text(
                """
                SELECT sl.id, sl.user_id, sl.pattern_id, sl.action_type::text AS action_type,
                       sl.suggestion_text, sl.suggestion_json, sl.was_accepted,
                       fb.feedback_type AS latest_feedback_type,
                       fb.feedback_reason AS latest_feedback_reason,
                       fb.feedback_time,
                       sl.created_at
                FROM suggestion_logs sl
                """
                + LATEST_FEEDBACK_JOIN
                + """
                WHERE sl.user_id = CAST(:user_id AS uuid)
                  AND sl.action_type::text = :action_type
                  AND sl.created_at >= NOW() - INTERVAL '30 days'
                ORDER BY sl.created_at DESC
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "action_type": action_type, "limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    @staticmethod
    def record_suggestion_feedback(
        session: Session,
        suggestion_id: int,
        user_id: str,
        feedback_type: str,
        feedback_reason: str | None = None,
    ) -> dict | None:
        if not SuggestionService._suggestion_belongs_to_user(session, suggestion_id, user_id):
            return None

        row = session.execute(
            text(
                """
                INSERT INTO suggestion_feedback_logs (
                    suggestion_id,
                    user_id,
                    feedback_type,
                    feedback_reason,
                    feedback_time
                )
                VALUES (
                    :suggestion_id,
                    CAST(:user_id AS uuid),
                    :feedback_type,
                    :feedback_reason,
                    NOW()
                )
                ON CONFLICT (suggestion_id)
                DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    feedback_type = EXCLUDED.feedback_type,
                    feedback_reason = EXCLUDED.feedback_reason,
                    feedback_time = EXCLUDED.feedback_time
                RETURNING id, suggestion_id, user_id, feedback_type::text AS feedback_type,
                          feedback_reason, feedback_time, created_at
                """
            ),
            {
                "suggestion_id": suggestion_id,
                "user_id": user_id,
                "feedback_type": feedback_type,
                "feedback_reason": feedback_reason,
            },
        ).mappings().first()

        if not row:
            return None

        session.execute(
            text(
                """
                UPDATE suggestion_logs
                SET was_accepted = CASE
                    WHEN :feedback_type = 'ACCEPT' THEN true
                    WHEN :feedback_type = 'REJECT' THEN false
                    ELSE NULL
                END
                WHERE id = :suggestion_id
                """
            ),
            {"suggestion_id": suggestion_id, "feedback_type": feedback_type},
        )

        session.commit()
        return dict(row)

    @staticmethod
    def mark_suggestion_accepted(
        session: Session,
        suggestion_id: int,
        user_id: str,
        was_accepted: bool,
    ) -> dict | None:
        if not SuggestionService._suggestion_belongs_to_user(session, suggestion_id, user_id):
            return None

        feedback_type = "ACCEPT" if was_accepted else "REJECT"
        return SuggestionService.record_suggestion_feedback(
            session=session,
            suggestion_id=suggestion_id,
            user_id=user_id,
            feedback_type=feedback_type,
            feedback_reason=None,
        )

    @staticmethod
    def get_active_suggestions_for_home(
        session: Session,
        home_id: str,
        limit: int = 100,
    ):
        suggestions = session.execute(
            text(
                """
                SELECT
                    sl.id, sl.user_id, sl.pattern_id, sl.action_type,
                    sl.suggestion_text, sl.suggestion_json,
                    sl.was_accepted,
                    fb.feedback_type AS latest_feedback_type,
                    fb.feedback_reason AS latest_feedback_reason,
                    fb.feedback_time,
                    sl.created_at,
                    u.full_name
                FROM suggestion_logs sl
                """
                + LATEST_FEEDBACK_JOIN
                + """
                JOIN users u ON u.id = sl.user_id
                JOIN home_users hu ON hu.user_id = u.id
                WHERE hu.home_id = :home_id
                  AND sl.created_at >= NOW() - INTERVAL '30 days'
                  AND fb.feedback_type IS NULL
                ORDER BY sl.created_at DESC
                LIMIT :limit
                """
            ),
            {"home_id": home_id, "limit": limit},
        ).fetchall()
        return suggestions

    @staticmethod
    def log_decision(
        session: Session,
        pattern_id: int,
        home_id: str,
        user_id: str,
        decision_score: float,
        should_suggest: bool,
        blocked_by: str | None = None,
        cooldown_signature: str | None = None,
        metadata_json: dict | None = None,
    ):
        session.execute(
            text(
                """
                INSERT INTO suggestion_decision_logs (
                    pattern_id, home_id, user_id, decision_score,
                    should_suggest, blocked_by, cooldown_signature, metadata_json
                )
                VALUES (
                    :pid, CAST(:hid AS uuid), CAST(:uid AS uuid), :score,
                    :should, :blocked, :signature, CAST(:meta AS jsonb)
                )
                """
            ),
            {
                "pid": pattern_id,
                "hid": home_id,
                "uid": user_id,
                "score": decision_score,
                "should": should_suggest,
                "blocked": blocked_by,
                "signature": cooldown_signature,
                "meta": json.dumps(metadata_json) if metadata_json else None,
            },
        )
        session.commit()

    @staticmethod
    def get_suggestion_dashboard_metrics(
        session: Session,
        home_id: str | None = None,
        user_id: str | None = None,
        days: int = 30,
    ) -> dict:
        since = datetime.now() - timedelta(days=days)

        metrics_query = """
            WITH filtered_suggestions AS (
                SELECT sl.*, up.pattern_type, up.home_id
                FROM suggestion_logs sl
                JOIN user_patterns up ON up.id = sl.pattern_id
                WHERE sl.created_at >= :since
                AND (:hid IS NULL OR up.home_id = CAST(:hid AS uuid))
                AND (:uid IS NULL OR sl.user_id = CAST(:uid AS uuid))
            ),
            feedback_stats AS (
                SELECT
                    COUNT(*) FILTER (WHERE was_accepted = true) as accepted,
                    COUNT(*) FILTER (WHERE was_accepted = false) as rejected,
                    COUNT(*) FILTER (WHERE latest_feedback_type = 'IGNORE') as ignored,
                    COUNT(*) as total_feedback
                FROM (
                    SELECT fs.*, fb.feedback_type as latest_feedback_type
                    FROM filtered_suggestions fs
                    """ + LATEST_FEEDBACK_JOIN.replace("sl.id", "fs.id") + """
                ) f
            )
            SELECT
                (SELECT COUNT(*) FROM filtered_suggestions) as sent_count,
                (SELECT accepted FROM feedback_stats) as accepted,
                (SELECT rejected FROM feedback_stats) as rejected,
                (SELECT ignored FROM feedback_stats) as ignored
        """

        res = session.execute(text(metrics_query), {"since": since, "hid": home_id, "uid": user_id}).mappings().first()
        sent_count = res["sent_count"] or 0
        accepted = res["accepted"] or 0
        rejected = res["rejected"] or 0
        ignored = res["ignored"] or 0
        total_feedback = accepted + rejected + ignored

        guardrail_query = """
            SELECT
                COUNT(*) FILTER (WHERE blocked_by = 'COOLDOWN' OR blocked_by = 'same_pattern_cooldown' OR blocked_by = 'daily_suggestion_cap') as cooldown_suppressions,
                COUNT(*) FILTER (WHERE metadata_json->'priority_reason' ? 'hard_override_anomaly_high_energy_repeated') as priority_overrides
            FROM suggestion_decision_logs
            WHERE created_at >= :since
            AND (:hid IS NULL OR home_id = CAST(:hid AS uuid))
            AND (:uid IS NULL OR user_id = CAST(:uid AS uuid))
        """
        guardrail_res = session.execute(text(guardrail_query), {"since": since, "hid": home_id, "uid": user_id}).mappings().first()
        cooldown_suppressions = guardrail_res["cooldown_suppressions"] or 0

        effective_accept_rate = (accepted / total_feedback * 100) if total_feedback > 0 else 0.0
        rejection_rate = (rejected / total_feedback * 100) if total_feedback > 0 else 0.0
        ignore_rate = (ignored / total_feedback * 100) if total_feedback > 0 else 0.0
        false_alert_rate = (rejected / sent_count * 100) if sent_count > 0 else 0.0

        action_dist_query = """
            SELECT action_type::text, COUNT(*) as count
            FROM suggestion_logs sl
            JOIN user_patterns up ON up.id = sl.pattern_id
            WHERE sl.created_at >= :since
            AND (:hid IS NULL OR up.home_id = CAST(:hid AS uuid))
            AND (:uid IS NULL OR sl.user_id = CAST(:uid AS uuid))
            GROUP BY action_type
        """
        action_rows = session.execute(text(action_dist_query), {"since": since, "hid": home_id, "uid": user_id}).fetchall()
        action_dist = {row[0]: row[1] for row in action_rows}

        top_patterns_query = """
            SELECT
                up.pattern_type::text,
                COUNT(sl.id) as sent,
                COUNT(sl.id) FILTER (WHERE sl.was_accepted = true) as accepted
            FROM suggestion_logs sl
            JOIN user_patterns up ON up.id = sl.pattern_id
            WHERE sl.created_at >= :since
            AND (:hid IS NULL OR up.home_id = CAST(:hid AS uuid))
            AND (:uid IS NULL OR sl.user_id = CAST(:uid AS uuid))
            GROUP BY up.pattern_type
            ORDER BY accepted DESC, sent DESC
            LIMIT 5
        """
        pattern_rows = session.execute(text(top_patterns_query), {"since": since, "hid": home_id, "uid": user_id}).fetchall()
        top_patterns = []
        for row in pattern_rows:
            sent = row[1]
            accepted_count = row[2]
            top_patterns.append(
                {
                    "pattern_type": row[0],
                    "sent": sent,
                    "accepted": accepted_count,
                    "accept_rate": (accepted_count / sent * 100) if sent > 0 else 0.0,
                }
            )

        trend_query = """
            SELECT
                TO_CHAR(created_at AT TIME ZONE 'Asia/Ho_Chi_Minh', 'YYYY-MM-DD') as date,
                COUNT(*) as count
            FROM suggestion_logs sl
            JOIN user_patterns up ON up.id = sl.pattern_id
            WHERE sl.created_at >= :since
            AND (:hid IS NULL OR up.home_id = CAST(:hid AS uuid))
            AND (:uid IS NULL OR sl.user_id = CAST(:uid AS uuid))
            GROUP BY date
            ORDER BY date
        """
        trend_rows = session.execute(text(trend_query), {"since": since, "hid": home_id, "uid": user_id}).fetchall()
        daily_trend = [{"date": row[0], "count": row[1]} for row in trend_rows]

        rejection_reasons_query = """
            SELECT
                feedback_reason,
                COUNT(*) as count
            FROM suggestion_feedback_logs sfl
            JOIN suggestion_logs sl ON sl.id = sfl.suggestion_id
            JOIN user_patterns up ON up.id = sl.pattern_id
            WHERE sfl.feedback_type = 'REJECT'
            AND sfl.feedback_time >= :since
            AND (:hid IS NULL OR up.home_id = CAST(:hid AS uuid))
            AND (:uid IS NULL OR sfl.user_id = CAST(:uid AS uuid))
            GROUP BY feedback_reason
            ORDER BY count DESC
            LIMIT 5
        """
        rejection_rows = session.execute(text(rejection_reasons_query), {"since": since, "hid": home_id, "uid": user_id}).fetchall()
        rejection_reasons = [{"reason": row[0] or "No reason provided", "count": row[1]} for row in rejection_rows]

        return {
            "sent_count": sent_count,
            "feedback": {
                "accepted": accepted,
                "rejected": rejected,
                "ignored": ignored,
                "total_feedback": total_feedback,
            },
            "effective_accept_rate": round(effective_accept_rate, 1),
            "rejection_rate": round(rejection_rate, 1),
            "ignore_rate": round(ignore_rate, 1),
            "false_alert_rate": round(false_alert_rate, 1),
            "cooldown_suppressions": cooldown_suppressions,
            "avg_suggestions_per_day": round(sent_count / days, 2) if days > 0 else 0,
            "action_type_dist": {
                "SCHEDULE": action_dist.get("SCHEDULE", 0),
                "ALERT": action_dist.get("ALERT", 0),
                "AUTOMATION": action_dist.get("AUTOMATION", 0),
            },
            "top_accepted_patterns": top_patterns,
            "daily_trend": daily_trend,
            "top_rejection_reasons": rejection_reasons,
        }
