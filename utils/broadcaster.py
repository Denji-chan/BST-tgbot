"""Rassilkani Telegram orqali yuborish (aiogram adapteri) va hisobotni adminga berish."""

import asyncio
import logging
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from services.broadcast import DeliveryStatus, RetryAfter, run_broadcast
from utils.db_api.repositories import broadcasts, users
from utils.misc.i18n import Translate

logger = logging.getLogger(__name__)
_running: set[asyncio.Task] = set()  # orqa fondagi vazifalar yo'qolib qolmasligi uchun


async def copy_to(bot: Bot, chat_id: int, from_chat_id: int, message_id: int) -> DeliveryStatus:
    try:
        await bot.copy_message(chat_id=chat_id, from_chat_id=from_chat_id, message_id=message_id)
        return DeliveryStatus.DELIVERED
    except TelegramRetryAfter as err:
        raise RetryAfter(err.retry_after) from err
    except TelegramForbiddenError:
        return DeliveryStatus.BLOCKED
    except TelegramAPIError as err:
        logger.warning("Rassilka: %s ga yuborilmadi: %s", chat_id, err)
        return DeliveryStatus.FAILED


async def _run(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    t: Translate,
    broadcast_id: int,
    admin_chat_id: int,
    recipients: list[tuple[int, int]],
    from_chat_id: int,
    message_id: int,
    tz,
) -> None:
    try:
        report = await run_broadcast(recipients, lambda chat_id: copy_to(bot, chat_id, from_chat_id, message_id))
    except Exception:
        logger.exception("Rassilka #%s to'xtab qoldi", broadcast_id)
        await bot.send_message(admin_chat_id, t("broadcast.crashed", broadcast_id=broadcast_id))
        return

    async with session_factory() as session:
        await users.set_blocked_by_ids(session, report.blocked_user_ids)
        await broadcasts.finish(
            session,
            broadcast_id,
            delivered=report.delivered,
            failed=report.failed,
            blocked=report.blocked,
            now=datetime.now(tz),
        )
        await session.commit()

    await bot.send_message(
        admin_chat_id,
        t(
            "broadcast.report",
            broadcast_id=broadcast_id,
            total=report.total,
            delivered=report.delivered,
            failed=report.failed,
            blocked=report.blocked,
        ),
    )


def start_broadcast(**kwargs) -> None:
    """Rassilkani orqa fonda boshlaydi, handler kutib qolmaydi."""
    task = asyncio.create_task(_run(**kwargs))
    _running.add(task)
    task.add_done_callback(_running.discard)
