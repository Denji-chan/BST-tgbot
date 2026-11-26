"""Admin panel: xabar yuborish, statistika, Excel, cashback, foiz, adminlar."""
import asyncio
import logging
from datetime import datetime
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from config import DEVELOPER_ID, MAX_CASHBACK_PERCENT, TZ
from database import db
from excel_export import build_customers_excel
from filters import IsAdmin, IsDeveloper
from helpers import customer_card_text, history_text, notify_user, parse_amount, safe_edit
from keyboards import admin_menu, admins_kb, cancel_kb, confirm_kb, stats_kb
from states import AddAdmin, Broadcast, Cashback, FindCustomer, SetPercent
from texts import LANG_NAMES, money, t, variants

log = logging.getLogger(__name__)

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())

_background_tasks: set[asyncio.Task] = set()


def _lang(event) -> str:
    return db.get_lang(event.from_user.id)


def _menu(tg_id: int, lang: str):
    return admin_menu(lang, db.is_developer(tg_id))


# ================================================================ panel
@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = _lang(message)
    await message.answer(t("admin_panel", lang), reply_markup=_menu(message.from_user.id, lang))


# ================================================================ statistika
def stats_text(lang: str) -> str:
    s = db.stats()
    langs = "\n".join(f"• {LANG_NAMES.get(k, k)}: {c}" for k, c in s["langs"]) or "—"
    sources = "\n".join(f"• {t('src_' + k, lang)}: {c}" for k, c in s["sources"]) or "—"
    return t(
        "stats", lang,
        total=s["total"], today=s["today"], week=s["week"], month=s["month"], blocked=s["blocked"],
        langs=langs, sources=sources,
        cb_balance=money(s["cb_balance"], lang),
        cb_given=money(s["cb_given"], lang),
        cb_spent=money(s["cb_spent"], lang),
        percent=s["percent"],
    )


@router.message(F.text.in_(variants("btn_stats")))
async def stats(message: Message) -> None:
    lang = _lang(message)
    await message.answer(stats_text(lang), reply_markup=stats_kb(lang))


async def send_excel(message: Message, lang: str) -> None:
    wait = await message.answer(t("excel_preparing", lang))
    data, filename = build_customers_excel(db, lang)
    caption = t(
        "excel_caption", lang,
        date=datetime.now(TZ).strftime("%Y-%m-%d %H:%M"),
        total=db.stats()["total"],
    )
    await message.answer_document(BufferedInputFile(data, filename=filename), caption=caption)
    try:
        await wait.delete()
    except TelegramBadRequest:
        pass


@router.message(F.text.in_(variants("btn_excel")))
async def excel_msg(message: Message) -> None:
    await send_excel(message, _lang(message))


@router.callback_query(F.data == "excel")
async def excel_cb(call: CallbackQuery) -> None:
    await call.answer()
    await send_excel(call.message, _lang(call))


# ================================================================ xabar yuborish
@router.message(F.text.in_(variants("btn_broadcast")))
async def bc_start(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    await state.set_state(Broadcast.content)
    await message.answer(t("bc_ask", lang), reply_markup=cancel_kb(lang))


@router.message(Broadcast.content)
async def bc_content(message: Message, state: FSMContext, bot: Bot) -> None:
    lang = _lang(message)
    if not (message.text or message.photo or message.video or message.animation):
        await message.answer(t("bc_unsupported", lang))
        return
    count = len(db.active_customer_ids())
    if count == 0:
        await state.clear()
        await message.answer(t("bc_no_customers", lang), reply_markup=_menu(message.from_user.id, lang))
        return
    await state.update_data(chat_id=message.chat.id, message_id=message.message_id)
    await state.set_state(Broadcast.confirm)
    # Ko'rib chiqish uchun xabar nusxasi
    await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=message.message_id)
    await message.answer(t("bc_preview", lang, count=count), reply_markup=confirm_kb(lang, "bc", "btn_send"))


async def run_broadcast(bot: Bot, admin_chat_id: int, from_chat_id: int, message_id: int, lang: str) -> None:
    ok = fail = 0
    for tg_id in db.active_customer_ids():
        for attempt in range(2):
            try:
                await bot.copy_message(chat_id=tg_id, from_chat_id=from_chat_id, message_id=message_id)
                ok += 1
                break
            except TelegramRetryAfter as e:  # Telegram limiti — kutib, qayta urinamiz
                await asyncio.sleep(e.retry_after + 1)
                if attempt == 1:
                    fail += 1
            except TelegramForbiddenError:   # mijoz botni bloklagan
                db.mark_blocked(tg_id)
                fail += 1
                break
            except TelegramAPIError as e:
                log.warning("Broadcast error for %s: %s", tg_id, e)
                fail += 1
                break
        await asyncio.sleep(0.05)  # sekundiga ~20 ta xabar (Telegram limitidan past)
    try:
        await bot.send_message(admin_chat_id, t("bc_done", lang, ok=ok, fail=fail))
    except TelegramAPIError:
        log.exception("Could not send broadcast report")


@router.callback_query(Broadcast.confirm, F.data == "bc:yes")
async def bc_confirm(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.clear()
    lang = _lang(call)
    await call.answer()
    await safe_edit(call.message, t("bc_started", lang))
    await call.message.answer(t("admin_panel", lang), reply_markup=_menu(call.from_user.id, lang))
    task = asyncio.create_task(
        run_broadcast(bot, call.from_user.id, data["chat_id"], data["message_id"], lang)
    )
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


@router.callback_query(F.data.in_({"bc:no", "cb:no"}))
async def flow_cancel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    lang = _lang(call)
    await call.answer()
    await safe_edit(call.message, t("cancelled", lang))
    await call.message.answer(t("admin_panel", lang), reply_markup=_menu(call.from_user.id, lang))


# ================================================================ cashback
async def _cashback_start(message: Message, state: FSMContext, mode: str) -> None:
    lang = _lang(message)
    await state.set_state(Cashback.find)
    await state.update_data(mode=mode)
    await message.answer(t("cb_ask_customer", lang), reply_markup=cancel_kb(lang))


@router.message(F.text.in_(variants("btn_cb_add")))
async def cb_add_start(message: Message, state: FSMContext) -> None:
    await _cashback_start(message, state, "add")


@router.message(F.text.in_(variants("btn_cb_spend")))
async def cb_spend_start(message: Message, state: FSMContext) -> None:
    await _cashback_start(message, state, "spend")


@router.message(Cashback.find, F.text)
async def cb_find(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    data = await state.get_data()
    customer = db.find_customer(message.text)
    if customer is None:
        await message.answer(t("cb_not_found", lang))
        return
    card = customer_card_text(customer, lang)
    if data.get("mode") == "spend":
        if customer["cashback"] <= 0:
            await state.clear()
            await message.answer(card + "\n\n" + t("zero_balance", lang), reply_markup=_menu(message.from_user.id, lang))
            return
        prompt = t("cb_ask_spend", lang, balance=money(customer["cashback"], lang))
    else:
        prompt = t("cb_ask_purchase", lang, percent=db.get_percent())
    await state.update_data(user_id=customer["id"])
    await state.set_state(Cashback.amount)
    await message.answer(card + "\n\n" + prompt)


@router.message(Cashback.amount, F.text)
async def cb_amount(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    data = await state.get_data()
    amount = parse_amount(message.text)
    if amount is None:
        await message.answer(t("amount_invalid", lang))
        return
    customer = db.get_customer(data["user_id"])
    if customer is None:
        await state.clear()
        await message.answer(t("cb_not_found", lang), reply_markup=_menu(message.from_user.id, lang))
        return
    name = escape(customer["full_name"] or "")

    if data.get("mode") == "add":
        percent = db.get_percent()
        cashback = amount * percent // 100
        if cashback <= 0:
            await message.answer(t("cb_zero", lang))
            return
        await state.update_data(purchase=amount, amount=cashback, percent=percent)
        text = t(
            "cb_confirm_add", lang,
            name=name, card=customer["id"], purchase=money(amount, lang), percent=percent,
            amount=money(cashback, lang), new_balance=money(customer["cashback"] + cashback, lang),
        )
    else:
        if amount > customer["cashback"]:
            await message.answer(t("spend_too_much", lang, balance=money(customer["cashback"], lang)))
            return
        await state.update_data(amount=amount)
        text = t(
            "cb_confirm_spend", lang,
            name=name, card=customer["id"], amount=money(amount, lang),
            new_balance=money(customer["cashback"] - amount, lang),
        )
    await state.set_state(Cashback.confirm)
    await message.answer(text, reply_markup=confirm_kb(lang, "cb"))


@router.callback_query(Cashback.confirm, F.data == "cb:yes")
async def cb_confirm(call: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    await state.clear()  # ikki marta bosilsa, ikkinchisi hech narsa qilmaydi
    lang = _lang(call)
    await call.answer()
    menu = _menu(call.from_user.id, lang)

    customer = db.get_customer(data["user_id"])
    if customer is None:
        await safe_edit(call.message, t("cb_not_found", lang))
        await call.message.answer(t("admin_panel", lang), reply_markup=menu)
        return
    c_lang = customer["lang"] or "uz"

    if data["mode"] == "add":
        balance = db.add_cashback(customer["id"], call.from_user.id, data["purchase"], data["amount"], data["percent"])
        done = t("cb_done_add", lang, balance=money(balance, lang))
        notify = t(
            "cashback_added_notify", c_lang,
            amount=money(data["amount"], c_lang),
            purchase=money(data["purchase"], c_lang),
            balance=money(balance, c_lang),
        )
    else:
        balance = db.spend_cashback(customer["id"], call.from_user.id, data["amount"])
        if balance is None:
            fresh = db.get_customer(customer["id"])
            await safe_edit(call.message, t("spend_too_much", lang, balance=money(fresh["cashback"], lang)))
            await call.message.answer(t("admin_panel", lang), reply_markup=menu)
            return
        done = t("cb_done_spend", lang, balance=money(balance, lang))
        notify = t(
            "cashback_spent_notify", c_lang,
            amount=money(data["amount"], c_lang),
            balance=money(balance, c_lang),
        )

    delivered = await notify_user(bot, customer["tg_id"], notify)
    status = t("notify_ok", lang) if delivered else t("notify_failed", lang)
    await safe_edit(call.message, customer_card_text(db.get_customer(customer["id"]), lang) + "\n\n" + done + "\n" + status)
    await call.message.answer(t("admin_panel", lang), reply_markup=menu)


# ================================================================ mijozni topish
@router.message(F.text.in_(variants("btn_find")))
async def find_start(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    await state.set_state(FindCustomer.query)
    await message.answer(t("cb_ask_customer", lang), reply_markup=cancel_kb(lang))


@router.message(FindCustomer.query, F.text)
async def find_customer(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    customer = db.find_customer(message.text)
    if customer is None:
        await message.answer(t("cb_not_found", lang))
        return
    await state.clear()
    await message.answer(
        customer_card_text(customer, lang) + "\n\n" + history_text(customer["id"], lang),
        reply_markup=_menu(message.from_user.id, lang),
    )


# ================================================================ cashback foizi
@router.message(F.text.in_(variants("btn_percent")))
async def percent_start(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    await state.set_state(SetPercent.value)
    await message.answer(
        t("percent_ask", lang, percent=db.get_percent(), max=MAX_CASHBACK_PERCENT),
        reply_markup=cancel_kb(lang),
    )


@router.message(SetPercent.value, F.text)
async def percent_set(message: Message, state: FSMContext) -> None:
    lang = _lang(message)
    raw = message.text.strip().rstrip("%").strip()
    if not raw.isdigit() or int(raw) > MAX_CASHBACK_PERCENT:
        await message.answer(t("percent_invalid", lang, max=MAX_CASHBACK_PERCENT))
        return
    db.set_percent(int(raw))
    await state.clear()
    await message.answer(t("percent_set", lang, percent=int(raw)), reply_markup=_menu(message.from_user.id, lang))


# ================================================================ adminlar (faqat developer)
def admins_view(lang: str):
    rows = db.list_admins()
    lines = []
    for r in rows:
        line = f"• <code>{r['tg_id']}</code>"
        if r["full_name"]:
            line += f" — {escape(r['full_name'])}"
        if r["username"]:
            line += f" (@{escape(r['username'])})"
        lines.append(line)
    text = t("admins_list", lang, dev=DEVELOPER_ID, list="\n".join(lines) or t("admins_empty", lang))
    return text, admins_kb(lang, [r["tg_id"] for r in rows])


@router.message(F.text.in_(variants("btn_admins")))
async def admins(message: Message, state: FSMContext) -> None:
    await state.clear()
    lang = _lang(message)
    if not db.is_developer(message.from_user.id):
        await message.answer(t("only_developer", lang))
        return
    text, kb = admins_view(lang)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "adm:add", IsDeveloper())
async def admin_add_start(call: CallbackQuery, state: FSMContext) -> None:
    lang = _lang(call)
    await call.answer()
    await state.set_state(AddAdmin.tg_id)
    await call.message.answer(t("admin_ask_id", lang), reply_markup=cancel_kb(lang))


@router.message(AddAdmin.tg_id, F.text, IsDeveloper())
async def admin_add(message: Message, state: FSMContext, bot: Bot) -> None:
    lang = _lang(message)
    raw = message.text.strip()
    if not raw.isdigit() or not 5 <= len(raw) <= 15:
        await message.answer(t("admin_id_invalid", lang))
        return
    new_id = int(raw)
    await state.clear()
    menu = _menu(message.from_user.id, lang)
    if db.is_admin(new_id):
        await message.answer(t("admin_exists", lang), reply_markup=menu)
    else:
        db.add_admin(new_id, message.from_user.id)
        await message.answer(t("admin_added", lang, id=new_id), reply_markup=menu)
        await notify_user(bot, new_id, t("you_are_admin", db.get_lang(new_id)))
    text, kb = admins_view(lang)
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("adm:del:"), IsDeveloper())
async def admin_delete(call: CallbackQuery) -> None:
    lang = _lang(call)
    raw = call.data.rsplit(":", 1)[1]
    if raw.isdigit():
        db.remove_admin(int(raw))
        await call.answer(t("admin_removed", lang, id=raw).replace("<code>", "").replace("</code>", ""))
    else:
        await call.answer()
    text, kb = admins_view(lang)
    await safe_edit(call.message, text, reply_markup=kb)
