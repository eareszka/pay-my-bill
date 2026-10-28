from collections.abc import Callable
from typing import Any

from flask_wtf import FlaskForm
from wtforms import EmailField, Field, PasswordField, SelectChoice, SelectField, StringField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional,
    Regexp,
    ValidationError,
)

from app.payment_links import normalize_cashapp, normalize_paypal, normalize_venmo
from app.regions import US_STATES


def _lower(value: str | None) -> str | None:
    return value.strip().lower() if value else value


class SignupForm(FlaskForm):
    username = StringField(
        "Username",
        filters=[_lower],
        validators=[
            DataRequired(),
            Length(min=3, max=30),
            Regexp(r"^[a-z0-9_.]+$", message="Use letters, numbers, dots, and underscores."),
        ],
    )
    email = EmailField(
        "Email",
        filters=[_lower],
        validators=[DataRequired(), Email(check_deliverability=False), Length(max=254)],
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )


class LoginForm(FlaskForm):
    identifier = StringField(
        "Username or email", filters=[_lower], validators=[DataRequired(), Length(max=254)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])


def _handle_field(label: str, normalize: Callable[[str | None], str | None], hint: str) -> Any:
    def check(form: FlaskForm, field: Field) -> None:
        try:
            field.data = normalize(field.data)
        except ValueError:
            raise ValidationError(hint) from None

    return StringField(label, validators=[Optional(), check], description=hint)


class ProfileForm(FlaskForm):
    city = StringField(
        "City", filters=[lambda v: v.strip() if v else None], validators=[Length(max=80)]
    )
    state = SelectField(
        "State",
        choices=[SelectChoice("", "Choose a state")]
        + [SelectChoice(code, name) for code, name in US_STATES.items()],
        validate_choice=True,
    )
    cashapp_handle = _handle_field(
        "Cash App", normalize_cashapp, "Your $cashtag: up to 20 letters or numbers."
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


class EmptyForm(FlaskForm):
    pass
