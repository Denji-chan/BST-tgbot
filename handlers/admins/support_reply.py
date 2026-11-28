"""Admin murojaatga bot ichida javob beradi."""

from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import DEVELOPER_ID, TIMEZONE
from filters.menu import NOT_ADMIN_MENU
from keyboards.default.main_menu import admin_menu, cancel_keyboard
from keyboards.inline.callbacks import SupportReplyCb
from services.support_service import save_answer
from states.support import SupportReply
from utils.misc.formatting import esc
from utils.misc.i18n import Translate, Translator
from utils.notify_users import send_to_user

router = Router(name="admins.support_reply")


@router.callback_query(SupportReplyCb.filter())
async def reply_start(call: CallbackQuery, callback_data: SupportReplyCb, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await state.update_data(support_message_id=callback_data.message_id)
    await state.set_state(SupportReply.waiting_answer)
    text = t("support.ask_answer", request_id=callback_data.message_id)
    await call.message.answer(text, reply_markup=cancel_keyboard(t))
    await call.answer()


@router.message(SupportReply.waiting_answer, F.text, NOT_ADMIN_MENU)
async def reply_send(
    message: Message, state: FSMContext, session: AsyncSession, t: Translate, i18n: Translator, bot: Bot
) -> None:
    data = await state.get_data()
    await state.clear()
    menu = admin_menu(t, message.from_user.id == DEVELOPER_ID)
    result = await save_answer(
        session, data["support_message_id"], message.text, message.from_user.id, datetime.now(TIMEZONE)
    )
    if result is None:
        await message.answer(t("support.request_not_found"), reply_markup=menu)
        return

    customer_t = i18n.bind(result.customer.language)
    delivered = await send_to_user(
        bot,
        session,
        result.customer.telegram_id,
        customer_t("support.answer", question=esc(result.message.text), answer=esc(message.text)),
    )
    key = "support.answer_sent" if delivered else "support.answer_not_delivered"
    await message.answer(t(key), reply_markup=menu)
    if result.already_answered_by is not None and result.already_answered_by != message.from_user.id:
        await message.answer(t("support.was_answered_before"))


@router.message(SupportReply.waiting_answer, NOT_ADMIN_MENU)
async def reply_need_text(message: Message, t: Translate) -> None:
    await message.answer(t("support.need_text"))
