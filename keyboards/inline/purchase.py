from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import PurchaseCb
from utils.misc.formatting import money
from utils.misc.i18n import Translate


def cashback_choice_keyboard(t: Translate, available: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn.use_cashback", amount=money(available)), callback_data=PurchaseCb(action="use"))
    builder.button(text=t("btn.skip_cashback"), callback_data=PurchaseCb(action="skip"))
    builder.button(text=t("btn.cancel"), callback_data=PurchaseCb(action="cancel"))
    builder.adjust(1)
    return builder.as_markup()


def confirm_purchase_keyboard(t: Translate) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn.confirm"), callback_data=PurchaseCb(action="confirm"))
    builder.button(text=t("btn.cancel"), callback_data=PurchaseCb(action="cancel"))
    builder.adjust(2)
    return builder.as_markup()
