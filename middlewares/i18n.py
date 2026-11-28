from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject
from aiogram.types import User as TgUser

from utils.db_api.repositories import admins, users
from utils.misc.i18n import LANGUAGES, Translator, guess_language


class LanguageMiddleware(BaseMiddleware):
    """Foydalanuvchini bazadan yuklaydi va tilni aniqlaydi.

    Handlerlarga beriladi: `user` (mijoz yoki None), `admin` (admin yoki None),
    `lang` (til kodi), `t` (shu tilga bog'langan tarjimon), `i18n` (umumiy tarjimon).
    Til tartibi: admin tili -> mijoz tili -> ro'yxatdan o'tishda tanlangan til -> Telegram tili.
    """

    def __init__(self, translator: Translator) -> None:
        self.translator = translator

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user: TgUser | None = data.get("event_from_user")
        session = data["session"]
        user = admin = None
        lang = None

        if tg_user is not None:
            admin = await admins.get_by_telegram_id(session, tg_user.id)
            user = await users.get_by_telegram_id(session, tg_user.id)
            if admin is not None:
                lang = admin.language
            elif user is not None:
                lang = user.language
            else:
                state: FSMContext | None = data.get("state")
                if state is not None:
                    lang = (await state.get_data()).get("lang")
            if lang not in LANGUAGES:
                lang = guess_language(tg_user.language_code)

        lang = lang or self.translator.default
        data["user"] = user
        data["admin"] = admin
        data["lang"] = lang
        data["t"] = self.translator.bind(lang)
        data["i18n"] = self.translator
        return await handler(event, data)
