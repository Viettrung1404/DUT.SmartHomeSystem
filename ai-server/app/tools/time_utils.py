from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


def resolve_time_range(name: str | None, timezone_name: str) -> tuple[datetime, datetime]:
    tz = ZoneInfo(timezone_name or "Asia/Ho_Chi_Minh")
    now = datetime.now(tz)
    today = datetime.combine(now.date(), time.min, tzinfo=tz)

    if name == "last_night":
        yesterday = today - timedelta(days=1)
        return yesterday.replace(hour=18), today.replace(hour=6)
    if name == "yesterday":
        start = today - timedelta(days=1)
        return start, today
    if name == "this_week":
        start = today - timedelta(days=today.weekday())
        return start, now
    if name == "last_week":
        this_week = today - timedelta(days=today.weekday())
        return this_week - timedelta(days=7), this_week
    if name == "today":
        return today, now
    return now - timedelta(days=7), now

