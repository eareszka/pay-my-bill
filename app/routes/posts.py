import smtplib
from datetime import timedelta

import click
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user
from sqlalchemy import func, or_, select
from sqlalchemy.orm import joinedload
from werkzeug.wrappers import Response

from app import format_date, photos, stripe_pay
from app.accounts import delete_post
from app.auth import login_required, verified_required
from app.extensions import db
from app.forms import GiftForm, PostForm, ResultsUpdateForm
from app.mail import send_email, send_later
from app.models import (
    LATE_GIFT_HOURS,
    MAX_DB_INT,
    MAX_OPEN_POSTS,
    MIN_CARD_GIFT_CENTS,
    PUBLIC_STATUSES,
    UPDATE_DUE_DAYS,
    Post,
    PostKind,
    PostStatus,
    Reaction,
    ReactionKind,
    User,
    open_posts,
    posts_with_confirmed_gifts,
    utcnow,
)
from app.moderation import is_flagged
from app.money import format_cents
from app.payment_links import pay_options
from app.routes.admin import notify_admins

bp = Blueprint("posts", __name__, url_prefix="/posts")

DUPLICATE_POST_SECONDS = 60


def active_post_count(user: User) -> int:
    count = db.session.scalar(
        select(func.count())
        .select_from(Post)
        .where(
            Post.user_id == user.id,
            or_(open_posts(), Post.status == PostStatus.PENDING_REVIEW),
        )
    )
    return count or 0


def just_posted(user: User, title: str | None, body: str | None) -> Post | None:
    # The same post again within moments is a double tap or a resubmit, not a new ask.
    return db.session.scalars(
        select(Post).where(
            Post.user_id == user.id,
            Post.title == title,
            Post.body == body,
            Post.created_at > utcnow() - timedelta(seconds=DUPLICATE_POST_SECONDS),
        )
    ).first()


def posts_owing_update(user: User | None = None) -> list[Post]:
    query = select(Post).where(
        Post.update_posted_at.is_(None),
        posts_with_confirmed_gifts(),
    )
    if user:
        query = query.where(Post.user_id == user.id)
    query = query.options(joinedload(Post.user)).order_by(Post.id)
    return [post for post in db.session.scalars(query) if post.owes_update]


def overdue_post(user: User) -> Post | None:
    # Worked out from dates when asked, so a missed job can't block or unblock anyone.
    return next((post for post in posts_owing_update(user) if post.update_overdue), None)


@bp.route("/new", methods=["GET", "POST"])
@verified_required
def new() -> str | Response | tuple[str, int]:
    user: User = current_user
    overdue = overdue_post(user)
    if overdue:
        flash("You have an overdue results update. Post it before creating a new post.", "info")
        return redirect(url_for("posts.show", post_id=overdue.id, _anchor="update"))
    if not user.can_be_paid:
        flash(
            "Connect Stripe or add a Cash App, Venmo, or PayPal handle so people can pay you.",
            "info",
        )
        return redirect(url_for("profile.edit"))
    form = PostForm(require_rules=user.rules_accepted_at is None)
    if form.is_submitted():
        # Lock the user row so parallel submits can't all pass the open-post limit.
        db.session.execute(select(User.id).where(User.id == user.id).with_for_update())
    at_limit = active_post_count(user) >= MAX_OPEN_POSTS
    if not at_limit and form.validate_on_submit():
        repeat = just_posted(user, form.title.data, form.body.data)
        if repeat:
            db.session.rollback()
            return redirect(url_for("posts.show", post_id=repeat.id))
        if form.require_rules:
            user.rules_accepted_at = utcnow()
        flagged = is_flagged(form.title.data, form.body.data)
        photo_key = None
        if form.photo_data:
            try:
                photo_key = photos.save(form.photo_data)
            except Exception:  # storage can fail in many ways; the poster can try again
                current_app.logger.exception("Couldn't store a post photo")
                db.session.rollback()
                form.photo.errors = ["We couldn't save that photo. Try again, or post without it."]
                return render_template("posts/new.html", form=form, at_limit=at_limit), 503
        post = Post(
            user=user,
            kind=PostKind(form.kind.data),
            title=form.title.data,
            body=form.body.data,
            goal_cents=form.goal_cents,
            status=PostStatus.PENDING_REVIEW if flagged else PostStatus.OPEN,
            photo_key=photo_key,
        )
        db.session.add(post)
        db.session.commit()
        if flagged:
            notify_admins(
                "A post is waiting for review",
                f"{user.username}'s post “{post.title}” matched the fundraising word list.",
            )
            flash("Thanks! Your post will show in the feed after a quick review.", "info")
        else:
            flash("Your post is live.", "success")
        return redirect(url_for("posts.show", post_id=post.id))
    db.session.rollback()
    page = render_template("posts/new.html", form=form, at_limit=at_limit)
    return page, 409 if at_limit and form.is_submitted() else 200


def can_view(post: Post) -> bool:
    if post.status in PUBLIC_STATUSES:
        return True
    viewer: User | None = current_user if current_user.is_authenticated else None
    return viewer is not None and (viewer.id == post.user_id or viewer.is_admin)


@bp.get("/<int:post_id>")
def show(post_id: int) -> str:
    post = (
        db.session.get(Post, post_id, options=[joinedload(Post.user)])
        if post_id <= MAX_DB_INT
        else None
    )
    if post is None or not can_view(post):
        abort(404)
    return render_post(post, GiftForm.for_post(post))


def gave_to(post: Post, user: User) -> bool:
    return any(gift.donor_id == user.id for gift in post.confirmed_gifts)


def reaction_view(post: Post) -> dict[str, object]:
    viewer: User | None = current_user if current_user.is_authenticated else None
    counts = {kind: 0 for kind in ReactionKind}
    mine = set()
    for reaction in post.reactions:
        counts[reaction.kind] += 1
        if viewer and reaction.user_id == viewer.id:
            mine.add(reaction.kind)
    can_react = bool(
        viewer
        and viewer.is_verified
        and viewer.id != post.user_id
        and post.status in PUBLIC_STATUSES
    )
    return {
        "counts": counts,
        "mine": mine,
        "can_kudos": can_react,
        "can_judge": bool(viewer and can_react and gave_to(post, viewer)),
        "sees_hmm": viewer is not None and viewer.is_admin,
    }


def chip_in_context(post: Post, form: GiftForm | None = None) -> dict[str, object]:
    # What the Chip in panel needs, on the post page and beside the ticket on the feed.
    return {
        "form": form or GiftForm.for_post(post),
        "pay_options": pay_options(post.user),
        "waiting_gift": (
            post.pending_gift_from(current_user.id) if current_user.is_authenticated else None
        ),
        "late_gift_hours": LATE_GIFT_HOURS,
        "card_ready": stripe_pay.enabled() and post.user.stripe_ready and post.is_open,
        "min_card_gift": MIN_CARD_GIFT_CENTS,
    }


def render_post(
    post: Post,
    form: GiftForm,
    update_form: ResultsUpdateForm | None = None,
    card_error: str | None = None,
) -> str:
    return render_template(
        "posts/show.html",
        post=post,
        card_error=card_error,
        reactions=reaction_view(post) if post.update_body else None,
        update_form=update_form or ResultsUpdateForm(formdata=None),
        **chip_in_context(post, form),
    )


def locked_post(post_id: int) -> Post | None:
    # Lock the post so a gift confirmed or recorded at the same moment can't be lost.
    if post_id > MAX_DB_INT:
        return None
    return db.session.scalars(
        select(Post)
        .where(Post.id == post_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).one_or_none()


def own_post_for_update(post_id: int) -> Post:
    post = locked_post(post_id)
    if post is None or post.user_id != current_user.id:
        db.session.rollback()
        abort(404)
    return post


@bp.post("/<int:post_id>/close")
@login_required
def close(post_id: int) -> Response:
    post = own_post_for_update(post_id)
    if post.is_open:
        post.close()
        db.session.commit()
        flash("Your post is closed.", "success")
    else:
        db.session.rollback()
        flash("That post isn't open anymore.", "info")
    return redirect(url_for("posts.show", post_id=post_id))


def send_update_notice(post: Post, donor: User) -> None:
    if donor.is_deleted:
        return
    link = url_for("posts.show", post_id=post.id, _external=True)
    body = (
        f"Hi {donor.username},\n\n{post.user.username} shared how it went "
        f'on "{post.title}", a post you chipped in on.\n\nRead it here:\n{link}'
    )
    send_later(donor.email, f"{post.user.username} shared how it went", body)


@bp.post("/<int:post_id>/update")
@login_required
def update(post_id: int) -> Response | tuple[str, int]:
    post = own_post_for_update(post_id)
    if not post.owes_update:
        db.session.rollback()
        flash("This post doesn't need an update.", "info")
        return redirect(url_for("posts.show", post_id=post_id))
    form = ResultsUpdateForm()
    if not form.validate_on_submit():
        db.session.rollback()
        return render_post(post, GiftForm.for_post(post), form), 400
    post.update_body = form.note.data
    post.update_posted_at = utcnow()
    db.session.commit()
    for donor in post.confirmed_donors:
        send_update_notice(post, donor)
    flash("Thanks for sharing how it went.", "success")
    return redirect(url_for("posts.show", post_id=post_id))


@bp.post("/<int:post_id>/react/<any(kudos, up, hmm):kind>")
@verified_required
def react(post_id: int, kind: str) -> Response:
    post = locked_post(post_id)
    if post is None or post.status not in PUBLIC_STATUSES or not post.update_body:
        db.session.rollback()
        abort(404)
    user: User = current_user
    chosen = ReactionKind(kind)
    if user.id == post.user_id or (chosen is not ReactionKind.KUDOS and not gave_to(post, user)):
        db.session.rollback()
        abort(403)
    mine = {r.kind: r for r in post.reactions if r.user_id == user.id}
    # The form says what the tap wants, so a double tap can't undo itself.
    wanted = request.form.get("on") == "1"
    if chosen in mine and not wanted:
        post.reactions.remove(mine[chosen])
    elif chosen not in mine and wanted:
        post.reactions.append(Reaction(user_id=user.id, kind=chosen))
        # 👍 and 🤨 replace each other; kudos stands apart.
        other = {ReactionKind.UP: ReactionKind.HMM, ReactionKind.HMM: ReactionKind.UP}.get(chosen)
        if other in mine:
            post.reactions.remove(mine[other])
    db.session.commit()
    return redirect(url_for("posts.show", post_id=post_id, _anchor="update"))


@bp.post("/<int:post_id>/photo/delete")
@login_required
def delete_photo(post_id: int) -> Response:
    post = own_post_for_update(post_id)
    photo_key, post.photo_key = post.photo_key, None
    db.session.commit()
    photos.discard(photo_key)
    flash("Your photo was removed.", "success")
    return redirect(url_for("posts.show", post_id=post.id))


@bp.post("/<int:post_id>/delete")
@login_required
def delete(post_id: int) -> Response:
    photo_key = delete_post(own_post_for_update(post_id))
    db.session.commit()
    photos.discard(photo_key)
    flash("Your post was deleted.", "success")
    return redirect(url_for("main.index"))


@bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@verified_required
def edit(post_id: int) -> str | Response:
    post = own_post_for_update(post_id)
    if not post.can_edit:
        db.session.rollback()
        flash("Only open posts can be edited.", "info")
        return redirect(url_for("posts.show", post_id=post_id))
    form = PostForm(
        data={
            "kind": post.kind.value,
            "title": post.title,
            "body": post.body,
            "goal": format_cents(post.goal_cents),
        }
    )
    del form.accept_rules, form.photo
    if post.story_only:
        del form.kind, form.title, form.goal
    if form.validate_on_submit():
        before = (post.kind, post.title, post.body, post.goal_cents)
        if not post.story_only:
            post.kind = PostKind(form.kind.data)
            post.title = form.title.data
            post.goal_cents = form.goal_cents
        post.body = form.body.data
        if (post.kind, post.title, post.body, post.goal_cents) == before:
            db.session.rollback()
            return redirect(url_for("posts.show", post_id=post_id))
        post.edited_at = utcnow()
        flagged = post.status == PostStatus.OPEN and is_flagged(post.title, post.body)
        if flagged:
            post.status = PostStatus.PENDING_REVIEW
        db.session.commit()
        if flagged:
            notify_admins(
                "An edited post is waiting for review",
                f"{post.user.username}'s post “{post.title}” matched the fundraising word list.",
            )
            flash("Thanks! Your changes will show after a quick review.", "info")
        else:
            flash("Your post was updated.", "success")
        return redirect(url_for("posts.show", post_id=post_id))
    db.session.rollback()
    return render_template("posts/edit.html", form=form, post=post)


REMINDER_DAYS = (3, 6)


def reminders_due(post: Post) -> int:
    """How many of the day 3 and day 6 reminders should have gone out by now."""
    # By calendar date, so a daily run always lands before the last day the email names.
    started = post.update_due_at - timedelta(days=UPDATE_DUE_DAYS)
    return sum(utcnow().date() >= (started + timedelta(days=day)).date() for day in REMINDER_DAYS)


def send_update_reminders() -> int:
    """Email posters whose results update is due soon; returns emails sent."""
    site = current_app.config["APP_URL"].rstrip("/")
    emails = []
    for post in posts_owing_update():
        due = reminders_due(post)
        if post.update_overdue or post.user.is_deleted or due <= post.update_reminders_sent:
            continue
        body = (
            f"Hi {post.user.username},\n\n"
            f'People chipped in on "{post.title}", and they\'d love to hear how it went. '
            f"Your results update is due by {format_date(post.update_last_day)}.\n\n"
            f"Post it here:\n{site}/posts/{post.id}#update\n\n"
            "Until it's up after that date, you won't be able to create new posts."
        )
        emails.append((post.id, post.user.email, body, due))
    # End the read transaction before slow SMTP sends; mark each post as soon as
    # its email goes out so a later failure can't cause a repeat.
    db.session.rollback()
    sent = 0
    for post_id, address, body, due in emails:
        try:
            send_email(address, "Your results update is due soon", body)
        except (smtplib.SMTPException, OSError):
            current_app.logger.exception("Could not send the update reminder for post %s", post_id)
            continue
        reminded = db.session.get_one(Post, post_id)
        reminded.update_reminders_sent = due
        db.session.commit()
        sent += 1
    return sent


@bp.cli.command("remind")
def remind_command() -> None:
    """Email posters on day 3 and day 6 of their results update deadline (run daily)."""
    click.echo(f"Update reminder emails sent: {send_update_reminders()}")
