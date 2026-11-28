"""Sozlamalarni tekshirish va yig'ish.

Bu modul hech qanday tashqi kutubxonaga bog'liq emas: u oddiy lug'atdan (os.environ)
o'qiydi. `.env` faylini yuklash `data/config.py` da. Shuning uchun bu yerdagi
tekshiruvlarni alohida testlash mumkin.
"""

import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TIMEZONE = "Asia/Tashkent"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_DIR = "logs"
DEFAULT_CASHBACK_MAX_USE_PERCENT = 50

_TOKEN_RE = re.compile(r"^\d{5,}:[A-Za-z0-9_-]{30,}$")
_DB_PREFIX = "postgresql+asyncpg://"
_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


class ConfigError(Exception):
    """Bir yoki bir nechta sozlama noto'g'ri. Xabarda barcha muammolar ro'yxati bo'ladi."""

    def __init__(self, problems: list[str]) -> None:
        self.problems = problems
        lines = "\n".join(f"  - {p}" for p in problems)
        super().__init__(f".env sozlamalarida xato:\n{lines}")


@dataclass(frozen=True)
class Settings:
    bot_token: str
    developer_id: int
    database_url: str
    timezone_name: str
    timezone: ZoneInfo
    log_level: int
    log_dir: Path
    cashback_max_use_percent: int = 50


def _get(raw: Mapping[str, str], name: str) -> str:
    return (raw.get(name) or "").strip()


def build_settings(raw: Mapping[str, str]) -> Settings:
    problems: list[str] = []

    bot_token = _get(raw, "BOT_TOKEN")
    if not bot_token:
        problems.append("BOT_TOKEN bo'sh. @BotFather bergan tokenni yozing")
    elif not _TOKEN_RE.match(bot_token):
        problems.append("BOT_TOKEN formati noto'g'ri (kutilgan ko'rinish: 123456789:AA...)")

    developer_raw = _get(raw, "DEVELOPER_ID")
    developer_id = 0
    if not developer_raw:
        problems.append("DEVELOPER_ID bo'sh. Bosh adminning Telegram ID raqamini yozing")
    else:
        try:
            developer_id = int(developer_raw)
            if developer_id <= 0:
                raise ValueError
        except ValueError:
            problems.append("DEVELOPER_ID musbat butun son bo'lishi kerak")

    database_url = _get(raw, "DATABASE_URL")
    if not database_url:
        problems.append("DATABASE_URL bo'sh")
    elif not database_url.startswith(_DB_PREFIX):
        problems.append(f"DATABASE_URL '{_DB_PREFIX}' bilan boshlanishi kerak")

    timezone_name = _get(raw, "TIMEZONE") or DEFAULT_TIMEZONE
    timezone: ZoneInfo | None = None
    try:
        timezone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        problems.append(f"TIMEZONE '{timezone_name}' topilmadi (masalan: {DEFAULT_TIMEZONE})")

    log_level_name = (_get(raw, "LOG_LEVEL") or DEFAULT_LOG_LEVEL).upper()
    if log_level_name not in _LOG_LEVELS:
        problems.append(f"LOG_LEVEL quyidagilardan biri bo'lishi kerak: {', '.join(_LOG_LEVELS)}")

    log_dir = Path(_get(raw, "LOG_DIR") or DEFAULT_LOG_DIR)

    max_use_raw = _get(raw, "CASHBACK_MAX_USE_PERCENT") or str(DEFAULT_CASHBACK_MAX_USE_PERCENT)
    cashback_max_use_percent = DEFAULT_CASHBACK_MAX_USE_PERCENT
    try:
        cashback_max_use_percent = int(max_use_raw)
        if not 0 <= cashback_max_use_percent <= 100:
            raise ValueError
    except ValueError:
        problems.append("CASHBACK_MAX_USE_PERCENT 0 dan 100 gacha butun son bo'lishi kerak")

    if problems:
        raise ConfigError(problems)

    return Settings(
        bot_token=bot_token,
        developer_id=developer_id,
        database_url=database_url,
        timezone_name=timezone_name,
        timezone=timezone,  # type: ignore[arg-type]
        log_level=getattr(logging, log_level_name),
        log_dir=log_dir,
        cashback_max_use_percent=cashback_max_use_percent,
    )
