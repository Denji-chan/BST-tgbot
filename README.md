# BEST SHOP TREND — Telegram bot (mijozlar bazasi + cashback)

Python (aiogram 3) da yozilgan bot. Mijozlarni ro'yxatga oladi, ularga cashback yig'adi va do'konga qayta jalb qilish uchun xabar yuborishga yordam beradi.

## Imkoniyatlar

**Mijoz tomoni**
- `/start` → til tanlash (O'zbekcha / Русский / Qaraqalpaqsha)
- "Biz haqimizda qayerdan eshitdingiz?" (Instagram, Telegram, do'stlardan, do'kon yonidan, reklama, boshqa)
- Telegramga ulangan telefon raqam (faqat tugma orqali, faqat o'z raqami)
- Ism Familiya → bazaga saqlanadi, mijozga **mijoz raqami (ID)** beriladi
- 👤 **Profil** — ID, ism, telefon, **cashback balansi**, cashback tarixi
- ⚙️ **Sozlamalar** — tilni va ism-familiyani o'zgartirish
- Cashback qo'shilganda yoki ishlatilganda mijozga avtomatik xabar boradi

**Admin tomoni**
- 📢 **Xabar yuborish** — rasm + pastida matn (yoki faqat matn / video), oldin ko'rib chiqib, keyin tasdiqlab yuboriladi
- 📊 **Statistika** — jami mijozlar, bugun / 7 kun / 30 kun, til va "qayerdan eshitgan" bo'yicha, cashback summalari
- 📥 **Excel yuklab olish** — 3 varaqli fayl: Mijozlar, Statistika, Cashback amallari
- ➕ **Cashback qo'shish** — mijoz ID yoki telefon → xarid summasi → bot foizni (boshida 3%) hisoblaydi → tasdiqlash
- ➖ **Cashback ishlatish** — mijoz balansidan ayirish (balansdan ortiq bo'lmaydi)
- 🔎 **Mijozni topish** — ID yoki telefon bo'yicha, tarixi bilan
- 💯 **Cashback foizi** — 0–50% oralig'ida o'zgartirish
- ⚙️ **Sozlamalar** — admin ham tilni o'zgartira oladi
- 👥 **Adminlar** — faqat DEVELOPER (`8897276236`) ko'radi: admin qo'shish / olib tashlash

## O'rnatish (Windows)

1. **Python 3.10+** o'rnating: https://www.python.org/downloads/ — o'rnatishda **"Add Python to PATH"** ga belgi qo'ying.
2. **Bot token oling:** Telegramda @BotFather → `/newbot` → nom va username bering → tokenni nusxalang.
3. Shu papkadagi `.env.example` faylini nusxalab, nomini **`.env`** qiling va `BOT_TOKEN=` dan keyin tokenni yozing.
4. **`run_bot.bat`** faylini ikki marta bosing — kutubxonalarni o'rnatadi va botni ishga tushiradi.

Yoki terminalda qo'lda:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python bot.py
```

5. Telegramda botingizga kiring va `/start` bosing. `8897276236` ID li akkaunt avtomatik **developer** bo'ladi va admin panelni ko'radi.

> ⚠️ Bot faqat kompyuter yoqiq va `bot.py` ishlab turganda javob beradi. Doimiy (24/7) ishlashi uchun keyin VPS serverga joylash kerak.

## Cashback qanday ishlaydi

1. Mijoz kassada mijoz raqamini (ID) yoki telefonini aytadi.
2. Admin: **➕ Cashback qo'shish** → ID/telefon → xarid summasi (masalan `250000`).
3. Bot hisoblaydi: 250 000 × 3% = **7 500 so'm**, admin tasdiqlaydi → mijozga xabar boradi.
4. Mijoz cashbackni ishlatmoqchi bo'lsa: **➖ Cashback ishlatish** → summa → tasdiqlash.

## Fayllar

| Fayl | Vazifasi |
|---|---|
| `bot.py` | Botni ishga tushiradi |
| `config.py` | Sozlamalar (`.env` dan o'qiydi) |
| `database.py` | SQLite baza: mijozlar, adminlar, cashback amallari |
| `texts.py` | Barcha matnlar 3 tilda |
| `keyboards.py` | Tugmalar |
| `states.py` | Bosqichlar (FSM) |
| `helpers.py` | Yordamchi funksiyalar |
| `excel_export.py` | Excel fayl yaratish |
| `handlers/common.py` | `/start`, bekor qilish |
| `handlers/user.py` | Mijoz tomoni |
| `handlers/admin.py` | Admin panel |

Baza `best_shop.db` faylida saqlanadi — bu faylni o'chirmang va vaqti-vaqti bilan nusxasini oling.

## Claude Code + ECC

Loyihani Claude Code'da davom ettirish uchun [ECC](https://github.com/affaan-m/ECC) ni o'rnating (Node.js 18+ kerak). Bitta usulni tanlang:

```bash
# 1-usul: terminalda
npx ecc-universal@2.2.3 setup

# 2-usul: Claude Code ichida
/plugin marketplace add https://github.com/affaan-m/ECC
/plugin install ecc@ecc
```

Keyin shu papkani Claude Code'da oching (`cd best_shop_bot` → `claude`). Python kodini tekshirish uchun `/python-review` buyrug'idan foydalanish mumkin. Loyiha haqidagi ma'lumot `CLAUDE.md` faylida.
