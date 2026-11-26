"""BEST SHOP TREND — mijozlar bazasi va cashback Telegram boti.

Ishga tushirish:  python bot.py
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat

from config import BOT_TOKEN, DEVELOPER_ID
from handlers import admin, common, user


async def main() -> None:
    if not BOT_TOKEN:
        sys.exit("❌ BOT_TOKEN topilmadi. .env faylini yarating va tokenni yozing (README.md ga qarang).")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Tartib muhim: common (/start, bekor qilish) -> admin -> user
    dp.include_routers(common.router, admin.router, user.router)

    await bot.set_my_commands([BotCommand(command="start", description="Boshlash / Начать / Baslaw")])
    try:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Boshlash"),
                BotCommand(command="admin", description="Admin panel"),
                BotCommand(command="cancel", description="Bekor qilish"),
            ],
            scope=BotCommandScopeChat(chat_id=DEVELOPER_ID),
        )
    except Exception:  # developer hali botga /start bosmagan bo'lsa
        pass

    await bot.delete_webhook(drop_pending_updates=True)
    me = await bot.get_me()
    logging.info("Bot ishga tushdi: @%s", me.username)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit) as e:
        if isinstance(e, SystemExit) and e.code not in (None, 0):
            print(e.code)
        logging.info("Bot to'xtatildi.")
