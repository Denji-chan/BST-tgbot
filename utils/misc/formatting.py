"""Matn formatlash yordamchilari (aiogram'ga bog'liq emas)."""

import html
from datetime import date, datetime
from zoneinfo import ZoneInfo


def money(amount: int) -> str:
    """150000 -> '150 000'."""
    return f"{amount:,}".replace(",", " ")


def esc(text: str | None) -> str:
    """Foydalanuvchi yozgan matnni HTML xabarga xavfsiz qo'yish."""
    return html.escape(text or "", quote=False)


def fmt_date(value: date) -> str:
    return value.strftime("%d.%m.%Y")


def fmt_datetime(value: datetime, tz: ZoneInfo) -> str:
    return value.astimezone(tz).strftime("%d.%m.%Y %H:%M")


def local_date(value: datetime, tz: ZoneInfo) -> date:
    return value.astimezone(tz).date()
