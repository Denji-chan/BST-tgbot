from datetime import date, timedelta
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services import cashback_service  # noqa: E402
from services.items import Item  # noqa: E402
from services.purchase_service import CustomerNotFound, register_purchase  # noqa: E402
from services.rules import BusinessRules  # noqa: E402
from utils.db_api.repositories import cashback, purchases, users  # noqa: E402

TZ = ZoneInfo("Asia/Tashkent")
RULES = BusinessRules()


async def _buy(session, user, items, now, use_cashback=False):
    return await register_purchase(
        session,
        user_id=user.id,
        admin_telegram_id=1,
        items=items,
        use_cashback=use_cashback,
        now=now,
        tz=TZ,
        business=RULES,
    )


async def test_first_purchase_earns_cashback(session, make_user, now):
    user = await make_user()
    result = await _buy(session, user, [Item("Ko'ylak", 1, 150_000), Item("Shim", 2, 50_000)], now)
    assert result.calc.total == 250_000
    assert result.calc.cashback_earned == 7_500
    assert result.balance == 7_500
    assert len(await purchases.items_for(session, result.purchase.id)) == 2
    refreshed = await users.get_by_id(session, user.id)
    assert refreshed.last_purchase_at == now


async def test_second_purchase_uses_cashback_fifo(session, make_user, now):
    user = await make_user()
    await _buy(session, user, [Item("A", 1, 100_000)], now - timedelta(days=10))  # +3 000
    await _buy(session, user, [Item("B", 1, 200_000)], now - timedelta(days=5))  # +6 000
    result = await _buy(session, user, [Item("C", 1, 10_000)], now, use_cashback=True)
    # 50% chegarasi: 5 000 ishlatiladi, avval eski partiyadan (3 000), keyin 2 000
    assert result.calc.cashback_used == 5_000
    assert result.calc.paid == 5_000
    assert result.calc.cashback_earned == 150
    assert result.balance == 9_000 - 5_000 + 150
    lots = await cashback.active_lots(session, user.id, now)
    assert [lot.remaining for lot in lots] == [4_000, 150]
    assert await cashback.ledger_sum(session, user.id) == result.balance


async def test_birthday_discount_once_per_year(session, make_user, now):
    today = now.astimezone(TZ).date()
    user = await make_user(birth_date=date(2004, today.month, today.day))
    first = await _buy(session, user, [Item("A", 1, 100_000)], now)
    assert first.calc.birthday_discount == 10_000
    second = await _buy(session, user, [Item("B", 1, 100_000)], now + timedelta(hours=1))
    assert second.calc.birthday_discount == 0


async def test_failure_rolls_back_everything(session, make_user, now, monkeypatch):
    user = await make_user()
    user_id = user.id  # rollback'dan keyin ORM obyektini o'qimaymiz

    async def broken(*args, **kwargs):
        raise RuntimeError("baza xatosi")

    monkeypatch.setattr(cashback_service, "add_credit", broken)
    with pytest.raises(RuntimeError):
        await _buy(session, user, [Item("A", 1, 100_000)], now)
    assert await purchases.count_for_user(session, user_id) == 0
    assert await cashback.ledger_sum(session, user_id) == 0


async def test_unknown_customer(session, now):
    with pytest.raises(CustomerNotFound):
        await register_purchase(
            session,
            user_id=999,
            admin_telegram_id=1,
            items=[Item("A", 1, 1000)],
            use_cashback=False,
            now=now,
            tz=TZ,
            business=RULES,
        )
