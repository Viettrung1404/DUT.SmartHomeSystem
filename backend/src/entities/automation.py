from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class Automation(Base):
    __tablename__ = 'automations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = Column(UUID(as_uuid=True), ForeignKey('homes.id', ondelete='CASCADE'), nullable=False)
    name = Column(String, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    home = relationship("Home", back_populates="automations")
    conditions = relationship("AutomationCondition", back_populates="automation", cascade="all, delete-orphan")
    actions = relationship("AutomationAction", back_populates="automation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Automation(name='{self.name}', enabled={self.enabled})>"


class AutomationCondition(Base):
    __tablename__ = 'automation_conditions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    automation_id = Column(UUID(as_uuid=True), ForeignKey('automations.id', ondelete='CASCADE'), nullable=False)
    condition_type = Column(String, nullable=False)  # 'time', 'device_status', 'motion', 'energy', 'temperature'
    value = Column(String, nullable=False)  # e.g., '22:00', 'device_d1_off', '> 15 kWh'

    # Relationships
    automation = relationship("Automation", back_populates="conditions")

    def __repr__(self):
        return f"<AutomationCondition(type='{self.condition_type}', value='{self.value}')>"


class AutomationAction(Base):
    __tablename__ = 'automation_actions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    automation_id = Column(UUID(as_uuid=True), ForeignKey('automations.id', ondelete='CASCADE'), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id'), nullable=True)
    action = Column(String, nullable=False)  # 'toggle', 'set_brightness', 'set_temperature', 'lock', 'notify'
    value = Column(String, nullable=True)    # e.g., 'off', '50', '24'

    # Relationships
    automation = relationship("Automation", back_populates="actions")
    device = relationship("Device", back_populates="automation_actions")

    def __repr__(self):
        return f"<AutomationAction(action='{self.action}', value='{self.value}')>"
