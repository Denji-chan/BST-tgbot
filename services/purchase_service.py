"""Xarid: ko'rib chiqish (preview) va saqlash.

Saqlashda xarid, mahsulotlar, cashback yechish (FIFO), yangi cashback, tug'ilgan kun belgisi
va referal bonusi BITTA DB tranzaksiyasida bajariladi.
"""

from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from services import birthday as birthday_rules
from services import cashback as cashback_rules
from services import cashback_service, referral_service
from services.items import Item, items_total
from services.referral_service import ReferralReward
from services.rules import BusinessRules
from utils.db_api.models import CashbackTransaction, Purchase, User
from utils.db_api.repositories import birthdays, cashback, purchases, users


@dataclass(frozen=True)
class CustomerState:
    user: User
    balance: int
    birthday_year: int | None  # chegirma bugun ishlatilishi mumkin bo'lsa, tug'ilgan kun yili


@dataclass(frozen=True)
class PurchaseResult:
    user: User
    purchase: Purchase
    calc: cashback_rules.PurchaseCalculation
    balance: int
    referral_reward: ReferralReward | None


class CustomerNotFound(Exception):
    pass


async def customer_state(
    session: AsyncSession, user: User, now: datetime, tz: ZoneInfo, business: BusinessRules
) -> CustomerState:
    balance = await cashback.balance(session, user.id, now)
    year = birthday_rules.discount_year(user.birth_date, now.astimezone(tz).date(), business.birthday_extra_days)
    if year is not None and await birthdays.is_used(session, user.id, year):
        year = None
    return CustomerState(user=user, balance=balance, birthday_year=year)


async def preview(
    session: AsyncSession,
    user: User,
    items: list[Item],
    use_cashback: bool,
    now: datetime,
    tz: ZoneInfo,
    business: BusinessRules,
) -> tuple[CustomerState, cashback_rules.PurchaseCalculation]:
    state = await customer_state(session, user, now, tz, business)
    calc = cashback_rules.calculate_purchase(
        items_total(items), state.balance, use_cashback, state.birthday_year is not None, business
    )
    return state, calc


async def register_purchase(
    session: AsyncSession,
    *,
    user_id: int,
    admin_telegram_id: int,
    items: list[Item],
    use_cashback: bool,
    now: datetime,
    tz: ZoneInfo,
    business: BusinessRules,
) -> PurchaseResult:
    try:
        user = await users.get_by_id(session, user_id, for_update=True)
        if user is None:
            raise CustomerNotFound(user_id)
        # Hisob bazadagi eng so'nggi holat bo'yicha qayta qilinadi (preview'dan keyin balans o'zgargan bo'lishi mumkin).
        state, calc = await preview(session, user, items, use_cashback, now, tz, business)
        is_first = await purchases.count_for_user(session, user.id) == 0

        purchase = await purchases.create(
            session,
            user_id=user.id,
            admin_telegram_id=admin_telegram_id,
            subtotal=calc.subtotal,
            birthday_discount=calc.birthday_discount,
            total=calc.total,
            cashback_used=calc.cashback_used,
            paid=calc.paid,
            cashback_earned=calc.cashback_earned,
            items=items,
            created_at=now,
        )
        await cashback_service.spend(
            session, user_id=user.id, amount=calc.cashback_used, now=now, purchase_id=purchase.id
        )
        await cashback_service.add_credit(
            session,
            user_id=user.id,
            type_=CashbackTransaction.TYPE_EARN,
            amount=calc.cashback_earned,
            now=now,
            tz=tz,
            business=business,
            purchase_id=purchase.id,
        )
        if state.birthday_year is not None:
            await birthdays.add(session, user.id, state.birthday_year, purchase.id, now)
        user.last_purchase_at = now

        reward = await referral_service.process_purchase(
            session,
            friend=user,
            purchase=purchase,
            is_first_purchase=is_first,
            now=now,
            tz=tz,
            business=business,
        )
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    balance = await cashback.balance(session, user.id, now)
    return PurchaseResult(user=user, purchase=purchase, calc=calc, balance=balance, referral_reward=reward)
