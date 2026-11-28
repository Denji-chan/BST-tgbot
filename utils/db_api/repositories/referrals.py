from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import Referral


async def create(session: AsyncSession, referrer_id: int, referred_id: int, created_at: datetime) -> Referral:
    referral = Referral(
        referrer_id=referrer_id,
        referred_id=referred_id,
        status=Referral.STATUS_PENDING,
        created_at=created_at,
    )
    session.add(referral)
    await session.flush()
    return referral


async def get_by_referred(session: AsyncSession, referred_id: int, for_update: bool = False) -> Referral | None:
    stmt = select(Referral).where(Referral.referred_id == referred_id)
    if for_update:
        stmt = stmt.with_for_update()
    return await session.scalar(stmt)


async def counts_for_referrer(session: AsyncSession, referrer_id: int) -> tuple[int, int]:
    """(taklif qilinganlar soni, bonus berilganlar soni)."""
    invited = await session.scalar(select(func.count(Referral.id)).where(Referral.referrer_id == referrer_id))
    rewarded = await session.scalar(
        select(func.count(Referral.id)).where(
            Referral.referrer_id == referrer_id, Referral.status == Referral.STATUS_REWARDED
        )
    )
    return int(invited or 0), int(rewarded or 0)
