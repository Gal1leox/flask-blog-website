from wtforms import SubmitField
from wtforms.validators import EqualTo

from .base import BaseForm
from .fields import gmail_email_field, password_field


class RegisterForm(BaseForm):
    email = gmail_email_field("Your email", placeholder="user@gmail.com")
    password = password_field("Password", placeholder="Password")
    confirm_password = password_field(
        "Confirm password",
        placeholder="Confirm password",
        extra_validators=[EqualTo("password", message="Must match.")],
    )
    submit = SubmitField(
        "Sign up",
        render_kw={
            "class": "py-2 px-4 bg-green-500 text-white rounded hover:bg-green-600"
        },
    )


class LoginForm(BaseForm):
    email = gmail_email_field("Your email", placeholder="user@gmail.com")
    password = password_field("Password", placeholder="Password")
    submit = SubmitField(
        "Sign in",
        render_kw={
            "class": "py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
        },
    )


class ForgotPasswordForm(BaseForm):
    email = gmail_email_field("Your registered email", placeholder="user@gmail.com")
    submit = SubmitField(
        "Submit",
        render_kw={
            "class": "py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
        },
    )


class ResetPasswordForm(BaseForm):
    password = password_field("New Password", placeholder="New password")
    confirm_password = password_field(
        "Confirm New Password",
        placeholder="Confirm new password",
        extra_validators=[EqualTo("password", message="Must match.")],
    )
    submit = SubmitField(
        "Reset",
        render_kw={
            "class": "py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
        },
    )
