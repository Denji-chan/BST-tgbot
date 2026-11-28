from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.models import SupportMessage


async def create(session: AsyncSession, user_id: int, text: str, now: datetime) -> SupportMessage:
    message = SupportMessage(user_id=user_id, text=text, created_at=now)
    session.add(message)
    await session.flush()
    return message


async def get(session: AsyncSession, message_id: int) -> SupportMessage | None:
    return await session.get(SupportMessage, message_id)


async def set_answer(
    session: AsyncSession, message: SupportMessage, answer: str, admin_telegram_id: int, now: datetime
) -> None:
    message.answer = answer
    message.answered_by = admin_telegram_id
    message.answered_at = now
    await session.flush()
