import pytest

from services.validators import parse_telegram_id


@pytest.mark.parametrize(
    "text, expected",
    [("8897276236", 8897276236), (" 123456 ", 123456), ("1234", None), ("abc", None), ("-123456", None), (None, None)],
)
def test_parse_telegram_id(text, expected):
    assert parse_telegram_id(text) == expected
