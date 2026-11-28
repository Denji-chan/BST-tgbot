"""Loglar sozlamasi.

- konsolga va `LOG_DIR/bot.log` fayliga yoziladi (10 MB dan 5 ta fayl, aylanma);
- vaqt Asia/Tashkent bo'yicha ko'rsatiladi;
- bot tokeni loglarga tushmaydi, telefon raqamlarining faqat oxirgi 4 raqami qoladi.

Bu modul aiogram'ga bog'liq emas.
"""

import logging
import re
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from zoneinfo import ZoneInfo

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_NAME = "bot.log"
MAX_BYTES = 10 * 1024 * 1024
BACKUP_COUNT = 5

# +998XXXXXXXXX yoki 998XXXXXXXXX ko'rinishidagi raqamlar
_PHONE_RE = re.compile(r"(\+?998)(\d{5})(\d{4})\b")


def mask_phone_numbers(text: str) -> str:
    return _PHONE_RE.sub(lambda m: f"{m.group(1)}*****{m.group(3)}", text)


class SensitiveDataFilter(logging.Filter):
    """Log xabaridan maxfiy ma'lumotlarni olib tashlaydi."""

    def __init__(self, secrets: list[str] | None = None) -> None:
        super().__init__()
        self._secrets = [s for s in (secrets or []) if s]

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        cleaned = message
        for secret in self._secrets:
            cleaned = cleaned.replace(secret, "***")
        cleaned = mask_phone_numbers(cleaned)
        if cleaned != message:
            record.msg = cleaned
            record.args = None
        return True


class TimezoneFormatter(logging.Formatter):
    def __init__(self, fmt: str, datefmt: str, tz: ZoneInfo) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._tz = tz

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=self._tz)
        return dt.strftime(datefmt or DATE_FORMAT)


def setup_logging(
    level: int = logging.INFO,
    log_dir: Path | None = None,
    tz: ZoneInfo | None = None,
    secrets: list[str] | None = None,
) -> None:
    formatter = TimezoneFormatter(LOG_FORMAT, DATE_FORMAT, tz or ZoneInfo("Asia/Tashkent"))
    sensitive = SensitiveDataFilter(secrets)

    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_dir is not None:
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(
            RotatingFileHandler(
                log_dir / LOG_FILE_NAME,
                maxBytes=MAX_BYTES,
                backupCount=BACKUP_COUNT,
                encoding="utf-8",
            )
        )

    root = logging.getLogger()
    for old in list(root.handlers):
        root.removeHandler(old)
    for handler in handlers:
        handler.setFormatter(formatter)
        handler.addFilter(sensitive)
        root.addHandler(handler)
    root.setLevel(level)

    # aiogram har bir update haqida INFO yozadi; DEBUG bo'lmasa, shovqinni kamaytiramiz.
    if level > logging.DEBUG:
        logging.getLogger("aiogram.event").setLevel(logging.WARNING)
