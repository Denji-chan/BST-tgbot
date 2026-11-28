"""Mijozlarga xabar yuborish. Mijoz botni bloklagan bo'lsa, bazada belgilanadi."""

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError
from sqlalchemy.ext.asyncio import AsyncSession

from utils.db_api.repositories import users

logger = logging.getLogger(__name__)


async def send_to_user(
    bot: Bot, session: AsyncSession, telegram_id: int, text: str, parse_mode: str | None = "HTML"
) -> bool:
    try:
        await bot.send_message(telegram_id, text, parse_mode=parse_mode)
        return True
    except TelegramForbiddenError:
        await users.set_blocked_by_telegram_id(session, telegram_id, True)
        await session.commit()
        logger.info("Mijoz %s botni bloklagan", telegram_id)
    except TelegramAPIError as err:
        logger.warning("Mijozga %s xabar yuborilmadi: %s", telegram_id, err)
    return False
