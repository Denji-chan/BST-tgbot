"""Rassilka: matn, rasm yoki video -> ko'rib chiqish -> tasdiqlash -> orqa fonda yuborish -> hisobot."""

from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from data.config import DEVELOPER_ID, TIMEZONE
from filters.menu import NOT_ADMIN_MENU
from keyboards.default.main_menu import admin_menu, cancel_keyboard
from keyboards.inline.broadcast import broadcast_confirm_keyboard
from keyboards.inline.callbacks import BroadcastCb
from states.broadcast import BroadcastState
from utils.broadcaster import start_broadcast
from utils.db_api.repositories import broadcasts, users
from utils.misc.i18n import Translate, i18n

router = Router(name="admins.broadcast")


def _content_type(message: Message) -> str | None:
    """Faqat matn, rasm yoki video qabul qilinadi."""
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.text:
        return "text"
    return None


@router.message(F.text.in_(i18n.variants("btn.admin_broadcast")))
async def broadcast_start(message: Message, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await state.set_state(BroadcastState.waiting_content)
    await message.answer(t("broadcast.ask"), reply_markup=cancel_keyboard(t))


@router.message(BroadcastState.waiting_content, NOT_ADMIN_MENU)
async def broadcast_content(message: Message, state: FSMContext, session: AsyncSession, t: Translate, bot: Bot) -> None:
    content_type = _content_type(message)
    if content_type is None:
        await message.answer(t("broadcast.unsupported"))
        return
    recipients = await users.active_users(session)
    await state.update_data(
        content_type=content_type, source_chat_id=message.chat.id, source_message_id=message.message_id
    )
    await state.set_state(BroadcastState.confirm)
    await message.answer(t("broadcast.preview_title"))
    await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(t("broadcast.confirm", count=len(recipients)), reply_markup=broadcast_confirm_keyboard(t))


@router.message(BroadcastState.confirm, NOT_ADMIN_MENU)
async def broadcast_use_buttons(message: Message, t: Translate) -> None:
    await message.answer(t("common.use_buttons"))


@router.callback_query(BroadcastState.confirm, BroadcastCb.filter(F.action == "send"))
async def broadcast_send(
    call: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    t: Translate,
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    data = await state.get_data()
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    recipients = [(u.id, u.telegram_id) for u in await users.active_users(session)]
    record = await broadcasts.create(
        session,
        admin_telegram_id=call.from_user.id,
        content_type=data["content_type"],
        source_chat_id=data["source_chat_id"],
        source_message_id=data["source_message_id"],
        total=len(recipients),
        now=datetime.now(TIMEZONE),
    )
    await session.commit()

    start_broadcast(
        bot=bot,
        session_factory=session_factory,
        t=t,
        broadcast_id=record.id,
        admin_chat_id=call.message.chat.id,
        recipients=recipients,
        from_chat_id=data["source_chat_id"],
        message_id=data["source_message_id"],
        tz=TIMEZONE,
    )
    await call.message.answer(
        t("broadcast.started", broadcast_id=record.id, count=len(recipients)),
        reply_markup=admin_menu(t, call.from_user.id == DEVELOPER_ID),
    )
    await call.answer()


@router.callback_query(BroadcastCb.filter(F.action == "cancel"))
async def broadcast_cancel(call: CallbackQuery, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t("common.cancelled"), reply_markup=admin_menu(t, call.from_user.id == DEVELOPER_ID))
    await call.answer()
