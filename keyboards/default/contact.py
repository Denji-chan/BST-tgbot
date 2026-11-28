from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from utils.misc.i18n import Translate


def contact_keyboard(t: Translate) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t("btn.send_contact"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
