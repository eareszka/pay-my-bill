from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


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


class EmptyForm(FlaskForm):
    pass
