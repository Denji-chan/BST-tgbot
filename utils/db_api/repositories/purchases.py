from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from services.items import Item
from utils.db_api.models import Purchase, PurchaseItem


async def create(
    session: AsyncSession,
    *,
    user_id: int,
    admin_telegram_id: int,
    subtotal: int,
    birthday_discount: int,
    total: int,
    cashback_used: int,
    paid: int,
    cashback_earned: int,
    items: list[Item],
    created_at: datetime,
) -> Purchase:
    purchase = Purchase(
        user_id=user_id,
        admin_telegram_id=admin_telegram_id,
        subtotal=subtotal,
        birthday_discount=birthday_discount,
        total=total,
        cashback_used=cashback_used,
        paid=paid,
        cashback_earned=cashback_earned,
        created_at=created_at,
    )
    session.add(purchase)
    await session.flush()
    for item in items:
        session.add(
            PurchaseItem(
                purchase_id=purchase.id,
                name=item.name,
                quantity=item.quantity,
                price=item.price,
                amount=item.amount,
            )
        )
    await session.flush()
    return purchase


async def count_for_user(session: AsyncSession, user_id: int) -> int:
    return int(await session.scalar(select(func.count(Purchase.id)).where(Purchase.user_id == user_id)) or 0)


async def last_for_user(session: AsyncSession, user_id: int, limit: int = 5) -> list[Purchase]:
    stmt = (
        select(Purchase)
        .where(Purchase.user_id == user_id)
        .order_by(Purchase.created_at.desc(), Purchase.id.desc())
        .limit(limit)
    )
    return list(await session.scalars(stmt))


async def items_for(session: AsyncSession, purchase_id: int) -> list[PurchaseItem]:
    stmt = select(PurchaseItem).where(PurchaseItem.purchase_id == purchase_id).order_by(PurchaseItem.id)
    return list(await session.scalars(stmt))


async def stats(session: AsyncSession, since: datetime | None) -> tuple[int, int]:
    """(xaridlar soni, xaridlar summasi) davr bo'yicha."""
    stmt = select(func.count(Purchase.id), func.coalesce(func.sum(Purchase.total), 0))
    if since is not None:
        stmt = stmt.where(Purchase.created_at >= since)
    count, total = (await session.execute(stmt)).one()
    return int(count), int(total)
