from datetime import datetime, timezone, timedelta

def get_now_wib() -> datetime:
    """
    Returns current time in WIB (UTC+7).
    Returns a naive datetime object suitable for MySQL DATETIME columns.
    """
    # Create timezone-aware UTC time, then convert to WIB, then make naive
    wib_tz = timezone(timedelta(hours=7))
    return datetime.now(timezone.utc).astimezone(wib_tz).replace(tzinfo=None)

def get_now_wib_aware() -> datetime:
    """
    Returns current time in WIB (UTC+7) as a timezone-aware object.
    Suitable for ISO formatting in API responses.
    """
    wib_tz = timezone(timedelta(hours=7))
    return datetime.now(timezone.utc).astimezone(wib_tz)
