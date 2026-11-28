from aiogram import F, Router

from . import chat_member, help, profile, referral, settings, start, support

router = Router(name="users")
# Foydalanuvchi handlerlari faqat bot bilan shaxsiy chatda ishlaydi.
router.message.filter(F.chat.type == "private")
router.include_routers(
    chat_member.router,
    start.router,
    help.router,
    profile.router,
    referral.router,
    support.router,
    settings.router,
)
