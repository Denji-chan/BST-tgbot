from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import SupportReplyCb
from utils.misc.i18n import Translate


def reply_keyboard(t: Translate, message_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn.support_reply"), callback_data=SupportReplyCb(message_id=message_id))
    return builder.as_markup()
