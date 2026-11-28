from datetime import date

import pytest

from services.birthday import birthday_in_year, discount_year, is_birthday_today, window_end

EXTRA = 3


@pytest.mark.parametrize(
    "today, expected",
    [
        (date(2026, 5, 13), None),  # bir kun oldin
        (date(2026, 5, 14), 2026),  # tug'ilgan kun
        (date(2026, 5, 17), 2026),  # +3 kun, oxirgi kun
        (date(2026, 5, 18), None),  # +4 kun, tugadi
    ],
)
def test_window_is_birthday_plus_three_days(today, expected):
    assert discount_year(date(2004, 5, 14), today, EXTRA) == expected


def test_window_crosses_new_year():
    birth = date(2003, 12, 30)
    assert discount_year(birth, date(2026, 12, 30), EXTRA) == 2026
    assert discount_year(birth, date(2027, 1, 2), EXTRA) == 2026  # o'tgan yilgi tug'ilgan kun
    assert discount_year(birth, date(2027, 1, 3), EXTRA) is None


def test_leap_day_birthday():
    birth = date(2004, 2, 29)
    assert birthday_in_year(birth, 2027) == date(2027, 2, 28)
    assert birthday_in_year(birth, 2028) == date(2028, 2, 29)
    assert discount_year(birth, date(2027, 2, 28), EXTRA) == 2027
    assert discount_year(birth, date(2027, 3, 3), EXTRA) == 2027
    assert discount_year(birth, date(2027, 3, 4), EXTRA) is None
    assert is_birthday_today(birth, date(2027, 2, 28)) is True
    assert is_birthday_today(birth, date(2028, 2, 28)) is False


def test_is_birthday_today_and_window_end():
    birth = date(2004, 5, 14)
    assert is_birthday_today(birth, date(2026, 5, 14))
    assert not is_birthday_today(birth, date(2026, 5, 15))
    assert window_end(birth, 2026, EXTRA) == date(2026, 5, 17)
