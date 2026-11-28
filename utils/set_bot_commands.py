from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

from utils.misc.i18n import LANGUAGES, Translator


def _commands(translator: Translator, lang: str) -> list[BotCommand]:
    return [
        BotCommand(command="start", description=translator.get(lang, "commands.start")),
        BotCommand(command="help", description=translator.get(lang, "commands.help")),
    ]


async def set_default_commands(bot: Bot, translator: Translator) -> None:
    # Standart (til ko'rsatilmagan) buyruqlar o'zbekcha, qolgan tillar alohida.
    await bot.set_my_commands(_commands(translator, translator.default), scope=BotCommandScopeDefault())
    for lang in LANGUAGES:
        if lang == translator.default:
            continue
        await bot.set_my_commands(_commands(translator, lang), scope=BotCommandScopeDefault(), language_code=lang)
