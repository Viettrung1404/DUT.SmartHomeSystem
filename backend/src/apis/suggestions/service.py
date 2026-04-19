from sqlalchemy.orm import Session
from sqlalchemy import text


class SuggestionService:
    @staticmethod
    def get_user_suggestions(
        session: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_old: bool = False,
    ) -> tuple[int, list[dict]]:
        """
        Lấy danh sách gợi ý cho user.
        
        include_old=False: chỉ lấy gợi ý 30 ngày gần nhất (active)
        include_old=True: lấy tất cả gợi ý
        """
        total_sql = """
            SELECT COUNT(*)
            FROM suggestion_logs
            WHERE user_id = CAST(:user_id AS uuid)
        """
        list_sql = """
            SELECT id, user_id, pattern_id, action_type::text AS action_type,
                   suggestion_text, suggestion_json, was_accepted, created_at
            FROM suggestion_logs
            WHERE user_id = CAST(:user_id AS uuid)
        """
        params = {"user_id": user_id, "limit": limit, "offset": offset}

        if not include_old:
            total_sql += " AND created_at >= NOW() - INTERVAL '30 days'"
            list_sql += " AND created_at >= NOW() - INTERVAL '30 days'"

        list_sql += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"

        total = int(session.execute(text(total_sql), params).scalar() or 0)
        rows = session.execute(text(list_sql), params).mappings().all()
        return total, [dict(r) for r in rows]

    @staticmethod
    def get_user_suggestions_by_action_type(
        session: Session,
        user_id: str,
        action_type: str,
        limit: int = 20,
    ) -> list[dict]:
        """Lấy gợi ý theo loại action."""
        rows = session.execute(text("""
            SELECT id, user_id, pattern_id, action_type::text AS action_type,
                   suggestion_text, suggestion_json, was_accepted, created_at
            FROM suggestion_logs
                        WHERE user_id = CAST(:user_id AS uuid)
              AND action_type::text = :action_type
              AND created_at >= NOW() - INTERVAL '30 days'
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"user_id": user_id, "action_type": action_type, "limit": limit}).mappings().all()
        return [dict(r) for r in rows]

    @staticmethod
    def mark_suggestion_accepted(
        session: Session,
        suggestion_id: int,
        was_accepted: bool,
    ) -> dict | None:
        """Đánh dấu gợi ý là được chấp nhận hay từ chối."""
        row = session.execute(text("""
            UPDATE suggestion_logs
            SET was_accepted = :was_accepted
            WHERE id = :id
            RETURNING id, user_id, pattern_id, action_type::text AS action_type,
                      suggestion_text, suggestion_json, was_accepted, created_at
        """), {"id": suggestion_id, "was_accepted": was_accepted}).mappings().first()

        if not row:
            return None

        session.commit()
        return dict(row)

    @staticmethod
    def get_active_suggestions_for_home(
        session: Session,
        home_id: str,
        limit: int = 100,
    ):
        """
        Lấy tất cả gợi ý active của nhà (từ tất cả thành viên).
        Dùng cho admin dashboard.
        """
        suggestions = session.execute(text("""
            SELECT
                sl.id, sl.user_id, sl.pattern_id, sl.action_type,
                sl.suggestion_text, sl.suggestion_json,
                sl.was_accepted, sl.created_at,
                u.full_name
            FROM suggestion_logs sl
            JOIN users u ON u.id = sl.user_id
            JOIN home_users hu ON hu.user_id = u.id
            WHERE hu.home_id = :home_id
              AND sl.created_at >= NOW() - INTERVAL '30 days'
              AND sl.was_accepted IS NULL
            ORDER BY sl.created_at DESC
            LIMIT :limit
        """), {"home_id": home_id, "limit": limit}).fetchall()
        
        return suggestions
