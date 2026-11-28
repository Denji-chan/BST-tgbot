"""Scheduler vazifalari: soxta bot bilan, vaqt "muzlatilgan"."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")
pytest.importorskip("aiogram")
pytest.importorskip("apscheduler")

from services import template_service  # noqa: E402
from services.items import Item  # noqa: E402
from services.purchase_service import register_purchase  # noqa: E402
from services.rules import BusinessRules  # noqa: E402
from utils import scheduler as jobs  # noqa: E402
from utils.db_api.repositories import admins, users  # noqa: E402
from utils.misc.i18n import Translator  # noqa: E402

TZ = ZoneInfo("Asia/Tashkent")
RULES = BusinessRules()


class FakeBot:
    def __init__(self):
        self.sent: list[tuple[int, str]] = []

    async def send_message(self, chat_id, text, **kwargs):
        self.sent.append((chat_id, text))


class FrozenDatetime(datetime):
    current: datetime

    @classmethod
    def now(cls, tz=None):
        return cls.current.astimezone(tz) if tz else cls.current


@pytest.fixture
def freeze(monkeypatch):
    def _set(value: datetime):
        FrozenDatetime.current = value
        monkeypatch.setattr(jobs, "datetime", FrozenDatetime)

    monkeypatch.setattr(jobs, "SEND_PAUSE", 0)
    return _set


async def _buy(session, user, at):
    await register_purchase(
        session,
        user_id=user.id,
        admin_telegram_id=1,
        items=[Item("X", 1, 100_000)],
        use_cashback=False,
        now=at,
        tz=TZ,
        business=RULES,
    )


async def test_reengagement_once_per_stage(session_factory, session, make_user, freeze):
    tr = Translator()
    user = await make_user(language="ru")
    await make_user()  # hech xarid qilmagan: xabar olmaydi
    await _buy(session, user, datetime(2026, 9, 1, 12, tzinfo=TZ))
    bot = FakeBot()

    freeze(datetime(2026, 10, 31, 20, tzinfo=TZ))  # 60-kun
    await jobs.reengagement_job(bot, session_factory, tr, TZ, RULES)
    await jobs.reengagement_job(bot, session_factory, tr, TZ, RULES)  # qayta ishga tushsa ham bir marta
    assert len(bot.sent) == 1
    assert bot.sent[0][0] == user.telegram_id
    assert user.first_name in bot.sent[0][1]
    assert "3 000" in bot.sent[0][1]

    freeze(datetime(2026, 11, 30, 20, tzinfo=TZ))  # 90-kun
    await jobs.reengagement_job(bot, session_factory, tr, TZ, RULES)
    assert len(bot.sent) == 2


async def test_reengagement_uses_edited_text(session_factory, session, make_user, freeze, now):
    tr = Translator()
    user = await make_user()
    await _buy(session, user, datetime(2026, 9, 1, 12, tzinfo=TZ))
    await template_service.save_text(session, "inactive_60", "uz", "Kelavering, {name}!", 1, now)
    bot = FakeBot()
    freeze(datetime(2026, 10, 31, 20, tzinfo=TZ))
    await jobs.reengagement_job(bot, session_factory, tr, TZ, RULES)
    assert bot.sent == [(user.telegram_id, f"Kelavering, {user.first_name}!")]


async def test_new_purchase_resets_period(session_factory, session, make_user, freeze):
    tr = Translator()
    user = await make_user()
    await _buy(session, user, datetime(2026, 9, 1, 12, tzinfo=TZ))
    await _buy(session, user, datetime(2026, 10, 20, 12, tzinfo=TZ))
    bot = FakeBot()
    freeze(datetime(2026, 10, 31, 20, tzinfo=TZ))  # oxirgi xariddan 11 kun
    await jobs.reengagement_job(bot, session_factory, tr, TZ, RULES)
    assert bot.sent == []


async def test_birthday_greeting_once(session_factory, make_user, freeze):
    tr = Translator()
    user = await make_user(birth_date=date(2004, 5, 14))
    await make_user(birth_date=date(2004, 5, 15))
    bot = FakeBot()
    freeze(datetime(2026, 5, 14, 10, tzinfo=TZ))
    await jobs.birthday_job(bot, session_factory, tr, TZ, RULES)
    await jobs.birthday_job(bot, session_factory, tr, TZ, RULES)
    assert len(bot.sent) == 1
    assert bot.sent[0][0] == user.telegram_id
    assert "17.05.2026" in bot.sent[0][1]


async def test_payment_reminder_to_all_admins_once_per_month(session_factory, session, freeze):
    tr = Translator()
    await admins.ensure(session, 111, "Dev")
    await admins.add(session, 222, "Admin", added_by=111)
    await session.commit()
    bot = FakeBot()
    freeze(datetime(2026, 12, 25, 10, tzinfo=TZ))
    await jobs.payment_reminder_job(bot, session_factory, tr, TZ)
    await jobs.payment_reminder_job(bot, session_factory, tr, TZ)
    assert sorted(chat for chat, _ in bot.sent) == [111, 222]
    freeze(datetime(2027, 1, 25, 10, tzinfo=TZ))
    await jobs.payment_reminder_job(bot, session_factory, tr, TZ)
    assert len(bot.sent) == 4


async def test_expire_job(session_factory, session, make_user, freeze):
    user = await make_user()
    await _buy(session, user, datetime(2026, 9, 1, 12, tzinfo=TZ))
    freeze(datetime(2026, 11, 30, 0, 5, tzinfo=TZ))
    await jobs.expire_cashback_job(session_factory, TZ)
    async with session_factory() as s:
        rows = await users.list_all(s, datetime(2026, 11, 30, 1, tzinfo=TZ))
    assert [(r.user.id, r.balance) for r in rows] == [(user.id, 0)]


def test_scheduler_jobs_and_times():
    sched = jobs.setup_scheduler(FakeBot(), None, Translator(), TZ, RULES)
    by_id = {job.id: job for job in sched.get_jobs()}
    assert set(by_id) == {"expire_cashback", "birthday", "reengagement", "payment_reminder"}
    fields = {f.name: str(f) for f in by_id["payment_reminder"].trigger.fields}
    assert fields["day"] == "25" and fields["hour"] == "10" and fields["minute"] == "0"
    expire = {f.name: str(f) for f in by_id["expire_cashback"].trigger.fields}
    assert expire["hour"] == "0" and expire["minute"] == "5"
    assert str(by_id["birthday"].trigger.timezone) == "Asia/Tashkent"
