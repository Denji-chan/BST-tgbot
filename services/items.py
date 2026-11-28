"""Admin yozgan mahsulotlar ro'yxatini o'qish.

Har bir qator: `Nomi - narx` yoki `Nomi - soni x narx`.
Ajratuvchi: `-`, `–`, `—`, `;` yoki `:`. Narxda bo'sh joy bo'lishi mumkin: `150 000`.
Misollar:
    Ko'ylak - 150000
    Shim - 2 x 120 000
    Sumka; 89000 so'm
"""

import re
from dataclasses import dataclass

MAX_ITEMS = 50
MAX_QUANTITY = 100
MAX_PRICE = 100_000_000
MAX_NAME_LENGTH = 128

_LINE_RE = re.compile(
    r"^(?P<name>.+?)\s*[-–—;:]\s*"
    r"(?:(?P<qty>\d{1,3})\s*[xX×хХ*]\s*)?"
    r"(?P<price>\d[\d\s]*?)\s*(?:so['ʻ’]?m|sum|сум|uzs)?\.?$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Item:
    name: str
    quantity: int
    price: int

    @property
    def amount(self) -> int:
        return self.quantity * self.price


@dataclass(frozen=True)
class ParseResult:
    items: list[Item]
    bad_lines: list[int]  # 1 dan boshlanadigan qator raqamlari
    too_many: bool = False

    @property
    def ok(self) -> bool:
        return bool(self.items) and not self.bad_lines and not self.too_many


def parse_line(line: str) -> Item | None:
    match = _LINE_RE.match(line.strip())
    if not match:
        return None
    name = " ".join(match.group("name").split())
    quantity = int(match.group("qty") or 1)
    price = int(re.sub(r"\s", "", match.group("price")))
    if not name or len(name) > MAX_NAME_LENGTH:
        return None
    if not 1 <= quantity <= MAX_QUANTITY or not 1 <= price <= MAX_PRICE:
        return None
    return Item(name=name, quantity=quantity, price=price)


def parse_items(text: str) -> ParseResult:
    items: list[Item] = []
    bad: list[int] = []
    lines = [ln for ln in (text or "").splitlines()]
    numbered = [(i, ln) for i, ln in enumerate(lines, start=1) if ln.strip()]
    if len(numbered) > MAX_ITEMS:
        return ParseResult(items=[], bad_lines=[], too_many=True)
    for number, line in numbered:
        item = parse_line(line)
        if item is None:
            bad.append(number)
        else:
            items.append(item)
    return ParseResult(items=items, bad_lines=bad)


def items_total(items: list[Item]) -> int:
    return sum(item.amount for item in items)
