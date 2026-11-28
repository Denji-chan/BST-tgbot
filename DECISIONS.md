# DECISIONS

Topshiriqda aniq yozilmagan yoki ikki xil tushunish mumkin bo'lgan joylarda qabul qilingan qarorlar.

## Umumiy

1. **Asosiy manba.** Oxirgi topshiriq ("TAYYOR QARORLAR" bilan) avvalgi arxitektura hujjatidagi qarorlar o'rnini egalladi. Shuning uchun:
   - xarid Billz'dan avtomatik olinmaydi, uni admin kiritadi;
   - tillar 3 ta (uz, ru, en), qoraqalpoq tili yo'q;
   - cashback summaning 50% igacha ishlatiladi;
   - summalar pastga yaxlitlanadi.
   Billz, qoraqalpoq tili, baho, audit log va boshqa avvalgi g'oyalar "qo'shimcha funksiya qo'shma" qoidasi sababli IDEAS.md ga ko'chirildi.
2. **Git ishlatilmadi.** Siz "git ishlatma" degansiz, muhit ham git'ga ruxsat bermadi. Har bir task o'rniga PROGRESS.md da belgilandi.
3. **Shablon zip'i kelmadi.** Papkalar tuzilmasi va nomlash topshiriqdagi tavsif bo'yicha qurildi: `app.py`, `loader.py`, `data/config.py`, `handlers/{users,admins,errors,groups,channels}`, `keyboards/{default,inline}`, `states`, `filters`, `middlewares`, `utils/{db_api,misc}`, `notify_admins.py`, `set_bot_commands.py`.
4. **i18n.** Matnlar `locales/{uz,ru,en}.json` da, o'zgaruvchilar `{nom}` ko'rinishida. Fluent/gettext o'rniga oddiy o'z implementatsiyasi tanlandi: tashqi bog'liqlik yo'q va testlar har bir kalit uchala tilda borligini hamda o'zgaruvchilar bir xilligini tekshiradi.
5. **FSM xotirasi.** Shablondagidek `MemoryStorage`. Bot qayta ishga tushsa, yarim qolgan jarayonlar (ro'yxatdan o'tish, xarid kiritish) qaytadan boshlanadi.
6. **Vaqt.** Bazada hamma vaqt UTC'da saqlanadi (maxsus `UTCDateTime` turi). Hisob-kitob va ko'rsatish Asia/Tashkent bo'yicha.

## Mijoz va ro'yxatdan o'tish

7. **Mijoz ID raqami.** Mijoz ID raqami `users.id` (1, 2, 3...). U profilda va ro'yxatdan o'tgach ko'rsatiladi.
8. **Eski mijoz.** Telefon raqami bazada bor bo'lsa (boshqa Telegram akkaunt), ro'yxatdan o'tish rad etiladi va mijozga administratorga murojaat qilish aytiladi. Shu bilan eski mijoz "yangi do'st" bo'lib qayta taklif qilinolmaydi.
9. **Kontakt.** Faqat "Kontaktni yuborish" tugmasi qabul qilinadi va kontakt aynan yozayotgan odamniki ekani tekshiriladi.
10. **Ism va familiya.** 2–40 ta harf. Apostrof, defis va bo'sh joyga ruxsat bor.
11. **Tug'ilgan kun.** `KK.OO.YYYY` formatida (`/` va `-` ham qabul qilinadi), yosh 7 dan 100 gacha.
12. **Adminlar.** Admin `/start` yozganda ro'yxatdan o'tmaydi, darhol admin paneli ochiladi. Developer ham `admins` jadvalida saqlanadi (tilini eslab qolish uchun), lekin uning huquqi faqat `.env` dagi `DEVELOPER_ID` dan keladi va uni o'chirib bo'lmaydi.

## Cashback

13. **Hisob tartibi.** Mahsulotlar yig'indisi → tug'ilgan kun chegirmasi (10%, pastga yaxlitlanadi) → **xarid summasi** → ishlatilgan cashback → **to'langan pul** → 3% cashback (pastga yaxlitlanadi).
14. **Cashback ishlatish.** Admin "ishlatish" yoki "ishlatmaslik"ni tanlaydi. "Ishlatish" bosilsa, ruxsat etilgan eng katta summa yechiladi: `min(balans, xarid summasi × 50%)`. Aniq summa kiritish yo'q, chunki topshiriqda faqat ikki variant aytilgan.
15. **90 kun.** Cashback olingan kun 1-kun hisoblanadi. Cashback 91-kuni soat 00:00 da (Toshkent) yaroqsiz bo'ladi, 00:05 dagi vazifa uni ledger'da `expire` deb yozadi. Profil va balansda faqat muddati o'tmagan cashback ko'rsatiladi. Profildagi "kuyish sanasi" — kuyadigan kunning o'zi.
16. **Ledger.** `cashback_transactions`: musbat yozuvlar (earn, referral) partiya bo'ladi, ularda `remaining` va `expires_at` bor. Manfiy yozuvlar (spend, expire) partiyalardan FIFO bo'yicha yechiladi. Qaysi partiyadan qancha olinganini alohida saqlaydigan jadval yo'q: `remaining` maydoni yetarli.
17. **Bitta tranzaksiya.** Xarid, mahsulotlar, cashback yechish, yangi cashback, tug'ilgan kun belgisi va referal bonusi bitta tranzaksiyada saqlanadi. Xato bo'lsa, hammasi bekor qilinadi. Mijoz qatori `FOR UPDATE` bilan bloklanadi.

## Referal

18. **Havola.** `https://t.me/<bot>?start=ref<ID>`. Havola faqat yangi ro'yxatdan o'tayotgan odam uchun hisobga olinadi.
19. **Chegara.** Bonus do'stning birinchi xaridining **xarid summasi** (tug'ilgan kun chegirmasidan keyin, cashbackdan oldin) **300 000 so'm va undan ko'p** bo'lsa beriladi. Topshiriqda "ko'p" deyilgan, siz esa avvalroq "300 ming va undan ko'pi" deb javob bergansiz. Shu javob olindi.
20. **Faqat birinchi xarid.** Birinchi xarid chegaradan kam bo'lsa, referal yopiladi (`rejected`) va keyingi xaridlar hisobga olinmaydi.
21. **Bonus.** Bonus do'stning xaridi saqlangan zahoti taklif qilgan mijozga qo'shiladi va unga xabar boradi. Bonus ham 90 kun amal qiladi.

## Tug'ilgan kun

22. **Chegirma muddati.** Chegirma tug'ilgan kuni va keyingi 3 kun (jami 4 kun) amal qiladi, har bir tug'ilgan kun uchun bir marta (birinchi xaridga).
23. **Maxsus holatlar.** 29-fevralda tug'ilganlar uchun kabisa bo'lmagan yilda 28-fevral olinadi. Oyna yangi yilga o'tsa (masalan, 30-dekabr), u o'tgan yil hisobiga yoziladi.
24. **Tabrik.** Tabrik tug'ilgan kuni soat 10:00 da yuboriladi va qaysi sanagacha chegirma amal qilishi aytiladi.

## Avtomatik xabarlar

25. **60/90/120 kunlik xabarlar.**
    - Vaqti: har kuni 20:00. Topshiriqda vaqt yo'q edi, siz avvalroq 20:00 ni tanlagansiz.
    - Kun oxirgi xariddan hisoblanadi. Hech xarid qilmaganlarga yuborilmaydi.
    - Bot bir necha kun ishlamay qolsa, faqat yetib kelingan eng oxirgi bosqich yuboriladi.
    - Har bir bosqich bitta "kelmay qolish davri"da bir marta ketadi. Yangi xarid bo'lsa, hisob qaytadan boshlanadi.
26. **25-sana eslatmasi.** Soat 10:00 da barcha adminlarga (Developer bilan birga) yuboriladi, oyiga bir marta.
27. **Tahrirlanadigan matnlar.** "Matnlar" bo'limida 4 ta matn bor: 60, 90, 120 kun va 25-sana eslatmasi. Har biri 3 tilda. O'zgaruvchilar: `{name}` va `{balance}` (eslatmada faqat `{name}`). Noma'lum o'zgaruvchili matn saqlanmaydi. Bu matnlar oddiy matn sifatida yuboriladi (HTML'siz), shuning uchun admin yozgan belgilar xabarni buzmaydi.
28. **Takrorlanmaslik.** Har bir avtomatik xabar `notification_logs` jadvaliga yoziladi, shuning uchun bot qayta ishga tushsa ham xabar ikki marta ketmaydi.

## Admin bo'limlari

29. **Mijozni topish.** 7 xonagacha bo'lgan son ID raqam deb, undan uzunrog'i telefon deb olinadi. 9 xonali raqam oldiga 998 qo'shiladi.
30. **Mahsulotlar formati.** `Nomi - narx` yoki `Nomi - soni x narx`, bitta xaridda eng ko'pi bilan 50 qator. Bitta qator noto'g'ri bo'lsa, ro'yxat to'liq qayta so'raladi.
31. **Statistika.**
    - "Xaridlar summasi" chegirmadan keyingi xarid summalari yig'indisi.
    - "Yangi mijozlar" ro'yxatdan o'tgan sana bo'yicha.
    - "Bugun" mahalliy yarim tundan boshlanadi, 7 va 30 kun hozirgi vaqtdan orqaga sanaladi.
32. **Mijozlar ro'yxati.** Sahifada 10 ta, yangilari birinchi. Excel'ga barcha mijozlar chiqariladi.
33. **Support.** Faqat matnli murojaat qabul qilinadi. U barcha adminlarning shaxsiy chatiga "Javob berish" tugmasi bilan boradi. Bir nechta admin javob berishi mumkin, bunda ikkinchi adminga ogohlantirish chiqadi.
34. **Rassilka.**
    - Xabar `copy_message` bilan yuboriladi, shuning uchun formatlash, rasm va video saqlanadi.
    - Tezlik 25 xabar/soniya. RetryAfter kelsa, ko'rsatilgan vaqt kutiladi va 3 martagacha qayta uriniladi.
    - Rassilka orqa fonda ishlaydi, tugagach adminga hisobot keladi.
35. **Bloklangan mijozlar.** Ular ikki yo'l bilan aniqlanadi: Telegram'ning `my_chat_member` xabari va yuborishdagi `Forbidden` xatosi. Bunday mijozlar rassilka va avtomatik xabarlarga kirmaydi. Mijoz botni qayta ochsa, belgi olib tashlanadi.
36. **Jarayon ichida menyu tugmasi.** Admin biror jarayon ichida menyu tugmasini bossa, jarayon bekor bo'ladi va o'sha bo'lim ochiladi. `/start` va "Bekor qilish" ham istalgan jarayondan chiqaradi.

## Texnik

37. **Docker.** Migratsiya konteyner ishga tushganda avtomatik bajariladi. Baza porti tashqariga ochilmaydi. Konteyner ichidagi `DATABASE_URL` `POSTGRES_*` o'zgaruvchilaridan yig'iladi.
38. **Testlar.** Testlar SQLite (aiosqlite, `StaticPool`) bilan ishlaydi. Paketlar o'rnatilmagan bo'lsa, bazaga va aiogram'ga bog'liq testlar o'tkazib yuboriladi. Biznes qoidalari aiogram'siz alohida modullarda yozilgan, shuning uchun ular har qanday muhitda tekshiriladi.
