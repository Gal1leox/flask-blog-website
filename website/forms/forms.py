from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

from ..models import User


def strip_filter(value):
    return value.strip() if value else value


gmail_validators = [
    DataRequired(),
    Email(),
    Length(min=6, max=100),
    Regexp(
        r"^[A-Za-z0-9_.+-]+@gmail\.com$",
        flags=0,
        message="Email must be a Gmail address.",
    ),
]


def gmail_email_field(label, placeholder="user@gmail.com", extra_validators=None):
    validators = gmail_validators.copy()
    if extra_validators:
        validators.extend(extra_validators)
    return StringField(
        label,
        validators=validators,
        render_kw={"placeholder": placeholder},
        filters=[strip_filter],
    )


def password_field(label, placeholder="password", extra_validators=None):
    validators = [DataRequired(), Length(min=8)]
    if extra_validators:
        validators.extend(extra_validators)
    return PasswordField(
        label,
        validators=validators,
        render_kw={"placeholder": placeholder},
        filters=[strip_filter],
    )


def validate_username(_, field):
    username = field.data or ""

    if not username[0].isalpha():
        raise ValidationError("Username must start with a letter.")

    if username[-1] in "._":
        raise ValidationError("Username must end with a letter or digit.")

    for char in username:
        if char.isalpha() and not char.islower():
            raise ValidationError("Username must use only lowercase letters.")
        if not (char.isdigit() or char.islower() or char in "._"):
            raise ValidationError(
                "Username may only contain lowercase letters, digits, '.' or '_'."
            )


def unique_username(_, field):
    user = User.query.filter_by(username=field.data).first()
    if user and user.id != current_user.id:
        raise ValidationError("This username is already taken.")


class RegisterForm(FlaskForm):
    email = gmail_email_field("Your email")
    password = password_field("Password")
    confirm_password = password_field(
        "Confirm password",
        extra_validators=[EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Sign up")


class LoginForm(FlaskForm):
    email = gmail_email_field("Your email")
    password = password_field("Password")
    submit = SubmitField("Sign in")


class ForgotPasswordForm(FlaskForm):
    email = gmail_email_field("Your registered email")
    submit = SubmitField("Submit")


class ResetPasswordForm(FlaskForm):
    password = password_field("Password")
    confirm_password = password_field(
        "Confirm password",
        extra_validators=[EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Reset")


class UpdateProfileForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            validate_username,
            unique_username,
        ],
        render_kw={"placeholder": "username"},
        filters=[strip_filter],
    )
    email = StringField(
        "Email address",
        render_kw={"placeholder": "user@gmail.com", "disabled": True},
    )
    profile_image = FileField(
        "Profile image",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png"], "Profile image must be a JPG or PNG file."
            ),
        ],
    )
    submit = SubmitField("Save")


class ChangePasswordForm(FlaskForm):
    current_password = password_field(
        "Current Password", placeholder="Current password"
    )
    new_password = password_field("New Password", placeholder="New password")
    confirm_new_password = password_field(
        "Confirm New Password",
        placeholder="Confirm new password",
        extra_validators=[EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Change Password")
