from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from utils.misc.i18n import Translator

from .database import DbSessionMiddleware
from .i18n import LanguageMiddleware
from .throttling import ThrottlingMiddleware


def setup_middlewares(
    dp: Dispatcher, session_factory: async_sessionmaker[AsyncSession], translator: Translator
) -> None:
    # Tashqi (outer) middleware'lar har bir update uchun: avval sessiya, keyin til.
    # aiogram'ning o'z UserContext va FSM middleware'lari ulardan oldin ishlaydi.
    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.update.outer_middleware(LanguageMiddleware(translator))

    # Ichki middleware: handler flaglarini ko'radi (rate_limit).
    throttling = ThrottlingMiddleware()
    dp.message.middleware(throttling)
    dp.callback_query.middleware(throttling)
