"""Labeled test wants on the live site, so the iPhone app has a feed to swipe (#214).

`flask --app app demo seed` adds them and `flask --app app demo clear` removes every trace.
Demo accounts can't log in, and their emails use a reserved domain that never delivers.
"""

import secrets
from datetime import timedelta

import click
from flask import Flask
from flask.cli import AppGroup
from sqlalchemy import delete, func, select
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models import Post, PostKind, Report, User, utcnow
from app.moderation import is_flagged

DEMO_EMAIL_DOMAIN = "@demo.yearnly.invalid"
DEMO_LABEL = "Test post for trying out Yearnly. Don't send real money."
DEMO_POSTERS = [
    ("demo_maria", "Sarasota", "FL"),
    ("demo_tom", "Tampa", "FL"),
    ("demo_kayla", "Fort Myers", "FL"),
    ("demo_jordan", "Milwaukee", "WI"),
    ("demo_priya", "Austin", "TX"),
    ("demo_lee", "Denver", "CO"),
    ("demo_ana", "Columbus", "OH"),
    ("demo_nina", "Portland", "OR"),
]
DEMO_WANTS = [
    ("Concert tickets for my sister", "Her favorite band plays here in March.", 12_000),
    ("New running shoes", "Training for my first 5K and my shoes are done.", 9_000),
    ("Art supplies", "Getting back into painting this winter.", 6_000),
    ("Dinosaur birthday cake", "My son turns 7 and loves dinosaurs.", 4_500),
    ("Guitar strings and a tuner", "Teaching myself guitar from videos.", 3_500),
    ("A board game for game night", "Our group has played the same one for a year.", 5_000),
    ("Tickets to the aquarium", "Taking my niece for her first visit.", 7_000),
    ("Noise-canceling headphones", "My roommate works nights and I study days.", 15_000),
    ("Yarn for a winter blanket", "Knitting one for my grandma.", 4_000),
    ("A good chef's knife", "Learning to cook real meals this year.", 8_000),
    ("Bike tune-up", "The brakes squeak and the chain slips.", 6_500),
    ("Movie night for the family", "Tickets and popcorn for four.", 6_000),
    ("Plants for my first apartment", "It's very beige in here.", 3_000),
    ("Camping gear for a weekend trip", "First trip with friends since college.", 20_000),
    ("Swim lessons for my daughter", "She wants to join her friends at the pool.", 18_000),
    ("Sketchbook and pens", "Drawing on my lunch break.", 2_500),
]


class DemoError(Exception):
    pass


def demo_users() -> list[User]:
    return list(db.session.scalars(select(User).where(User.email.endswith(DEMO_EMAIL_DOMAIN))))


def seed_demo() -> int:
    if demo_users():
        raise DemoError("demo wants are already there; run `flask demo clear` first")
    now = utcnow()
    users = []
    for username, city, state in DEMO_POSTERS:
        if db.session.scalar(select(func.count()).where(User.username == username)):
            raise DemoError(f"the username {username} is taken by a real account")
        users.append(
            User(
                username=username,
                email=f"{username}{DEMO_EMAIL_DOMAIN}",
                # A random password nobody knows, so nobody can log in as a demo poster.
                password_hash=generate_password_hash(secrets.token_urlsafe(32)),
                email_verified_at=now,
                city=city,
                state=state,
                venmo_handle=f"@{username.replace('_', '-')}-not-real",
                rules_accepted_at=now,
                adult_attested_at=now,
                created_at=now - timedelta(days=30),
            )
        )
    posts = [
        Post(
            # Two per poster keeps every demo account within the 2-open-posts rule.
            user=users[i // 2],
            kind=PostKind.WANT,
            title=title,
            body=f"{body}\n\n{DEMO_LABEL}",
            goal_cents=goal,
            created_at=now - timedelta(hours=3 * i + 1),
        )
        for i, (title, body, goal) in enumerate(DEMO_WANTS)
    ]
    if any(is_flagged(p.title, p.body) for p in posts):
        raise DemoError("a demo want trips the fundraising filter")
    db.session.add_all([*users, *posts])
    db.session.commit()
    return len(posts)


def clear_demo() -> int:
    users = demo_users()
    ids = [u.id for u in users]
    if not ids:
        return 0
    posts = list(db.session.scalars(select(Post).where(Post.user_id.in_(ids))))
    for post in posts:
        db.session.delete(post)  # gifts, reactions, and reports on it go with it
    db.session.execute(delete(Report).where(Report.user_id.in_(ids)))
    db.session.flush()
    for user in users:
        db.session.delete(user)
    db.session.commit()
    return len(posts)


demo_cli = AppGroup("demo", help="Labeled test wants on the live site.")


@demo_cli.command("seed")
def seed_command() -> None:
    """Add the labeled test wants."""
    try:
        count = seed_demo()
    except DemoError as err:
        raise click.ClickException(str(err)) from err
    click.echo(f"Added {count} test wants from {len(DEMO_POSTERS)} demo accounts.")


@demo_cli.command("clear")
def clear_command() -> None:
    """Remove the demo accounts, their wants, and every gift on them."""
    click.echo(f"Removed {clear_demo()} test wants and their demo accounts.")


def register(app: Flask) -> None:
    app.cli.add_command(demo_cli)
