"""Bot sozlamalari. Qiymatlar .env faylidan o'qiladi."""
import os
from datetime import timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

# @BotFather bergan token
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

# Eng katta admin (DEVELOPER) — boshqalarni admin qila oladi
DEVELOPER_ID: int = int(os.getenv("DEVELOPER_ID", "8897276236"))

# SQLite baza fayli
DB_PATH: str = os.getenv("DB_PATH", "best_shop.db")

# Boshlang'ich cashback foizi (keyin admin paneldan o'zgartiriladi)
DEFAULT_CASHBACK_PERCENT: int = int(os.getenv("CASHBACK_PERCENT", "3"))
MAX_CASHBACK_PERCENT: int = 50

SHOP_NAME: str = "BEST SHOP TREND"

# O'zbekiston vaqti (UTC+5, yozgi vaqt yo'q)
TZ = timezone(timedelta(hours=5))
