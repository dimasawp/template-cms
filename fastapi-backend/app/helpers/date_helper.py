from typing import Optional
from datetime import datetime, timezone, timedelta

WIB_TZ = timezone(timedelta(hours=7))


def get_now_wib() -> datetime:
    return datetime.now(timezone.utc).astimezone(WIB_TZ).replace(tzinfo=None)


def get_now_wib_aware() -> datetime:
    return datetime.now(timezone.utc).astimezone(WIB_TZ)


def fmt_dt(dt: Optional[datetime]) -> Optional[str]:
    """Serialize datetime to ISO-8601 with +07:00 offset.
    Naive datetimes are assumed to be WIB."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=WIB_TZ).isoformat()
    return dt.isoformat()
