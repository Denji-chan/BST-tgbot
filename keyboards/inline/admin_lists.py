from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import StatsCb, UsersExportCb, UsersPageCb
from services.periods import PERIODS
from utils.misc.i18n import Translate


def stats_keyboard(t: Translate, current: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for period in PERIODS:
        label = t(f"stats.period_{period}")
        if period == current:
            label = f"• {label} •"
        builder.button(text=label, callback_data=StatsCb(period=period))
    builder.adjust(4)
    return builder.as_markup()


def users_page_keyboard(t: Translate, page: int, pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav = 0
    if page > 0:
        builder.button(text=t("btn.prev"), callback_data=UsersPageCb(page=page - 1))
        nav += 1
    if page < pages - 1:
        builder.button(text=t("btn.next"), callback_data=UsersPageCb(page=page + 1))
        nav += 1
    builder.button(text=t("btn.export_excel"), callback_data=UsersExportCb())
    builder.adjust(*([nav] if nav else []), 1)
    return builder.as_markup()
