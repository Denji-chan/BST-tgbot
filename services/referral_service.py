"""Referal bonusini berish. Xarid tranzaksiyasi ichida chaqiriladi, commit qilmaydi."""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from services import cashback_service
from services import referral as referral_rules
from services.rules import BusinessRules
from utils.db_api.models import CashbackTransaction, Purchase, Referral, User
from utils.db_api.repositories import referrals, users


@dataclass(frozen=True)
class ReferralReward:
    referrer: User
    friend: User
    amount: int


async def process_purchase(
    session: AsyncSession,
    *,
    friend: User,
    purchase: Purchase,
    is_first_purchase: bool,
    now: datetime,
    tz: ZoneInfo,
    business: BusinessRules,
) -> ReferralReward | None:
    """Do'stning xaridi referal shartini bajarsa, taklif qilganga bonus beradi.

    Faqat birinchi xarid hisobga olinadi: shart bajarilmasa referal yopiladi (rejected).
    """
    referral = await referrals.get_by_referred(session, friend.id, for_update=True)
    if referral is None or referral.status != Referral.STATUS_PENDING:
        return None

    referral.purchase_id = purchase.id
    referral.resolved_at = now
    if not referral_rules.is_bonus_due(is_first_purchase, purchase.total, business):
        referral.status = Referral.STATUS_REJECTED
        return None

    referrer = await users.get_by_id(session, referral.referrer_id)
    if referrer is None:
        referral.status = Referral.STATUS_REJECTED
        return None

    await cashback_service.add_credit(
        session,
        user_id=referrer.id,
        type_=CashbackTransaction.TYPE_REFERRAL,
        amount=business.referral_bonus,
        now=now,
        tz=tz,
        business=business,
        purchase_id=purchase.id,
    )
    referral.status = Referral.STATUS_REWARDED
    return ReferralReward(referrer=referrer, friend=friend, amount=business.referral_bonus)
