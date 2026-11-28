"""APScheduler vazifalari (Asia/Tashkent vaqti bilan):

- 00:05 har kuni  - muddati o'tgan cashbackni kuydirish
- 10:00 har kuni  - tug'ilgan kun tabriki va chegirma haqida xabar
- 20:00 har kuni  - 60/90/120 kun kelmagan mijozlarga xabar
- 25-sana 10:00   - adminlarga oylik to'lov eslatmasi

Har bir xabar notification_logs orqali bir marta yuboriladi (bot qayta ishga tushsa ham).
"""

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from services import birthday as birthday_rules
from services import birthday_service, cashback_service, reengagement_service, template_service
from services.rules import BusinessRules
from services.templates import render
from utils.db_api.repositories import admins, cashback, notifications
from utils.misc.formatting import fmt_date, money
from utils.misc.i18n import Translator
from utils.notify_users import send_to_user

logger = logging.getLogger(__name__)
SEND_PAUSE = 0.05  # xabarlar orasida (Telegram limitidan ancha past)
PAYMENT_KIND = "payment_reminder"


async def expire_cashback_job(session_factory: async_sessionmaker[AsyncSession], tz: ZoneInfo) -> None:
    async with session_factory() as session:
        burned = await cashback_service.expire_due(session, datetime.now(tz))
    if burned:
        logger.info("Cashback kuydi: %s mijoz, jami %s so'm", len(burned), sum(burned.values()))


async def birthday_job(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    tz: ZoneInfo,
    business: BusinessRules,
) -> None:
    today = datetime.now(tz).date()
    async with session_factory() as session:
        for user in await birthday_service.birthday_users(session, today):
            key = birthday_service.notification_key(user.id, today)
            if await notifications.was_sent(session, birthday_service.NOTIFICATION_KIND, key):
                continue
            t = translator.bind(user.language)
            text = t(
                "birthday.greeting",
                name=user.first_name,
                percent=business.birthday_discount_percent,
                until=fmt_date(birthday_rules.window_end(user.birth_date, today.year, business.birthday_extra_days)),
            )
            await send_to_user(bot, session, user.telegram_id, text, parse_mode=None)
            await notifications.mark_sent(session, birthday_service.NOTIFICATION_KIND, key, datetime.now(tz))
            await session.commit()
            await asyncio.sleep(SEND_PAUSE)


async def reengagement_job(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    tz: ZoneInfo,
    business: BusinessRules,
) -> None:
    now = datetime.now(tz)
    async with session_factory() as session:
        due = await reengagement_service.collect_due(session, now.date(), tz, business.reengagement_stages)
        for item in due:
            user = item.user
            template = await template_service.get_text(session, translator, f"inactive_{item.stage}", user.language)
            balance = await cashback.balance(session, user.id, now)
            text = render(template, name=user.first_name, balance=money(balance))
            await send_to_user(bot, session, user.telegram_id, text, parse_mode=None)
            await notifications.mark_sent(session, reengagement_service.NOTIFICATION_KIND, item.key, now)
            await session.commit()
            await asyncio.sleep(SEND_PAUSE)
    if due:
        logger.info("Qaytish xabarlari yuborildi: %s ta", len(due))


async def payment_reminder_job(
    bot: Bot, session_factory: async_sessionmaker[AsyncSession], translator: Translator, tz: ZoneInfo
) -> None:
    now = datetime.now(tz)
    async with session_factory() as session:
        for admin in await admins.list_all(session):
            key = f"{admin.telegram_id}:{now:%Y-%m}"
            if await notifications.was_sent(session, PAYMENT_KIND, key):
                continue
            template = await template_service.get_text(session, translator, "payment_reminder", admin.language)
            try:
                await bot.send_message(admin.telegram_id, render(template, name=admin.full_name), parse_mode=None)
            except TelegramAPIError as err:
                logger.warning("Adminga %s eslatma yuborilmadi: %s", admin.telegram_id, err)
            await notifications.mark_sent(session, PAYMENT_KIND, key, now)
            await session.commit()


def setup_scheduler(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    translator: Translator,
    tz: ZoneInfo,
    business: BusinessRules,
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=tz)
    common = {"replace_existing": True, "coalesce": True, "max_instances": 1, "misfire_grace_time": 3600}
    messaging = {"bot": bot, "session_factory": session_factory, "translator": translator, "tz": tz}

    scheduler.add_job(
        expire_cashback_job,
        CronTrigger(hour=0, minute=5, timezone=tz),
        kwargs={"session_factory": session_factory, "tz": tz},
        id="expire_cashback",
        **common,
    )
    scheduler.add_job(
        birthday_job,
        CronTrigger(hour=10, minute=0, timezone=tz),
        kwargs={**messaging, "business": business},
        id="birthday",
        **common,
    )
    scheduler.add_job(
        reengagement_job,
        CronTrigger(hour=20, minute=0, timezone=tz),
        kwargs={**messaging, "business": business},
        id="reengagement",
        **common,
    )
    scheduler.add_job(
        payment_reminder_job,
        CronTrigger(day=25, hour=10, minute=0, timezone=tz),
        kwargs=messaging,
        id="payment_reminder",
        **common,
    )
    return scheduler
