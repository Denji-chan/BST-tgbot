"""Tug'ilgan kun chegirmasi qoidalari (sof funksiyalar).

Chegirma tug'ilgan kuni va undan keyingi 3 kun ichida (jami 4 kun), yiliga bir marta amal qiladi.
29-fevralda tug'ilganlar uchun kabisa bo'lmagan yilda 28-fevral olinadi.
"""

from datetime import date, timedelta


def birthday_in_year(birth: date, year: int) -> date:
    try:
        return birth.replace(year=year)
    except ValueError:  # 29-fevral, kabisa bo'lmagan yil
        return date(year, 2, 28)


def discount_year(birth: date, today: date, extra_days: int) -> int | None:
    """Bugun chegirma oynasi ichida bo'lsa, o'sha tug'ilgan kunning yili. Aks holda None.

    Yil "yiliga bir marta" qoidasi uchun kalit bo'ladi (31-dekabr oynasi yanvarga o'tsa ham).
    """
    for year in (today.year, today.year - 1):
        start = birthday_in_year(birth, year)
        if start <= today <= start + timedelta(days=extra_days):
            return year
    return None


def is_birthday_today(birth: date, today: date) -> bool:
    return birthday_in_year(birth, today.year) == today


def window_end(birth: date, year: int, extra_days: int) -> date:
    return birthday_in_year(birth, year) + timedelta(days=extra_days)
