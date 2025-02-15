from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp


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
        "Your registered password",
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
