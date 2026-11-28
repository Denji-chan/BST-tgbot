from aiogram import F, Router

from filters import IsAdmin

from . import admins, broadcast, menu, purchase, stats, support_reply, texts, users_list

router = Router(name="admins")
# Admin handlerlari faqat shaxsiy chatda va faqat adminlar uchun.
router.message.filter(F.chat.type == "private", IsAdmin())
router.callback_query.filter(IsAdmin())
router.include_routers(
    menu.router,  # bekor qilish birinchi bo'lishi kerak
    purchase.router,
    support_reply.router,
    stats.router,
    users_list.router,
    texts.router,
    broadcast.router,
    admins.router,  # ichida IsDeveloper filtri
)
