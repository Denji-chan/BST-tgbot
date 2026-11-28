"""Xarid kiritish: mijozni topish -> mahsulotlar -> cashback ishlatish -> tasdiqlash -> mijozga chek."""

from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import DEVELOPER_ID, RULES, TIMEZONE
from filters.menu import NOT_ADMIN_MENU
from keyboards.default.main_menu import admin_menu, cancel_keyboard
from keyboards.inline.callbacks import PurchaseCb
from keyboards.inline.purchase import cashback_choice_keyboard, confirm_purchase_keyboard
from services.cashback import InsufficientCashback, PurchaseCalculation
from services.customer_search import parse_customer_query
from services.items import MAX_ITEMS, Item, parse_items
from services.purchase_service import CustomerNotFound, customer_state, preview, register_purchase
from states.purchase import PurchaseEntry
from utils.db_api.models import User
from utils.db_api.repositories import cashback, users
from utils.misc.formatting import esc, money
from utils.misc.i18n import Translate, Translator, i18n
from utils.misc.receipts import admin_preview, customer_receipt
from utils.notify_users import send_to_user

router = Router(name="admins.purchase")


def _now() -> datetime:
    return datetime.now(TIMEZONE)


def _items(data: dict) -> list[Item]:
    return [Item(**item) for item in data.get("items", [])]


async def _show_confirm(
    message: Message,
    state: FSMContext,
    t: Translate,
    user: User,
    items: list[Item],
    calc: PurchaseCalculation,
    use_cashback: bool,
) -> None:
    await state.update_data(use_cashback=use_cashback)
    await state.set_state(PurchaseEntry.confirm)
    text = admin_preview(t, user.full_name, user.id, items, calc)
    await message.answer(text, reply_markup=confirm_purchase_keyboard(t))


@router.message(F.text.in_(i18n.variants("btn.admin_purchase")))
async def purchase_start(message: Message, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await state.set_state(PurchaseEntry.customer)
    await message.answer(t("purchase.ask_customer"), reply_markup=cancel_keyboard(t))


@router.message(PurchaseEntry.customer, F.text, NOT_ADMIN_MENU)
async def purchase_customer(message: Message, state: FSMContext, session: AsyncSession, t: Translate) -> None:
    query = parse_customer_query(message.text)
    if query is None:
        await message.answer(t("purchase.bad_query"))
        return
    if query.customer_id is not None:
        customer = await users.get_by_id(session, query.customer_id)
    else:
        customer = await users.get_by_phone(session, query.phone)
    if customer is None:
        await message.answer(t("purchase.customer_not_found"))
        return

    state_info = await customer_state(session, customer, _now(), TIMEZONE, RULES)
    await state.update_data(user_id=customer.id)
    await state.set_state(PurchaseEntry.items)
    birthday = t("purchase.birthday_active") if state_info.birthday_year is not None else ""
    await message.answer(
        t(
            "purchase.customer_card",
            name=esc(customer.full_name),
            customer_id=customer.id,
            phone=customer.phone,
            balance=money(state_info.balance),
            birthday=birthday,
        )
    )
    await message.answer(t("purchase.ask_items"))


@router.message(PurchaseEntry.items, F.text, NOT_ADMIN_MENU)
async def purchase_items(message: Message, state: FSMContext, session: AsyncSession, t: Translate) -> None:
    result = parse_items(message.text)
    if result.too_many:
        await message.answer(t("purchase.too_many_items", max=MAX_ITEMS))
        return
    if result.bad_lines:
        await message.answer(t("purchase.bad_items", lines=", ".join(map(str, result.bad_lines))))
        return
    if not result.items:
        await message.answer(t("purchase.ask_items"))
        return

    data = await state.get_data()
    customer = await users.get_by_id(session, data["user_id"])
    if customer is None:
        await state.clear()
        await message.answer(t("purchase.customer_not_found"))
        return

    await state.update_data(items=[{"name": i.name, "quantity": i.quantity, "price": i.price} for i in result.items])
    state_info, calc = await preview(session, customer, result.items, False, _now(), TIMEZONE, RULES)
    if calc.cashback_available > 0:
        await state.set_state(PurchaseEntry.cashback)
        await message.answer(
            t(
                "purchase.ask_cashback",
                balance=money(state_info.balance),
                available=money(calc.cashback_available),
                percent=RULES.cashback_max_use_percent,
            ),
            reply_markup=cashback_choice_keyboard(t, calc.cashback_available),
        )
    else:
        await _show_confirm(message, state, t, customer, result.items, calc, use_cashback=False)


@router.message(PurchaseEntry.customer, NOT_ADMIN_MENU)
@router.message(PurchaseEntry.items, NOT_ADMIN_MENU)
async def purchase_need_text(message: Message, t: Translate) -> None:
    await message.answer(t("purchase.need_text"))


@router.message(PurchaseEntry.cashback, NOT_ADMIN_MENU)
@router.message(PurchaseEntry.confirm, NOT_ADMIN_MENU)
async def purchase_use_buttons(message: Message, t: Translate) -> None:
    await message.answer(t("common.use_buttons"))


@router.callback_query(PurchaseEntry.cashback, PurchaseCb.filter(F.action.in_({"use", "skip"})))
async def purchase_cashback_choice(
    call: CallbackQuery, callback_data: PurchaseCb, state: FSMContext, session: AsyncSession, t: Translate
) -> None:
    data = await state.get_data()
    customer = await users.get_by_id(session, data["user_id"])
    await call.message.edit_reply_markup(reply_markup=None)
    if customer is None:
        await state.clear()
        await call.message.answer(t("purchase.customer_not_found"))
        await call.answer()
        return
    items = _items(data)
    use = callback_data.action == "use"
    _, calc = await preview(session, customer, items, use, _now(), TIMEZONE, RULES)
    await _show_confirm(call.message, state, t, customer, items, calc, use_cashback=use)
    await call.answer()


@router.callback_query(PurchaseEntry.confirm, PurchaseCb.filter(F.action == "confirm"))
async def purchase_confirm(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, t: Translate, i18n: Translator, bot: Bot
) -> None:
    data = await state.get_data()
    await call.message.edit_reply_markup(reply_markup=None)
    menu = admin_menu(t, call.from_user.id == DEVELOPER_ID)
    items = _items(data)
    now = _now()
    try:
        result = await register_purchase(
            session,
            user_id=data["user_id"],
            admin_telegram_id=call.from_user.id,
            items=items,
            use_cashback=data.get("use_cashback", False),
            now=now,
            tz=TIMEZONE,
            business=RULES,
        )
    except CustomerNotFound:
        await state.clear()
        await call.message.answer(t("purchase.customer_not_found"), reply_markup=menu)
        await call.answer()
        return
    except InsufficientCashback:
        await state.clear()
        await call.message.answer(t("purchase.balance_changed"), reply_markup=menu)
        await call.answer()
        return

    await state.clear()
    customer = result.user
    await call.message.answer(
        t("purchase.saved", purchase_id=result.purchase.id, name=esc(customer.full_name)), reply_markup=menu
    )

    customer_t = i18n.bind(customer.language)
    delivered = await send_to_user(
        bot, session, customer.telegram_id, customer_receipt(customer_t, items, result.calc, result.balance)
    )
    if not delivered:
        await call.message.answer(t("purchase.customer_not_notified"))

    reward = result.referral_reward
    if reward is not None:
        referrer_t = i18n.bind(reward.referrer.language)
        referrer_balance = await cashback.balance(session, reward.referrer.id, now)
        await send_to_user(
            bot,
            session,
            reward.referrer.telegram_id,
            referrer_t(
                "referral.bonus_received",
                name=esc(reward.friend.first_name),
                amount=money(reward.amount),
                balance=money(referrer_balance),
            ),
        )
    await call.answer()


@router.callback_query(PurchaseCb.filter(F.action == "cancel"))
async def purchase_cancel(call: CallbackQuery, state: FSMContext, t: Translate) -> None:
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t("common.cancelled"), reply_markup=admin_menu(t, call.from_user.id == DEVELOPER_ID))
    await call.answer()
