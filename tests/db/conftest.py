"""Baza testlari uchun umumiy fixture'lar (SQLite xotirada, aiosqlite).

Kerakli paketlar (sqlalchemy, aiosqlite, pytest-asyncio) o'rnatilmagan bo'lsa,
bu papkadagi testlar avtomatik o'tkazib yuboriladi.
"""

from datetime import UTC, date, datetime

import pytest

try:
    import pytest_asyncio
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import StaticPool

    from utils.db_api import models  # noqa: F401
    from utils.db_api.base import Base

    HAS_DB_DEPS = True
except ImportError:  # pragma: no cover
    HAS_DB_DEPS = False

NOW = datetime(2026, 12, 1, 9, 0, tzinfo=UTC)  # 14:00 Toshkent vaqti

if HAS_DB_DEPS:

    @pytest_asyncio.fixture
    async def session_factory():
        # StaticPool: barcha sessiyalar bitta xotiradagi bazani ko'radi
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=StaticPool)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        yield factory
        await engine.dispose()

    @pytest_asyncio.fixture
    async def session(session_factory):
        async with session_factory() as s:
            yield s

    @pytest_asyncio.fixture
    async def make_user(session):
        from utils.db_api.repositories import users

        counter = {"n": 0}

        async def _make(**overrides):
            counter["n"] += 1
            n = counter["n"]
            data = {
                "telegram_id": 1000 + n,
                "first_name": f"Ism{n}",
                "last_name": f"Familiya{n}",
                "phone": f"+99890000{n:04d}",
                "birth_date": date(2004, 5, 14),
                "language": "uz",
                "registered_at": NOW,
            }
            data.update(overrides)
            user = await users.create(session, **data)
            await session.commit()
            return user

        return _make


@pytest.fixture
def now():
    return NOW
