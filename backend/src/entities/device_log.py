from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class DeviceLog(Base):
    __tablename__ = 'device_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    action = Column(String, nullable=False)  # 'toggle', 'brightness', 'temperature', 'mode', etc.
    value = Column(String, nullable=True)    # action value as string
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    device = relationship("Device", back_populates="logs")

    def __repr__(self):
        return f"<DeviceLog(device_id='{self.device_id}', action='{self.action}')>"
