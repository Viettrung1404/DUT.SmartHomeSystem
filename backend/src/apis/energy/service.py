from src.entities.models import EnergyLog, Device, Room, HomeUser

from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.exceptions import ForbiddenError
from . import models

def _check_home_access(db: Session, home_id: UUID, user_id: UUID):
    member = db.query(HomeUser).filter(
        HomeUser.home_id == home_id, HomeUser.user_id == user_id
    ).first()
    if not member:
        raise ForbiddenError("Bạn không có quyền truy cập")

def _get_home_devices(db: Session, home_id: UUID) -> list[Device]:
    rooms = db.query(Room).filter(Room.home_id == home_id).all()
    room_ids = [r.id for r in rooms]
    if not room_ids:
        return []
    return db.query(Device).filter(Device.room_id.in_(room_ids)).all()

def get_daily_energy(db: Session, home_id: UUID, user_id: UUID) -> models.EnergySummaryResponse:
    _check_home_access(db, home_id, user_id)
    devices = _get_home_devices(db, home_id)
    device_ids = [d.id for d in devices]

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday = today - timedelta(days=1)

    # Today's data by 3-hour intervals
    data_points = []
    total_today = 0.0
    for hour in range(0, 24, 3):
        start = today + timedelta(hours=hour)
        end = start + timedelta(hours=3)
        usage = 0.0
        if device_ids:
            result = db.query(func.sum(EnergyLog.power_usage)).filter(
                EnergyLog.device_id.in_(device_ids),
                EnergyLog.timestamp >= start, EnergyLog.timestamp < end
            ).scalar()
            usage = result or 0.0
        total_today += usage
        data_points.append(models.EnergyDataPoint(label=f"{hour}h", value=round(usage, 2)))

    # Yesterday total for comparison
    total_yesterday = 0.0
    if device_ids:
        result = db.query(func.sum(EnergyLog.power_usage)).filter(
            EnergyLog.device_id.in_(device_ids),
            EnergyLog.timestamp >= yesterday, EnergyLog.timestamp < today
        ).scalar()
        total_yesterday = result or 0.0

    comparison = None
    if total_yesterday > 0:
        comparison = round(((total_today - total_yesterday) / total_yesterday) * 100, 1)

    # Breakdown by device
    breakdown = []
    for d in devices:
        usage = 0.0
        result = db.query(func.sum(EnergyLog.power_usage)).filter(
            EnergyLog.device_id == d.id,
            EnergyLog.timestamp >= today
        ).scalar()
        usage = result or 0.0
        if usage > 0:
            breakdown.append(models.EnergyBreakdown(
                device_name=d.name, device_type=d.type, usage=round(usage, 2),
                percentage=round((usage / total_today * 100) if total_today > 0 else 0, 1)
            ))
    breakdown.sort(key=lambda x: x.usage, reverse=True)

    return models.EnergySummaryResponse(
        total=round(total_today, 2), data=data_points,
        breakdown=breakdown, comparison=comparison
    )

def get_weekly_energy(db: Session, home_id: UUID, user_id: UUID) -> models.EnergySummaryResponse:
    _check_home_access(db, home_id, user_id)
    devices = _get_home_devices(db, home_id)
    device_ids = [d.id for d in devices]

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    day_labels = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']

    data_points = []
    total = 0.0
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        next_day = day + timedelta(days=1)
        usage = 0.0
        if device_ids:
            result = db.query(func.sum(EnergyLog.power_usage)).filter(
                EnergyLog.device_id.in_(device_ids),
                EnergyLog.timestamp >= day, EnergyLog.timestamp < next_day
            ).scalar()
            usage = result or 0.0
        total += usage
        dow = day.weekday()
        data_points.append(models.EnergyDataPoint(label=day_labels[dow], value=round(usage, 2)))

    return models.EnergySummaryResponse(total=round(total, 2), data=data_points)

def get_monthly_energy(db: Session, home_id: UUID, user_id: UUID) -> models.EnergySummaryResponse:
    _check_home_access(db, home_id, user_id)
    devices = _get_home_devices(db, home_id)
    device_ids = [d.id for d in devices]

    now = datetime.now(timezone.utc)
    month_labels = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']

    data_points = []
    total = 0.0
    for m in range(1, now.month + 1):
        start = now.replace(month=m, day=1, hour=0, minute=0, second=0, microsecond=0)
        if m < 12:
            end = now.replace(month=m + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        usage = 0.0
        if device_ids:
            result = db.query(func.sum(EnergyLog.power_usage)).filter(
                EnergyLog.device_id.in_(device_ids),
                EnergyLog.timestamp >= start, EnergyLog.timestamp < end
            ).scalar()
            usage = result or 0.0
        total += usage
        data_points.append(models.EnergyDataPoint(label=month_labels[m - 1], value=round(usage, 2)))

    return models.EnergySummaryResponse(total=round(total, 2), data=data_points)
