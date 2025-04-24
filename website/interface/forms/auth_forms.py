from wtforms import SubmitField
from wtforms.validators import EqualTo

from .base import BaseForm
from .fields import gmail_email_field, password_field


class RegisterForm(BaseForm):
    email = gmail_email_field("Your email")
    password = password_field("Password")
    confirm_password = password_field(
        "Confirm password",
        extra_validators=[EqualTo("password", message="Must match.")],
    )
    submit = SubmitField("Sign up")


class LoginForm(BaseForm):
    email = gmail_email_field("Your email")
    password = password_field("Password")
    submit = SubmitField("Sign in")


class ForgotPasswordForm(BaseForm):
    email = gmail_email_field("Your registered email")
    submit = SubmitField("Submit")


class ResetPasswordForm(BaseForm):
    password = password_field("Password")
    confirm_password = password_field(
        "Confirm password",
        extra_validators=[EqualTo("password")],
    )
    submit = SubmitField("Reset")
