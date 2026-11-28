import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services.admin_service import AdminChange, add_admin, remove_admin  # noqa: E402
from utils.db_api.repositories import admins  # noqa: E402

DEV = 111


async def test_add_and_remove_admin(session):
    assert await add_admin(session, 222, "Admin", DEV, DEV) is AdminChange.OK
    assert await add_admin(session, 222, "Admin", DEV, DEV) is AdminChange.ALREADY_ADMIN
    assert await admins.all_telegram_ids(session) == [222]
    assert await remove_admin(session, 222, DEV) is AdminChange.OK
    assert await remove_admin(session, 222, DEV) is AdminChange.NOT_FOUND
    assert await admins.all_telegram_ids(session) == []


async def test_developer_protected(session):
    await admins.ensure(session, DEV, "Dev")
    await session.commit()
    assert await add_admin(session, DEV, "Dev", DEV, DEV) is AdminChange.IS_DEVELOPER
    assert await remove_admin(session, DEV, DEV) is AdminChange.IS_DEVELOPER
    assert await admins.all_telegram_ids(session) == [DEV]
