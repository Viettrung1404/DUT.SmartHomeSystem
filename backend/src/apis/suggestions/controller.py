from fastapi import APIRouter, Depends, HTTPException, Query
import json
from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database.core import get_db
from src.apis.suggestions.models import (
    SuggestionResponse,
    SuggestionsListResponse,
    SuggestionAcceptRequest,
    SuggestionFeedbackRequest,
    SuggestionFeedbackResponse,
)
from src.apis.suggestions.service import SuggestionService
from src.entities.suggestion_log import SuggestionLog

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


# ─── Dependencies ─────────────────────────────────────────────────────────────
# TODO: Thêm dependency check_current_user khi authenticate hoàn chỉnh
# def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
#     ...

def get_user_id_from_request(db: Session) -> str:
    """
    Placeholder: lấy user_id từ request.
    Trong production, dùng JWT token từ header Authorization.
    """
    # TODO: Implement authentication
    row = db.execute(text("""
        SELECT user_id
        FROM suggestion_logs
        ORDER BY created_at DESC
        LIMIT 1
    """)).fetchone()

    if row and row[0]:
        return str(row[0])

    return "550e8400-e29b-41d4-a716-446655440000"


def _load_suggestion_detail(db: Session, suggestion_id: int):
    return db.execute(text("""
        SELECT sl.id, sl.user_id, sl.pattern_id, sl.action_type::text AS action_type,
               sl.suggestion_text, sl.suggestion_json, sl.was_accepted,
               fb.feedback_type AS latest_feedback_type,
               fb.feedback_reason AS latest_feedback_reason,
               fb.feedback_time,
               sl.created_at
        FROM suggestion_logs sl
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
        WHERE sl.id = :id
    """), {"id": suggestion_id}).mappings().first()


# ─── Routes ────────────────────────────────────────────────────────────────────

@router.get("/me", response_model=SuggestionsListResponse)
def get_my_suggestions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    include_old: bool = Query(False),
    db: Session = Depends(get_db),
):
    """
    Lấy danh sách gợi ý cho user hiện tại.
    
    Query parameters:
    - limit: số gợi ý mỗi trang (mặc định 50)
    - offset: vị trí bắt đầu (mặc định 0)
    - include_old: bao gồm gợi ý cũ hơn 30 ngày? (mặc định False)
    
    Response: danh sách gợi ý + tổng số lượng
    """
    user_id = get_user_id_from_request(db)
    
    # Lấy danh sách gợi ý từ service
    total, suggestions = SuggestionService.get_user_suggestions(
        session=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        include_old=include_old,
    )
    
    # Convert ORM objects to Pydantic models
    suggestion_responses = [SuggestionResponse.model_validate(s) for s in suggestions]
    
    return SuggestionsListResponse(
        total=total,
        suggestions=suggestion_responses,
    )


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
def get_suggestion_detail(
    suggestion_id: int,
    db: Session = Depends(get_db),
):
    """Lấy chi tiết 1 gợi ý."""
    suggestion = _load_suggestion_detail(db, suggestion_id)
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    return SuggestionResponse.model_validate(dict(suggestion))


@router.post("/{suggestion_id}/accept", response_model=SuggestionResponse)
def accept_suggestion(
    suggestion_id: int,
    request: SuggestionAcceptRequest,
    db: Session = Depends(get_db),
):
    """
    Đánh dấu gợi ý là được chấp nhận hay từ chối.
    
    Body:
    - was_accepted: true/false
    - action_taken: (optional) "SCHEDULED", "DISMISSED", etc.
    """
    suggestion = SuggestionService.mark_suggestion_accepted(
        session=db,
        suggestion_id=suggestion_id,
        was_accepted=request.was_accepted,
    )
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Nếu thêm action_taken, lưu vào JSONB metadata
    if request.action_taken:
        db.execute(text("""
            UPDATE suggestion_logs
            SET suggestion_json = COALESCE(suggestion_json, '{}'::jsonb) || CAST(:payload AS jsonb)
            WHERE id = :id
        """), {
            "id": suggestion_id,
            "payload": json.dumps({"action_taken": request.action_taken}),
        })
        db.commit()
        suggestion = _load_suggestion_detail(db, suggestion_id)
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    return SuggestionResponse.model_validate(dict(suggestion))


@router.post("/{suggestion_id}/feedback", response_model=SuggestionFeedbackResponse)
def submit_suggestion_feedback(
    suggestion_id: int,
    request: SuggestionFeedbackRequest,
    db: Session = Depends(get_db),
):
    """Lưu feedback chuẩn hóa cho suggestion."""
    feedback_type = request.feedback_type.upper().strip()
    if feedback_type not in {"ACCEPT", "REJECT", "IGNORE"}:
        raise HTTPException(status_code=400, detail="feedback_type must be ACCEPT, REJECT, or IGNORE")

    user_id = get_user_id_from_request(db)
    feedback = SuggestionService.record_suggestion_feedback(
        session=db,
        suggestion_id=suggestion_id,
        user_id=user_id,
        feedback_type=feedback_type,
        feedback_reason=request.feedback_reason,
    )

    if not feedback:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    return SuggestionFeedbackResponse.model_validate(feedback)


@router.get("/filter/by-type", response_model=list[SuggestionResponse])
def get_suggestions_by_type(
    action_type: str = Query(..., description="SCHEDULE | ALERT | AUTOMATION"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Lấy gợi ý theo loại action."""
    user_id = get_user_id_from_request(db)
    
    suggestions = SuggestionService.get_user_suggestions_by_action_type(
        session=db,
        user_id=user_id,
        action_type=action_type.upper(),
        limit=limit,
    )
    
    return [SuggestionResponse.model_validate(s) for s in suggestions]
    return [SuggestionResponse.model_validate(s) for s in suggestions]


@router.get("/metrics/dashboard", response_model=SuggestionDashboardResponse)
def get_suggestion_dashboard(
    home_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Lấy dữ liệu metrics cho dashboard (A. Suggestion, B. Quality, C. Guardrail).
    """
    metrics = SuggestionService.get_suggestion_dashboard_metrics(
        session=db,
        home_id=home_id,
        user_id=user_id,
        days=days,
    )
    return SuggestionDashboardResponse.model_validate(metrics)
