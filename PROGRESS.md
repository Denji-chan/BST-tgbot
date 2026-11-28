# PROGRESS

Ish uzilib qolsa, birinchi belgilanmagan taskdan davom etiladi.
Git ishlatilmadi (DECISIONS.md, 2-band), har bir task shu yerda belgilandi.

- [x] 1. Shablonni aiogram 3 ga o'tkazish, requirements.txt, .env.dist
- [x] 2. Baza modellari va Alembic migratsiyasi
- [x] 3. i18n va middleware'lar
- [x] 4. Ro'yxatdan o'tish
- [x] 5. Asosiy menyu va Profil
- [x] 6. Cashback service va testlari
- [x] 7. Admin: xarid kiritish va mijozga xabar
- [x] 8. Referal tizimi va testlari
- [x] 9. Tug'ilgan kun chegirmasi va testlari
- [x] 10. Support
- [x] 11. Sozlamalar
- [x] 12. Admin: statistika, ro'yxat, Excel
- [x] 13. Admin: matnlarni tahrirlash
- [x] 14. Rassilka
- [x] 15. Scheduler vazifalari va testlari
- [x] 16. Developer: adminlarni boshqarish
- [x] 17. Docker, docker-compose
- [x] 18. Yakuniy tekshiruv

## Yakuniy tekshiruv natijasi (ishlab chiqish muhitida)

- `ruff check .` — xato yo'q
- `flake8 .` — xato yo'q
- `pytest` — 173 ta test o'tdi. 13 ta test fayli o'tkazib yuborildi: muhitda aiogram, SQLAlchemy va aiosqlite o'rnatib bo'lmadi (tarmoq o'chiq).
- `docker compose config` — konfiguratsiya to'g'ri

O'tkazib yuborilgan testlarni `pip install -r requirements-dev.txt && pytest` bilan ishga tushiring. Ular baza, migratsiya, xarid, referal, tug'ilgan kun, scheduler, barcha modullar importi va routerlar ulanishini tekshiradi.
