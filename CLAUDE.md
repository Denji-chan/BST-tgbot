# BEST SHOP TREND bot — loyiha konteksti

Nukusdagi BEST SHOP TREND qizlar kiyim do'koni uchun Telegram bot: mijozlar bazasini yig'ish, cashback va qayta jalb qilish uchun xabar yuborish.

## Stack
- Python 3.10+, aiogram 3.x (polling), SQLite (`sqlite3`, sinxron), openpyxl, python-dotenv
- FSM: MemoryStorage. Ro'yxatdan o'tish bosqichi bazadan aniqlanadi (`helpers.resume_registration`), shuning uchun restartdan keyin ham davom etadi.

## Tuzilma
- `handlers/common.py` → `/start`, `/cancel`, «Bekor qilish» (birinchi router — har qanday holatdan ustun)
- `handlers/admin.py` → `IsAdmin` filtri router darajasida; adminlar boshqaruvi faqat `IsDeveloper`
- `handlers/user.py` → ro'yxatdan o'tish, profil, sozlamalar, fallback
- Router tartibi: common → admin → user (`bot.py`)

## Qoidalar
- Barcha foydalanuvchiga ko'rinadigan matnlar `texts.py` da, 3 tilda (`uz`, `ru`, `kaa`). Yangi kalit qo'shilsa — uchala tilda, bir xil `{placeholder}` lar bilan.
- Tugma matnlarini filtrlashda `F.text.in_(variants("btn_..."))` ishlatiladi.
- `parse_mode=HTML` — foydalanuvchi kiritgan matnni (ism va h.k.) `html.escape` qiling.
- Pul so'mda, butun son (`INTEGER`). Formatlash: `texts.money()`.
- Vaqt: UTC+5 (`config.TZ`), bazada `YYYY-MM-DD HH:MM:SS` satr.
- DEVELOPER ID `.env` dagi `DEVELOPER_ID` (standart 8897276236); faqat u admin qo'sha/olib tashlay oladi.
- `.env` va `*.db` ni gitga qo'shmang.

## Ishga tushirish
`pip install -r requirements.txt` → `.env` ga `BOT_TOKEN` → `python bot.py`
