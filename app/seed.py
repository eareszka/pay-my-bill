import random
from datetime import timedelta

import click
from flask import Flask, current_app
from sqlalchemy import func, select
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import (
    Donation,
    DonationStatus,
    PaymentMethod,
    Post,
    PostKind,
    PostStatus,
    User,
    utcnow,
)

SEED_PASSWORD = "password123"  # noqa: S105 - dev-only fake accounts

USERNAMES = [
    "maria_g",
    "dev_tom",
    "kayla.r",
    "jordan88",
    "sam_helps",
    "priya_k",
    "lee_w",
    "ana.b",
    "chris_p",
    "nina_s",
]
REGIONS = [
    ("Sarasota", "FL"),
    ("Bradenton", "FL"),
    ("Tampa", "FL"),
    ("Fort Myers", "FL"),
    ("Milwaukee", "WI"),
    ("Madison", "WI"),
    ("Austin", "TX"),
    ("Denver", "CO"),
    ("Columbus", "OH"),
    ("Portland", "OR"),
]
NEEDS = [
    ("Short on rent this month", "Hours got cut at work and I'm about $300 short."),
    ("Electric bill help", "AC broke in August and the bill came in high."),
    ("Car battery died", "Need a new battery to get to work this week."),
    ("Groceries until payday", "Two kids and payday is Friday. Anything helps."),
    ("Textbook for class", "Need the required textbook for my stats class."),
    ("Vet visit for my dog", "My dog ate something bad and needs a checkup."),
    ("Phone bill past due", "Need my phone working for job interviews."),
]
WANTS = [
    ("Want the new Zelda", "Been saving but would love some help getting there."),
    ("Concert tickets", "My favorite band is finally touring near me."),
    ("New running shoes", "Training for my first 5K and my shoes are done."),
    ("Art supplies", "Trying to get back into painting this winter."),
    ("Birthday cake for my son", "He's turning 7 and loves dinosaurs."),
    ("Guitar strings and a tuner", "Teaching myself guitar."),
    ("Board game for game night", "Our group has played the same game for a year."),
]
FLAGGED = ("Help launch my startup", "Looking for seed money for my small business LLC.")
SECONDARY_STATUSES = [PostStatus.FUNDED, PostStatus.CLOSED, PostStatus.PENDING_REVIEW]


# Confirmed amounts stay under the smallest seeded goal ($20) so open posts stay open.
SEED_GIFTS = [
    (500, DonationStatus.CONFIRMED),
    (1000, DonationStatus.PENDING),
    (300, DonationStatus.DISPUTED),
]


class SeedError(Exception):
    pass


def seed_donations(users: list[User], posts: list[Post]) -> list[Donation]:
    now = utcnow()
    open_posts = [p for p in posts if p.status is PostStatus.OPEN]
    donations = []
    for i, post in enumerate(open_posts):
        donor = next(u for u in users[i + 1 :] + users if u is not post.user)
        amount, status = SEED_GIFTS[i % len(SEED_GIFTS)]
        donations.append(
            Donation(
                post=post,
                donor=donor,
                amount_cents=amount,
                method=PaymentMethod.VENMO,
                status=status,
                created_at=now - timedelta(days=1),
                resolved_at=None if status is DonationStatus.PENDING else now,
            )
        )
    return donations


def seed(n_users: int = 10, posts_per_user: int = 2, rng_seed: int = 42) -> tuple[int, int]:
    if not current_app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
        raise SeedError("seed data is for local SQLite dev databases only")
    if db.session.scalar(select(func.count()).select_from(User)):
        raise SeedError("database already has users; refusing to seed twice")

    rng = random.Random(rng_seed)  # noqa: S311 - fake data, not security
    password_hash = generate_password_hash(SEED_PASSWORD)
    now = utcnow()
    users: list[User] = []
    posts: list[Post] = []
    for i in range(n_users):
        username = USERNAMES[i % len(USERNAMES)] + (str(i) if i >= len(USERNAMES) else "")
        city, state = REGIONS[i % len(REGIONS)]
        user = User(
            username=username,
            email=f"{username}@example.com",
            password_hash=password_hash,
            email_verified_at=now,
            city=city,
            state=state,
            cashapp_handle="$" + "".join(c for c in username if c.isalnum())
            if i % 3 != 2
            else None,
            venmo_handle=f"@{username}" if i % 3 != 0 else None,
            paypal_handle=username if i % 3 == 2 else None,
            rules_accepted_at=now,
            is_admin=i == 0,
            created_at=now - timedelta(days=30 - i),
        )
        users.append(user)
        for j in range(posts_per_user):
            # At most one open post per user keeps the seed within the 2-open-posts rule.
            status = PostStatus.OPEN if j == 0 else SECONDARY_STATUSES[(i + j) % 3]
            if status is PostStatus.PENDING_REVIEW:
                kind, (title, body) = PostKind.WANT, FLAGGED
            elif rng.random() < 0.5:
                kind, (title, body) = PostKind.NEED, rng.choice(NEEDS)
            else:
                kind, (title, body) = PostKind.WANT, rng.choice(WANTS)
            posts.append(
                Post(
                    user=user,
                    kind=kind,
                    title=title,
                    body=body,
                    goal_cents=rng.randrange(20, 1001) * 100,
                    status=status,
                    created_at=now - timedelta(hours=rng.randrange(1, 24 * 14)),
                )
            )
    db.session.add_all([*users, *posts, *seed_donations(users, posts)])
    db.session.commit()
    return len(users), len(posts)


@click.command("seed")
def seed_command() -> None:
    """Fill the local dev database with fake users and posts."""
    try:
        n_users, n_posts = seed()
    except SeedError as err:
        raise click.ClickException(str(err)) from err
    click.echo(f"Seeded {n_users} users and {n_posts} posts (password: {SEED_PASSWORD}).")


def register(app: Flask) -> None:
    app.cli.add_command(seed_command)
