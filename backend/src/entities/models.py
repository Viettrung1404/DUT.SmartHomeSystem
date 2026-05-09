# backend/src/entities/models.py
# Phiên bản hoàn chỉnh — có thêm bảng Home để support multi-tenant

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, DateTime, Enum, Text, Time, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from src.database.core import Base


# ═══════════════════════════════════════════════════════════════════
# ENUMS — giữ nguyên hoàn toàn
# ═══════════════════════════════════════════════════════════════════

class DeviceType(str, enum.Enum):
    LIGHT  = "LIGHT"
    FAN    = "FAN"
    AC     = "AC"
    SENSOR = "SENSOR"
    CAMERA = "CAMERA"
    LOCK   = "LOCK"

class UserRole(str, enum.Enum):
    ADMIN  = "ADMIN"
    MEMBER = "MEMBER"
    GUEST  = "GUEST"

class MetricType(str, enum.Enum):
    TEMP     = "TEMP"
    HUMIDITY = "HUMIDITY"
    POWER_W  = "POWER_W"
    VOLTAGE  = "VOLTAGE"

class EventType(str, enum.Enum):
    DEVICE_ON   = "DEVICE_ON"
    DEVICE_OFF  = "DEVICE_OFF"
    FACE_UNLOCK = "FACE_UNLOCK"
    FORGOT_OFF  = "FORGOT_OFF"
    SCENE_ON    = "SCENE_ON"

class TriggerSource(str, enum.Enum):
    USER                = "USER"
    SCHEDULE            = "SCHEDULE"
    SENSOR              = "SENSOR"
    AUTOMATION          = "AUTOMATION"
    PHYSICAL_ATTRIBUTED = "PHYSICAL_ATTRIBUTED"
    PHYSICAL_UNKNOWN    = "PHYSICAL_UNKNOWN"

class PatternType(str, enum.Enum):
    CLUSTER     = "CLUSTER"
    TIME_HABIT  = "TIME_HABIT"
    CORRELATION = "CORRELATION"
    ANOMALY     = "ANOMALY"

class ActionType(str, enum.Enum):
    SCHEDULE   = "SCHEDULE"
    ALERT      = "ALERT"
    AUTOMATION = "AUTOMATION"

class SuggestionFeedbackType(str, enum.Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    IGNORE = "IGNORE"


# ═══════════════════════════════════════════════════════════════════
# HOME — Bảng mới thêm
# ═══════════════════════════════════════════════════════════════════

class Home(Base):
    """
    Đơn vị tổ chức cao nhất — 1 gia đình / 1 căn nhà.
    Mọi Room, Device, Schedule đều thuộc về 1 Home.
    User có thể thuộc nhiều Home qua bảng HomeUser.
    """
    __tablename__ = "homes"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name       = Column(String(100), nullable=False)  # "Nhà Nguyễn", "Văn phòng A"
    address    = Column(String(255), nullable=True)
    timezone   = Column(String(50), default="Asia/Ho_Chi_Minh")
    # timezone quan trọng cho analytics:
    # thói quen tính theo giờ địa phương, không phải UTC
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    members  = relationship("HomeUser", back_populates="home",
                            cascade="all, delete-orphan")
    rooms    = relationship("Room", back_populates="home",
                            cascade="all, delete-orphan")
    patterns = relationship("UserPattern", back_populates="home")


class HomeUser(Base):
    """
    Bảng trung gian User ↔ Home (many-to-many).
    1 user có thể thuộc nhiều nhà.
    1 nhà có nhiều thành viên với role khác nhau.

    Ví dụ:
        Minh → Nhà bố mẹ (MEMBER) + Nhà riêng (ADMIN)
        Bố   → Nhà bố mẹ (ADMIN)
    """
    __tablename__ = "home_users"

    id        = Column(Integer, primary_key=True, index=True)
    home_id   = Column(UUID(as_uuid=True), ForeignKey("homes.id", ondelete="CASCADE"),
                       nullable=False)
    user_id   = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                       nullable=False)
    role      = Column(Enum(UserRole), default=UserRole.MEMBER)
    # ADMIN  = chủ nhà — thêm/xóa thiết bị, quản lý thành viên
    # MEMBER = thành viên — điều khiển thiết bị, xem analytics
    # GUEST  = khách — chỉ điều khiển thiết bị được phép

    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    home = relationship("Home", back_populates="members")
    user = relationship("User", back_populates="home_memberships")

    __table_args__ = (
        UniqueConstraint("home_id", "user_id", name="uq_home_user"),
        # Mỗi user chỉ có 1 role trong 1 nhà
    )


# ═══════════════════════════════════════════════════════════════════
# CORE TABLES — Thêm home_id vào Room
# ═══════════════════════════════════════════════════════════════════

class Room(Base):
    __tablename__ = "rooms"

    id         = Column(Integer, primary_key=True, index=True)
    home_id    = Column(UUID(as_uuid=True), ForeignKey("homes.id", ondelete="CASCADE"),
                        nullable=False)             # ← THÊM MỚI
    name       = Column(String(50), nullable=False)
    icon       = Column(String(50))
    image_url  = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    home      = relationship("Home", back_populates="rooms")
    devices   = relationship("Device", back_populates="room")
    presences = relationship("UserPresence", back_populates="room")


class Device(Base):
    __tablename__ = "devices"

    id         = Column(String(50), primary_key=True)
    room_id    = Column(Integer, ForeignKey("rooms.id", ondelete="SET NULL"),
                        nullable=True)
    name       = Column(String(100))
    type       = Column(Enum(DeviceType), nullable=False)
    mqtt_topic = Column(String(255), unique=True, nullable=False)
    config     = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    room      = relationship("Room", back_populates="devices")
    state     = relationship("DeviceState", uselist=False, back_populates="device",
                             cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="device")
    logs      = relationship("ActivityLog", back_populates="device")
    patterns  = relationship("UserPattern", back_populates="device")


class User(Base):
    __tablename__ = "users"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email         = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name     = Column(String(100))
    avatar_url    = Column(Text)
    role          = Column(Enum(UserRole), default=UserRole.MEMBER)
    # Lưu ý: role này là role hệ thống (superadmin v.v.)
    # Role trong từng nhà cụ thể → lưu ở HomeUser.role
    face_encoding = Column(ARRAY(Float))
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    home_memberships = relationship("HomeUser", back_populates="user") # ← ĐỔI TÊN
    logs             = relationship("ActivityLog", back_populates="user")
    patterns         = relationship("UserPattern", back_populates="user")
    suggestions      = relationship("SuggestionLog", back_populates="user")
    presence         = relationship("UserPresence", uselist=False, back_populates="user")


# ═══════════════════════════════════════════════════════════════════
# REALTIME STATE — Giữ nguyên
# ═══════════════════════════════════════════════════════════════════

class DeviceState(Base):
    __tablename__ = "device_states"

    device_id    = Column(String(50), ForeignKey("devices.id", ondelete="CASCADE"),
                          primary_key=True)
    is_online    = Column(Boolean, default=False)
    state        = Column(JSONB, default={}, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(),
                          onupdate=func.now())

    device = relationship("Device", back_populates="state")


class Schedule(Base):
    __tablename__ = "schedules"

    id                   = Column(Integer, primary_key=True, index=True)
    device_id            = Column(String(50), ForeignKey("devices.id", ondelete="CASCADE"))
    name                 = Column(String(100))
    time                 = Column(Time, nullable=False)
    days_of_week         = Column(ARRAY(Integer))
    action_payload       = Column(JSONB, nullable=False)
    is_active            = Column(Boolean, default=True)
    source_suggestion_id = Column(Integer, ForeignKey("suggestion_logs.id"), nullable=True)

    device = relationship("Device", back_populates="schedules")


# ═══════════════════════════════════════════════════════════════════
# PRESENCE — Thêm home_id
# ═══════════════════════════════════════════════════════════════════

class UserPresence(Base):
    __tablename__ = "user_presence"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                         unique=True, nullable=False)
    home_id     = Column(UUID(as_uuid=True), ForeignKey("homes.id"),
                         nullable=True)                # ← THÊM MỚI
    # null = chưa xác định đang ở nhà nào (user có nhiều nhà)
    room_id     = Column(Integer, ForeignKey("rooms.id"), nullable=True)
    is_home     = Column(Boolean, default=False)
    detected_by = Column(String(20), default="APP")
    last_seen   = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="presence")
    room = relationship("Room", back_populates="presences")


# ═══════════════════════════════════════════════════════════════════
# ACTIVITY LOG — Thêm home_id
# ═══════════════════════════════════════════════════════════════════

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id               = Column(Integer, primary_key=True, index=True)
    timestamp        = Column(DateTime(timezone=True), server_default=func.now(),
                              nullable=False, index=True)
    session_end      = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    event_type       = Column(Enum(EventType), nullable=False)
    trigger_source   = Column(Enum(TriggerSource), default=TriggerSource.USER,
                              nullable=False)
    device_id        = Column(String(50), ForeignKey("devices.id"), nullable=False)
    user_id          = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    home_id          = Column(UUID(as_uuid=True), ForeignKey("homes.id"),
                              nullable=False, index=True)  # ← THÊM MỚI
    # index=True vì analytics luôn filter theo home_id trước
    description      = Column(Text)
    metadata_json    = Column("metadata", JSONB)

    device = relationship("Device", back_populates="logs")
    user   = relationship("User", back_populates="logs")


# ═══════════════════════════════════════════════════════════════════
# BIG DATA — Giữ nguyên
# ═══════════════════════════════════════════════════════════════════

class SensorData(Base):
    __tablename__ = "sensor_data"

    time        = Column(DateTime(timezone=True), primary_key=True,
                         server_default=func.now())
    device_id   = Column(String(50), ForeignKey("devices.id"), primary_key=True)
    metric_type = Column(Enum(MetricType), primary_key=True)
    value       = Column(Float, nullable=False)


# ═══════════════════════════════════════════════════════════════════
# ANALYTICS OUTPUT — Thêm home_id vào UserPattern
# ═══════════════════════════════════════════════════════════════════

class UserPattern(Base):
    __tablename__ = "user_patterns"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    home_id      = Column(UUID(as_uuid=True), ForeignKey("homes.id"),
                          nullable=False)               # ← THÊM MỚI
    # Quan trọng: cùng 1 user, thói quen ở nhà bố mẹ ≠ nhà riêng
    # KMeans train riêng cho từng (user_id, home_id)
    device_id    = Column(String(50), ForeignKey("devices.id"), nullable=True)
    pattern_type = Column(Enum(PatternType), nullable=False)
    pattern_data = Column(JSONB, nullable=False)
    confidence   = Column(Float, default=1.0)
    computed_at  = Column(DateTime(timezone=True), server_default=func.now())
    is_active    = Column(Boolean, default=True)

    user        = relationship("User", back_populates="patterns")
    home        = relationship("Home", back_populates="patterns")
    device      = relationship("Device", back_populates="patterns")
    suggestions = relationship("SuggestionLog", back_populates="pattern")


class SuggestionLog(Base):
    __tablename__ = "suggestion_logs"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    pattern_id      = Column(Integer, ForeignKey("user_patterns.id"), nullable=True)
    action_type     = Column(Enum(ActionType), nullable=False)
    suggestion_text = Column(Text, nullable=False)
    suggestion_json = Column(JSONB)
    was_accepted    = Column(Boolean, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    user    = relationship("User", back_populates="suggestions")
    pattern = relationship("UserPattern", back_populates="suggestions")
    feedback = relationship("SuggestionFeedbackLog", back_populates="suggestion",
                            cascade="all, delete-orphan", uselist=False)


class SuggestionFeedbackLog(Base):
    __tablename__ = "suggestion_feedback_logs"

    id             = Column(Integer, primary_key=True, index=True)
    suggestion_id  = Column(Integer, ForeignKey("suggestion_logs.id", ondelete="CASCADE"), nullable=False, unique=True)
    user_id        = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    feedback_type   = Column(Enum(SuggestionFeedbackType), nullable=False)
    feedback_reason = Column(Text, nullable=True)
    feedback_time   = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    suggestion = relationship("SuggestionLog", back_populates="feedback")
    user       = relationship("User")


class SuggestionDecisionLog(Base):
    __tablename__ = "suggestion_decision_logs"

    id                 = Column(Integer, primary_key=True, index=True)
    pattern_id         = Column(Integer, ForeignKey("user_patterns.id", ondelete="CASCADE"), nullable=False)
    home_id            = Column(UUID(as_uuid=True), ForeignKey("homes.id", ondelete="CASCADE"), nullable=False)
    user_id            = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    decision_score     = Column(Float, nullable=False)
    should_suggest     = Column(Boolean, nullable=False)
    blocked_by         = Column(String(50), nullable=True)  # e.g., "COOLDOWN", "LOW_SCORE", "USELESS"
    cooldown_signature = Column(String(255), nullable=True)
    metadata_json      = Column(JSONB, nullable=True)
    created_at         = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    pattern = relationship("UserPattern")
    home    = relationship("Home")
    user    = relationship("User")