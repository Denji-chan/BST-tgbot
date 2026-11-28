from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from services.cashback import (
    InsufficientCashback,
    Lot,
    active_balance,
    allocate_fifo,
    calculate_purchase,
    earned_for,
    expires_at_for,
    max_usable,
    nearest_expiry,
    select_expired,
)
from services.rules import BusinessRules

TZ = ZoneInfo("Asia/Tashkent")
RULES = BusinessRules()
UTC = UTC


def dt(y, m, d, h=12):
    return datetime(y, m, d, h, tzinfo=TZ)


# --- 3% va yaxlitlash ---


@pytest.mark.parametrize("paid, expected", [(100_000, 3000), (123_456, 3703), (99, 2), (33, 0), (0, 0)])
def test_earned_is_3_percent_rounded_down(paid, expected):
    assert earned_for(paid, RULES) == expected


# --- 50% chegara ---


def test_max_usable_limited_by_half_of_total():
    assert max_usable(total=100_000, balance=80_000, rules=RULES) == 50_000


def test_max_usable_limited_by_balance():
    assert max_usable(total=100_000, balance=12_000, rules=RULES) == 12_000


def test_max_usable_respects_config():
    assert max_usable(total=100_000, balance=80_000, rules=BusinessRules(cashback_max_use_percent=30)) == 30_000
    assert max_usable(total=100_000, balance=80_000, rules=BusinessRules(cashback_max_use_percent=0)) == 0


def test_max_usable_rounds_down():
    assert max_usable(total=99_999, balance=10**9, rules=RULES) == 49_999


# --- To'liq hisob ---


def test_purchase_without_cashback():
    calc = calculate_purchase(250_000, balance=20_000, use_cashback=False, birthday_applies=False, rules=RULES)
    assert calc.total == 250_000
    assert calc.cashback_available == 20_000
    assert calc.cashback_used == 0
    assert calc.paid == 250_000
    assert calc.cashback_earned == 7_500


def test_purchase_with_cashback_earns_on_paid_only():
    calc = calculate_purchase(250_000, balance=5_000, use_cashback=True, birthday_applies=False, rules=RULES)
    assert calc.cashback_used == 5_000
    assert calc.paid == 245_000
    assert calc.cashback_earned == 7_350


def test_birthday_discount_first_then_cashback():
    # 400 000 -> 10% -> 360 000; cashback 50% chegarasi 180 000, balans 200 000 -> 180 000
    calc = calculate_purchase(400_000, balance=200_000, use_cashback=True, birthday_applies=True, rules=RULES)
    assert calc.birthday_discount == 40_000
    assert calc.total == 360_000
    assert calc.cashback_used == 180_000
    assert calc.paid == 180_000
    assert calc.cashback_earned == 5_400


def test_birthday_discount_rounds_down():
    calc = calculate_purchase(99_995, balance=0, use_cashback=False, birthday_applies=True, rules=RULES)
    assert calc.birthday_discount == 9_999
    assert calc.total == 89_996


def test_invalid_subtotal():
    with pytest.raises(ValueError):
        calculate_purchase(0, balance=0, use_cashback=False, birthday_applies=False, rules=RULES)


# --- 90 kun ---


def test_expiry_is_90_days_from_earning_day():
    earned = dt(2026, 9, 1, 23)  # 1-sentabr kechqurun
    expires = expires_at_for(earned, TZ, 90)
    assert expires.tzinfo is not None
    assert expires.astimezone(TZ) == datetime(2026, 11, 30, 0, 0, tzinfo=TZ)
    assert expires.utcoffset() == timedelta(0)


def test_expiry_uses_local_day_not_utc_day():
    # 1-sentabr 02:00 Toshkent = 31-avgust 21:00 UTC. Mahalliy kun hisoblanadi.
    earned = dt(2026, 9, 1, 2)
    assert expires_at_for(earned, TZ, 90).astimezone(TZ).date() == date(2026, 11, 30)


# --- FIFO ---


def _lots():
    return [
        Lot(id=2, remaining=10_000, expires_at=dt(2027, 1, 20)),
        Lot(id=1, remaining=3_000, expires_at=dt(2026, 12, 5)),
    ]


def test_fifo_takes_oldest_first():
    assert allocate_fifo(_lots(), 8_000) == [(1, 3_000), (2, 5_000)]


def test_fifo_exact_and_zero():
    assert allocate_fifo(_lots(), 3_000) == [(1, 3_000)]
    assert allocate_fifo(_lots(), 0) == []


def test_fifo_insufficient():
    with pytest.raises(InsufficientCashback):
        allocate_fifo(_lots(), 13_001)


def test_fifo_same_expiry_by_id():
    lots = [Lot(id=5, remaining=100, expires_at=dt(2026, 12, 1)), Lot(id=3, remaining=100, expires_at=dt(2026, 12, 1))]
    assert allocate_fifo(lots, 150) == [(3, 100), (5, 50)]


# --- Kuyish va balans ---


def test_select_expired_and_active_balance():
    now = dt(2026, 12, 6)
    lots = _lots() + [Lot(id=3, remaining=0, expires_at=dt(2026, 11, 1))]
    assert [lot.id for lot in select_expired(lots, now)] == [1]
    assert active_balance(lots, now) == 10_000


def test_nearest_expiry_sums_same_day():
    now = dt(2026, 12, 1)
    lots = _lots() + [Lot(id=3, remaining=500, expires_at=dt(2026, 12, 5, 0))]
    assert nearest_expiry(lots, now, TZ) == (date(2026, 12, 5), 3_500)


def test_nearest_expiry_empty():
    assert nearest_expiry([], dt(2026, 12, 1), TZ) is None
    assert nearest_expiry([Lot(id=1, remaining=0, expires_at=dt(2027, 1, 1))], dt(2026, 12, 1), TZ) is None
