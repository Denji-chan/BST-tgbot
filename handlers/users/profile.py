from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from data.config import TIMEZONE
from filters import IsRegistered
from services.profile_service import get_profile
from utils.db_api.models import User
from utils.misc.formatting import esc, fmt_date, local_date, money
from utils.misc.i18n import Translate, i18n
from utils.misc.throttling import rate_limit

router = Router(name="users.profile")


@router.message(F.text.in_(i18n.variants("btn.profile")), IsRegistered(), flags=rate_limit(2, "profile"))
async def show_profile(message: Message, session: AsyncSession, t: Translate, user: User) -> None:
    now = datetime.now(TIMEZONE)
    profile = await get_profile(session, user, now, TIMEZONE)

    if profile.nearest_expiry is None:
        expiry = t("profile.no_expiry")
    else:
        burn_day, amount = profile.nearest_expiry
        expiry = t("profile.expiry", date=fmt_date(burn_day), amount=money(amount))

    if profile.last_purchases:
        lines = [
            t(
                "profile.purchase_line",
                date=fmt_date(local_date(p.created_at, TIMEZONE)),
                total=money(p.total),
                earned=money(p.cashback_earned),
            )
            for p in profile.last_purchases
        ]
        purchases_text = "\n".join(lines)
    else:
        purchases_text = t("profile.no_purchases")

    await message.answer(
        t(
            "profile.text",
            name=esc(user.full_name),
            phone=user.phone,
            customer_id=user.id,
            balance=money(profile.balance),
            expiry=expiry,
            purchases=purchases_text,
        )
    )
