from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.inline.callbacks import AdminAddCb, AdminRemoveCb
from utils.db_api.models import Admin
from utils.misc.i18n import Translate


def admins_keyboard(t: Translate, items: list[Admin], developer_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for admin in items:
        if admin.telegram_id == developer_id:
            continue
        label = admin.full_name or str(admin.telegram_id)
        builder.button(
            text=t("btn.remove_admin", name=label), callback_data=AdminRemoveCb(telegram_id=admin.telegram_id)
        )
    builder.button(text=t("btn.add_admin"), callback_data=AdminAddCb())
    builder.adjust(1)
    return builder.as_markup()
