from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services.birthday_service import birthday_users  # noqa: E402
from services.items import Item  # noqa: E402
from services.purchase_service import customer_state, register_purchase  # noqa: E402
from services.rules import BusinessRules  # noqa: E402
from utils.db_api.repositories import users  # noqa: E402

TZ = ZoneInfo("Asia/Tashkent")
RULES = BusinessRules()


def local(y, m, d, h=12):
    return datetime(y, m, d, h, tzinfo=TZ)


async def _buy(session, user, amount, at, use_cashback=False):
    return await register_purchase(
        session,
        user_id=user.id,
        admin_telegram_id=1,
        items=[Item("X", 1, amount)],
        use_cashback=use_cashback,
        now=at,
        tz=TZ,
        business=RULES,
    )


async def test_discount_on_third_day_after_birthday(session, make_user):
    user = await make_user(birth_date=date(2004, 5, 14))
    result = await _buy(session, user, 200_000, local(2026, 5, 17))
    assert result.calc.birthday_discount == 20_000
    assert result.calc.total == 180_000
    assert result.calc.cashback_earned == 5_400


async def test_no_discount_outside_window(session, make_user):
    user = await make_user(birth_date=date(2004, 5, 14))
    assert (await _buy(session, user, 200_000, local(2026, 5, 13))).calc.birthday_discount == 0
    assert (await _buy(session, user, 200_000, local(2026, 5, 18))).calc.birthday_discount == 0


async def test_once_per_year_but_again_next_year(session, make_user):
    user = await make_user(birth_date=date(2004, 5, 14))
    assert (await _buy(session, user, 100_000, local(2026, 5, 14))).calc.birthday_discount == 10_000
    assert (await _buy(session, user, 100_000, local(2026, 5, 15))).calc.birthday_discount == 0
    assert (await _buy(session, user, 100_000, local(2027, 5, 14))).calc.birthday_discount == 10_000


async def test_discount_with_cashback(session, make_user):
    user = await make_user(birth_date=date(2004, 5, 14))
    await _buy(session, user, 1_000_000, local(2026, 4, 1))  # +30 000 cashback
    result = await _buy(session, user, 400_000, local(2026, 5, 14), use_cashback=True)
    assert result.calc.birthday_discount == 40_000  # avval chegirma
    assert result.calc.cashback_used == 30_000  # keyin cashback (balans bilan cheklangan)
    assert result.calc.paid == 330_000
    assert result.calc.cashback_earned == 9_900


async def test_customer_state_shows_birthday(session, make_user):
    user = await make_user(birth_date=date(2004, 5, 14))
    state = await customer_state(session, user, local(2026, 5, 16), TZ, RULES)
    assert state.birthday_year == 2026
    state = await customer_state(session, user, local(2026, 5, 20), TZ, RULES)
    assert state.birthday_year is None


async def test_birthday_users_today_skips_blocked(session, make_user):
    a = await make_user(birth_date=date(2004, 5, 14))
    b = await make_user(birth_date=date(2001, 5, 14))
    await make_user(birth_date=date(2004, 5, 15))
    await users.set_blocked_by_telegram_id(session, b.telegram_id, True)
    await session.commit()
    found = await birthday_users(session, date(2026, 5, 14))
    assert [u.id for u in found] == [a.id]
    assert await birthday_users(session, date(2026, 5, 14) + timedelta(days=1)) != []
