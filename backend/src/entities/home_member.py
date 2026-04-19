from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from ..database.core import Base


class HomeMember(Base):
    __tablename__ = 'home_members'
    __table_args__ = (
        UniqueConstraint('home_id', 'user_id', name='uq_home_member'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    home_id = Column(UUID(as_uuid=True), ForeignKey('homes.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role = Column(String, nullable=False, default='member')  # 'owner' | 'member'
    joined_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    home = relationship("Home", back_populates="members")
    user = relationship("User", back_populates="home_memberships")

    def __repr__(self):
        return f"<HomeMember(home_id='{self.home_id}', user_id='{self.user_id}', role='{self.role}')>"
