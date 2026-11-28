"""Tug'ilgan kun tabriklari uchun mijozlarni tanlash."""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from services import birthday as rules
from utils.db_api.models import User
from utils.db_api.repositories import users

NOTIFICATION_KIND = "birthday"


def notification_key(user_id: int, today: date) -> str:
    return f"{user_id}:{today.year}"


async def birthday_users(session: AsyncSession, today: date) -> list[User]:
    """Bugun tug'ilgan kuni bo'lgan (botni bloklamagan) mijozlar."""
    return [u for u in await users.active_users(session) if rules.is_birthday_today(u.birth_date, today)]
