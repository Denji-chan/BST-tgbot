from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import TextActionCb, TextKeyCb, TextLangCb
from services.templates import TEMPLATE_KEYS
from utils.misc.i18n import LANGUAGES, Translate, Translator


def template_keys_keyboard(t: Translate) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key in TEMPLATE_KEYS:
        builder.button(text=t(f"texts.name_{key}"), callback_data=TextKeyCb(key=key))
    builder.adjust(1)
    return builder.as_markup()


def template_languages_keyboard(t: Translate, translator: Translator, key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code in LANGUAGES:
        builder.button(text=translator.get(code, "lang.name"), callback_data=TextLangCb(key=key, code=code))
    builder.button(text=t("btn.back"), callback_data=TextActionCb(action="back", key=key, code=""))
    builder.adjust(len(LANGUAGES), 1)
    return builder.as_markup()


def template_actions_keyboard(t: Translate, key: str, code: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=t("btn.edit"), callback_data=TextActionCb(action="edit", key=key, code=code))
    builder.button(text=t("btn.back"), callback_data=TextKeyCb(key=key))
    builder.adjust(2)
    return builder.as_markup()
