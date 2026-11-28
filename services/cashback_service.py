"""Cashback ledger'i bilan ishlash. Funksiyalar commit qilmaydi: chaqiruvchi bitta tranzaksiyada yakunlaydi."""

from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from services import cashback as rules
from services.rules import BusinessRules
from utils.db_api.models import CashbackTransaction
from utils.db_api.repositories import cashback


async def add_credit(
    session: AsyncSession,
    *,
    user_id: int,
    type_: str,
    amount: int,
    now: datetime,
    tz: ZoneInfo,
    business: BusinessRules,
    purchase_id: int | None = None,
) -> CashbackTransaction | None:
    """Yangi partiya qo'shadi (xarid cashbacki yoki referal bonusi). 0 bo'lsa hech narsa yozilmaydi."""
    if amount <= 0:
        return None
    return await cashback.add_lot(
        session,
        user_id=user_id,
        type_=type_,
        amount=amount,
        expires_at=rules.expires_at_for(now, tz, business.cashback_lifetime_days),
        created_at=now,
        purchase_id=purchase_id,
    )


async def spend(
    session: AsyncSession,
    *,
    user_id: int,
    amount: int,
    now: datetime,
    purchase_id: int | None = None,
) -> None:
    """Cashbackni FIFO tartibida yechadi. Balans yetmasa InsufficientCashback."""
    if amount <= 0:
        return
    rows = await cashback.active_lots(session, user_id, now, for_update=True)
    plan = rules.allocate_fifo(
        [rules.Lot(id=r.id, remaining=r.remaining, expires_at=r.expires_at) for r in rows], amount
    )
    by_id = {r.id: r for r in rows}
    for lot_id, take in plan:
        by_id[lot_id].remaining -= take
    await cashback.add_debit(
        session,
        user_id=user_id,
        type_=CashbackTransaction.TYPE_SPEND,
        amount=amount,
        created_at=now,
        purchase_id=purchase_id,
    )


async def expire_due(session: AsyncSession, now: datetime) -> dict[int, int]:
    """Muddati o'tgan partiyalar qoldig'ini kuydiradi. {user_id: kuygan summa} qaytaradi va commit qiladi."""
    burned: dict[int, int] = defaultdict(int)
    for lot in await cashback.expired_lots(session, now):
        burned[lot.user_id] += lot.remaining
        lot.remaining = 0
    for user_id, amount in burned.items():
        await cashback.add_debit(
            session, user_id=user_id, type_=CashbackTransaction.TYPE_EXPIRE, amount=amount, created_at=now
        )
    await session.commit()
    return dict(burned)
