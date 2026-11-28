import logging
from zoneinfo import ZoneInfo

from utils.misc.logging import (
    LOG_FILE_NAME,
    SensitiveDataFilter,
    TimezoneFormatter,
    mask_phone_numbers,
    setup_logging,
)

TOKEN = "123456789:AAH_test_token_abcdefghijklmnopqrstuv"


def make_record(msg, *args):
    return logging.LogRecord("test", logging.INFO, __file__, 1, msg, args, None)


def test_mask_phone_numbers():
    assert mask_phone_numbers("tel +998901234567") == "tel +998*****4567"
    assert mask_phone_numbers("tel 998901234567") == "tel 998*****4567"
    assert mask_phone_numbers("summa 250000") == "summa 250000"


def test_filter_removes_token_and_phone_from_args():
    record = make_record("token=%s phone=%s", TOKEN, "+998901234567")
    SensitiveDataFilter([TOKEN]).filter(record)
    text = record.getMessage()
    assert TOKEN not in text
    assert "***" in text
    assert "+998*****4567" in text


def test_filter_keeps_normal_message():
    record = make_record("Bot ishga tushdi, %s ta router", 4)
    SensitiveDataFilter([TOKEN]).filter(record)
    assert record.getMessage() == "Bot ishga tushdi, 4 ta router"


def test_formatter_uses_tashkent_time():
    record = make_record("x")
    record.created = 1767225600  # 2026-01-01 00:00:00 UTC
    fmt = TimezoneFormatter("%(asctime)s", "%Y-%m-%d %H:%M", ZoneInfo("Asia/Tashkent"))
    assert fmt.format(record) == "2026-01-01 05:00"


def test_setup_logging_writes_masked_file(tmp_path):
    setup_logging(level=logging.INFO, log_dir=tmp_path, secrets=[TOKEN])
    logging.getLogger("test").info("token %s, mijoz %s", TOKEN, "+998901234567")
    for handler in logging.getLogger().handlers:
        handler.flush()
    content = (tmp_path / LOG_FILE_NAME).read_text(encoding="utf-8")
    assert TOKEN not in content
    assert "+998901234567" not in content
    assert "+998*****4567" in content


def test_setup_logging_is_idempotent(tmp_path):
    setup_logging(log_dir=tmp_path)
    setup_logging(log_dir=tmp_path)
    assert len(logging.getLogger().handlers) == 2  # konsol + fayl, takrorlanmaydi
