from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from services import cashback as rules
from utils.db_api.models import CashbackTransaction, Purchase, User
from utils.db_api.repositories import cashback, purchases


@dataclass(frozen=True)
class ProfileData:
    balance: int
    nearest_expiry: tuple[date, int] | None
    last_purchases: list[Purchase]


def to_lots(rows: list[CashbackTransaction]) -> list[rules.Lot]:
    return [rules.Lot(id=r.id, remaining=r.remaining, expires_at=r.expires_at) for r in rows]


async def get_profile(session: AsyncSession, user: User, now: datetime, tz: ZoneInfo, limit: int = 5) -> ProfileData:
    lots = to_lots(await cashback.active_lots(session, user.id, now))
    return ProfileData(
        balance=rules.active_balance(lots, now),
        nearest_expiry=rules.nearest_expiry(lots, now, tz),
        last_purchases=await purchases.last_for_user(session, user.id, limit),
    )
