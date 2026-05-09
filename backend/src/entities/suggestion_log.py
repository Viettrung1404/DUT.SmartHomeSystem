from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..database.core import Base


class SuggestionLog(Base):
    __tablename__ = "suggestion_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # Keep pattern_id optional without FK because the current modular schema
    # does not define a user_patterns table/model.
    pattern_id = Column(Integer, nullable=True)
    action_type = Column(String, nullable=False)
    suggestion_text = Column(Text, nullable=False)
    suggestion_json = Column(JSON, nullable=True)
    was_accepted = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
