"""Sozlamalar faqat .env faylidan (yoki muhit o'zgaruvchilaridan) o'qiladi.

Kodda hech qanday maxfiy qiymat yo'q. Adminlar .env da emas, bazada saqlanadi;
.env da faqat bosh admin (Developer) turadi.

Shablon uslubidagi qisqa nomlar ham saqlangan: `from data.config import BOT_TOKEN`.
"""

import os
import sys

from environs import Env

from data.settings import ConfigError, Settings, build_settings
from services.rules import BusinessRules

env = Env()
env.read_env()  # .env faylini os.environ ga yuklaydi (mavjud o'zgaruvchilarni almashtirmaydi)

try:
    settings: Settings = build_settings(os.environ)
except ConfigError as err:
    print(err, file=sys.stderr)
    raise SystemExit(1) from err

BOT_TOKEN: str = settings.bot_token
DEVELOPER_ID: int = settings.developer_id
DATABASE_URL: str = settings.database_url
TIMEZONE = settings.timezone

RULES = BusinessRules(cashback_max_use_percent=settings.cashback_max_use_percent)
