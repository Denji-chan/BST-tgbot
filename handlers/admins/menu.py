"""Admin menyusi va har qanday admin jarayonini bekor qilish."""

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data.config import DEVELOPER_ID
from keyboards.default.main_menu import admin_menu
from utils.misc.i18n import Translate, i18n

router = Router(name="admins.menu")


@router.message(CommandStart())
@router.message(Command("admin"))
async def admin_home(message: Message, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await message.answer(t("admin.menu"), reply_markup=admin_menu(t, message.from_user.id == DEVELOPER_ID))


@router.message(F.text.in_(i18n.variants("btn.cancel")))
async def admin_cancel(message: Message, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await message.answer(t("common.cancelled"), reply_markup=admin_menu(t, message.from_user.id == DEVELOPER_ID))
