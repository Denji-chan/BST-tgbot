"""Mijozlar bazasi va statistikani Excel (.xlsx) faylga chiqarish."""
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from config import TZ
from database import Database
from texts import LANG_NAMES, t

L = {
    "uz": {
        "sheets": ("Mijozlar", "Statistika", "Cashback amallari"),
        "customers": ["№", "Mijoz ID", "Ism Familiya", "Telefon", "Telegram ID", "Username", "Til",
                      "Qayerdan eshitgan", "Cashback balansi (so'm)", "Ro'yxatdan o'tgan sana", "Holat"],
        "status": ("Faol", "Botni bloklagan"),
        "tx": ["№", "Sana", "Mijoz ID", "Ism Familiya", "Telefon", "Turi", "Xarid summasi (so'm)",
               "Cashback (so'm)", "Foiz", "Admin ID"],
        "kinds": {"add": "Qo'shildi", "spend": "Ishlatildi"},
        "stats": {
            "total": "Jami mijozlar", "today": "Bugun ro'yxatdan o'tganlar",
            "week": "Oxirgi 7 kun", "month": "Oxirgi 30 kun", "blocked": "Botni bloklaganlar",
            "cb_balance": "Mijozlardagi jami cashback (so'm)", "cb_given": "Jami berilgan cashback (so'm)",
            "cb_spent": "Jami ishlatilgan cashback (so'm)", "percent": "Cashback foizi (%)",
            "lang": "Til bo'yicha", "source": "Qayerdan eshitgan", "generated": "Fayl yaratilgan vaqt",
        },
    },
    "ru": {
        "sheets": ("Клиенты", "Статистика", "Операции кэшбэка"),
        "customers": ["№", "ID клиента", "Имя Фамилия", "Телефон", "Telegram ID", "Username", "Язык",
                      "Откуда узнал(а)", "Баланс кэшбэка (сум)", "Дата регистрации", "Статус"],
        "status": ("Активен", "Заблокировал бота"),
        "tx": ["№", "Дата", "ID клиента", "Имя Фамилия", "Телефон", "Тип", "Сумма покупки (сум)",
               "Кэшбэк (сум)", "Процент", "ID админа"],
        "kinds": {"add": "Начислено", "spend": "Списано"},
        "stats": {
            "total": "Всего клиентов", "today": "Зарегистрировались сегодня",
            "week": "За 7 дней", "month": "За 30 дней", "blocked": "Заблокировали бота",
            "cb_balance": "Кэшбэк на балансах (сум)", "cb_given": "Всего начислено (сум)",
            "cb_spent": "Всего списано (сум)", "percent": "Процент кэшбэка (%)",
            "lang": "По языкам", "source": "Откуда узнали", "generated": "Файл создан",
        },
    },
    "kaa": {
        "sheets": ("Klientler", "Statistika", "Keshbek ámelleri"),
        "customers": ["№", "Klient ID", "Atı Familiyası", "Telefon", "Telegram ID", "Username", "Til",
                      "Qay jerden esitken", "Keshbek balansı (sum)", "Dizimnen ótken sánesi", "Jaǵdayı"],
        "status": ("Aktiv", "Bottı bloklaǵan"),
        "tx": ["№", "Sáne", "Klient ID", "Atı Familiyası", "Telefon", "Túri", "Satıp alıw summası (sum)",
               "Keshbek (sum)", "Procent", "Admin ID"],
        "kinds": {"add": "Qosıldı", "spend": "Paydalanıldı"},
        "stats": {
            "total": "Barlıq klientler", "today": "Búgin dizimnen ótkenler",
            "week": "Sońǵı 7 kún", "month": "Sońǵı 30 kún", "blocked": "Bottı bloklaǵanlar",
            "cb_balance": "Klientlerdegi keshbek (sum)", "cb_given": "Barlıǵı berilgen (sum)",
            "cb_spent": "Barlıǵı paydalanılǵan (sum)", "percent": "Keshbek procenti (%)",
            "lang": "Tiller boyınsha", "source": "Qay jerden esitken", "generated": "Fayl jaratılǵan waqıt",
        },
    },
}

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill("solid", fgColor="111111")
TITLE_FONT = Font(bold=True)


def _strip_emoji(text: str) -> str:
    """'📸 Instagram' -> 'Instagram' (Excelda toza ko'rinishi uchun)."""
    parts = text.split(" ", 1)
    return parts[1] if len(parts) == 2 and not parts[0].isalnum() else text


def _style_header(ws, ncols: int) -> None:
    for col in range(1, ncols + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 30


def _autowidth(ws) -> None:
    for col_cells in ws.columns:
        length = max((len(str(c.value)) if c.value is not None else 0) for c in col_cells)
        ws.column_dimensions[get_column_letter(col_cells[0].column)].width = min(max(10, length + 2), 45)


def build_customers_excel(db: Database, lang: str = "uz") -> tuple[bytes, str]:
    """Excel faylni bytes ko'rinishida va fayl nomini qaytaradi."""
    tr = L.get(lang, L["uz"])
    wb = Workbook()

    # 1) Mijozlar
    ws = wb.active
    ws.title = tr["sheets"][0]
    ws.append(tr["customers"])
    for i, u in enumerate(db.all_customers(), start=1):
        ws.append([
            i,
            u["id"],
            u["full_name"],
            u["phone"],
            u["tg_id"],
            f"@{u['username']}" if u["username"] else "",
            _strip_emoji(LANG_NAMES.get(u["lang"] or "uz", "")),
            _strip_emoji(t(f"src_{u['source'] or 'other'}", lang)),
            u["cashback"],
            u["registered_at"],
            tr["status"][1] if u["is_blocked"] else tr["status"][0],
        ])
    _style_header(ws, len(tr["customers"]))
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=5):
        for cell in row:  # telefon va Telegram ID matn bo'lib qolsin
            cell.number_format = "@"
    for row in ws.iter_rows(min_row=2, min_col=9, max_col=9):
        for cell in row:
            cell.number_format = "#,##0"
    if ws.max_row > 1:
        ws.auto_filter.ref = ws.dimensions
    _autowidth(ws)

    # 2) Statistika
    s = db.stats()
    st = tr["stats"]
    ws2 = wb.create_sheet(tr["sheets"][1])
    for key in ("total", "today", "week", "month", "blocked", "cb_balance", "cb_given", "cb_spent", "percent"):
        ws2.append([st[key], s[key]])
    ws2.append([])
    ws2.append([st["lang"]])
    ws2.cell(row=ws2.max_row, column=1).font = TITLE_FONT
    for code, count in s["langs"]:
        ws2.append([_strip_emoji(LANG_NAMES.get(code, code)), count])
    ws2.append([])
    ws2.append([st["source"]])
    ws2.cell(row=ws2.max_row, column=1).font = TITLE_FONT
    for key, count in s["sources"]:
        ws2.append([_strip_emoji(t(f"src_{key}", lang)), count])
    ws2.append([])
    ws2.append([st["generated"], datetime.now(TZ).strftime("%Y-%m-%d %H:%M")])
    for row in ws2.iter_rows(min_row=1, max_row=9, max_col=1):
        row[0].font = TITLE_FONT
    ws2.column_dimensions["A"].width = 38
    ws2.column_dimensions["B"].width = 20

    # 3) Cashback amallari
    ws3 = wb.create_sheet(tr["sheets"][2])
    ws3.append(tr["tx"])
    for i, tx in enumerate(db.all_transactions(), start=1):
        ws3.append([
            i,
            tx["created_at"],
            tx["user_id"],
            tx["full_name"],
            tx["phone"],
            tr["kinds"][tx["kind"]],
            tx["purchase_amount"] or None,
            tx["amount"],
            f"{tx['percent']}%" if tx["percent"] is not None else "",
            tx["admin_id"],
        ])
    _style_header(ws3, len(tr["tx"]))
    for row in ws3.iter_rows(min_row=2, min_col=7, max_col=8):
        for cell in row:
            cell.number_format = "#,##0"
    if ws3.max_row > 1:
        ws3.auto_filter.ref = ws3.dimensions
    _autowidth(ws3)

    buf = BytesIO()
    wb.save(buf)
    filename = f"best_shop_mijozlar_{datetime.now(TZ).strftime('%Y-%m-%d_%H-%M')}.xlsx"
    return buf.getvalue(), filename
