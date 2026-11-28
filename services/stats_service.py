from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from services.periods import period_start
from utils.db_api.models import CashbackTransaction as Tx
from utils.db_api.repositories import cashback, purchases, users


@dataclass(frozen=True)
class Stats:
    customers_total: int
    customers_new: int
    purchases_count: int
    purchases_sum: int
    cashback_given: int
    cashback_used: int
    cashback_expired: int


async def get_stats(session: AsyncSession, period: str, now: datetime, tz: ZoneInfo) -> Stats:
    since = period_start(period, now, tz)
    count, total = await purchases.stats(session, since)
    return Stats(
        customers_total=await users.count_registered(session),
        customers_new=await users.count_registered(session, since),
        purchases_count=count,
        purchases_sum=total,
        cashback_given=await cashback.sum_by_types(session, [Tx.TYPE_EARN, Tx.TYPE_REFERRAL], since),
        cashback_used=await cashback.sum_by_types(session, [Tx.TYPE_SPEND], since),
        cashback_expired=await cashback.sum_by_types(session, [Tx.TYPE_EXPIRE], since),
    )
