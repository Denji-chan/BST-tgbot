from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services import cashback_service  # noqa: E402
from services.items import Item  # noqa: E402
from services.purchase_service import register_purchase  # noqa: E402
from services.rules import BusinessRules  # noqa: E402
from services.stats_service import get_stats  # noqa: E402
from utils.db_api.repositories import users  # noqa: E402

TZ = ZoneInfo("Asia/Tashkent")
RULES = BusinessRules()


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


async def test_stats_by_period(session, make_user, now):
    old_user = await make_user(registered_at=now - timedelta(days=40))
    new_user = await make_user()
    await _buy(session, old_user, 100_000, now - timedelta(days=20))  # +3 000, 20 kun oldin
    await _buy(session, new_user, 200_000, now)  # +6 000, bugun
    await _buy(session, old_user, 10_000, now, use_cashback=True)  # 3 000 ishlatildi, +150

    today = await get_stats(session, "today", now, TZ)
    assert today.customers_total == 2
    assert today.customers_new == 1
    assert today.purchases_count == 2
    assert today.purchases_sum == 210_000
    assert today.cashback_given == 6_150
    assert today.cashback_used == 3_000
    assert today.cashback_expired == 0

    month = await get_stats(session, "d30", now, TZ)
    assert month.purchases_count == 3
    assert month.cashback_given == 9_150

    everything = await get_stats(session, "all", now, TZ)
    assert everything.customers_new == 2


async def test_expired_cashback_in_stats(session, make_user, now):
    user = await make_user()
    await _buy(session, user, 100_000, now - timedelta(days=95))
    later = now
    await cashback_service.expire_due(session, later)
    stats = await get_stats(session, "today", later, TZ)
    assert stats.cashback_expired == 3_000


async def test_users_list_rows(session, make_user, now):
    user = await make_user()
    await _buy(session, user, 100_000, now)
    rows = await users.list_page(session, now, 0, 10)
    assert len(rows) == 1
    assert rows[0].balance == 3_000
    assert rows[0].purchases_count == 1
    assert rows[0].purchases_sum == 100_000
    assert len(await users.list_all(session, now)) == 1
