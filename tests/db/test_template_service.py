import pytest

pytest.importorskip("sqlalchemy")
pytest.importorskip("aiosqlite")
pytest.importorskip("pytest_asyncio")

from services import template_service  # noqa: E402
from services.templates import TemplateError  # noqa: E402
from utils.misc.i18n import Translator  # noqa: E402


async def test_default_then_custom_text(session, now):
    tr = Translator()
    default = await template_service.get_text(session, tr, "inactive_60", "ru")
    assert default == tr.raw("ru", "template.inactive_60")

    await template_service.save_text(session, "inactive_60", "ru", "Привет, {name}!", 1, now)
    assert await template_service.get_text(session, tr, "inactive_60", "ru") == "Привет, {name}!"
    # boshqa til o'zgarmaydi
    assert await template_service.get_text(session, tr, "inactive_60", "uz") == tr.raw("uz", "template.inactive_60")

    await template_service.save_text(session, "inactive_60", "ru", "Снова {name}", 2, now)
    assert await template_service.get_text(session, tr, "inactive_60", "ru") == "Снова {name}"


async def test_invalid_text_not_saved(session, now):
    tr = Translator()
    with pytest.raises(TemplateError):
        await template_service.save_text(session, "inactive_90", "uz", "{nomalum}", 1, now)
    assert await template_service.get_text(session, tr, "inactive_90", "uz") == tr.raw("uz", "template.inactive_90")
