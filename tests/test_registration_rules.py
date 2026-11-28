from datetime import date

import pytest

from services import referral
from services.validators import clean_name, parse_birth_date
from utils.misc.formatting import esc, money
from utils.misc.phone import normalize_phone

TODAY = date(2026, 11, 28)


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Malika", "Malika"),
        ("  Gulnoza   Bahodirovna ", "Gulnoza Bahodirovna"),
        ("O'g'iloy", "O'g'iloy"),
        ("Ma'mura-Xon", "Ma'mura-Xon"),
        ("Анна", "Анна"),
        ("A", None),
        ("Malika123", None),
        ("<b>x</b>", None),
        ("'-'", None),
        ("x" * 41, None),
        ("", None),
        (None, None),
    ],
)
def test_clean_name(raw, expected):
    assert clean_name(raw) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("14.05.2004", date(2004, 5, 14)),
        ("14/05/2004", date(2004, 5, 14)),
        ("14-05-2004", date(2004, 5, 14)),
        (" 1.1.2000 ", date(2000, 1, 1)),
        ("29.02.2004", date(2004, 2, 29)),
        ("29.02.2005", None),  # bunday sana yo'q
        ("31.12.2026", None),  # kelajak
        ("01.01.2022", None),  # 7 yoshdan kichik
        ("01.01.1900", None),  # 100 yoshdan katta
        ("2004-05-14", None),  # boshqa format
        ("bugun", None),
    ],
)
def test_parse_birth_date(raw, expected):
    assert parse_birth_date(raw, TODAY) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("998901234567", "+998901234567"),
        ("+998 90 123-45-67", "+998901234567"),
        ("901234567", "+998901234567"),
        ("+77011234567", "+77011234567"),
        ("12345", None),
        ("", None),
        (None, None),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected


def test_referral_payload_round_trip():
    assert referral.make_payload(15) == "ref15"
    assert referral.parse_payload("ref15") == 15
    assert referral.parse_payload(" ref7 ") == 7
    assert referral.parse_payload("ref") is None
    assert referral.parse_payload("refabc") is None
    assert referral.parse_payload("promo15") is None
    assert referral.parse_payload(None) is None
    assert referral.make_link("bestshop_bot", 15) == "https://t.me/bestshop_bot?start=ref15"


def test_self_referral_forbidden():
    assert referral.is_valid_referrer(100, 200) is True
    assert referral.is_valid_referrer(100, 100) is False


def test_formatting_helpers():
    assert money(0) == "0"
    assert money(1500) == "1 500"
    assert money(1234567) == "1 234 567"
    assert esc("<b>Ali & Vali</b>") == "&lt;b&gt;Ali &amp; Vali&lt;/b&gt;"
