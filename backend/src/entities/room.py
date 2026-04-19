from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class Room(Base):
    __tablename__ = 'rooms'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = Column(UUID(as_uuid=True), ForeignKey('homes.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=True, default='home')
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    home = relationship("Home", back_populates="rooms")
    devices = relationship("Device", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Room(name='{self.name}', home_id='{self.home_id}')>"
