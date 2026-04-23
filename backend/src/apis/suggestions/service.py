from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from src.entities.suggestion_log import SuggestionLog
from datetime import datetime


class SuggestionService:
    @staticmethod
    def get_user_suggestions(
        session: Session,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        include_old: bool = False,
    ) -> tuple[int, list]:
        """
        Lấy danh sách gợi ý cho user.
        
        include_old=False: chỉ lấy gợi ý 30 ngày gần nhất (active)
        include_old=True: lấy tất cả gợi ý
        """
        query = session.query(SuggestionLog).filter(
            SuggestionLog.user_id == user_id
        )
        
        if not include_old:
            # Chỉ gợi ý trong 30 ngày gần nhất
            query = query.filter(
                SuggestionLog.created_at >= text("NOW() - INTERVAL '30 days'")
            )
        
        # Sắp xếp mới nhất trước
        total = query.count()
        suggestions = query.order_by(desc(SuggestionLog.created_at)).offset(offset).limit(limit).all()
        
        return total, suggestions

    @staticmethod
    def get_user_suggestions_by_action_type(
        session: Session,
        user_id: str,
        action_type: str,
        limit: int = 20,
    ):
        """Lấy gợi ý theo loại action."""
        suggestions = session.query(SuggestionLog).filter(
            SuggestionLog.user_id == user_id,
            SuggestionLog.action_type == action_type,
            SuggestionLog.created_at >= text("NOW() - INTERVAL '30 days'")
        ).order_by(desc(SuggestionLog.created_at)).limit(limit).all()
        
        return suggestions

    @staticmethod
    def mark_suggestion_accepted(
        session: Session,
        suggestion_id: int,
        was_accepted: bool,
    ) -> SuggestionLog | None:
        """Đánh dấu gợi ý là được chấp nhận hay từ chối."""
        suggestion = session.query(SuggestionLog).filter(
            SuggestionLog.id == suggestion_id
        ).first()
        
        if suggestion:
            suggestion.was_accepted = was_accepted
            session.commit()
            return suggestion
        
        return None

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
