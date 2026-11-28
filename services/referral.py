"""Referal qoidalari (bazaga bog'liq emas)."""

import re

from services.rules import BusinessRules

PAYLOAD_PREFIX = "ref"
_PAYLOAD_RE = re.compile(rf"^{PAYLOAD_PREFIX}(\d{{1,10}})$")


def make_payload(user_id: int) -> str:
    return f"{PAYLOAD_PREFIX}{user_id}"


def make_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start={make_payload(user_id)}"


def parse_payload(payload: str | None) -> int | None:
    """'/start ref15' dagi 'ref15' -> 15."""
    match = _PAYLOAD_RE.match((payload or "").strip())
    return int(match.group(1)) if match else None


def is_valid_referrer(referrer_telegram_id: int, new_telegram_id: int) -> bool:
    """O'zini o'zi taklif qilish taqiqlangan."""
    return referrer_telegram_id != new_telegram_id


def is_bonus_due(is_first_purchase: bool, purchase_total: int, rules: BusinessRules) -> bool:
    """Bonus faqat do'stning birinchi xaridi uchun va summasi chegaradan kam bo'lmasa."""
    return is_first_purchase and purchase_total >= rules.referral_min_purchase
