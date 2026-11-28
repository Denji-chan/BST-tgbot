from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.misc.i18n import Translate
from utils.misc.throttling import rate_limit

router = Router(name="users.help")


@router.message(Command("help"), flags=rate_limit(5, "help"))
async def bot_help(message: Message, t: Translate) -> None:
    await message.answer(t("help.text"))
