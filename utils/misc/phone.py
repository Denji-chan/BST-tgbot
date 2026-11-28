"""Telefon raqamlarini bir xil ko'rinishga keltirish: +998901234567."""

import re

_NON_DIGIT = re.compile(r"\D")


def normalize_phone(raw: str | None) -> str | None:
    digits = _NON_DIGIT.sub("", raw or "")
    if len(digits) == 9:  # 901234567 -> O'zbekiston raqami
        digits = "998" + digits
    if len(digits) == 12 and digits.startswith("998"):
        return "+" + digits
    if 8 <= len(digits) <= 15 and not digits.startswith("998"):
        return "+" + digits  # chet el raqami (masalan, Qozog'iston)
    return None
