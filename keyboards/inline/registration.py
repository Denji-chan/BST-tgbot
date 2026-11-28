from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import RegistrationCb
from utils.misc.i18n import Translate


def confirm_registration_keyboard(t: Translate) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn.confirm"), callback_data=RegistrationCb(action="ok"))
    builder.button(text=t("btn.restart"), callback_data=RegistrationCb(action="restart"))
    builder.adjust(2)
    return builder.as_markup()
