"""Statistika davrlari: bugun, 7 kun, 30 kun, jami."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

PERIODS: tuple[str, ...] = ("today", "d7", "d30", "all")


def period_start(period: str, now: datetime, tz: ZoneInfo) -> datetime | None:
    """Davr boshlanishi (timezone'li). "all" uchun None."""
    if period == "today":
        return datetime.combine(now.astimezone(tz).date(), time(0, 0), tzinfo=tz)
    if period == "d7":
        return now - timedelta(days=7)
    if period == "d30":
        return now - timedelta(days=30)
    if period == "all":
        return None
    raise ValueError(f"Noma'lum davr: {period}")


def total_pages(total: int, per_page: int) -> int:
    return max(1, -(-total // per_page))


def clamp_page(page: int, total: int, per_page: int) -> int:
    return min(max(page, 0), total_pages(total, per_page) - 1)
