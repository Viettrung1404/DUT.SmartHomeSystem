from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class DeviceTelemetry(Base):
    __tablename__ = "device_telemetry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = Column(UUID(as_uuid=True), ForeignKey("homes.id", ondelete="CASCADE"), nullable=False)
    source_device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    channel = Column(String, nullable=False)  # status | sensors
    metric_key = Column(String, nullable=False)
    metric_value = Column(JSON, nullable=True)
    recorded_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    home = relationship("Home")
    source_device = relationship("Device")

    __table_args__ = (
        Index("idx_device_telemetry_home_id", "home_id"),
        Index("idx_device_telemetry_source_device_id", "source_device_id"),
        Index("idx_device_telemetry_channel", "channel"),
    )
