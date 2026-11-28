"""Xarid matnlari: admin uchun ko'rib chiqish va mijoz uchun chek. Barcha so'zlar locales'dan."""

from collections.abc import Callable

from services.cashback import PurchaseCalculation
from services.items import Item
from utils.misc.formatting import esc, money

Translate = Callable[..., str]


def items_text(t: Translate, items: list[Item]) -> str:
    lines = []
    for item in items:
        if item.quantity == 1:
            lines.append(t("receipt.item_single", name=esc(item.name), amount=money(item.amount)))
        else:
            lines.append(
                t(
                    "receipt.item_multi",
                    name=esc(item.name),
                    quantity=item.quantity,
                    price=money(item.price),
                    amount=money(item.amount),
                )
            )
    return "\n".join(lines)


def _amount_lines(t: Translate, calc: PurchaseCalculation) -> str:
    lines = [t("receipt.subtotal", amount=money(calc.subtotal))]
    if calc.birthday_discount:
        lines.append(t("receipt.birthday_discount", amount=money(calc.birthday_discount)))
        lines.append(t("receipt.total", amount=money(calc.total)))
    lines.append(t("receipt.cashback_used", amount=money(calc.cashback_used)))
    lines.append(t("receipt.paid", amount=money(calc.paid)))
    lines.append(t("receipt.cashback_earned", amount=money(calc.cashback_earned)))
    return "\n".join(lines)


def admin_preview(
    t: Translate, customer_name: str, customer_id: int, items: list[Item], calc: PurchaseCalculation
) -> str:
    return t(
        "purchase.preview",
        name=esc(customer_name),
        customer_id=customer_id,
        items=items_text(t, items),
        amounts=_amount_lines(t, calc),
    )


def customer_receipt(t: Translate, items: list[Item], calc: PurchaseCalculation, balance: int) -> str:
    return t(
        "receipt.customer",
        items=items_text(t, items),
        amounts=_amount_lines(t, calc),
        balance=money(balance),
    )
