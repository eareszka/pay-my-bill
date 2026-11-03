from datetime import UTC, datetime, timedelta
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    ColumnElement,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    and_,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import Base

MAX_GOAL_CENTS = 100_000
MAX_OPEN_POSTS = 2
PENDING_GIFT_DAYS = 14
POST_OPEN_DAYS = 30
LATE_GIFT_HOURS = 24
UPDATE_DUE_DAYS = 7
DELETED_EMAIL_DOMAIN = "@deleted.invalid"
DELETED_POST_TITLE = "Deleted post"
DELETED_POST_BODY = "The poster deleted this post."


def utcnow() -> datetime:
    return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
    # SQLite hands back naive datetimes; everything is stored in UTC.
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def gift_expiry_cutoff(now: datetime | None = None) -> datetime:
    # Pending gifts created at or before this moment have expired (T15).
    return (now or utcnow()) - timedelta(days=PENDING_GIFT_DAYS)


def post_open_cutoff(now: datetime | None = None) -> datetime:
    # Open posts created at or before this moment have closed on their own.
    return (now or utcnow()) - timedelta(days=POST_OPEN_DAYS)


class PostKind(StrEnum):
    WANT = "want"
    NEED = "need"


class PostStatus(StrEnum):
    PENDING_REVIEW = "pending_review"
    OPEN = "open"
    FUNDED = "funded"
    CLOSED = "closed"
    REMOVED = "removed"


PUBLIC_STATUSES = (PostStatus.OPEN, PostStatus.FUNDED, PostStatus.CLOSED)


class ReactionKind(StrEnum):
    KUDOS = "kudos"
    UP = "up"
    HMM = "hmm"


class PaymentMethod(StrEnum):
    CASHAPP = "cashapp"
    VENMO = "venmo"
    PAYPAL = "paypal"

    @property
    def label(self) -> str:
        return PAYMENT_LABELS[self]


PAYMENT_LABELS = {
    PaymentMethod.CASHAPP: "Cash App",
    PaymentMethod.VENMO: "Venmo",
    PaymentMethod.PAYPAL: "PayPal",
}


class DonationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DISPUTED = "disputed"

    @property
    def label(self) -> str:
        return DONATION_STATUS_LABELS[self]


DONATION_STATUS_LABELS = {
    DonationStatus.PENDING: "Waiting",
    DonationStatus.CONFIRMED: "Confirmed",
    DonationStatus.DISPUTED: "Not received",
}


def _enum_column(enum: type[StrEnum], name: str) -> Enum:
    return Enum(
        enum,
        name=name,
        native_enum=False,
        create_constraint=True,
        length=20,
        values_callable=lambda e: [m.value for m in e],
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    city: Mapped[str | None] = mapped_column(String(80))
    state: Mapped[str | None] = mapped_column(String(2))
    cashapp_handle: Mapped[str | None] = mapped_column(String(40))
    venmo_handle: Mapped[str | None] = mapped_column(String(40))
    paypal_handle: Mapped[str | None] = mapped_column(String(40))
    rules_accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    adult_attested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_admin: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    posts: Mapped[list["Post"]] = relationship(back_populates="user")

    is_authenticated = True
    is_active = True
    is_anonymous = False

    def get_id(self) -> str:
        return str(self.id)

    @property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def region(self) -> str | None:
        return f"{self.city}, {self.state}" if self.city and self.state else None

    @property
    def is_deleted(self) -> bool:
        return self.email.endswith(DELETED_EMAIL_DOMAIN)

    @property
    def has_payment_handle(self) -> bool:
        return any((self.cashapp_handle, self.venmo_handle, self.paypal_handle))


class Post(Base):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint(f"goal_cents > 0 AND goal_cents <= {MAX_GOAL_CENTS}", name="goal_range"),
        Index("ix_posts_status_created_at", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[PostKind] = mapped_column(_enum_column(PostKind, "post_kind"))
    title: Mapped[str] = mapped_column(String(80))
    body: Mapped[str] = mapped_column(Text)
    goal_cents: Mapped[int]
    status: Mapped[PostStatus] = mapped_column(
        _enum_column(PostStatus, "post_status"), default=PostStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    update_body: Mapped[str | None] = mapped_column(Text)
    update_posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    update_reminders_sent: Mapped[int] = mapped_column(default=0, server_default="0")

    user: Mapped[User] = relationship(back_populates="posts")
    donations: Mapped[list["Donation"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", lazy="selectin"
    )
    reactions: Mapped[list["Reaction"]] = relationship(cascade="all, delete-orphan")

    @property
    def is_deleted(self) -> bool:
        return self.title == DELETED_POST_TITLE and self.body == DELETED_POST_BODY

    @property
    def closes_at(self) -> datetime:
        # When it closed, or when it will close on its own.
        if self.closed_at is not None:
            return as_utc(self.closed_at)
        return as_utc(self.created_at) + timedelta(days=POST_OPEN_DAYS)

    @property
    def is_open(self) -> bool:
        return self.status == PostStatus.OPEN and as_utc(self.created_at) > post_open_cutoff()

    @property
    def last_open_day(self) -> datetime:
        # The last full day it's open; the exact closing time falls on the next UTC date.
        return self.closes_at - timedelta(days=1)

    @property
    def late_gift_until(self) -> datetime:
        # A donor can pay in their app just as a post closes, so they get a day to record it.
        return self.closes_at + timedelta(hours=LATE_GIFT_HOURS)

    @property
    def takes_gifts(self) -> bool:
        if self.is_open:
            return True
        return (
            self.status in PUBLIC_STATUSES
            and not self.is_deleted
            and utcnow() < self.late_gift_until
        )

    def close(self, status: PostStatus = PostStatus.CLOSED) -> None:
        # Keeps the date it first closed: a post past its 30 days closed back then.
        self.closed_at = min(utcnow(), self.closes_at)
        self.status = status

    @property
    def confirmed_gifts(self) -> list["Donation"]:
        return [d for d in self.donations if d.status == DonationStatus.CONFIRMED]

    @property
    def confirmed_donors(self) -> list[User]:
        return list({gift.donor_id: gift.donor for gift in self.confirmed_gifts}.values())

    @property
    def owes_update(self) -> bool:
        # A deleted post still owes one, so deleting can't dodge the follow-through (ADR 0008).
        return (
            self.update_posted_at is None
            and self.status in PUBLIC_STATUSES
            and not self.is_open
            and bool(self.confirmed_gifts)
        )

    @property
    def update_due_at(self) -> datetime:
        # A late confirm moves the deadline, so it can't make the update overdue at once.
        # Once a deadline has passed, only posting the update lifts the block (ADR 0008).
        window = timedelta(days=UPDATE_DUE_DAYS)
        due = None
        for confirmed in sorted(
            as_utc(g.resolved_at or self.closes_at) for g in self.confirmed_gifts
        ):
            if due is None:
                due = max(self.closes_at, confirmed) + window
            elif confirmed < due:
                due = confirmed + window
        return due or self.closes_at + window

    @property
    def update_overdue(self) -> bool:
        return self.owes_update and self.update_due_at <= utcnow()

    @property
    def update_last_day(self) -> datetime:
        return self.update_due_at - timedelta(days=1)

    @property
    def raised_cents(self) -> int:
        # Only recipient-confirmed donations count (ADR 0004).
        return sum(d.amount_cents for d in self.confirmed_gifts)

    @property
    def progress_percent(self) -> int:
        # Any confirmed gift shows some progress, even under 1% of the goal.
        raised = self.raised_cents
        return min(100, max(1, raised * 100 // self.goal_cents)) if raised else 0


def open_posts() -> ColumnElement[bool]:
    # The query form of Post.is_open.
    return and_(Post.status == PostStatus.OPEN, Post.created_at > post_open_cutoff())


class Donation(Base):
    __tablename__ = "donations"
    __table_args__ = (
        CheckConstraint(
            f"amount_cents > 0 AND amount_cents <= {MAX_GOAL_CENTS}", name="amount_range"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    donor_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    amount_cents: Mapped[int]
    method: Mapped[PaymentMethod] = mapped_column(_enum_column(PaymentMethod, "payment_method"))
    status: Mapped[DonationStatus] = mapped_column(
        _enum_column(DonationStatus, "donation_status"), default=DonationStatus.PENDING
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reminded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    post: Mapped[Post] = relationship(back_populates="donations")
    donor: Mapped[User] = relationship()

    @property
    def is_expired(self) -> bool:
        return (
            self.status == DonationStatus.PENDING
            and self.created_at is not None
            and as_utc(self.created_at) <= gift_expiry_cutoff()
        )

    @property
    def status_label(self) -> str:
        return "Expired" if self.is_expired else self.status.label

    @property
    def status_class(self) -> str:
        return "expired" if self.is_expired else self.status.value


class Reaction(Base):
    __tablename__ = "reactions"
    __table_args__ = (UniqueConstraint("post_id", "user_id", "kind", name="one_reaction_each"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[ReactionKind] = mapped_column(_enum_column(ReactionKind, "reaction_kind"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    __table_args__ = (Index("ix_login_attempts_identifier_created_at", "identifier", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    identifier: Mapped[str] = mapped_column(String(254))
    ip: Mapped[str | None] = mapped_column(String(45))
    succeeded: Mapped[bool]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
