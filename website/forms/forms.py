from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, FileField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from flask_login import current_user
from ..models.user import User


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


def unique_username(form, field):
    user = User.query.filter_by(username=field.data).first()
    if user and user.id != current_user.id:
        raise ValidationError("This username is already taken.")


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
    profile_image = FileField(
        "Profile Image",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png"], "Profile image must be a JPG or PNG file."
            ),
        ],
    )
    submit = SubmitField("Save")
