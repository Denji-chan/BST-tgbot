"""Har qanday holatda ishlaydigan buyruqlar: /start, /cancel, «Bekor qilish».
Bu router birinchi ulanadi, shuning uchun boshqa holatlardan ustun turadi."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database import db
from helpers import resume_registration
from keyboards import menu_for
from texts import t, variants

router = Router(name="common")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    db.ensure_user(message.from_user.id, message.from_user.username)
    await resume_registration(message, state, message.from_user.id)


@router.message(Command("cancel"))
@router.message(F.text.in_(variants("btn_cancel")))
async def cancel(message: Message, state: FSMContext) -> None:
    tg_id = message.from_user.id
    await state.clear()
    user = db.get_user(tg_id)
    if user is None or (not user["is_registered"] and not db.is_admin(tg_id)):
        db.ensure_user(tg_id, message.from_user.username)
        await resume_registration(message, state, tg_id)
        return
    lang = db.get_lang(tg_id)
    await message.answer(t("cancelled", lang), reply_markup=menu_for(tg_id, lang))
