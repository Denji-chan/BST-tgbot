"""Support murojaatlari: saqlash va javobni yozish."""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import Admin, SupportMessage, User
from utils.db_api.repositories import admins, support, users

MAX_TEXT_LENGTH = 2000


@dataclass(frozen=True)
class NewRequest:
    message: SupportMessage
    recipients: list[Admin]


@dataclass(frozen=True)
class AnswerResult:
    message: SupportMessage
    customer: User
    already_answered_by: int | None


async def create_request(session: AsyncSession, user: User, text: str, now: datetime) -> NewRequest:
    message = await support.create(session, user.id, text[:MAX_TEXT_LENGTH], now)
    await session.commit()
    return NewRequest(message=message, recipients=await admins.list_all(session))


async def save_answer(
    session: AsyncSession, message_id: int, answer: str, admin_telegram_id: int, now: datetime
) -> AnswerResult | None:
    message = await support.get(session, message_id)
    if message is None:
        return None
    customer = await users.get_by_id(session, message.user_id)
    if customer is None:
        return None
    previous = message.answered_by
    await support.set_answer(session, message, answer[:MAX_TEXT_LENGTH], admin_telegram_id, now)
    await session.commit()
    return AnswerResult(message=message, customer=customer, already_answered_by=previous)
