from collections.abc import Callable
from typing import Any

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    Field,
    PasswordField,
    RadioField,
    SelectChoice,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    Regexp,
    ValidationError,
)

from app.models import MAX_GOAL_CENTS, Post, PostKind
from app.money import format_cents, parse_dollars
from app.payment_links import normalize_cashapp, normalize_paypal, normalize_venmo, pay_options
from app.regions import US_STATES


def _lower(value: str | None) -> str | None:
    return value.strip().lower() if value else value


def _strip_to_none(value: str | None) -> str | None:
    return (value or "").strip() or None


class SignupForm(FlaskForm):
    username = StringField(
        "Username",
        filters=[_lower],
        validators=[
            DataRequired(message="Choose a username."),
            Length(min=3, max=30, message="Usernames are 3 to 30 characters."),
            Regexp(r"^[a-z0-9_.]+$", message="Use letters, numbers, dots, and underscores."),
        ],
    )
    email = EmailField(
        "Email",
        filters=[_lower],
        validators=[
            DataRequired(message="Enter your email."),
            Email(check_deliverability=False, message="Enter a valid email address."),
            Length(max=254, message="Emails are up to 254 characters."),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Choose a password."),
            Length(min=8, max=128, message="Passwords are 8 to 128 characters."),
        ],
    )
    confirm = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(message="Type your password again."),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    adult = BooleanField(
        "I'm 18 or older",
        validators=[DataRequired(message="You need to be 18 or older to join.")],
    )


class LoginForm(FlaskForm):
    identifier = StringField(
        "Username or email",
        filters=[_lower],
        validators=[DataRequired(message="Enter your username or email."), Length(max=254)],
    )
    password = PasswordField(
        "Password", validators=[DataRequired(message="Enter your password."), Length(max=128)]
    )


def _handle_field(label: str, normalize: Callable[[str | None], str | None], hint: str) -> Any:
    def check(form: FlaskForm, field: Field) -> None:
        try:
            field.data = normalize(field.data)
        except ValueError:
            raise ValidationError(hint) from None

    return StringField(
        label, filters=[_strip_to_none], validators=[Optional(), check], description=hint
    )


class ProfileForm(FlaskForm):
    city = StringField(
        "City",
        filters=[_strip_to_none],
        validators=[Length(max=80, message="City names are up to 80 characters.")],
    )
    state = SelectField(
        "State",
        choices=[SelectChoice("", "Choose a state")]
        + [SelectChoice(code, name) for code, name in US_STATES.items()],
        validate_choice=True,
    )
    cashapp_handle = _handle_field(
        "Cash App",
        normalize_cashapp,
        "Your $cashtag: up to 20 letters or numbers, with at least one letter.",
    )
    venmo_handle = _handle_field(
        "Venmo", normalize_venmo, "Your @username: 5 to 30 letters, numbers, - or _."
    )
    paypal_handle = _handle_field(
        "PayPal", normalize_paypal, "Your paypal.me name: up to 20 letters or numbers."
    )

    def validate_state(self, field: Field) -> None:
        if bool(self.city.data) != bool(field.data):
            raise ValidationError("Enter both a city and a state, or neither.")


class PostForm(FlaskForm):
    kind = RadioField(
        "This is a",
        choices=[
            SelectChoice(PostKind.NEED.value, "Need"),
            SelectChoice(PostKind.WANT.value, "Want"),
        ],
        validators=[DataRequired(message="Choose Need or Want.")],
    )
    title = StringField(
        "Title",
        filters=[_strip_to_none],
        validators=[
            DataRequired(message="Give your post a title."),
            Length(min=3, max=80, message="Titles are 3 to 80 characters."),
        ],
    )
    body = TextAreaField(
        "Your story",
        filters=[_strip_to_none],
        validators=[
            DataRequired(message="Tell people what it's for."),
            Length(min=10, max=2000, message="Your story needs 10 to 2,000 characters."),
        ],
        description="What it's for and why. Be honest; people can see your history.",
    )
    goal = StringField(
        "Goal amount",
        filters=[_strip_to_none],
        validators=[DataRequired(message="Enter a goal amount.")],
        description=f"Up to {format_cents(MAX_GOAL_CENTS)}.",
    )
    accept_rules = BooleanField("I agree to the Community Rules")

    goal_cents = 0

    def __init__(self, *args: Any, require_rules: bool = False, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.require_rules = require_rules

    def validate_accept_rules(self, field: Field) -> None:
        if self.require_rules and not field.data:
            raise ValidationError("You need to agree to the Community Rules to post.")

    def validate_goal(self, field: Field) -> None:
        try:
            cents = parse_dollars(field.data)
        except ValueError:
            raise ValidationError("Enter a dollar amount, like 120 or 45.50.") from None
        if cents <= 0:
            raise ValidationError("The goal has to be more than $0.")
        if cents > MAX_GOAL_CENTS:
            raise ValidationError(
                f"Goals are capped at {format_cents(MAX_GOAL_CENTS)}. Pay My Bill is for "
                "everyday wants and needs."
            )
        self.goal_cents = cents


class GiftForm(FlaskForm):
    amount = StringField(
        "Amount", filters=[_strip_to_none], validators=[DataRequired(message="Enter an amount.")]
    )
    method = SelectField(
        "via", validators=[DataRequired(message="Pick the app you used.")], validate_choice=True
    )

    amount_cents = 0
    max_cents = MAX_GOAL_CENTS

    def validate_amount(self, field: Field) -> None:
        try:
            cents = parse_dollars(field.data)
        except ValueError:
            raise ValidationError("Enter an amount like 20 or 12.50.") from None
        if cents <= 0:
            raise ValidationError("The amount has to be more than $0.")
        if cents > self.max_cents:
            raise ValidationError(
                f"Gifts to this post can be up to {format_cents(self.max_cents)}."
            )
        self.amount_cents = cents

    @classmethod
    def for_post(cls, post: Post) -> "GiftForm":
        form = cls()
        form.method.choices = [SelectChoice("", "Choose app")] + [
            SelectChoice(o.method.value, o.label) for o in pay_options(post.user)
        ]
        form.max_cents = post.goal_cents
        return form


class DeleteAccountForm(FlaskForm):
    password = PasswordField(
        "Your password", validators=[DataRequired(message="Enter your password."), Length(max=128)]
    )


class EmptyForm(FlaskForm):
    pass
