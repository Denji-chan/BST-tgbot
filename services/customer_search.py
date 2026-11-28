"""Admin mijozni qanday qidirayotganini aniqlash: ID raqami yoki telefon."""

import re
from dataclasses import dataclass

from utils.misc.phone import normalize_phone

MAX_ID_DIGITS = 7  # 7 xonagacha son - mijoz ID raqami, undan uzuni - telefon


@dataclass(frozen=True)
class CustomerQuery:
    customer_id: int | None = None
    phone: str | None = None


def parse_customer_query(text: str | None) -> CustomerQuery | None:
    raw = (text or "").strip()
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None
    is_plain_number = raw.lstrip("#").isdigit()
    if is_plain_number and len(digits) <= MAX_ID_DIGITS:
        return CustomerQuery(customer_id=int(digits))
    phone = normalize_phone(raw)
    return CustomerQuery(phone=phone) if phone else None
