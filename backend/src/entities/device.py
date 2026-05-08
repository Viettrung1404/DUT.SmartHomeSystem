from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class Device(Base):
    __tablename__ = 'devices'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'light', 'ac', 'sensor', 'camera', 'lock', 'fan', 'curtain'
    status = Column(Boolean, nullable=False, default=False)  # True = on, False = off
    online_status = Column(Boolean, nullable=False, default=False)
    last_seen = Column(DateTime, nullable=True)
    metadata_json = Column('metadata', MutableDict.as_mutable(JSON), nullable=True, default=dict)
    # metadata can store: brightness, temperature, targetTemp, mode, humidity, battery, isLocked, etc.
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    room = relationship("Room", back_populates="devices")
    logs = relationship("DeviceLog", back_populates="device", cascade="all, delete-orphan")
    energy_logs = relationship("EnergyLog", back_populates="device", cascade="all, delete-orphan")
    automation_actions = relationship("AutomationAction", back_populates="device")

    def __repr__(self):
        return f"<Device(name='{self.name}', type='{self.type}', status={self.status})>"
