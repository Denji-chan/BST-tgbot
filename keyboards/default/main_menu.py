from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from utils.misc.i18n import Translate


def user_menu(t: Translate) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t("btn.profile")), KeyboardButton(text=t("btn.referral"))],
            [KeyboardButton(text=t("btn.support")), KeyboardButton(text=t("btn.settings"))],
        ],
        resize_keyboard=True,
    )


def admin_menu(t: Translate, is_developer: bool) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=t("btn.admin_purchase"))],
        [KeyboardButton(text=t("btn.admin_stats")), KeyboardButton(text=t("btn.admin_users"))],
        [KeyboardButton(text=t("btn.admin_texts")), KeyboardButton(text=t("btn.admin_broadcast"))],
    ]
    last = [KeyboardButton(text=t("btn.settings"))]
    if is_developer:
        last.insert(0, KeyboardButton(text=t("btn.admin_admins")))
    rows.append(last)
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def menu_for(t: Translate, is_admin: bool, is_developer: bool) -> ReplyKeyboardMarkup:
    return admin_menu(t, is_developer) if is_admin else user_menu(t)


def cancel_keyboard(t: Translate) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t("btn.cancel"))]], resize_keyboard=True)


ADMIN_MENU_KEYS = (
    "btn.admin_purchase",
    "btn.admin_stats",
    "btn.admin_users",
    "btn.admin_texts",
    "btn.admin_broadcast",
    "btn.admin_admins",
    "btn.settings",
)
