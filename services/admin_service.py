from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.repositories import admins


class AdminChange(Enum):
    OK = "ok"
    ALREADY_ADMIN = "already_admin"
    NOT_FOUND = "not_found"
    IS_DEVELOPER = "is_developer"


async def add_admin(
    session: AsyncSession, telegram_id: int, full_name: str, added_by: int, developer_id: int
) -> AdminChange:
    if telegram_id == developer_id:
        return AdminChange.IS_DEVELOPER
    if await admins.get_by_telegram_id(session, telegram_id) is not None:
        return AdminChange.ALREADY_ADMIN
    await admins.add(session, telegram_id, full_name, added_by)
    await session.commit()
    return AdminChange.OK


async def remove_admin(session: AsyncSession, telegram_id: int, developer_id: int) -> AdminChange:
    if telegram_id == developer_id:
        return AdminChange.IS_DEVELOPER
    removed = await admins.remove(session, telegram_id)
    await session.commit()
    return AdminChange.OK if removed else AdminChange.NOT_FOUND
