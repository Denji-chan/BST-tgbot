"""Adminlarni boshqarish: faqat Developer (.env dagi DEVELOPER_ID)."""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import DEVELOPER_ID
from filters import IsDeveloper
from filters.menu import NOT_ADMIN_MENU
from keyboards.default.main_menu import admin_menu, cancel_keyboard
from keyboards.inline.admins import admins_keyboard
from keyboards.inline.callbacks import AdminAddCb, AdminRemoveCb
from services.admin_service import AdminChange, add_admin, remove_admin
from services.validators import parse_telegram_id
from states.admins import AdminManage
from utils.db_api.repositories import admins
from utils.misc.formatting import esc
from utils.misc.i18n import Translate, Translator, i18n

router = Router(name="admins.admins")
router.message.filter(IsDeveloper())
router.callback_query.filter(IsDeveloper())
logger = logging.getLogger(__name__)


async def _list_text(session: AsyncSession, t: Translate) -> tuple[str, list]:
    items = await admins.list_all(session)
    lines = []
    for admin in items:
        role = t("admins.role_developer") if admin.telegram_id == DEVELOPER_ID else t("admins.role_admin")
        lines.append(t("admins.line", name=esc(admin.full_name or "—"), telegram_id=admin.telegram_id, role=role))
    return t("admins.title", count=len(items)) + "\n\n" + "\n".join(lines), items


@router.message(F.text.in_(i18n.variants("btn.admin_admins")))
async def admins_list(message: Message, state: FSMContext, session: AsyncSession, t: Translate) -> None:
    await state.clear()
    text, items = await _list_text(session, t)
    await message.answer(text, reply_markup=admins_keyboard(t, items, DEVELOPER_ID))


@router.callback_query(AdminAddCb.filter())
async def admin_add_start(call: CallbackQuery, state: FSMContext, t: Translate) -> None:
    await state.set_state(AdminManage.waiting_id)
    await call.message.answer(t("admins.ask_id"), reply_markup=cancel_keyboard(t))
    await call.answer()


@router.message(AdminManage.waiting_id, NOT_ADMIN_MENU)
async def admin_add_id(
    message: Message, state: FSMContext, session: AsyncSession, t: Translate, i18n: Translator, bot: Bot
) -> None:
    # Forward qilingan xabar egasi (agar u yashirmagan bo'lsa) yoki yozilgan ID raqam
    sender = getattr(getattr(message, "forward_origin", None), "sender_user", None)
    telegram_id = sender.id if sender else parse_telegram_id(message.text)
    if telegram_id is None:
        await message.answer(t("admins.bad_id"))
        return

    full_name = ""
    try:
        chat = await bot.get_chat(telegram_id)
        full_name = chat.full_name or ""
    except TelegramAPIError:
        pass  # foydalanuvchi botni hali ochmagan bo'lishi mumkin

    result = await add_admin(session, telegram_id, full_name, message.from_user.id, DEVELOPER_ID)
    menu = admin_menu(t, is_developer=True)
    if result is AdminChange.IS_DEVELOPER:
        await message.answer(t("admins.is_developer"))
        return
    if result is AdminChange.ALREADY_ADMIN:
        await message.answer(t("admins.already"))
        return

    await state.clear()
    await message.answer(t("admins.added", telegram_id=telegram_id), reply_markup=menu)
    try:
        await bot.send_message(telegram_id, i18n.get(i18n.default, "admins.you_are_admin"))
    except TelegramAPIError as err:
        logger.info("Yangi adminga %s xabar yuborilmadi: %s", telegram_id, err)
        await message.answer(t("admins.notify_failed"))
    text, items = await _list_text(session, t)
    await message.answer(text, reply_markup=admins_keyboard(t, items, DEVELOPER_ID))


@router.callback_query(AdminRemoveCb.filter())
async def admin_remove(call: CallbackQuery, callback_data: AdminRemoveCb, session: AsyncSession, t: Translate) -> None:
    result = await remove_admin(session, callback_data.telegram_id, DEVELOPER_ID)
    if result is AdminChange.IS_DEVELOPER:
        await call.answer(t("admins.cannot_remove_developer"), show_alert=True)
        return
    text, items = await _list_text(session, t)
    await call.message.edit_text(text, reply_markup=admins_keyboard(t, items, DEVELOPER_ID))
    await call.answer(t("admins.removed") if result is AdminChange.OK else t("admins.not_found"))
