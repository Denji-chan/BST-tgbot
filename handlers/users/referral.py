from aiogram import F, Router
from aiogram.types import LinkPreviewOptions, Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import RULES
from filters import IsRegistered
from services import referral
from utils.db_api.models import User
from utils.db_api.repositories import referrals
from utils.misc.formatting import money
from utils.misc.i18n import Translate, i18n
from utils.misc.throttling import rate_limit

router = Router(name="users.referral")


@router.message(F.text.in_(i18n.variants("btn.referral")), IsRegistered(), flags=rate_limit(2, "referral"))
async def show_referral(message: Message, session: AsyncSession, t: Translate, user: User, bot_username: str) -> None:
    invited, rewarded = await referrals.counts_for_referrer(session, user.id)
    await message.answer(
        t(
            "referral.info",
            link=referral.make_link(bot_username, user.id),
            bonus=money(RULES.referral_bonus),
            min_purchase=money(RULES.referral_min_purchase),
            days=RULES.cashback_lifetime_days,
            invited=invited,
            rewarded=rewarded,
        ),
        link_preview_options=LinkPreviewOptions(is_disabled=True),
    )
