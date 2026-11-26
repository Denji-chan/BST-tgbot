"""Umumiy yordamchi funksiyalar."""
import re
from html import escape
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from database import db
from keyboards import admin_menu, lang_kb, phone_kb, source_kb, user_menu
from states import Reg
from texts import money, t

NAME_ALLOWED_EXTRA = set(" '-.`ʻʼ‘’")


async def safe_edit(message: Message, text: str, reply_markup=None) -> None:
    """Xabarni tahrirlash; eski yoki o'zgarmagan xabar bo'lsa xatoni yutadi."""
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest:
        pass


async def resume_registration(message: Message, state: FSMContext, tg_id: int) -> None:
    """Foydalanuvchini kerakli bosqichga olib boradi:
    til -> (admin bo'lsa admin panel) -> qayerdan eshitgan -> telefon -> ism familiya -> menyu.
    Bosqich bazadan aniqlanadi, shuning uchun bot qayta ishga tushsa ham davom etadi."""
    user = db.get_user(tg_id)
    if user is None or not user["lang"]:
        await state.set_state(Reg.lang)
        await message.answer(t("choose_lang"), reply_markup=lang_kb("reglang"))
        return

    lang = user["lang"]
    if db.is_admin(tg_id):
        await state.clear()
        await message.answer(t("admin_panel", lang), reply_markup=admin_menu(lang, db.is_developer(tg_id)))
        return
    if user["is_registered"]:
        await state.clear()
        await message.answer(t("use_menu", lang), reply_markup=user_menu(lang))
        return
    if not user["source"]:
        await state.set_state(Reg.source)
        await message.answer(t("ask_source", lang), reply_markup=source_kb(lang))
    elif not user["phone"]:
        await state.set_state(Reg.phone)
        await message.answer(t("ask_phone", lang), reply_markup=phone_kb(lang))
    else:
        await state.set_state(Reg.name)
        await message.answer(t("ask_name", lang), reply_markup=ReplyKeyboardRemove())


def clean_name(text: Optional[str]) -> Optional[str]:
    """Ism-familiyani tekshiradi va chiroyli ko'rinishga keltiradi. Noto'g'ri bo'lsa None."""
    if not text or text.startswith("/"):
        return None
    name = " ".join(text.split())
    if not 3 <= len(name) <= 60 or len(name.split()) < 2:
        return None
    if not all(ch.isalpha() or ch in NAME_ALLOWED_EXTRA for ch in name):
        return None
    return " ".join(w[:1].upper() + w[1:] for w in name.split())


def parse_amount(text: Optional[str]) -> Optional[int]:
    """'250 000 so'm' -> 250000. Noto'g'ri bo'lsa None."""
    digits = re.sub(r"\D", "", text or "")
    if not digits or len(digits) > 12:
        return None
    value = int(digits)
    return value if value > 0 else None


def normalize_phone(phone: str) -> str:
    return "+" + re.sub(r"\D", "", phone)


def customer_card_text(customer, lang: str) -> str:
    return t(
        "customer_card", lang,
        name=escape(customer["full_name"] or ""),
        card=customer["id"],
        phone=customer["phone"] or "—",
        balance=money(customer["cashback"], lang),
    )


def history_text(user_id: int, lang: str, limit: int = 10) -> str:
    rows = db.history(user_id, limit)
    if not rows:
        return t("history_empty", lang)
    lines = []
    for r in rows:
        if r["kind"] == "add":
            line = t("hist_add", lang, amount=money(r["amount"], lang), purchase=money(r["purchase_amount"], lang))
        else:
            line = t("hist_spend", lang, amount=money(r["amount"], lang))
        lines.append(f"<code>{r['created_at'][:16]}</code>  {line}")
    return t("history_title", lang) + "\n\n" + "\n".join(lines)


async def notify_user(bot: Bot, tg_id: int, text: str) -> bool:
    """Mijozga xabar yuboradi. Yetib bormasa False."""
    try:
        await bot.send_message(tg_id, text)
        return True
    except TelegramForbiddenError:
        db.mark_blocked(tg_id)
        return False
    except TelegramAPIError:
        return False
