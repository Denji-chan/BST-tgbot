from datetime import timedelta
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services import cashback_service  # noqa: E402
from services.cashback import InsufficientCashback  # noqa: E402
from services.profile_service import get_profile  # noqa: E402
from services.rules import BusinessRules  # noqa: E402
from utils.db_api.repositories import cashback  # noqa: E402

TZ = ZoneInfo("Asia/Tashkent")
RULES = BusinessRules()


async def _credit(session, user, amount, at):
    await cashback_service.add_credit(
        session, user_id=user.id, type_="earn", amount=amount, now=at, tz=TZ, business=RULES
    )


async def test_spend_fifo_and_ledger_invariant(session, make_user, now):
    user = await make_user()
    await _credit(session, user, 3_000, now - timedelta(days=30))
    await _credit(session, user, 10_000, now)
    await session.commit()

    await cashback_service.spend(session, user_id=user.id, amount=8_000, now=now)
    await session.commit()

    lots = await cashback.active_lots(session, user.id, now)
    assert [lot.remaining for lot in lots] == [5_000]  # eski partiya tugadi
    assert await cashback.balance(session, user.id, now) == 5_000
    assert await cashback.ledger_sum(session, user.id) == 5_000


async def test_spend_more_than_balance_fails(session, make_user, now):
    user = await make_user()
    user_id = user.id
    await _credit(session, user, 1_000, now)
    await session.commit()
    with pytest.raises(InsufficientCashback):
        await cashback_service.spend(session, user_id=user_id, amount=1_001, now=now)
    await session.rollback()
    assert await cashback.balance(session, user_id, now) == 1_000


async def test_zero_credit_is_not_written(session, make_user, now):
    user = await make_user()
    assert (
        await cashback_service.add_credit(
            session, user_id=user.id, type_="earn", amount=0, now=now, tz=TZ, business=RULES
        )
        is None
    )


async def test_expire_after_90_days(session, make_user, now):
    user = await make_user()
    other = await make_user()
    await _credit(session, user, 4_000, now)
    await _credit(session, other, 1_000, now + timedelta(days=10))
    await session.commit()
    await cashback_service.spend(session, user_id=user.id, amount=1_500, now=now)
    await session.commit()

    # 89-kun: hali kuymaydi
    assert await cashback_service.expire_due(session, now + timedelta(days=89)) == {}
    # 91-kun: qolgan 2 500 kuyadi, boshqa mijozniki tegmaydi
    burned = await cashback_service.expire_due(session, now + timedelta(days=91))
    assert burned == {user.id: 2_500}
    assert await cashback.ledger_sum(session, user.id) == 0
    assert await cashback.ledger_sum(session, other.id) == 1_000
    # Qayta ishga tushsa, ikkinchi marta kuymaydi
    assert await cashback_service.expire_due(session, now + timedelta(days=92)) == {}


async def test_profile_shows_balance_and_nearest_expiry(session, make_user, now):
    user = await make_user()
    await _credit(session, user, 2_000, now - timedelta(days=60))
    await _credit(session, user, 5_000, now)
    await session.commit()
    profile = await get_profile(session, user, now, TZ)
    assert profile.balance == 7_000
    burn_day, amount = profile.nearest_expiry
    assert amount == 2_000
    assert burn_day == (now - timedelta(days=60)).astimezone(TZ).date() + timedelta(days=90)
    assert profile.last_purchases == []
