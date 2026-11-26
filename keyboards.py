"""Tugmalar (reply va inline klaviaturalar)."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from database import db
from texts import LANG_NAMES, LANGS, SOURCES, t


def _ikb(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=txt, callback_data=data) for txt, data in row] for row in rows]
    )


def _rkb(rows: list[list[str]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=txt) for txt in row] for row in rows],
        resize_keyboard=True,
    )


# ------------------------------------------------------------------ inline
def lang_kb(prefix: str) -> InlineKeyboardMarkup:
    """prefix: 'reglang' (ro'yxatdan o'tishda) yoki 'chlang' (sozlamalarda)."""
    return _ikb([[(LANG_NAMES[code], f"{prefix}:{code}")] for code in LANGS])


def source_kb(lang: str) -> InlineKeyboardMarkup:
    buttons = [(t(f"src_{key}", lang), f"src:{key}") for key in SOURCES]
    return _ikb([buttons[i:i + 2] for i in range(0, len(buttons), 2)])


def settings_kb(lang: str, registered: bool) -> InlineKeyboardMarkup:
    rows = [[(t("btn_change_lang", lang), "set:lang")]]
    if registered:
        rows.append([(t("btn_change_name", lang), "set:name")])
    return _ikb(rows)


def profile_kb(lang: str) -> InlineKeyboardMarkup:
    return _ikb([[(t("btn_history", lang), "history")]])


def confirm_kb(lang: str, prefix: str, yes_key: str = "btn_confirm") -> InlineKeyboardMarkup:
    return _ikb([[(t(yes_key, lang), f"{prefix}:yes"), (t("btn_cancel", lang), f"{prefix}:no")]])


def stats_kb(lang: str) -> InlineKeyboardMarkup:
    return _ikb([[(t("btn_excel", lang), "excel")]])


def admins_kb(lang: str, admin_ids: list[int]) -> InlineKeyboardMarkup:
    rows = [[(f"🗑 {aid}", f"adm:del:{aid}")] for aid in admin_ids]
    rows.append([(t("btn_add_admin", lang), "adm:add")])
    return _ikb(rows)


# ------------------------------------------------------------------ reply
def phone_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn_send_phone", lang), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    return _rkb([[t("btn_cancel", lang)]])


def user_menu(lang: str) -> ReplyKeyboardMarkup:
    return _rkb([[t("btn_profile", lang), t("btn_settings", lang)]])


def admin_menu(lang: str, is_developer: bool) -> ReplyKeyboardMarkup:
    rows = [
        [t("btn_broadcast", lang), t("btn_stats", lang)],
        [t("btn_cb_add", lang), t("btn_cb_spend", lang)],
        [t("btn_find", lang), t("btn_excel", lang)],
        [t("btn_percent", lang), t("btn_settings", lang)],
    ]
    if is_developer:
        rows.append([t("btn_admins", lang)])
    return _rkb(rows)


def menu_for(tg_id: int, lang: str) -> ReplyKeyboardMarkup:
    """Foydalanuvchiga mos asosiy menyu: admin yoki mijoz."""
    if db.is_admin(tg_id):
        return admin_menu(lang, db.is_developer(tg_id))
    return user_menu(lang)
