"""Ro'yxatdan o'tishdagi ma'lumotlarni tekshirish."""

import re
from datetime import date, datetime

NAME_MIN = 2
NAME_MAX = 40
AGE_MIN = 7
AGE_MAX = 100
_NAME_EXTRA = set(" '-ʻ’`‘")
_DATE_FORMATS = ("%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y")


def clean_name(raw: str | None) -> str | None:
    """Ism yoki familiyani tozalaydi. Noto'g'ri bo'lsa None."""
    name = " ".join((raw or "").split())
    if not NAME_MIN <= len(name) <= NAME_MAX:
        return None
    if not all(ch.isalpha() or ch in _NAME_EXTRA for ch in name):
        return None
    if not any(ch.isalpha() for ch in name):
        return None
    return name


def _age(birth: date, today: date) -> int:
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def parse_birth_date(raw: str | None, today: date) -> date | None:
    """'14.05.2004' -> date. Kelajakdagi sana yoki 7-100 yosh oralig'idan tashqari bo'lsa None."""
    text = re.sub(r"\s", "", raw or "")
    for fmt in _DATE_FORMATS:
        try:
            value = datetime.strptime(text, fmt).date()
        except ValueError:
            continue
        if value > today or not AGE_MIN <= _age(value, today) <= AGE_MAX:
            return None
        return value
    return None


def parse_telegram_id(text: str | None) -> int | None:
    """Admin qo'shishda yozilgan Telegram ID raqami."""
    raw = (text or "").strip()
    if raw.isdigit() and 5 <= len(raw) <= 15:
        return int(raw)
    return None
