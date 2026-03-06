from sqlalchemy import Column, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class EnergyLog(Base):
    __tablename__ = 'energy_logs'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), ForeignKey('devices.id', ondelete='CASCADE'), nullable=False)
    power_usage = Column(Float, nullable=False)  # kWh
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    device = relationship("Device", back_populates="energy_logs")

    def __repr__(self):
        return f"<EnergyLog(device_id='{self.device_id}', power_usage={self.power_usage})>"
