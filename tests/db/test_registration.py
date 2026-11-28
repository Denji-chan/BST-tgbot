from datetime import date

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services.registration_service import RegistrationStatus, register_user  # noqa: E402
from utils.db_api.repositories import referrals  # noqa: E402


def _data(**overrides):
    data = {
        "telegram_id": 777,
        "first_name": "Malika",
        "last_name": "Karimova",
        "phone": "+998901234567",
        "birth_date": date(2004, 5, 14),
        "language": "ru",
        "referrer_id": None,
    }
    data.update(overrides)
    return data


async def test_register_new_user(session, now):
    result = await register_user(session, now=now, **_data())
    assert result.status is RegistrationStatus.OK
    assert result.user.id is not None
    assert result.user.language == "ru"
    assert result.referrer is None


async def test_register_twice_same_telegram(session, now):
    await register_user(session, now=now, **_data())
    result = await register_user(session, now=now, **_data(phone="+998909999999"))
    assert result.status is RegistrationStatus.ALREADY_REGISTERED


async def test_phone_taken_by_other_account(session, now):
    await register_user(session, now=now, **_data())
    result = await register_user(session, now=now, **_data(telegram_id=888))
    assert result.status is RegistrationStatus.PHONE_TAKEN


async def test_referral_attached(session, make_user, now):
    referrer = await make_user()
    result = await register_user(session, now=now, **_data(referrer_id=referrer.id))
    assert result.referrer.id == referrer.id
    assert result.user.referred_by_id == referrer.id
    referral = await referrals.get_by_referred(session, result.user.id)
    assert referral.referrer_id == referrer.id
    assert referral.status == "pending"


async def test_self_referral_ignored(session, make_user, now):
    # O'z havolasi orqali: referrer bilan bir xil telegram_id (amalda ro'yxatdan o'tgan bo'ladi,
    # lekin tekshiruv baribir ishlashi kerak)
    referrer = await make_user(telegram_id=999)
    result = await register_user(session, now=now, **_data(telegram_id=999, referrer_id=referrer.id))
    assert result.status is RegistrationStatus.ALREADY_REGISTERED


async def test_unknown_referrer_ignored(session, now):
    result = await register_user(session, now=now, **_data(referrer_id=12345))
    assert result.status is RegistrationStatus.OK
    assert result.referrer is None
    assert await referrals.get_by_referred(session, result.user.id) is None
