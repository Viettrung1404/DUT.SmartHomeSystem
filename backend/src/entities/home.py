from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class Home(Base):
    __tablename__ = 'homes'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    owner = relationship("User", back_populates="owned_homes")
    members = relationship("HomeMember", back_populates="home", cascade="all, delete-orphan")
    rooms = relationship("Room", back_populates="home", cascade="all, delete-orphan")
    automations = relationship("Automation", back_populates="home", cascade="all, delete-orphan")
    security_events = relationship("SecurityEvent", back_populates="home", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Home(name='{self.name}', owner_id='{self.owner_id}')>"
