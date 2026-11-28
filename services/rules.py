"""Do'konning biznes qoidalari bir joyda. Pul butun so'mda."""

from dataclasses import dataclass


@dataclass(frozen=True)
class BusinessRules:
    cashback_percent: int = 3  # to'langan pulning necha foizi cashback
    cashback_max_use_percent: int = 50  # xaridning necha foizini cashback bilan to'lash mumkin (.env)
    cashback_lifetime_days: int = 90  # cashback necha kun amal qiladi
    birthday_discount_percent: int = 10
    birthday_extra_days: int = 3  # tug'ilgan kundan keyin yana necha kun amal qiladi
    referral_bonus: int = 30_000
    referral_min_purchase: int = 300_000  # do'stning birinchi xaridi kamida shuncha bo'lsa
    reengagement_stages: tuple[int, ...] = (60, 90, 120)
