import pytest

from services.cashback import calculate_purchase
from services.customer_search import parse_customer_query
from services.items import MAX_ITEMS, Item, items_total, parse_items, parse_line
from services.rules import BusinessRules
from utils.misc.i18n import Translator
from utils.misc.receipts import admin_preview, customer_receipt

RULES = BusinessRules()


@pytest.mark.parametrize(
    "line, expected",
    [
        ("Ko'ylak - 150000", Item("Ko'ylak", 1, 150_000)),
        ("Shim - 2 x 120 000", Item("Shim", 2, 120_000)),
        ("Sumka; 89000 so'm", Item("Sumka", 1, 89_000)),
        ("Kurtka — 950 000 сум", Item("Kurtka", 1, 950_000)),
        ("Futbolka: 3х90000", Item("Futbolka", 3, 90_000)),
        ("  Yubka   uzun  -  200000 ", Item("Yubka uzun", 1, 200_000)),
        ("Ko'ylak 150000", None),  # ajratuvchi yo'q
        ("Ko'ylak - narx", None),
        ("Ko'ylak - 0", None),
        ("Ko'ylak - 0 x 1000", None),
        ("Ko'ylak - 101 x 1000", None),
        ("- 150000", None),
    ],
)
def test_parse_line(line, expected):
    assert parse_line(line) == expected


def test_parse_items_reports_bad_lines():
    result = parse_items("Ko'ylak - 150000\n\nyomon qator\nShim - 2 x 120000")
    assert result.items == [Item("Ko'ylak", 1, 150_000), Item("Shim", 2, 120_000)]
    assert result.bad_lines == [3]
    assert not result.ok


def test_parse_items_ok_and_total():
    result = parse_items("Ko'ylak - 150000\nShim - 2 x 120000")
    assert result.ok
    assert items_total(result.items) == 390_000


def test_parse_items_limits():
    assert parse_items("").ok is False
    assert parse_items("\n".join(f"T{i} - 1000" for i in range(MAX_ITEMS + 1))).too_many


@pytest.mark.parametrize(
    "text, customer_id, phone",
    [
        ("125", 125, None),
        ("#125", 125, None),
        ("1234567", 1234567, None),
        ("901234567", None, "+998901234567"),
        ("+998 90 123 45 67", None, "+998901234567"),
        ("998901234567", None, "+998901234567"),
    ],
)
def test_parse_customer_query(text, customer_id, phone):
    query = parse_customer_query(text)
    assert query.customer_id == customer_id
    assert query.phone == phone


@pytest.mark.parametrize("text", ["", "abc", "12-34", None])
def test_parse_customer_query_invalid(text):
    assert parse_customer_query(text) is None


@pytest.fixture(scope="module")
def tr():
    return Translator()


def test_customer_receipt_contains_all_parts(tr):
    t = tr.bind("uz")
    items = [Item("Ko'ylak", 1, 150_000), Item("Shim", 2, 50_000)]
    calc = calculate_purchase(250_000, balance=5_000, use_cashback=True, birthday_applies=False, rules=RULES)
    text = customer_receipt(t, items, calc, balance=7_350)
    for part in ("Ko'ylak", "150 000", "2 x 50 000", "250 000", "5 000", "245 000", "7 350"):
        assert part in text
    assert "Tug'ilgan kun" not in text  # chegirma bo'lmasa ko'rsatilmaydi


def test_receipt_shows_birthday_and_escapes_names(tr):
    t = tr.bind("ru")
    items = [Item("<script>", 1, 100_000)]
    calc = calculate_purchase(100_000, balance=0, use_cashback=False, birthday_applies=True, rules=RULES)
    text = customer_receipt(t, items, calc, balance=2_700)
    assert "&lt;script&gt;" in text
    assert "10 000" in text and "90 000" in text


def test_admin_preview(tr):
    t = tr.bind("en")
    calc = calculate_purchase(100_000, balance=0, use_cashback=False, birthday_applies=False, rules=RULES)
    text = admin_preview(t, "Malika Karimova", 15, [Item("Dress", 1, 100_000)], calc)
    assert "Malika Karimova" in text and "ID 15" in text and "3 000" in text
