from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import LanguageCb, SettingsLanguageCb
from utils.misc.i18n import LANGUAGES, Translator


def language_keyboard(translator: Translator, settings: bool = False) -> InlineKeyboardMarkup:
    """Til tugmalari. Har bir til o'z tilida yoziladi: O'zbekcha, Русский, English."""
    builder = InlineKeyboardBuilder()
    for code in LANGUAGES:
        data = SettingsLanguageCb(code=code) if settings else LanguageCb(code=code)
        builder.button(text=translator.get(code, "lang.name"), callback_data=data)
    builder.adjust(len(LANGUAGES))
    return builder.as_markup()
