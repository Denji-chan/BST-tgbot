"""Admin tahrirlaydigan avtomatik matnlar: kalitlar, ruxsat etilgan o'zgaruvchilar, tekshirish."""

import string

# kalit -> matnda ishlatish mumkin bo'lgan o'zgaruvchilar
TEMPLATE_FIELDS: dict[str, frozenset[str]] = {
    "inactive_60": frozenset({"name", "balance"}),
    "inactive_90": frozenset({"name", "balance"}),
    "inactive_120": frozenset({"name", "balance"}),
    "payment_reminder": frozenset({"name"}),
}
TEMPLATE_KEYS: tuple[str, ...] = tuple(TEMPLATE_FIELDS)
MAX_LENGTH = 3500


class TemplateError(ValueError):
    def __init__(self, reason: str, fields: list[str] | None = None) -> None:
        self.reason = reason  # "format" | "unknown_fields" | "too_long" | "empty"
        self.fields = fields or []
        super().__init__(reason)


def default_key(key: str) -> str:
    """locales'dagi standart matn kaliti."""
    return f"template.{key}"


def validate(key: str, text: str) -> None:
    if not text or not text.strip():
        raise TemplateError("empty")
    if len(text) > MAX_LENGTH:
        raise TemplateError("too_long")
    try:
        names = [name for _, name, spec, conv in string.Formatter().parse(text) if name is not None]
    except ValueError as err:
        raise TemplateError("format") from err
    if any(not n for n in names):  # "{}" kabi nomsiz o'zgaruvchi
        raise TemplateError("format")
    unknown = sorted({n for n in names if n not in TEMPLATE_FIELDS[key]})
    if unknown:
        raise TemplateError("unknown_fields", unknown)


def render(text: str, **values) -> str:
    """Tekshirilgan matnni to'ldiradi. Kutilmagan xato bo'lsa, matnni o'zgarishsiz qaytaradi."""
    try:
        return text.format(**values)
    except (KeyError, IndexError, ValueError):
        return text
