from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp

from ..utils import validate_username, unique_username


class RegisterForm(FlaskForm):
    email = StringField(
        "Your email",
        validators=[
            DataRequired(),
            Email(),
            Length(min=6, max=100),
            Regexp(
                r"^[A-Za-z0-9_.+-]+@gmail\.com$",
                flags=0,
                message="Email must be a Gmail address.",
            ),
        ],
        render_kw={"placeholder": "user@gmail.com"},
        filters=[lambda value: value.strip() if value else value],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)],
        render_kw={"placeholder": "password"},
        filters=[lambda value: value.strip() if value else value],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "password"},
        filters=[lambda value: value.strip() if value else value],
    )
    submit = SubmitField("Sign up")


class LoginForm(FlaskForm):
    email = StringField(
        "Your email",
        validators=[
            DataRequired(),
            Email(),
            Length(min=6, max=100),
            Regexp(
                r"^[A-Za-z0-9_.+-]+@gmail\.com$",
                flags=0,
                message="Email must be a Gmail address.",
            ),
        ],
        render_kw={"placeholder": "user@gmail.com"},
        filters=[lambda value: value.strip() if value else value],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)],
        render_kw={"placeholder": "password"},
        filters=[lambda value: value.strip() if value else value],
    )
    submit = SubmitField("Sign in")


class ForgotPasswordForm(FlaskForm):
    email = StringField(
        "Your registered email",
        validators=[
            DataRequired(),
            Email(),
            Length(min=6, max=100),
            Regexp(
                r"^[A-Za-z0-9_.+-]+@gmail\.com$",
                flags=0,
                message="Email must be a Gmail address.",
            ),
        ],
        render_kw={"placeholder": "user@gmail.com"},
        filters=[lambda value: value.strip() if value else value],
    )
    submit = SubmitField("Submit")


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)],
        render_kw={"placeholder": "password"},
        filters=[lambda value: value.strip() if value else value],
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            Length(min=8),
            EqualTo("password", message="Passwords must match."),
        ],
        render_kw={"placeholder": "password"},
        filters=[lambda value: value.strip() if value else value],
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
        filters=[lambda value: value.strip() if value else value],
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
