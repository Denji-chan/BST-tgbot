from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from data import config
from utils.db_api.base import create_engine, create_session_factory
from utils.misc.i18n import i18n

bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

engine = create_engine(config.DATABASE_URL)
session_factory = create_session_factory(engine)

__all__ = ["bot", "dp", "storage", "engine", "session_factory", "i18n"]
