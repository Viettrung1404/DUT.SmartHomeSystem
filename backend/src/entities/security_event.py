from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class SecurityEvent(Base):
    __tablename__ = 'security_events'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = Column(UUID(as_uuid=True), ForeignKey('homes.id', ondelete='CASCADE'), nullable=False)
    event_type = Column(String, nullable=False)  # 'motion_detected', 'door_opened', 'device_offline', 'unusual_activity', 'smoke_detected'
    severity = Column(String, nullable=False, default='low')  # 'low', 'medium', 'high'
    description = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    home = relationship("Home", back_populates="security_events")

    def __repr__(self):
        return f"<SecurityEvent(type='{self.event_type}', severity='{self.severity}')>"
