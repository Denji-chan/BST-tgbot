"""Mijoz adminga murojaat yozadi. Murojaat barcha adminlarga "Javob berish" tugmasi bilan boradi."""

import logging
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from data.config import TIMEZONE
from filters import IsRegistered
from keyboards.default.main_menu import cancel_keyboard, user_menu
from keyboards.inline.support import reply_keyboard
from services.support_service import create_request
from states.support import SupportRequest
from utils.db_api.models import User
from utils.misc.formatting import esc
from utils.misc.i18n import Translate, Translator, i18n
from utils.misc.throttling import rate_limit

router = Router(name="users.support")
logger = logging.getLogger(__name__)


@router.message(F.text.in_(i18n.variants("btn.support")), IsRegistered())
async def support_start(message: Message, state: FSMContext, t: Translate) -> None:
    await state.set_state(SupportRequest.waiting_message)
    await message.answer(t("support.ask"), reply_markup=cancel_keyboard(t))


@router.message(SupportRequest.waiting_message, F.text.in_(i18n.variants("btn.cancel")))
async def support_cancel(message: Message, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await message.answer(t("common.cancelled"), reply_markup=user_menu(t))


@router.message(SupportRequest.waiting_message, F.text, IsRegistered(), flags=rate_limit(10, "support"))
async def support_message(
    message: Message, state: FSMContext, session, t: Translate, i18n: Translator, user: User, bot: Bot
) -> None:
    request = await create_request(session, user, message.text, datetime.now(TIMEZONE))
    await state.clear()
    for admin in request.recipients:
        admin_t = i18n.bind(admin.language)
        text = admin_t(
            "support.new_request",
            request_id=request.message.id,
            name=esc(user.full_name),
            customer_id=user.id,
            phone=user.phone,
            text=esc(request.message.text),
        )
        try:
            await bot.send_message(admin.telegram_id, text, reply_markup=reply_keyboard(admin_t, request.message.id))
        except TelegramAPIError as err:
            logger.warning("Adminga %s murojaat yuborilmadi: %s", admin.telegram_id, err)
    await message.answer(t("support.sent"), reply_markup=user_menu(t))


@router.message(SupportRequest.waiting_message)
async def support_need_text(message: Message, t: Translate) -> None:
    await message.answer(t("support.need_text"))
