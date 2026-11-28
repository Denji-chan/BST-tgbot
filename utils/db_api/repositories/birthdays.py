from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import BirthdayDiscountUse


async def is_used(session: AsyncSession, user_id: int, year: int) -> bool:
    stmt = select(BirthdayDiscountUse.id).where(
        BirthdayDiscountUse.user_id == user_id, BirthdayDiscountUse.year == year
    )
    return await session.scalar(stmt) is not None


async def add(session: AsyncSession, user_id: int, year: int, purchase_id: int, now: datetime) -> None:
    session.add(BirthdayDiscountUse(user_id=user_id, year=year, purchase_id=purchase_id, created_at=now))
    await session.flush()
