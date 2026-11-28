"""Sozlamalar: tilni almashtirish. Mijozlar ham, adminlar ham foydalanadi."""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import DEVELOPER_ID
from keyboards.default.main_menu import menu_for
from keyboards.inline.callbacks import SettingsLanguageCb
from keyboards.inline.language import language_keyboard
from utils.db_api.models import Admin, User
from utils.db_api.repositories import admins, users
from utils.misc.i18n import LANGUAGES, Translate, Translator, i18n

router = Router(name="users.settings")


@router.message(F.text.in_(i18n.variants("btn.settings")))
async def settings_menu(
    message: Message, state: FSMContext, t: Translate, i18n: Translator, user: User | None, admin: Admin | None
) -> None:
    await state.clear()
    if user is None and admin is None:
        await message.answer(t("common.need_registration"))
        return
    await message.answer(
        t("settings.text", language=t("lang.name")), reply_markup=language_keyboard(i18n, settings=True)
    )


@router.callback_query(SettingsLanguageCb.filter())
async def settings_language(
    call: CallbackQuery,
    callback_data: SettingsLanguageCb,
    session: AsyncSession,
    t: Translate,
    i18n: Translator,
    user: User | None,
    admin: Admin | None,
) -> None:
    if user is None and admin is None:
        await call.answer(t("common.need_registration"))
        return
    code = callback_data.code if callback_data.code in LANGUAGES else i18n.default
    if admin is not None:
        await admins.set_language(session, admin, code)
    if user is not None:
        await users.set_language(session, user, code)
    await session.commit()

    new_t = i18n.bind(code)
    await call.message.edit_text(new_t("settings.changed", language=new_t("lang.name")))
    markup = menu_for(new_t, is_admin=admin is not None, is_developer=call.from_user.id == DEVELOPER_ID)
    await call.message.answer(new_t("settings.menu_updated"), reply_markup=markup)
    await call.answer()
