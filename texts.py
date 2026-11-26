"""Bot matnlari: o'zbek (uz), rus (ru), qoraqalpoq (kaa) tillarida."""

LANGS = ("uz", "ru", "kaa")

LANG_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "kaa": "🌐 Qaraqalpaqsha",
}

# "Biz haqimizda qayerdan eshitdingiz?" variantlari (bazaga kalit saqlanadi)
SOURCES = ("instagram", "telegram", "friends", "passing", "ads", "other")

TEXTS: dict[str, dict[str, str]] = {
    # ------------------------------------------------------------ ro'yxatdan o'tish
    "choose_lang": {
        "uz": "🌐 Tilni tanlang:\n🌐 Выберите язык:\n🌐 Tildi saylań:",
        "ru": "🌐 Tilni tanlang:\n🌐 Выберите язык:\n🌐 Tildi saylań:",
        "kaa": "🌐 Tilni tanlang:\n🌐 Выберите язык:\n🌐 Tildi saylań:",
    },
    "welcome": {
        "uz": "👋 Assalomu alaykum! <b>BEST SHOP TREND</b> botiga xush kelibsiz!\n\n"
              "Ro'yxatdan o'ting va har bir xariddan <b>cashback</b> to'plang 🎁",
        "ru": "👋 Здравствуйте! Добро пожаловать в бот <b>BEST SHOP TREND</b>!\n\n"
              "Зарегистрируйтесь и получайте <b>кэшбэк</b> с каждой покупки 🎁",
        "kaa": "👋 Assalawma áleykum! <b>BEST SHOP TREND</b> botına xosh keldińiz!\n\n"
               "Dizimnen ótiń hám hár bir satıp alıwdan <b>keshbek</b> jıynań 🎁",
    },
    "ask_source": {
        "uz": "❓ Biz haqimizda qayerdan eshitdingiz?",
        "ru": "❓ Откуда вы о нас узнали?",
        "kaa": "❓ Biz haqqımızda qay jerden esittińiz?",
    },
    "src_instagram": {"uz": "📸 Instagram", "ru": "📸 Instagram", "kaa": "📸 Instagram"},
    "src_telegram": {"uz": "✈️ Telegram", "ru": "✈️ Telegram", "kaa": "✈️ Telegram"},
    "src_friends": {"uz": "👭 Do'stlarimdan", "ru": "👭 От друзей", "kaa": "👭 Doslarımnan"},
    "src_passing": {
        "uz": "🏬 Do'kon yonidan o'tib",
        "ru": "🏬 Проходил(а) мимо",
        "kaa": "🏬 Dúkan janınan ótip",
    },
    "src_ads": {"uz": "📢 Reklamadan", "ru": "📢 Из рекламы", "kaa": "📢 Reklamadan"},
    "src_other": {"uz": "🔹 Boshqa", "ru": "🔹 Другое", "kaa": "🔹 Basqa"},
    "source_chosen": {
        "uz": "✅ Javobingiz: {source}",
        "ru": "✅ Ваш ответ: {source}",
        "kaa": "✅ Juwabıńız: {source}",
    },
    "ask_phone": {
        "uz": "📱 Telegramga ulangan telefon raqamingizni yuboring.\n\n"
              "Pastdagi <b>«📱 Raqamni yuborish»</b> tugmasini bosing 👇",
        "ru": "📱 Отправьте номер телефона, привязанный к Telegram.\n\n"
              "Нажмите кнопку <b>«📱 Отправить номер»</b> ниже 👇",
        "kaa": "📱 Telegramǵa baylanǵan telefon nomerińizdi jiberiń.\n\n"
               "Tómendegi <b>«📱 Nomerdi jiberiw»</b> túymesin basıń 👇",
    },
    "btn_send_phone": {"uz": "📱 Raqamni yuborish", "ru": "📱 Отправить номер", "kaa": "📱 Nomerdi jiberiw"},
    "phone_use_button": {
        "uz": "⚠️ Raqamni qo'lda yozmang — pastdagi <b>«📱 Raqamni yuborish»</b> tugmasini bosing 👇",
        "ru": "⚠️ Не вводите номер вручную — нажмите кнопку <b>«📱 Отправить номер»</b> ниже 👇",
        "kaa": "⚠️ Nomerdi qolda jazbań — tómendegi <b>«📱 Nomerdi jiberiw»</b> túymesin basıń 👇",
    },
    "phone_not_own": {
        "uz": "⚠️ Iltimos, faqat o'zingizning raqamingizni yuboring.",
        "ru": "⚠️ Пожалуйста, отправьте свой собственный номер.",
        "kaa": "⚠️ Ótinish, tek óz nomerińizdi jiberiń.",
    },
    "ask_name": {
        "uz": "✍️ Ism va familiyangizni kiriting:\n\n<i>Masalan: Aziza Karimova</i>",
        "ru": "✍️ Введите ваше имя и фамилию:\n\n<i>Например: Азиза Каримова</i>",
        "kaa": "✍️ Atıńız hám familiyańızdı jazıń:\n\n<i>Mısalı: Aziza Karimova</i>",
    },
    "name_invalid": {
        "uz": "⚠️ Ism va familiyangizni to'liq yozing (2 ta so'z, raqamsiz).\n<i>Masalan: Aziza Karimova</i>",
        "ru": "⚠️ Введите имя и фамилию полностью (2 слова, без цифр).\n<i>Например: Азиза Каримова</i>",
        "kaa": "⚠️ Atıńız hám familiyańızdı tolıq jazıń (2 sóz, sanlarsız).\n<i>Mısalı: Aziza Karimova</i>",
    },
    "reg_done": {
        "uz": "🎉 Tabriklaymiz, <b>{name}</b>! Siz ro'yxatdan o'tdingiz.\n\n"
              "🆔 Mijoz raqamingiz: <b>{card}</b>\n"
              "💰 Har bir xariddan <b>{percent}%</b> cashback\n\n"
              "Xarid qilganingizda kassada mijoz raqamingiz yoki telefon raqamingizni ayting — "
              "cashback balansingizga qo'shiladi ✅",
        "ru": "🎉 Поздравляем, <b>{name}</b>! Вы зарегистрированы.\n\n"
              "🆔 Ваш номер клиента: <b>{card}</b>\n"
              "💰 <b>{percent}%</b> кэшбэка с каждой покупки\n\n"
              "При покупке назовите на кассе номер клиента или телефон — "
              "кэшбэк зачислится на ваш баланс ✅",
        "kaa": "🎉 Qutlıqlaymız, <b>{name}</b>! Siz dizimnen óttińiz.\n\n"
               "🆔 Klient nomerińiz: <b>{card}</b>\n"
               "💰 Hár bir satıp alıwdan <b>{percent}%</b> keshbek\n\n"
               "Satıp alǵanıńızda kassada klient nomerińizdi yamasa telefon nomerińizdi aytıń — "
               "keshbek balansıńızǵa qosıladı ✅",
    },

    # ------------------------------------------------------------ umumiy
    "use_menu": {
        "uz": "👇 Quyidagi menyudan foydalaning.",
        "ru": "👇 Воспользуйтесь меню ниже.",
        "kaa": "👇 Tómendegi menyudan paydalanıń.",
    },
    "btn_cancel": {"uz": "❌ Bekor qilish", "ru": "❌ Отмена", "kaa": "❌ Biykar etiw"},
    "btn_confirm": {"uz": "✅ Tasdiqlash", "ru": "✅ Подтвердить", "kaa": "✅ Tastıyıqlaw"},
    "btn_back": {"uz": "⬅️ Orqaga", "ru": "⬅️ Назад", "kaa": "⬅️ Artqa"},
    "cancelled": {"uz": "❌ Bekor qilindi.", "ru": "❌ Отменено.", "kaa": "❌ Biykar etildi."},
    "currency": {"uz": "so'm", "ru": "сум", "kaa": "sum"},

    # ------------------------------------------------------------ mijoz menyusi
    "btn_profile": {"uz": "👤 Profil", "ru": "👤 Профиль", "kaa": "👤 Profil"},
    "btn_settings": {"uz": "⚙️ Sozlamalar", "ru": "⚙️ Настройки", "kaa": "⚙️ Sazlawlar"},
    "profile": {
        "uz": "👤 <b>Profilingiz</b>\n\n"
              "🆔 Mijoz raqami: <b>{card}</b>\n"
              "👤 Ism-familiya: {name}\n"
              "📱 Telefon: {phone}\n"
              "📅 Ro'yxatdan o'tgan: {date}\n\n"
              "💰 <b>Cashback balansi: {balance}</b>\n"
              "📈 Har bir xariddan: {percent}%\n\n"
              "<i>Kassada mijoz raqamingizni ayting va cashbackdan foydalaning.</i>",
        "ru": "👤 <b>Ваш профиль</b>\n\n"
              "🆔 Номер клиента: <b>{card}</b>\n"
              "👤 Имя и фамилия: {name}\n"
              "📱 Телефон: {phone}\n"
              "📅 Дата регистрации: {date}\n\n"
              "💰 <b>Баланс кэшбэка: {balance}</b>\n"
              "📈 С каждой покупки: {percent}%\n\n"
              "<i>Назовите на кассе номер клиента и используйте кэшбэк.</i>",
        "kaa": "👤 <b>Profilińiz</b>\n\n"
               "🆔 Klient nomeri: <b>{card}</b>\n"
               "👤 Atı-familiyası: {name}\n"
               "📱 Telefon: {phone}\n"
               "📅 Dizimnen ótken sánesi: {date}\n\n"
               "💰 <b>Keshbek balansı: {balance}</b>\n"
               "📈 Hár bir satıp alıwdan: {percent}%\n\n"
               "<i>Kassada klient nomerińizdi aytıń hám keshbekten paydalanıń.</i>",
    },
    "btn_history": {"uz": "📜 Cashback tarixi", "ru": "📜 История кэшбэка", "kaa": "📜 Keshbek tariyxı"},
    "history_title": {
        "uz": "📜 <b>Oxirgi cashback amallari:</b>",
        "ru": "📜 <b>Последние операции с кэшбэком:</b>",
        "kaa": "📜 <b>Sońǵı keshbek ámelleri:</b>",
    },
    "history_empty": {
        "uz": "📜 Hozircha cashback amallari yo'q.",
        "ru": "📜 Пока операций с кэшбэком нет.",
        "kaa": "📜 Házirshe keshbek ámelleri joq.",
    },
    "hist_add": {
        "uz": "➕ {amount} — xarid {purchase}",
        "ru": "➕ {amount} — покупка {purchase}",
        "kaa": "➕ {amount} — satıp alıw {purchase}",
    },
    "hist_spend": {
        "uz": "➖ {amount} — ishlatildi",
        "ru": "➖ {amount} — списано",
        "kaa": "➖ {amount} — paydalanıldı",
    },
    "cashback_added_notify": {
        "uz": "🎉 Sizga <b>{amount}</b> cashback qo'shildi!\n\n"
              "🛍 Xarid summasi: {purchase}\n"
              "💰 Joriy balans: <b>{balance}</b>\n\n"
              "Xaridingiz uchun rahmat! 💖 BEST SHOP TREND",
        "ru": "🎉 Вам начислено <b>{amount}</b> кэшбэка!\n\n"
              "🛍 Сумма покупки: {purchase}\n"
              "💰 Текущий баланс: <b>{balance}</b>\n\n"
              "Спасибо за покупку! 💖 BEST SHOP TREND",
        "kaa": "🎉 Sizge <b>{amount}</b> keshbek qosıldı!\n\n"
               "🛍 Satıp alıw summası: {purchase}\n"
               "💰 Házirgi balans: <b>{balance}</b>\n\n"
               "Satıp alǵanıńız ushın raxmet! 💖 BEST SHOP TREND",
    },
    "cashback_spent_notify": {
        "uz": "✅ Balansingizdan <b>{amount}</b> cashback ishlatildi.\n"
              "💰 Qolgan balans: <b>{balance}</b>\n\n"
              "Rahmat! 💖 BEST SHOP TREND",
        "ru": "✅ С вашего баланса списано <b>{amount}</b> кэшбэка.\n"
              "💰 Остаток: <b>{balance}</b>\n\n"
              "Спасибо! 💖 BEST SHOP TREND",
        "kaa": "✅ Balansıńızdan <b>{amount}</b> keshbek paydalanıldı.\n"
               "💰 Qalǵan balans: <b>{balance}</b>\n\n"
               "Raxmet! 💖 BEST SHOP TREND",
    },

    # ------------------------------------------------------------ sozlamalar
    "settings": {
        "uz": "⚙️ <b>Sozlamalar</b>\n\n🌐 Joriy til: {lang}\n\nNimani o'zgartirmoqchisiz?",
        "ru": "⚙️ <b>Настройки</b>\n\n🌐 Текущий язык: {lang}\n\nЧто хотите изменить?",
        "kaa": "⚙️ <b>Sazlawlar</b>\n\n🌐 Házirgi til: {lang}\n\nNeni ózgertpekshisiz?",
    },
    "btn_change_lang": {"uz": "🌐 Tilni o'zgartirish", "ru": "🌐 Изменить язык", "kaa": "🌐 Tildi ózgertiw"},
    "btn_change_name": {
        "uz": "✏️ Ism-familiyani o'zgartirish",
        "ru": "✏️ Изменить имя и фамилию",
        "kaa": "✏️ Atı-familiyanı ózgertiw",
    },
    "lang_changed": {"uz": "✅ Til o'zgartirildi.", "ru": "✅ Язык изменён.", "kaa": "✅ Til ózgertildi."},
    "name_changed": {
        "uz": "✅ Ism-familiya saqlandi.",
        "ru": "✅ Имя и фамилия сохранены.",
        "kaa": "✅ Atı-familiya saqlandı.",
    },

    # ------------------------------------------------------------ admin panel
    "admin_panel": {
        "uz": "🛠 <b>Admin panel</b>\n\nKerakli bo'limni tanlang 👇",
        "ru": "🛠 <b>Админ-панель</b>\n\nВыберите раздел 👇",
        "kaa": "🛠 <b>Admin panel</b>\n\nKerekli bólimdi saylań 👇",
    },
    "btn_broadcast": {"uz": "📢 Xabar yuborish", "ru": "📢 Рассылка", "kaa": "📢 Xabar jiberiw"},
    "btn_stats": {"uz": "📊 Statistika", "ru": "📊 Статистика", "kaa": "📊 Statistika"},
    "btn_excel": {"uz": "📥 Excel yuklab olish", "ru": "📥 Скачать Excel", "kaa": "📥 Excel júklep alıw"},
    "btn_cb_add": {"uz": "➕ Cashback qo'shish", "ru": "➕ Начислить кэшбэк", "kaa": "➕ Keshbek qosıw"},
    "btn_cb_spend": {"uz": "➖ Cashback ishlatish", "ru": "➖ Списать кэшбэк", "kaa": "➖ Keshbekti paydalanıw"},
    "btn_find": {"uz": "🔎 Mijozni topish", "ru": "🔎 Найти клиента", "kaa": "🔎 Klientti tabıw"},
    "btn_percent": {"uz": "💯 Cashback foizi", "ru": "💯 Процент кэшбэка", "kaa": "💯 Keshbek procenti"},
    "btn_admins": {"uz": "👥 Adminlar", "ru": "👥 Админы", "kaa": "👥 Adminler"},

    # xabar yuborish
    "bc_ask": {
        "uz": "📢 Mijozlarga yuboriladigan xabarni yuboring:\n\n"
              "🖼 <b>Rasm + pastida matn</b> — rasmni tanlab, izoh (caption) qismiga matnni yozing\n"
              "📝 Yoki faqat matn yuboring",
        "ru": "📢 Отправьте сообщение для рассылки клиентам:\n\n"
              "🖼 <b>Фото + текст под ним</b> — выберите фото и напишите текст в подписи\n"
              "📝 Или отправьте только текст",
        "kaa": "📢 Klientlerge jiberiletuǵın xabardı jiberiń:\n\n"
               "🖼 <b>Súwret + astında tekst</b> — súwretti saylap, túsindirme (caption) bólimine tekst jazıń\n"
               "📝 Yamasa tek tekst jiberiń",
    },
    "bc_unsupported": {
        "uz": "⚠️ Faqat rasm (izoh bilan), video yoki matn yuboring.",
        "ru": "⚠️ Отправьте фото (с подписью), видео или текст.",
        "kaa": "⚠️ Tek súwret (túsindirme menen), video yamasa tekst jiberiń.",
    },
    "bc_preview": {
        "uz": "👆 Xabar mijozlarga aynan shu ko'rinishda boradi.\n"
              "👥 Qabul qiluvchilar: <b>{count}</b> ta mijoz\n\nYuborilsinmi?",
        "ru": "👆 Клиенты получат сообщение именно в таком виде.\n"
              "👥 Получателей: <b>{count}</b>\n\nОтправить?",
        "kaa": "👆 Xabar klientlerge tap usı kóriniste baradı.\n"
               "👥 Qabıl etiwshiler: <b>{count}</b> klient\n\nJiberilsin be?",
    },
    "bc_no_customers": {
        "uz": "ℹ️ Hozircha xabar yuboriladigan mijozlar yo'q.",
        "ru": "ℹ️ Пока нет клиентов для рассылки.",
        "kaa": "ℹ️ Házirshe xabar jiberiletuǵın klientler joq.",
    },
    "btn_send": {"uz": "✅ Yuborish", "ru": "✅ Отправить", "kaa": "✅ Jiberiw"},
    "bc_started": {
        "uz": "⏳ Yuborish boshlandi... Tugagach xabar beraman.",
        "ru": "⏳ Рассылка началась... Сообщу, когда закончится.",
        "kaa": "⏳ Jiberiw basladı... Tamamlanǵanda xabar beremen.",
    },
    "bc_done": {
        "uz": "✅ <b>Xabar yuborish tugadi</b>\n\n📨 Yetkazildi: <b>{ok}</b>\n🚫 Yetkazilmadi: <b>{fail}</b>",
        "ru": "✅ <b>Рассылка завершена</b>\n\n📨 Доставлено: <b>{ok}</b>\n🚫 Не доставлено: <b>{fail}</b>",
        "kaa": "✅ <b>Xabar jiberiw tamamlandı</b>\n\n📨 Jetkerildi: <b>{ok}</b>\n🚫 Jetkerilmedi: <b>{fail}</b>",
    },

    # statistika
    "stats": {
        "uz": "📊 <b>Statistika</b>\n\n"
              "👥 Jami mijozlar: <b>{total}</b>\n"
              "📅 Bugun: <b>{today}</b>\n"
              "🗓 Oxirgi 7 kun: <b>{week}</b>\n"
              "📆 Oxirgi 30 kun: <b>{month}</b>\n"
              "🚫 Botni bloklaganlar: {blocked}\n\n"
              "🌐 <b>Til bo'yicha:</b>\n{langs}\n\n"
              "📣 <b>Qayerdan eshitgan:</b>\n{sources}\n\n"
              "💰 Mijozlardagi jami cashback: <b>{cb_balance}</b>\n"
              "➕ Jami berilgan: {cb_given}\n"
              "➖ Jami ishlatilgan: {cb_spent}\n"
              "💯 Cashback foizi: {percent}%",
        "ru": "📊 <b>Статистика</b>\n\n"
              "👥 Всего клиентов: <b>{total}</b>\n"
              "📅 Сегодня: <b>{today}</b>\n"
              "🗓 За 7 дней: <b>{week}</b>\n"
              "📆 За 30 дней: <b>{month}</b>\n"
              "🚫 Заблокировали бота: {blocked}\n\n"
              "🌐 <b>По языкам:</b>\n{langs}\n\n"
              "📣 <b>Откуда узнали:</b>\n{sources}\n\n"
              "💰 Кэшбэк на балансах клиентов: <b>{cb_balance}</b>\n"
              "➕ Всего начислено: {cb_given}\n"
              "➖ Всего списано: {cb_spent}\n"
              "💯 Процент кэшбэка: {percent}%",
        "kaa": "📊 <b>Statistika</b>\n\n"
               "👥 Barlıq klientler: <b>{total}</b>\n"
               "📅 Búgin: <b>{today}</b>\n"
               "🗓 Sońǵı 7 kún: <b>{week}</b>\n"
               "📆 Sońǵı 30 kún: <b>{month}</b>\n"
               "🚫 Bottı bloklaǵanlar: {blocked}\n\n"
               "🌐 <b>Tiller boyınsha:</b>\n{langs}\n\n"
               "📣 <b>Qay jerden esitken:</b>\n{sources}\n\n"
               "💰 Klientlerdegi barlıq keshbek: <b>{cb_balance}</b>\n"
               "➕ Barlıǵı berilgen: {cb_given}\n"
               "➖ Barlıǵı paydalanılǵan: {cb_spent}\n"
               "💯 Keshbek procenti: {percent}%",
    },
    "excel_caption": {
        "uz": "📥 Mijozlar bazasi — {date}\n👥 Jami: {total} ta mijoz",
        "ru": "📥 База клиентов — {date}\n👥 Всего: {total}",
        "kaa": "📥 Klientler bazası — {date}\n👥 Barlıǵı: {total} klient",
    },
    "excel_preparing": {
        "uz": "⏳ Excel fayl tayyorlanmoqda...",
        "ru": "⏳ Готовлю Excel-файл...",
        "kaa": "⏳ Excel fayl tayarlanbaqta...",
    },
    "no_data": {"uz": "—", "ru": "—", "kaa": "—"},

    # cashback
    "cb_ask_customer": {
        "uz": "🔎 Mijoz raqami (ID) yoki telefon raqamini kiriting:\n\n<i>Masalan: 125 yoki 901234567</i>",
        "ru": "🔎 Введите номер клиента (ID) или номер телефона:\n\n<i>Например: 125 или 901234567</i>",
        "kaa": "🔎 Klient nomerin (ID) yamasa telefon nomerin jazıń:\n\n<i>Mısalı: 125 yamasa 901234567</i>",
    },
    "cb_not_found": {
        "uz": "❌ Mijoz topilmadi. Qaytadan kiriting yoki «❌ Bekor qilish» ni bosing.",
        "ru": "❌ Клиент не найден. Введите ещё раз или нажмите «❌ Отмена».",
        "kaa": "❌ Klient tabılmadı. Qaytadan jazıń yamasa «❌ Biykar etiw» túymesin basıń.",
    },
    "customer_card": {
        "uz": "👤 <b>{name}</b>\n🆔 ID: <b>{card}</b>\n📱 {phone}\n💰 Balans: <b>{balance}</b>",
        "ru": "👤 <b>{name}</b>\n🆔 ID: <b>{card}</b>\n📱 {phone}\n💰 Баланс: <b>{balance}</b>",
        "kaa": "👤 <b>{name}</b>\n🆔 ID: <b>{card}</b>\n📱 {phone}\n💰 Balans: <b>{balance}</b>",
    },
    "cb_ask_purchase": {
        "uz": "🛍 Xarid summasini kiriting (so'mda):\n<i>Masalan: 250000</i>\n\n💯 Cashback foizi: <b>{percent}%</b>",
        "ru": "🛍 Введите сумму покупки (в сумах):\n<i>Например: 250000</i>\n\n💯 Процент кэшбэка: <b>{percent}%</b>",
        "kaa": "🛍 Satıp alıw summasın jazıń (sumda):\n<i>Mısalı: 250000</i>\n\n💯 Keshbek procenti: <b>{percent}%</b>",
    },
    "cb_ask_spend": {
        "uz": "➖ Qancha cashback ishlatiladi? Summani kiriting (so'mda):\n\n💰 Mavjud balans: <b>{balance}</b>",
        "ru": "➖ Сколько кэшбэка списать? Введите сумму (в сумах):\n\n💰 Доступно: <b>{balance}</b>",
        "kaa": "➖ Qansha keshbek paydalanıladı? Summanı jazıń (sumda):\n\n💰 Bar balans: <b>{balance}</b>",
    },
    "amount_invalid": {
        "uz": "⚠️ To'g'ri summa kiriting (faqat raqam, masalan: 250000).",
        "ru": "⚠️ Введите корректную сумму (только цифры, например: 250000).",
        "kaa": "⚠️ Durıs summa jazıń (tek sanlar, mısalı: 250000).",
    },
    "cb_zero": {
        "uz": "⚠️ Bu summadan cashback 0 so'm chiqadi. Kattaroq summa kiriting.",
        "ru": "⚠️ С этой суммы кэшбэк равен 0. Введите сумму побольше.",
        "kaa": "⚠️ Bul summadan keshbek 0 sum boladı. Úlkenirek summa jazıń.",
    },
    "spend_too_much": {
        "uz": "⚠️ Balansda yetarli cashback yo'q. Mavjud: <b>{balance}</b>",
        "ru": "⚠️ Недостаточно кэшбэка. Доступно: <b>{balance}</b>",
        "kaa": "⚠️ Balansta jeterli keshbek joq. Bar: <b>{balance}</b>",
    },
    "zero_balance": {
        "uz": "⚠️ Bu mijozning cashback balansi 0 so'm.",
        "ru": "⚠️ У этого клиента баланс кэшбэка 0 сум.",
        "kaa": "⚠️ Bul klienttiń keshbek balansı 0 sum.",
    },
    "cb_confirm_add": {
        "uz": "❓ <b>Tasdiqlang:</b>\n\n👤 {name} (ID {card})\n🛍 Xarid: {purchase}\n"
              "➕ Cashback ({percent}%): <b>{amount}</b>\n💰 Yangi balans: <b>{new_balance}</b>",
        "ru": "❓ <b>Подтвердите:</b>\n\n👤 {name} (ID {card})\n🛍 Покупка: {purchase}\n"
              "➕ Кэшбэк ({percent}%): <b>{amount}</b>\n💰 Новый баланс: <b>{new_balance}</b>",
        "kaa": "❓ <b>Tastıyıqlań:</b>\n\n👤 {name} (ID {card})\n🛍 Satıp alıw: {purchase}\n"
               "➕ Keshbek ({percent}%): <b>{amount}</b>\n💰 Jańa balans: <b>{new_balance}</b>",
    },
    "cb_confirm_spend": {
        "uz": "❓ <b>Tasdiqlang:</b>\n\n👤 {name} (ID {card})\n"
              "➖ Ishlatiladi: <b>{amount}</b>\n💰 Qoladi: <b>{new_balance}</b>",
        "ru": "❓ <b>Подтвердите:</b>\n\n👤 {name} (ID {card})\n"
              "➖ Списать: <b>{amount}</b>\n💰 Останется: <b>{new_balance}</b>",
        "kaa": "❓ <b>Tastıyıqlań:</b>\n\n👤 {name} (ID {card})\n"
               "➖ Paydalanıladı: <b>{amount}</b>\n💰 Qaladı: <b>{new_balance}</b>",
    },
    "cb_done_add": {
        "uz": "✅ Cashback qo'shildi. Yangi balans: <b>{balance}</b>",
        "ru": "✅ Кэшбэк начислен. Новый баланс: <b>{balance}</b>",
        "kaa": "✅ Keshbek qosıldı. Jańa balans: <b>{balance}</b>",
    },
    "cb_done_spend": {
        "uz": "✅ Cashback ishlatildi. Qolgan balans: <b>{balance}</b>",
        "ru": "✅ Кэшбэк списан. Остаток: <b>{balance}</b>",
        "kaa": "✅ Keshbek paydalanıldı. Qalǵan balans: <b>{balance}</b>",
    },
    "notify_ok": {
        "uz": "📩 Mijozga xabar yuborildi.",
        "ru": "📩 Клиент получил уведомление.",
        "kaa": "📩 Klientke xabar jiberildi.",
    },
    "notify_failed": {
        "uz": "⚠️ Mijozga xabar yetib bormadi (botni bloklagan bo'lishi mumkin).",
        "ru": "⚠️ Не удалось уведомить клиента (возможно, бот заблокирован).",
        "kaa": "⚠️ Klientke xabar jetip barmadı (bottı bloklaǵan bolıwı múmkin).",
    },

    # foiz
    "percent_ask": {
        "uz": "💯 Joriy cashback foizi: <b>{percent}%</b>\n\nYangi foizni kiriting (0 dan {max} gacha):",
        "ru": "💯 Текущий процент кэшбэка: <b>{percent}%</b>\n\nВведите новый процент (от 0 до {max}):",
        "kaa": "💯 Házirgi keshbek procenti: <b>{percent}%</b>\n\nJańa procentti jazıń (0 den {max} ge shekem):",
    },
    "percent_invalid": {
        "uz": "⚠️ 0 dan {max} gacha butun son kiriting.",
        "ru": "⚠️ Введите целое число от 0 до {max}.",
        "kaa": "⚠️ 0 den {max} ge shekem pútin san jazıń.",
    },
    "percent_set": {
        "uz": "✅ Cashback foizi <b>{percent}%</b> qilib o'rnatildi.",
        "ru": "✅ Процент кэшбэка установлен: <b>{percent}%</b>.",
        "kaa": "✅ Keshbek procenti <b>{percent}%</b> etip ornatıldı.",
    },

    # adminlar
    "admins_list": {
        "uz": "👥 <b>Adminlar</b>\n\n👑 Developer: <code>{dev}</code>\n\n{list}",
        "ru": "👥 <b>Администраторы</b>\n\n👑 Разработчик: <code>{dev}</code>\n\n{list}",
        "kaa": "👥 <b>Adminler</b>\n\n👑 Developer: <code>{dev}</code>\n\n{list}",
    },
    "admins_empty": {
        "uz": "Qo'shimcha adminlar yo'q.",
        "ru": "Других администраторов нет.",
        "kaa": "Qosımsha adminler joq.",
    },
    "btn_add_admin": {"uz": "➕ Admin qo'shish", "ru": "➕ Добавить админа", "kaa": "➕ Admin qosıw"},
    "admin_ask_id": {
        "uz": "🆔 Yangi adminning Telegram ID raqamini yuboring.\n\n"
              "<i>ID ni @userinfobot orqali bilish mumkin. Yangi admin botga /start bosgan bo'lishi kerak.</i>",
        "ru": "🆔 Отправьте Telegram ID нового администратора.\n\n"
              "<i>ID можно узнать через @userinfobot. Новый админ должен нажать /start в боте.</i>",
        "kaa": "🆔 Jańa adminniń Telegram ID nomerin jiberiń.\n\n"
               "<i>ID di @userinfobot arqalı biliwge boladı. Jańa admin botqa /start basqan bolıwı kerek.</i>",
    },
    "admin_id_invalid": {
        "uz": "⚠️ Telegram ID faqat raqamlardan iborat bo'ladi. Qaytadan yuboring.",
        "ru": "⚠️ Telegram ID состоит только из цифр. Отправьте ещё раз.",
        "kaa": "⚠️ Telegram ID tek sanlardan ibarat boladı. Qaytadan jiberiń.",
    },
    "admin_added": {
        "uz": "✅ <code>{id}</code> admin qilindi.",
        "ru": "✅ <code>{id}</code> назначен администратором.",
        "kaa": "✅ <code>{id}</code> admin etildi.",
    },
    "admin_exists": {
        "uz": "ℹ️ Bu foydalanuvchi allaqachon admin.",
        "ru": "ℹ️ Этот пользователь уже администратор.",
        "kaa": "ℹ️ Bul paydalanıwshı áldeqashan admin.",
    },
    "admin_removed": {
        "uz": "🗑 <code>{id}</code> adminlikdan olindi.",
        "ru": "🗑 <code>{id}</code> больше не администратор.",
        "kaa": "🗑 <code>{id}</code> adminlikten alındı.",
    },
    "you_are_admin": {
        "uz": "🎉 Siz BEST SHOP TREND botida admin qilib tayinlandingiz! Admin panelni ochish uchun /start bosing.",
        "ru": "🎉 Вас назначили администратором бота BEST SHOP TREND! Нажмите /start, чтобы открыть админ-панель.",
        "kaa": "🎉 Siz BEST SHOP TREND botında admin etip tayınlandıńız! Admin paneldi ashıw ushın /start basıń.",
    },
    "only_developer": {
        "uz": "⛔ Bu bo'lim faqat developer uchun.",
        "ru": "⛔ Этот раздел только для разработчика.",
        "kaa": "⛔ Bul bólim tek developer ushın.",
    },
}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """Kalit bo'yicha matnni kerakli tilda qaytaradi."""
    item = TEXTS.get(key)
    if item is None:
        return key
    text = item.get(lang) or item["uz"]
    return text.format(**kwargs) if kwargs else text


def variants(key: str) -> set[str]:
    """Tugma matnining barcha tillardagi variantlari (handler filtrlari uchun)."""
    return set(TEXTS[key].values())


def money(amount: int, lang: str = "uz") -> str:
    """250000 -> '250 000 so'm'"""
    return f"{int(amount):,}".replace(",", " ") + " " + t("currency", lang)
