"""Mijozni ro'yxatdan o'tkazish (bitta DB tranzaksiyada)."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from services import referral as referral_rules
from utils.db_api.models import User
from utils.db_api.repositories import referrals, users


class RegistrationStatus(Enum):
    OK = "ok"
    ALREADY_REGISTERED = "already_registered"
    PHONE_TAKEN = "phone_taken"


@dataclass(frozen=True)
class RegistrationResult:
    status: RegistrationStatus
    user: User | None = None
    referrer: User | None = None


async def register_user(
    session: AsyncSession,
    *,
    telegram_id: int,
    first_name: str,
    last_name: str,
    phone: str,
    birth_date: date,
    language: str,
    referrer_id: int | None,
    now: datetime,
) -> RegistrationResult:
    if await users.get_by_telegram_id(session, telegram_id) is not None:
        return RegistrationResult(RegistrationStatus.ALREADY_REGISTERED)
    if await users.get_by_phone(session, phone) is not None:
        # Raqam allaqachon boshqa akkauntda: eski mijoz qayta "yangi" bo'la olmaydi.
        return RegistrationResult(RegistrationStatus.PHONE_TAKEN)

    referrer = None
    if referrer_id is not None:
        candidate = await users.get_by_id(session, referrer_id)
        if candidate is not None and referral_rules.is_valid_referrer(candidate.telegram_id, telegram_id):
            referrer = candidate

    try:
        user = await users.create(
            session,
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            language=language,
            referred_by_id=referrer.id if referrer else None,
            registered_at=now,
        )
        if referrer is not None:
            await referrals.create(session, referrer_id=referrer.id, referred_id=user.id, created_at=now)
        await session.commit()
    except IntegrityError:
        # Ikki so'rov bir vaqtda kelgan bo'lishi mumkin (telefon yoki telegram_id unikal).
        await session.rollback()
        return RegistrationResult(RegistrationStatus.PHONE_TAKEN)

    return RegistrationResult(RegistrationStatus.OK, user=user, referrer=referrer)
