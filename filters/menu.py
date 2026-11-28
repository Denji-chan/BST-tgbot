from aiogram import F

from keyboards.default.main_menu import ADMIN_MENU_KEYS
from utils.misc.i18n import i18n

_ADMIN_MENU_TEXTS = set().union(*(i18n.variants(key) for key in ADMIN_MENU_KEYS))

# Admin jarayon ichida menyu tugmasini bossa, matn jarayonga emas, o'sha bo'limga ketadi.
NOT_ADMIN_MENU = ~F.text.in_(_ADMIN_MENU_TEXTS)
