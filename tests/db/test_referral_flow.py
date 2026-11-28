from datetime import date, timedelta
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services.items import Item  # noqa: E402
from services.purchase_service import register_purchase  # noqa: E402
from services.registration_service import register_user  # noqa: E402
from services.rules import BusinessRules  # noqa: E402
from utils.db_api.repositories import cashback, referrals  # noqa: E402

TZ = ZoneInfo("Asia/Tashkent")
RULES = BusinessRules()


async def _register_friend(session, referrer, now, n=1):
    result = await register_user(
        session,
        telegram_id=5000 + n,
        first_name="Do'st",
        last_name="Test",
        phone=f"+99899000{n:04d}",
        birth_date=date(2005, 1, 1),
        language="uz",
        referrer_id=referrer.id,
        now=now,
    )
    return result.user


async def _buy(session, user, amount, now):
    return await register_purchase(
        session,
        user_id=user.id,
        admin_telegram_id=1,
        items=[Item("X", 1, amount)],
        use_cashback=False,
        now=now,
        tz=TZ,
        business=RULES,
    )


async def test_bonus_for_big_first_purchase(session, make_user, now):
    referrer = await make_user()
    friend = await _register_friend(session, referrer, now)
    result = await _buy(session, friend, 320_000, now)

    assert result.calc.cashback_earned == 9_600  # do'stga oddiy 3%
    assert result.referral_reward is not None
    assert result.referral_reward.referrer.id == referrer.id
    assert result.referral_reward.amount == 30_000
    assert await cashback.balance(session, referrer.id, now) == 30_000
    referral = await referrals.get_by_referred(session, friend.id)
    assert referral.status == "rewarded"
    assert referral.purchase_id == result.purchase.id


async def test_bonus_at_exact_threshold(session, make_user, now):
    referrer = await make_user()
    friend = await _register_friend(session, referrer, now)
    result = await _buy(session, friend, 300_000, now)
    assert result.referral_reward is not None


async def test_small_first_purchase_closes_referral(session, make_user, now):
    referrer = await make_user()
    friend = await _register_friend(session, referrer, now)
    first = await _buy(session, friend, 280_000, now)
    assert first.referral_reward is None
    assert (await referrals.get_by_referred(session, friend.id)).status == "rejected"

    second = await _buy(session, friend, 500_000, now + timedelta(days=1))
    assert second.referral_reward is None  # faqat birinchi xarid hisobga olinadi
    assert await cashback.balance(session, referrer.id, now + timedelta(days=1)) == 0


async def test_bonus_only_once_per_friend(session, make_user, now):
    referrer = await make_user()
    friend = await _register_friend(session, referrer, now)
    await _buy(session, friend, 400_000, now)
    again = await _buy(session, friend, 400_000, now + timedelta(days=1))
    assert again.referral_reward is None
    assert await cashback.balance(session, referrer.id, now + timedelta(days=1)) == 30_000


async def test_two_friends_two_bonuses(session, make_user, now):
    referrer = await make_user()
    f1 = await _register_friend(session, referrer, now, n=1)
    f2 = await _register_friend(session, referrer, now, n=2)
    await _buy(session, f1, 300_000, now)
    await _buy(session, f2, 300_000, now)
    assert await cashback.balance(session, referrer.id, now) == 60_000
    assert await referrals.counts_for_referrer(session, referrer.id) == (2, 2)


async def test_referral_bonus_expires_after_90_days(session, make_user, now):
    referrer = await make_user()
    friend = await _register_friend(session, referrer, now)
    await _buy(session, friend, 300_000, now)
    assert await cashback.balance(session, referrer.id, now + timedelta(days=89)) == 30_000
    assert await cashback.balance(session, referrer.id, now + timedelta(days=91)) == 0


async def test_user_without_referral_has_no_reward(session, make_user, now):
    user = await make_user()
    result = await _buy(session, user, 500_000, now)
    assert result.referral_reward is None
