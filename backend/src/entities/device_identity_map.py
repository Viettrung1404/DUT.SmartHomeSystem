from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class DeviceIdentityMap(Base):
    __tablename__ = "device_identity_map"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = Column(UUID(as_uuid=True), ForeignKey("homes.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    home_key = Column(String, nullable=False)
    device_key = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    home = relationship("Home")
    device = relationship("Device")

    __table_args__ = (
        UniqueConstraint("home_key", "device_key", name="uq_device_identity_map_topic"),
        UniqueConstraint("device_id", name="uq_device_identity_map_device"),
        Index("idx_device_identity_map_home_id", "home_id"),
        Index("idx_device_identity_map_device_id", "device_id"),
    )
