# BEST SHOP TREND bot

Nukusdagi BEST SHOP TREND qizlar kiyim do'koni uchun Telegram bot: mijozlar bazasi va cashback tizimi.

**Mijozlar uchun:** ro'yxatdan o'tish (til, ism, familiya, kontakt, tug'ilgan kun), har xariddan 3% cashback, 90 kunlik muddat, referal havola (30 000 so'm bonus), tug'ilgan kunda 10% chegirma, profil, support, tilni almashtirish (o'zbek, rus, ingliz).

**Adminlar uchun:** xarid kiritish, statistika, mijozlar ro'yxati va Excel, avtomatik matnlarni tahrirlash, rassilka. Developer adminlarni qo'shadi va o'chiradi.

Arxitektura "mukammal bot" shabloni asosida qurilgan va aiogram 3 ga o'tkazilgan.

---

## 1. Bot tokenini olish (BotFather)

1. Telegram'da [@BotFather](https://t.me/BotFather) ni oching va `/newbot` yozing.
2. Botga nom bering (masalan, `BEST SHOP TREND`), keyin `bot` bilan tugaydigan username (masalan, `bestshop_trend_bot`).
3. BotFather bergan tokenni nusxalang. U `123456789:AA...` ko'rinishida bo'ladi. **Tokenni hech kimga bermang.**
4. O'zingizning Telegram ID raqamingizni bilish uchun [@userinfobot](https://t.me/userinfobot) ga yozing. Bu raqam `DEVELOPER_ID` bo'ladi.

## 2. `.env` faylini to'ldirish

```bash
cp .env.dist .env        # Windows: copy .env.dist .env
```

`.env` ichida:

| O'zgaruvchi | Majburiy | Izoh |
| --- | --- | --- |
| `BOT_TOKEN` | ha | BotFather bergan token |
| `DEVELOPER_ID` | ha | Bosh admin (Developer) Telegram ID'si |
| `DATABASE_URL` | ha | Docker'siz ishga tushirish uchun: `postgresql+asyncpg://user:parol@localhost:5432/bestshop` |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Docker uchun | PostgreSQL konteyneri foydalanuvchisi, paroli va bazasi |
| `TIMEZONE` | yo'q | Standart: `Asia/Tashkent` |
| `CASHBACK_MAX_USE_PERCENT` | yo'q | Xarid summasining necha foizini cashback bilan to'lash mumkin. Standart: `50` |
| `LOG_LEVEL` | yo'q | Standart: `INFO` |
| `LOG_DIR` | yo'q | Standart: `logs` |

`POSTGRES_PASSWORD` ga murakkab parol yozing. `.env` faylini git'ga qo'shmang, u `.gitignore` da turibdi.

## 3. Docker bilan ishga tushirish (tavsiya etiladi)

Serverda Docker va Docker Compose o'rnatilgan bo'lishi kerak.

```bash
docker compose up -d --build
```

Bu buyruq ikkita konteynerni ishga tushiradi: `db` (PostgreSQL 16) va `bot`. Bot har ishga tushganda avval migratsiyalarni o'zi bajaradi (`alembic upgrade head`), keyin polling'ni boshlaydi.

Foydali buyruqlar:

```bash
docker compose logs -f bot         # loglarni ko'rish
docker compose restart bot         # botni qayta ishga tushirish
docker compose pull && docker compose up -d --build   # yangilash
docker compose down                # to'xtatish (ma'lumotlar saqlanib qoladi)
```

Baza ma'lumotlari `pgdata` volume'ida saqlanadi, loglar esa `./logs` papkasida. Baza porti tashqariga ochilmaydi.

## 4. Migratsiya

Docker'da migratsiya avtomatik bajariladi. Qo'lda bajarish uchun:

```bash
# Docker ichida
docker compose run --rm bot alembic upgrade head

# Docker'siz
alembic upgrade head
```

Migratsiya `.env` dagi `DATABASE_URL` dan foydalanadi.

## 5. Docker'siz ishga tushirish

Python 3.12 va PostgreSQL kerak.

```bash
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL'da baza va foydalanuvchi yarating, .env dagi DATABASE_URL ni moslang
alembic upgrade head
python app.py
```

## 6. Birinchi admin

- **Developer** `.env` dagi `DEVELOPER_ID` bo'yicha avtomatik tanilib qoladi. Botga `/start` yozing: ro'yxatdan o'tish o'rniga admin paneli ochiladi. Bot ishga tushganda Developer'ga "Bot ishga tushdi" xabari ham keladi.
- **Boshqa adminlar:** admin panelida **🛡 Adminlar → ➕ Admin qo'shish** ni bosing va yangi adminning Telegram ID raqamini yozing (yoki uning xabarini forward qiling). Yangi admin botga `/start` yoki `/admin` yozsa, panel ochiladi.
- Adminni o'chirish ham shu bo'limda. Developer'ni o'chirib bo'lmaydi.

## 7. Testlar va tekshiruv

```bash
pip install -r requirements-dev.txt
pytest                 # barcha testlar (baza testlari SQLite xotirada ishlaydi)
ruff check .           # kod sifati
flake8 .
```

Kerakli paketlar o'rnatilmagan bo'lsa, baza va aiogram'ga bog'liq testlar avtomatik o'tkazib yuboriladi (`skipped`). To'liq tekshiruv uchun `requirements-dev.txt` ni o'rnating.

## 8. Avtomatik vazifalar (Asia/Tashkent)

| Vaqt | Vazifa |
| --- | --- |
| Har kuni 00:05 | Muddati o'tgan cashback kuyadi |
| Har kuni 10:00 | Tug'ilgan kuni bo'lgan mijozlarga tabrik va chegirma haqida xabar |
| Har kuni 20:00 | 60, 90 va 120 kun kelmagan mijozlarga xabar (har bir bosqich bir marta) |
| Har oy 25-sana 10:00 | Barcha adminlarga oylik to'lov eslatmasi |

## 9. Xarid kiritish formati

Admin mahsulotlarni har birini yangi qatordan yozadi:

```
Ko'ylak - 150000
Shim - 2 x 120 000
```

Ajratuvchi sifatida `-`, `;` yoki `:` ishlatilishi mumkin. Narxda bo'sh joy bo'lishi mumkin.

## 10. Tuzilma

```
app.py                  # ishga tushirish: asyncio.run(main())
loader.py               # Bot, Dispatcher, baza ulanishi
data/                   # config.py (.env), settings.py (tekshiruv)
handlers/
  users/                # start, profile, referral, support, settings, chat_member, help, fallback
  admins/               # menu, purchase, stats, users_list, texts, broadcast, admins, support_reply
  errors/  groups/  channels/
keyboards/default/      # reply tugmalar
keyboards/inline/       # inline tugmalar va callback ma'lumotlari
states/                 # FSM: registration, purchase, broadcast, edit_text, support, admins
filters/                # IsAdmin, IsDeveloper, IsRegistered
middlewares/            # throttling, i18n (til), database (sessiya)
services/               # biznes mantiq: cashback, referal, tug'ilgan kun, xarid, statistika, rassilka...
utils/
  db_api/               # SQLAlchemy modellari va repository'lar
  misc/                 # i18n, logging, throttling, formatlash
  scheduler.py          # APScheduler vazifalari
locales/                # uz.json, ru.json, en.json
migrations/             # Alembic
tests/                  # pytest (tests/db - baza testlari)
```

Qabul qilingan qarorlar: [DECISIONS.md](DECISIONS.md). Keyingi g'oyalar: [IDEAS.md](IDEAS.md).
