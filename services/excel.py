"""Mijozlar ro'yxatini Excel (.xlsx) fayliga yozish. Bazaga va aiogram'ga bog'liq emas."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime
from io import BytesIO
from zoneinfo import ZoneInfo

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

HEADER_KEYS: tuple[str, ...] = (
    "excel.id",
    "excel.first_name",
    "excel.last_name",
    "excel.phone",
    "excel.birth_date",
    "excel.language",
    "excel.balance",
    "excel.purchases_count",
    "excel.purchases_sum",
    "excel.last_purchase",
    "excel.registered",
    "excel.blocked",
)


@dataclass(frozen=True)
class CustomerRow:
    id: int
    first_name: str
    last_name: str
    phone: str
    birth_date: date
    language: str
    balance: int
    purchases_count: int
    purchases_sum: int
    last_purchase_at: datetime | None
    registered_at: datetime
    is_blocked: bool


def build_users_workbook(rows: list[CustomerRow], t: Callable[..., str], tz: ZoneInfo) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = t("excel.sheet_title")[:31]
    ws.append([t(key) for key in HEADER_KEYS])
    for cell in ws[1]:
        cell.font = Font(bold=True)

    yes, no = t("excel.yes"), t("excel.no")
    for r in rows:
        ws.append(
            [
                r.id,
                r.first_name,
                r.last_name,
                r.phone,
                r.birth_date,
                r.language,
                r.balance,
                r.purchases_count,
                r.purchases_sum,
                r.last_purchase_at.astimezone(tz).replace(tzinfo=None) if r.last_purchase_at else None,
                r.registered_at.astimezone(tz).replace(tzinfo=None),
                yes if r.is_blocked else no,
            ]
        )

    for row in ws.iter_rows(min_row=2):
        row[4].number_format = "DD.MM.YYYY"
        for idx in (6, 8):
            row[idx].number_format = "#,##0"
        for idx in (9, 10):
            row[idx].number_format = "DD.MM.YYYY HH:MM"
    widths = (8, 16, 18, 16, 12, 6, 12, 10, 14, 18, 18, 10)
    for i, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width
    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
