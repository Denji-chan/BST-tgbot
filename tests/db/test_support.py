import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services.support_service import MAX_TEXT_LENGTH, create_request, save_answer  # noqa: E402
from utils.db_api.repositories import admins  # noqa: E402


async def test_request_goes_to_all_admins(session, make_user, now):
    await admins.ensure(session, 111, "Dev")
    await admins.add(session, 222, "Admin", added_by=111)
    await session.commit()
    user = await make_user()
    request = await create_request(session, user, "Kurtka bormi?", now)
    assert request.message.id is not None
    assert sorted(a.telegram_id for a in request.recipients) == [111, 222]


async def test_answer_saved_and_second_answer_detected(session, make_user, now):
    user = await make_user()
    request = await create_request(session, user, "Savol", now)
    first = await save_answer(session, request.message.id, "Ha, bor", 111, now)
    assert first.customer.id == user.id
    assert first.message.answer == "Ha, bor"
    assert first.already_answered_by is None
    second = await save_answer(session, request.message.id, "Yana", 222, now)
    assert second.already_answered_by == 111


async def test_long_text_is_trimmed_and_unknown_request(session, make_user, now):
    user = await make_user()
    request = await create_request(session, user, "x" * (MAX_TEXT_LENGTH + 100), now)
    assert len(request.message.text) == MAX_TEXT_LENGTH
    assert await save_answer(session, 9999, "javob", 1, now) is None
