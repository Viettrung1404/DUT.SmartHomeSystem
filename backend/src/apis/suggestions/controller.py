import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.apis.auth.service import CurrentUser
from src.apis.suggestions.models import (
    SuggestionAcceptRequest,
    SuggestionDashboardResponse,
    SuggestionFeedbackRequest,
    SuggestionFeedbackResponse,
    SuggestionResponse,
    SuggestionsListResponse,
)
from src.apis.suggestions.service import SuggestionService
from src.database.core import get_db

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


def _load_suggestion_detail(db: Session, suggestion_id: int, *, user_id: str | None = None):
    sql = """
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
    """
    params: dict[str, object] = {"id": suggestion_id}
    if user_id is not None:
        sql += " AND sl.user_id = CAST(:user_id AS uuid)"
        params["user_id"] = user_id
    return db.execute(text(sql), params).mappings().first()


@router.get("/me", response_model=SuggestionsListResponse)
def get_my_suggestions(
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    include_old: bool = Query(False),
    db: Session = Depends(get_db),
):
    user_id = str(current_user.get_uuid())
    total, suggestions = SuggestionService.get_user_suggestions(
        session=db,
        user_id=user_id,
        limit=limit,
        offset=offset,
        include_old=include_old,
    )
    return SuggestionsListResponse(
        total=total,
        suggestions=[SuggestionResponse.model_validate(suggestion) for suggestion in suggestions],
    )


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
def get_suggestion_detail(
    suggestion_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    suggestion = _load_suggestion_detail(db, suggestion_id, user_id=str(current_user.get_uuid()))
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return SuggestionResponse.model_validate(dict(suggestion))


@router.post("/{suggestion_id}/accept", response_model=SuggestionResponse)
def accept_suggestion(
    suggestion_id: int,
    request: SuggestionAcceptRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    updated = SuggestionService.mark_suggestion_accepted(
        session=db,
        suggestion_id=suggestion_id,
        user_id=str(current_user.get_uuid()),
        was_accepted=request.was_accepted,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    if request.action_taken:
        db.execute(
            text(
                """
                UPDATE suggestion_logs
                SET suggestion_json = COALESCE(suggestion_json, '{}'::jsonb) || CAST(:payload AS jsonb)
                WHERE id = :id
                """
            ),
            {
                "id": suggestion_id,
                "payload": json.dumps({"action_taken": request.action_taken}),
            },
        )
        db.commit()

    suggestion = _load_suggestion_detail(db, suggestion_id, user_id=str(current_user.get_uuid()))
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return SuggestionResponse.model_validate(dict(suggestion))


@router.post("/{suggestion_id}/feedback", response_model=SuggestionFeedbackResponse)
def submit_suggestion_feedback(
    suggestion_id: int,
    request: SuggestionFeedbackRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    feedback_type = request.feedback_type.upper().strip()
    if feedback_type not in {"ACCEPT", "REJECT", "IGNORE"}:
        raise HTTPException(status_code=400, detail="feedback_type must be ACCEPT, REJECT, or IGNORE")

    feedback = SuggestionService.record_suggestion_feedback(
        session=db,
        suggestion_id=suggestion_id,
        user_id=str(current_user.get_uuid()),
        feedback_type=feedback_type,
        feedback_reason=request.feedback_reason,
    )
    if not feedback:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return SuggestionFeedbackResponse.model_validate(feedback)


@router.get("/filter/by-type", response_model=list[SuggestionResponse])
def get_suggestions_by_type(
    action_type: str,
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    suggestions = SuggestionService.get_user_suggestions_by_action_type(
        session=db,
        user_id=str(current_user.get_uuid()),
        action_type=action_type.upper(),
        limit=limit,
    )
    return [SuggestionResponse.model_validate(suggestion) for suggestion in suggestions]


@router.get("/metrics/dashboard", response_model=SuggestionDashboardResponse)
def get_suggestion_dashboard(
    home_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    metrics = SuggestionService.get_suggestion_dashboard_metrics(
        session=db,
        home_id=home_id,
        user_id=user_id,
        days=days,
    )
    return SuggestionDashboardResponse.model_validate(metrics)
