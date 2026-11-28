from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import Admin


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> Admin | None:
    return await session.scalar(select(Admin).where(Admin.telegram_id == telegram_id))


async def list_all(session: AsyncSession) -> list[Admin]:
    return list(await session.scalars(select(Admin).order_by(Admin.id)))


async def all_telegram_ids(session: AsyncSession) -> list[int]:
    return list(await session.scalars(select(Admin.telegram_id).order_by(Admin.id)))


async def add(session: AsyncSession, telegram_id: int, full_name: str, added_by: int | None) -> Admin:
    admin = Admin(telegram_id=telegram_id, full_name=full_name, language="uz", added_by=added_by)
    session.add(admin)
    await session.flush()
    return admin


async def ensure(session: AsyncSession, telegram_id: int, full_name: str = "") -> Admin:
    """Admin bo'lmasa yaratadi (Developer uchun ishga tushganda)."""
    admin = await get_by_telegram_id(session, telegram_id)
    if admin is None:
        admin = await add(session, telegram_id, full_name, added_by=None)
    return admin


async def remove(session: AsyncSession, telegram_id: int) -> bool:
    result = await session.execute(delete(Admin).where(Admin.telegram_id == telegram_id))
    return (result.rowcount or 0) > 0


async def set_language(session: AsyncSession, admin: Admin, language: str) -> None:
    admin.language = language
    await session.flush()
