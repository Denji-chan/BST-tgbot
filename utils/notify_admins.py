import logging

from aiogram import Bot

from data.config import DEVELOPER_ID
from utils.misc.i18n import Translator

logger = logging.getLogger(__name__)


async def on_startup_notify(bot: Bot, translator: Translator) -> None:
    """Bot ishga tushganini Developer'ga bildiradi."""
    try:
        await bot.send_message(DEVELOPER_ID, translator.get(translator.default, "admin.bot_started"))
    except Exception as err:  # Developer botni hali ochmagan bo'lishi mumkin
        logger.warning("Developer'ga xabar yuborilmadi: %s", err)
