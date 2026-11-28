"""Cashback qoidalari (sof funksiyalar, bazaga bog'liq emas). Pul butun so'mda, float yo'q.

Hisob tartibi:
    subtotal (mahsulotlar)
    - tug'ilgan kun chegirmasi (10%, pastga yaxlitlanadi)
    = total (xarid summasi)
    - ishlatilgan cashback (balans va total'ning 50% i bilan cheklangan)
    = paid (mijoz haqiqatda to'lagan pul)
    cashback_earned = paid * 3% (pastga yaxlitlanadi)
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from services.rules import BusinessRules


class InsufficientCashback(Exception):
    pass


@dataclass(frozen=True)
class Lot:
    """Cashback partiyasi: qachon kuyadi va qancha qolgan."""

    id: int
    remaining: int
    expires_at: datetime


@dataclass(frozen=True)
class PurchaseCalculation:
    subtotal: int
    birthday_discount: int
    total: int
    cashback_available: int  # shu xaridda ishlatish mumkin bo'lgan eng ko'p summa
    cashback_used: int
    paid: int
    cashback_earned: int


def percent_of(amount: int, percent: int) -> int:
    """Butun sonli foiz, pastga yaxlitlab."""
    return amount * percent // 100


def birthday_discount(subtotal: int, rules: BusinessRules) -> int:
    return percent_of(subtotal, rules.birthday_discount_percent)


def max_usable(total: int, balance: int, rules: BusinessRules) -> int:
    return max(0, min(balance, percent_of(total, rules.cashback_max_use_percent)))


def earned_for(paid: int, rules: BusinessRules) -> int:
    return percent_of(paid, rules.cashback_percent)


def calculate_purchase(
    subtotal: int,
    balance: int,
    use_cashback: bool,
    birthday_applies: bool,
    rules: BusinessRules,
) -> PurchaseCalculation:
    if subtotal <= 0:
        raise ValueError("Xarid summasi musbat bo'lishi kerak")
    discount = birthday_discount(subtotal, rules) if birthday_applies else 0
    total = subtotal - discount
    available = max_usable(total, balance, rules)
    used = available if use_cashback else 0
    paid = total - used
    return PurchaseCalculation(
        subtotal=subtotal,
        birthday_discount=discount,
        total=total,
        cashback_available=available,
        cashback_used=used,
        paid=paid,
        cashback_earned=earned_for(paid, rules),
    )


def expires_at_for(earned_at: datetime, tz: ZoneInfo, lifetime_days: int) -> datetime:
    """Olingan kundan boshlab `lifetime_days` kun ishlaydi, keyingi kun 00:00 (mahalliy) da kuyadi."""
    earned_day = earned_at.astimezone(tz).date()
    burn_local = datetime.combine(earned_day + timedelta(days=lifetime_days), time(0, 0), tzinfo=tz)
    return burn_local.astimezone(UTC)


def allocate_fifo(lots: list[Lot], amount: int) -> list[tuple[int, int]]:
    """`amount` ni eng eski partiyalardan yechadi. [(lot_id, olingan summa), ...] qaytaradi."""
    if amount < 0:
        raise ValueError("Summa manfiy bo'lishi mumkin emas")
    plan: list[tuple[int, int]] = []
    left = amount
    for lot in sorted(lots, key=lambda x: (x.expires_at, x.id)):
        if left == 0:
            break
        take = min(lot.remaining, left)
        if take > 0:
            plan.append((lot.id, take))
            left -= take
    if left > 0:
        raise InsufficientCashback(f"Yetishmayapti: {left}")
    return plan


def active_balance(lots: list[Lot], now: datetime) -> int:
    return sum(lot.remaining for lot in lots if lot.remaining > 0 and lot.expires_at > now)


def select_expired(lots: list[Lot], now: datetime) -> list[Lot]:
    return [lot for lot in lots if lot.remaining > 0 and lot.expires_at <= now]


def nearest_expiry(lots: list[Lot], now: datetime, tz: ZoneInfo) -> tuple[date, int] | None:
    """Eng yaqin kuyish sanasi (mahalliy) va o'sha kuni kuyadigan jami summa."""
    active = [lot for lot in lots if lot.remaining > 0 and lot.expires_at > now]
    if not active:
        return None
    first_day = min(lot.expires_at.astimezone(tz).date() for lot in active)
    amount = sum(lot.remaining for lot in active if lot.expires_at.astimezone(tz).date() == first_day)
    return first_day, amount
