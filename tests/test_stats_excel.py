from datetime import UTC, date, datetime, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo

import pytest
from openpyxl import load_workbook

from services.excel import HEADER_KEYS, CustomerRow, build_users_workbook
from services.periods import PERIODS, clamp_page, period_start, total_pages
from utils.misc.i18n import Translator

TZ = ZoneInfo("Asia/Tashkent")
NOW = datetime(2026, 12, 1, 9, 30, tzinfo=UTC)  # 14:30 Toshkent


def test_period_today_starts_at_local_midnight():
    start = period_start("today", NOW, TZ)
    assert start.astimezone(TZ) == datetime(2026, 12, 1, 0, 0, tzinfo=TZ)


def test_other_periods():
    assert period_start("d7", NOW, TZ) == NOW - timedelta(days=7)
    assert period_start("d30", NOW, TZ) == NOW - timedelta(days=30)
    assert period_start("all", NOW, TZ) is None
    with pytest.raises(ValueError):
        period_start("year", NOW, TZ)
    assert PERIODS == ("today", "d7", "d30", "all")


@pytest.mark.parametrize("total, pages", [(0, 1), (1, 1), (10, 1), (11, 2), (25, 3)])
def test_total_pages(total, pages):
    assert total_pages(total, 10) == pages


def test_clamp_page():
    assert clamp_page(-1, 25, 10) == 0
    assert clamp_page(1, 25, 10) == 1
    assert clamp_page(9, 25, 10) == 2


def test_excel_workbook():
    t = Translator().bind("uz")
    rows = [
        CustomerRow(
            id=1,
            first_name="Malika",
            last_name="Karimova",
            phone="+998901234567",
            birth_date=date(2004, 5, 14),
            language="uz",
            balance=12_500,
            purchases_count=3,
            purchases_sum=780_000,
            last_purchase_at=NOW,
            registered_at=NOW - timedelta(days=30),
            is_blocked=False,
        ),
        CustomerRow(
            id=2,
            first_name="Анна",
            last_name="Ли",
            phone="+998911112233",
            birth_date=date(2001, 1, 2),
            language="ru",
            balance=0,
            purchases_count=0,
            purchases_sum=0,
            last_purchase_at=None,
            registered_at=NOW,
            is_blocked=True,
        ),
    ]
    content = build_users_workbook(rows, t, TZ)
    ws = load_workbook(BytesIO(content)).active
    assert ws.title == "Mijozlar"
    assert [c.value for c in ws[1]] == [t(k) for k in HEADER_KEYS]
    assert ws.max_row == 3
    first = [c.value for c in ws[2]]
    assert first[:4] == [1, "Malika", "Karimova", "+998901234567"]
    assert first[6] == 12_500 and first[8] == 780_000
    assert first[9] == datetime(2026, 12, 1, 14, 30)  # Toshkent vaqtida
    second = [c.value for c in ws[3]]
    assert second[9] is None
    assert second[11] == "Ha"
