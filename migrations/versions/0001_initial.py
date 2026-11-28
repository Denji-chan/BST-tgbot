"""Boshlang'ich sxema: barcha jadvallar

Revision ID: 0001_initial
Revises:
Create Date: 2026-11-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("first_name", sa.String(64), nullable=False),
        sa.Column("last_name", sa.String(64), nullable=False),
        sa.Column("phone", sa.String(20), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("language", sa.String(2), nullable=False),
        sa.Column("referred_by_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_blocked", sa.Boolean(), nullable=False),
        sa.Column("last_purchase_at", TS, nullable=True),
        sa.Column("registered_at", TS, nullable=False),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"], unique=True)
    op.create_index("ix_users_phone", "users", ["phone"], unique=True)

    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("full_name", sa.String(128), nullable=False),
        sa.Column("language", sa.String(2), nullable=False),
        sa.Column("added_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_admins_telegram_id", "admins", ["telegram_id"], unique=True)

    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("admin_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("subtotal", sa.BigInteger(), nullable=False),
        sa.Column("birthday_discount", sa.BigInteger(), nullable=False),
        sa.Column("total", sa.BigInteger(), nullable=False),
        sa.Column("cashback_used", sa.BigInteger(), nullable=False),
        sa.Column("paid", sa.BigInteger(), nullable=False),
        sa.Column("cashback_earned", sa.BigInteger(), nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_purchases_user_id", "purchases", ["user_id"])
    op.create_index("ix_purchases_created_at", "purchases", ["created_at"])

    op.create_table(
        "purchase_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("purchase_id", sa.Integer(), sa.ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("price", sa.BigInteger(), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
    )
    op.create_index("ix_purchase_items_purchase_id", "purchase_items", ["purchase_id"])

    op.create_table(
        "cashback_transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(16), nullable=False),
        sa.Column("amount", sa.BigInteger(), nullable=False),
        sa.Column("remaining", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", TS, nullable=True),
        sa.Column("purchase_id", sa.Integer(), sa.ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_cashback_transactions_user_id", "cashback_transactions", ["user_id"])
    op.create_index("ix_cashback_transactions_created_at", "cashback_transactions", ["created_at"])
    op.create_index("ix_cashback_active_lots", "cashback_transactions", ["user_id", "remaining", "expires_at"])

    op.create_table(
        "referrals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("referrer_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("referred_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("purchase_id", sa.Integer(), sa.ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", TS, nullable=False),
        sa.Column("resolved_at", TS, nullable=True),
        sa.UniqueConstraint("referred_id"),
    )
    op.create_index("ix_referrals_referrer_id", "referrals", ["referrer_id"])

    op.create_table(
        "birthday_discount_uses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("purchase_id", sa.Integer(), sa.ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", TS, nullable=False),
        sa.UniqueConstraint("user_id", "year", name="uq_birthday_user_year"),
    )

    op.create_table(
        "message_templates",
        sa.Column("key", sa.String(32), primary_key=True),
        sa.Column("language", sa.String(2), primary_key=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("updated_by", sa.BigInteger(), nullable=True),
        sa.Column("updated_at", TS, nullable=False),
    )

    op.create_table(
        "notification_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("sent_at", TS, nullable=False),
        sa.UniqueConstraint("kind", "key", name="uq_notification_kind_key"),
    )

    op.create_table(
        "support_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("answered_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", TS, nullable=False),
        sa.Column("answered_at", TS, nullable=True),
    )
    op.create_index("ix_support_messages_user_id", "support_messages", ["user_id"])

    op.create_table(
        "broadcasts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("admin_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("content_type", sa.String(16), nullable=False),
        sa.Column("source_chat_id", sa.BigInteger(), nullable=False),
        sa.Column("source_message_id", sa.Integer(), nullable=False),
        sa.Column("total", sa.Integer(), nullable=False),
        sa.Column("delivered", sa.Integer(), nullable=False),
        sa.Column("failed", sa.Integer(), nullable=False),
        sa.Column("blocked", sa.Integer(), nullable=False),
        sa.Column("created_at", TS, nullable=False),
        sa.Column("finished_at", TS, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("broadcasts")
    op.drop_index("ix_support_messages_user_id", table_name="support_messages")
    op.drop_table("support_messages")
    op.drop_table("notification_logs")
    op.drop_table("message_templates")
    op.drop_table("birthday_discount_uses")
    op.drop_index("ix_referrals_referrer_id", table_name="referrals")
    op.drop_table("referrals")
    op.drop_index("ix_cashback_active_lots", table_name="cashback_transactions")
    op.drop_index("ix_cashback_transactions_created_at", table_name="cashback_transactions")
    op.drop_index("ix_cashback_transactions_user_id", table_name="cashback_transactions")
    op.drop_table("cashback_transactions")
    op.drop_index("ix_purchase_items_purchase_id", table_name="purchase_items")
    op.drop_table("purchase_items")
    op.drop_index("ix_purchases_created_at", table_name="purchases")
    op.drop_index("ix_purchases_user_id", table_name="purchases")
    op.drop_table("purchases")
    op.drop_index("ix_admins_telegram_id", table_name="admins")
    op.drop_table("admins")
    op.drop_index("ix_users_phone", table_name="users")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
