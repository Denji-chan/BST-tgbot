from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import BroadcastCb
from utils.misc.i18n import Translate


def broadcast_confirm_keyboard(t: Translate) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn.broadcast_send"), callback_data=BroadcastCb(action="send"))
    builder.button(text=t("btn.cancel"), callback_data=BroadcastCb(action="cancel"))
    builder.adjust(2)
    return builder.as_markup()
