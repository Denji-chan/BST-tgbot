import logging
from pathlib import Path

import pytest

from data.settings import ConfigError, build_settings

VALID = {
    "BOT_TOKEN": "123456789:AAH_test_token_abcdefghijklmnopqrstuv",
    "DEVELOPER_ID": "8897276236",
    "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/bestshop",
}


def test_valid_settings_with_defaults():
    s = build_settings(VALID)
    assert s.developer_id == 8897276236
    assert s.timezone_name == "Asia/Tashkent"
    assert str(s.timezone) == "Asia/Tashkent"
    assert s.log_level == logging.INFO
    assert s.log_dir == Path("logs")


def test_optional_values_are_read():
    s = build_settings({**VALID, "TIMEZONE": "Europe/Moscow", "LOG_LEVEL": "debug", "LOG_DIR": "/var/log/bot"})
    assert s.timezone_name == "Europe/Moscow"
    assert s.log_level == logging.DEBUG
    assert s.log_dir == Path("/var/log/bot")


def test_whitespace_is_trimmed():
    s = build_settings({**VALID, "DEVELOPER_ID": "  42  "})
    assert s.developer_id == 42


def test_all_problems_reported_at_once():
    with pytest.raises(ConfigError) as exc:
        build_settings({})
    problems = " ".join(exc.value.problems)
    assert len(exc.value.problems) == 3
    assert "BOT_TOKEN" in problems
    assert "DEVELOPER_ID" in problems
    assert "DATABASE_URL" in problems


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("BOT_TOKEN", "not-a-token", "BOT_TOKEN"),
        ("DEVELOPER_ID", "abc", "DEVELOPER_ID"),
        ("DEVELOPER_ID", "-5", "DEVELOPER_ID"),
        ("DATABASE_URL", "postgresql://user:pass@localhost/db", "DATABASE_URL"),
        ("TIMEZONE", "Mars/Olympus", "TIMEZONE"),
        ("LOG_LEVEL", "LOUD", "LOG_LEVEL"),
    ],
)
def test_invalid_values(key, value, expected):
    with pytest.raises(ConfigError) as exc:
        build_settings({**VALID, key: value})
    assert len(exc.value.problems) == 1
    assert expected in exc.value.problems[0]


def test_error_message_does_not_leak_token():
    bad = "123:short"
    with pytest.raises(ConfigError) as exc:
        build_settings({**VALID, "BOT_TOKEN": bad})
    assert bad not in str(exc.value)
