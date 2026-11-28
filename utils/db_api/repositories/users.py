from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import CashbackTransaction, Purchase, User


@dataclass(frozen=True)
class UserListRow:
    user: User
    balance: int
    purchases_count: int
    purchases_sum: int


async def get_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    return await session.scalar(select(User).where(User.telegram_id == telegram_id))


async def get_by_id(session: AsyncSession, user_id: int, for_update: bool = False) -> User | None:
    stmt = select(User).where(User.id == user_id)
    if for_update:
        stmt = stmt.with_for_update()
    return await session.scalar(stmt)


async def get_by_phone(session: AsyncSession, phone: str) -> User | None:
    return await session.scalar(select(User).where(User.phone == phone))


async def create(
    session: AsyncSession,
    *,
    telegram_id: int,
    first_name: str,
    last_name: str,
    phone: str,
    birth_date: date,
    language: str,
    referred_by_id: int | None = None,
    registered_at: datetime | None = None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        birth_date=birth_date,
        language=language,
        referred_by_id=referred_by_id,
        is_blocked=False,
    )
    if registered_at is not None:
        user.registered_at = registered_at
    session.add(user)
    await session.flush()
    return user


async def set_language(session: AsyncSession, user: User, language: str) -> None:
    user.language = language
    await session.flush()


async def set_blocked_by_telegram_id(session: AsyncSession, telegram_id: int, blocked: bool) -> None:
    await session.execute(update(User).where(User.telegram_id == telegram_id).values(is_blocked=blocked))


async def set_blocked_by_ids(session: AsyncSession, user_ids: list[int]) -> None:
    if user_ids:
        await session.execute(update(User).where(User.id.in_(user_ids)).values(is_blocked=True))


async def count_registered(session: AsyncSession, since: datetime | None = None) -> int:
    stmt = select(func.count(User.id))
    if since is not None:
        stmt = stmt.where(User.registered_at >= since)
    return int(await session.scalar(stmt) or 0)


async def active_users(session: AsyncSession) -> list[User]:
    """Botni bloklamagan barcha mijozlar."""
    result = await session.scalars(select(User).where(User.is_blocked.is_(False)).order_by(User.id))
    return list(result)


def _list_query(now: datetime):
    balance = (
        select(
            CashbackTransaction.user_id.label("user_id"),
            func.coalesce(func.sum(CashbackTransaction.remaining), 0).label("balance"),
        )
        .where(CashbackTransaction.remaining > 0, CashbackTransaction.expires_at > now)
        .group_by(CashbackTransaction.user_id)
        .subquery()
    )
    purchases = (
        select(
            Purchase.user_id.label("user_id"),
            func.count(Purchase.id).label("cnt"),
            func.coalesce(func.sum(Purchase.total), 0).label("total"),
        )
        .group_by(Purchase.user_id)
        .subquery()
    )
    return (
        select(
            User,
            func.coalesce(balance.c.balance, 0),
            func.coalesce(purchases.c.cnt, 0),
            func.coalesce(purchases.c.total, 0),
        )
        .outerjoin(balance, balance.c.user_id == User.id)
        .outerjoin(purchases, purchases.c.user_id == User.id)
        .order_by(User.id.desc())
    )


async def list_page(session: AsyncSession, now: datetime, offset: int, limit: int) -> list[UserListRow]:
    result = await session.execute(_list_query(now).offset(offset).limit(limit))
    return [UserListRow(user=u, balance=int(b), purchases_count=int(c), purchases_sum=int(s)) for u, b, c, s in result]


async def list_all(session: AsyncSession, now: datetime) -> list[UserListRow]:
    result = await session.execute(_list_query(now))
    return [UserListRow(user=u, balance=int(b), purchases_count=int(c), purchases_sum=int(s)) for u, b, c, s in result]
