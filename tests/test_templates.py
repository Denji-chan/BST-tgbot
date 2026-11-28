import pytest

from services.templates import TEMPLATE_KEYS, TemplateError, default_key, render, validate
from utils.misc.i18n import LANGUAGES, Translator


def test_valid_template():
    validate("inactive_60", "Salom {name}, balansingiz {balance} so'm")
    validate("payment_reminder", "Bugun 25-sana")


@pytest.mark.parametrize(
    "key, text, reason",
    [
        ("inactive_60", "Salom {ism}", "unknown_fields"),
        ("payment_reminder", "{balance}", "unknown_fields"),
        ("inactive_60", "Salom {name", "format"),
        ("inactive_60", "Salom {}", "format"),
        ("inactive_60", "   ", "empty"),
        ("inactive_60", "x" * 4000, "too_long"),
    ],
)
def test_invalid_templates(key, text, reason):
    with pytest.raises(TemplateError) as exc:
        validate(key, text)
    assert exc.value.reason == reason


def test_unknown_fields_listed():
    with pytest.raises(TemplateError) as exc:
        validate("inactive_90", "{a} {b} {name}")
    assert exc.value.fields == ["a", "b"]


def test_render():
    assert render("Salom {name}, {balance}", name="Malika", balance="5 000") == "Salom Malika, 5 000"
    assert render("Salom {name", name="x") == "Salom {name"  # buzilgan matn yiqitmaydi


def test_default_templates_are_valid_in_all_languages():
    tr = Translator()
    for key in TEMPLATE_KEYS:
        for lang in LANGUAGES:
            validate(key, tr.raw(lang, default_key(key)))
