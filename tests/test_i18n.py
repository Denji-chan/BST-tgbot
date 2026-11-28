"""Tarjimalar to'liqligi: har bir kalit 3 tilda, o'zgaruvchilar bir xil, koddagi kalitlar mavjud."""

import re
import string
from pathlib import Path

import pytest

from utils.misc.i18n import LANGUAGES, Translator, guess_language

ROOT = Path(__file__).resolve().parents[1]
CODE_DIRS = ["handlers", "keyboards", "middlewares", "filters", "services", "utils", "app.py"]
KEY_LITERAL = re.compile(r"[\"']([a-z_]+(?:\.[a-z0-9_]+)+)[\"']")


@pytest.fixture(scope="module")
def tr():
    return Translator()


def _fields(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


def test_all_languages_have_same_keys(tr):
    base = tr.keys("uz")
    for lang in LANGUAGES:
        assert tr.keys(lang) == base, f"{lang}: farq {tr.keys(lang) ^ base}"


def test_placeholders_match_across_languages(tr):
    for key in tr.keys("uz"):
        expected = _fields(tr.raw("uz", key))
        for lang in LANGUAGES:
            assert _fields(tr.raw(lang, key)) == expected, f"{lang}:{key}"


def test_no_empty_texts(tr):
    for lang in LANGUAGES:
        for key in tr.keys(lang):
            assert tr.raw(lang, key).strip(), f"{lang}:{key} bo'sh"


def test_keys_used_in_code_exist(tr):
    keys = tr.keys("uz")
    prefixes = {k.split(".")[0] for k in keys}
    missing = []
    for entry in CODE_DIRS:
        path = ROOT / entry
        files = [path] if path.is_file() else path.rglob("*.py")
        for file in files:
            source = file.read_text(encoding="utf-8")
            for match in KEY_LITERAL.finditer(source):
                literal = match.group(1)
                before = source[max(0, match.start() - 12) : match.start()]
                if before.endswith(("name=", "ForeignKey(")):
                    continue  # router nomi yoki jadval bog'lanishi, tarjima kaliti emas
                if literal.split(".")[0] in prefixes and literal not in keys:
                    missing.append(f"{file.relative_to(ROOT)}: {literal}")
    assert not missing, "\n".join(missing)


def test_get_formats_and_falls_back(tr):
    assert tr.get("ru", "commands.help") == "Помощь"
    assert tr.get("xx", "commands.help") == tr.get("uz", "commands.help")
    assert tr.get("uz", "no.such.key") == "no.such.key"


def test_bind_and_variants(tr):
    t = tr.bind("en")
    assert t.lang == "en"
    assert t("commands.start") == "Start the bot"
    assert tr.bind("xx").lang == "uz"
    assert len(tr.variants("commands.help")) == 3


@pytest.mark.parametrize(
    "code, expected", [("ru", "ru"), ("ru-RU", "ru"), ("en-US", "en"), ("uz", "uz"), ("kk", "uz"), (None, "uz")]
)
def test_guess_language(code, expected):
    assert guess_language(code) == expected
