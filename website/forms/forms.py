from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    FileField,
    ValidationError,
    SelectField,
    TextAreaField,
)
from flask_wtf.recaptcha import RecaptchaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Regexp

from .validators import (
    gmail_validators,
    strip_filter,
    validate_username,
    calculate_word_count,
    validate_phone,
)
from ..models import User


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


class ContactForm(FlaskForm):
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(r"^[A-Za-z]+$", message="First name must contain only letters."),
        ],
        render_kw={"placeholder": "First name"},
        filters=[strip_filter],
    )
    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(r"^[A-Za-z]+$", message="Last name must contain only letters."),
        ],
        render_kw={"placeholder": "Last name"},
        filters=[strip_filter],
    )
    inquiry_type = SelectField(
        "I am interested in",
        choices=[
            ("general inquiry", "General Inquiry"),
            ("collaboration inquiry", "Collaboration Inquiry"),
            ("hiring inquiry", "Hiring Inquiry"),
        ],
        validators=[DataRequired()],
        filters=[strip_filter],
    )
    phone = StringField(
        "Phone Number (optional)",
        validators=[Optional(), validate_phone],
        render_kw={"placeholder": "123-456-7890"},
        filters=[strip_filter],
    )
    message = TextAreaField(
        "Message",
        validators=[DataRequired(), calculate_word_count],
        render_kw={"placeholder": "Your message (max 300 words)", "rows": 4},
        filters=[strip_filter],
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit")
