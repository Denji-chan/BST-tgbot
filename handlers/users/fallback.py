"""Hech qaysi handler ushlamagan xabar va tugmalar. Ildiz routerda eng oxirida ulanadi."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from data.config import DEVELOPER_ID
from keyboards.default.main_menu import menu_for
from utils.db_api.models import Admin, User
from utils.misc.i18n import Translate

router = Router(name="fallback")


@router.callback_query()
async def stale_callback(call: CallbackQuery, t: Translate) -> None:
    await call.answer(t("common.expired"))


@router.message(F.chat.type == "private")
async def unknown_message(message: Message, t: Translate, user: User | None, admin: Admin | None) -> None:
    if admin is None and user is None:
        await message.answer(t("common.need_registration"))
        return
    markup = menu_for(t, is_admin=admin is not None, is_developer=message.from_user.id == DEVELOPER_ID)
    await message.answer(t("common.unknown"), reply_markup=markup)
