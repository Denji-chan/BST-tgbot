from datetime import UTC, timedelta

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from sqlalchemy.exc import IntegrityError  # noqa: E402

from utils.db_api.repositories import admins, cashback, users  # noqa: E402


async def test_user_created_with_defaults(session, make_user):
    user = await make_user()
    loaded = await users.get_by_telegram_id(session, user.telegram_id)
    assert loaded is not None
    assert loaded.id == user.id
    assert loaded.is_blocked is False
    assert loaded.full_name == "Ism1 Familiya1"


async def test_datetime_round_trip_is_utc_aware(session, make_user, now):
    user = await make_user()
    session.expunge_all()
    loaded = await users.get_by_id(session, user.id)
    assert loaded.registered_at.tzinfo is not None
    assert loaded.registered_at == now
    assert loaded.registered_at.utcoffset() == timedelta(0)
    assert loaded.registered_at.astimezone(UTC) == now


async def test_phone_is_unique(session, make_user):
    await make_user(phone="+998901112233")
    with pytest.raises(IntegrityError):
        await make_user(phone="+998901112233")
    await session.rollback()


async def test_admin_ensure_is_idempotent(session):
    first = await admins.ensure(session, 555, "Dev")
    second = await admins.ensure(session, 555, "Dev")
    await session.commit()
    assert first.id == second.id
    assert await admins.all_telegram_ids(session) == [555]


async def test_cashback_lot_and_debit(session, make_user, now):
    user = await make_user()
    await cashback.add_lot(
        session, user_id=user.id, type_="earn", amount=5000, expires_at=now + timedelta(days=90), created_at=now
    )
    await cashback.add_debit(session, user_id=user.id, type_="spend", amount=2000, created_at=now)
    await session.commit()
    assert await cashback.ledger_sum(session, user.id) == 3000
