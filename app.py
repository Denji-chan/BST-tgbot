"""Botni ishga tushirish nuqtasi.

aiogram 2 shablonidagi `executor.start_polling` o'rniga aiogram 3 uslubi:
`asyncio.run(main())` va `dp.start_polling(bot)`.
"""

import asyncio
import logging

from aiogram import Bot

from data.config import DEVELOPER_ID, RULES, TIMEZONE, settings
from handlers import setup_routers
from loader import bot, dp, engine, i18n, session_factory
from middlewares import setup_middlewares
from utils.db_api.repositories import admins
from utils.misc.logging import setup_logging
from utils.notify_admins import on_startup_notify
from utils.scheduler import setup_scheduler
from utils.set_bot_commands import set_default_commands

scheduler = setup_scheduler(bot, session_factory, i18n, TIMEZONE, RULES)


async def on_startup(bot: Bot) -> None:
    # Developer adminlar jadvalida ham bo'lishi kerak (uning tilini saqlash uchun).
    async with session_factory() as session:
        await admins.ensure(session, DEVELOPER_ID, "Developer")
        await session.commit()

    me = await bot.get_me()
    dp["bot_username"] = me.username
    await set_default_commands(bot, i18n)
    await on_startup_notify(bot, i18n)
    scheduler.start()
    logging.info("Scheduler ishga tushdi: %s ta vazifa", len(scheduler.get_jobs()))


async def on_shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
    await engine.dispose()


async def main() -> None:
    setup_logging(
        level=settings.log_level,
        log_dir=settings.log_dir,
        tz=settings.timezone,
        secrets=[settings.bot_token],
    )

    dp["session_factory"] = session_factory
    setup_middlewares(dp, session_factory, i18n)
    dp.include_router(setup_routers())
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Bot o'chiq turgan paytda yig'ilib qolgan eski xabarlarga javob bermaymiz.
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Bot polling rejimida ishga tushmoqda")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
