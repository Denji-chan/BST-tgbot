"""Oddiy i18n: matnlar `locales/<til>.json` fayllarida, `{nom}` o'zgaruvchilari bilan.

aiogram'ga bog'liq emas. Kalit topilmasa, avval standart til (uz), keyin kalitning o'zi qaytadi.
"""

import json
from pathlib import Path

LANGUAGES: tuple[str, ...] = ("uz", "ru", "en")
DEFAULT_LANGUAGE = "uz"
LOCALES_DIR = Path(__file__).resolve().parents[2] / "locales"


def guess_language(telegram_code: str | None) -> str:
    code = (telegram_code or "").lower()
    if code.startswith("ru"):
        return "ru"
    if code.startswith("en"):
        return "en"
    return DEFAULT_LANGUAGE


class Translate:
    """Bitta tilga bog'langan tarjimon: `t("btn.profile")`."""

    def __init__(self, translator: "Translator", lang: str) -> None:
        self._translator = translator
        self.lang = lang

    def __call__(self, key: str, **kwargs) -> str:
        return self._translator.get(self.lang, key, **kwargs)


class Translator:
    def __init__(self, locales_dir: Path = LOCALES_DIR, default: str = DEFAULT_LANGUAGE) -> None:
        self.default = default
        self._data: dict[str, dict[str, str]] = {}
        for lang in LANGUAGES:
            path = locales_dir / f"{lang}.json"
            with path.open(encoding="utf-8") as f:
                self._data[lang] = json.load(f)

    def raw(self, lang: str, key: str) -> str:
        text = self._data.get(lang, {}).get(key)
        if text is None:
            text = self._data[self.default].get(key, key)
        return text

    def get(self, lang: str, key: str, **kwargs) -> str:
        text = self.raw(lang, key)
        return text.format(**kwargs) if kwargs else text

    def bind(self, lang: str) -> Translate:
        return Translate(self, lang if lang in LANGUAGES else self.default)

    def variants(self, key: str) -> set[str]:
        """Kalitning barcha tillardagi qiymatlari (reply tugmalarni ushlash uchun)."""
        return {self.raw(lang, key) for lang in LANGUAGES}

    def keys(self, lang: str) -> set[str]:
        return set(self._data[lang])


i18n = Translator()
