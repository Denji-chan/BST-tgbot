"""Baza jadvallari. Pul ustunlari BigInteger (butun so'm), vaqtlar UTC.

Async rejimda lazy-load xatolarining oldini olish uchun relationship ishlatilmaydi,
bog'lanishlar faqat ForeignKey orqali, kerakli ma'lumot alohida so'rov bilan olinadi.
"""

from datetime import date, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from utils.db_api.base import Base, UTCDateTime, utcnow


class User(Base):
    """Mijoz. `id` mijozning botdagi ID raqami (kassada aytiladi)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    birth_date: Mapped[date] = mapped_column(Date)
    language: Mapped[str] = mapped_column(String(2), default="uz")
    referred_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    last_purchase_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Admin(Base):
    """Adminlar. Developer ham shu yerda saqlanadi (til uchun), lekin uning huquqi .env'dan."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(128), default="")
    language: Mapped[str] = mapped_column(String(2), default="uz")
    added_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class Purchase(Base):
    """Xarid. subtotal - discount = total; total - cashback_used = paid."""

    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger)
    subtotal: Mapped[int] = mapped_column(BigInteger)  # mahsulotlar yig'indisi
    birthday_discount: Mapped[int] = mapped_column(BigInteger, default=0)
    total: Mapped[int] = mapped_column(BigInteger)  # chegirmadan keyingi xarid summasi
    cashback_used: Mapped[int] = mapped_column(BigInteger, default=0)
    paid: Mapped[int] = mapped_column(BigInteger)  # mijoz haqiqatda to'lagan pul
    cashback_earned: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, index=True)


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(BigInteger)  # bitta mahsulot narxi
    amount: Mapped[int] = mapped_column(BigInteger)  # quantity * price


class CashbackTransaction(Base):
    """Cashback ledger'i. Balans = SUM(amount).

    Musbat yozuvlar (earn, referral) "partiya": `remaining` va `expires_at` faqat ularda.
    Manfiy yozuvlar (spend, expire) partiyalardan FIFO tartibida yechiladi.
    """

    __tablename__ = "cashback_transactions"

    TYPE_EARN = "earn"
    TYPE_REFERRAL = "referral"
    TYPE_SPEND = "spend"
    TYPE_EXPIRE = "expire"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(16))
    amount: Mapped[int] = mapped_column(BigInteger)
    remaining: Mapped[int] = mapped_column(BigInteger, default=0)
    expires_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
    purchase_id: Mapped[int | None] = mapped_column(ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, index=True)

    __table_args__ = (Index("ix_cashback_active_lots", "user_id", "remaining", "expires_at"),)


class Referral(Base):
    __tablename__ = "referrals"

    STATUS_PENDING = "pending"
    STATUS_REWARDED = "rewarded"
    STATUS_REJECTED = "rejected"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    referred_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    status: Mapped[str] = mapped_column(String(16), default=STATUS_PENDING)
    purchase_id: Mapped[int | None] = mapped_column(ForeignKey("purchases.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)


class BirthdayDiscountUse(Base):
    """Tug'ilgan kun chegirmasi yiliga bir marta: (user_id, year) unikal."""

    __tablename__ = "birthday_discount_uses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    year: Mapped[int] = mapped_column(Integer)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    __table_args__ = (UniqueConstraint("user_id", "year", name="uq_birthday_user_year"),)


class MessageTemplate(Base):
    """Admin tahrirlaydigan avtomatik matnlar. Yo'q bo'lsa, locales'dagi standart matn olinadi."""

    __tablename__ = "message_templates"

    key: Mapped[str] = mapped_column(String(32), primary_key=True)
    language: Mapped[str] = mapped_column(String(2), primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    updated_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class NotificationLog(Base):
    """Avtomatik xabar bir marta ketishi uchun: (kind, key) unikal."""

    __tablename__ = "notification_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kind: Mapped[str] = mapped_column(String(32))
    key: Mapped[str] = mapped_column(String(128))
    sent_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    __table_args__ = (UniqueConstraint("kind", "key", name="uq_notification_kind_key"),)


class SupportMessage(Base):
    __tablename__ = "support_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_by: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    answered_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)


class Broadcast(Base):
    __tablename__ = "broadcasts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger)
    content_type: Mapped[str] = mapped_column(String(16))
    source_chat_id: Mapped[int] = mapped_column(BigInteger)
    source_message_id: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer, default=0)
    delivered: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    blocked: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True)
