from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import CashbackTransaction


async def active_lots(
    session: AsyncSession, user_id: int, now: datetime, for_update: bool = False
) -> list[CashbackTransaction]:
    """Muddati o'tmagan, qoldig'i bor partiyalar: eng eskisi birinchi (FIFO)."""
    stmt = (
        select(CashbackTransaction)
        .where(
            CashbackTransaction.user_id == user_id,
            CashbackTransaction.remaining > 0,
            CashbackTransaction.expires_at > now,
        )
        .order_by(CashbackTransaction.expires_at, CashbackTransaction.id)
    )
    if for_update:
        stmt = stmt.with_for_update()
    return list(await session.scalars(stmt))


async def balance(session: AsyncSession, user_id: int, now: datetime) -> int:
    stmt = select(func.coalesce(func.sum(CashbackTransaction.remaining), 0)).where(
        CashbackTransaction.user_id == user_id,
        CashbackTransaction.remaining > 0,
        CashbackTransaction.expires_at > now,
    )
    return int(await session.scalar(stmt) or 0)


async def ledger_sum(session: AsyncSession, user_id: int) -> int:
    """Barcha yozuvlar yig'indisi. Kuyish ishlagandan keyin balansga teng bo'ladi."""
    stmt = select(func.coalesce(func.sum(CashbackTransaction.amount), 0)).where(CashbackTransaction.user_id == user_id)
    return int(await session.scalar(stmt) or 0)


async def add_lot(
    session: AsyncSession,
    *,
    user_id: int,
    type_: str,
    amount: int,
    expires_at: datetime,
    created_at: datetime,
    purchase_id: int | None = None,
) -> CashbackTransaction:
    tx = CashbackTransaction(
        user_id=user_id,
        type=type_,
        amount=amount,
        remaining=amount,
        expires_at=expires_at,
        purchase_id=purchase_id,
        created_at=created_at,
    )
    session.add(tx)
    await session.flush()
    return tx


async def add_debit(
    session: AsyncSession,
    *,
    user_id: int,
    type_: str,
    amount: int,
    created_at: datetime,
    purchase_id: int | None = None,
) -> CashbackTransaction:
    """Yechish yozuvi: amount musbat beriladi, bazaga manfiy yoziladi."""
    tx = CashbackTransaction(
        user_id=user_id,
        type=type_,
        amount=-amount,
        remaining=0,
        expires_at=None,
        purchase_id=purchase_id,
        created_at=created_at,
    )
    session.add(tx)
    await session.flush()
    return tx


async def expired_lots(session: AsyncSession, now: datetime) -> list[CashbackTransaction]:
    stmt = (
        select(CashbackTransaction)
        .where(CashbackTransaction.remaining > 0, CashbackTransaction.expires_at <= now)
        .order_by(CashbackTransaction.user_id, CashbackTransaction.expires_at, CashbackTransaction.id)
        .with_for_update()
    )
    return list(await session.scalars(stmt))


async def sum_by_types(session: AsyncSession, types: list[str], since: datetime | None) -> int:
    """Davr bo'yicha yozuvlar yig'indisi (statistika uchun), musbat son qaytaradi."""
    stmt = select(func.coalesce(func.sum(CashbackTransaction.amount), 0)).where(CashbackTransaction.type.in_(types))
    if since is not None:
        stmt = stmt.where(CashbackTransaction.created_at >= since)
    return abs(int(await session.scalar(stmt) or 0))
