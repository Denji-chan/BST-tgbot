"""60/90/120 kunlik "sizni sog'indik" xabarlari qoidasi (sof funksiyalar)."""

from datetime import date, datetime


def due_stage(last_purchase: date, today: date, stages: tuple[int, ...]) -> int | None:
    """Oxirgi xariddan beri yetib kelingan eng katta bosqich (60, 90 yoki 120). Hali yetmagan bo'lsa None.

    Bot bir necha kun ishlamay qolsa ham, faqat oxirgi yetilgan bosqich yuboriladi.
    """
    days = (today - last_purchase).days
    reached = [s for s in stages if days >= s]
    return max(reached) if reached else None


def notification_key(user_id: int, stage: int, last_purchase_at: datetime) -> str:
    """Bitta "kelmay qolish davri" = oxirgi xarid vaqti. Yangi xarid bo'lsa, kalit o'zgaradi."""
    return f"{user_id}:{stage}:{last_purchase_at.isoformat()}"
