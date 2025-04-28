from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from flask_wtf.file import FileAllowed

from .base import BaseForm
from .fields import password_field, gmail_email_field
from .validators import validate_username, unique_username


class UpdateProfileForm(BaseForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=2, max=15),
            validate_username,
            unique_username,
        ],
        render_kw={"placeholder": "username"},
    )
    email = StringField(
        "Email address",
        render_kw={"placeholder": "user@gmail.com", "disabled": True},
    )
    profile_image = FileField(
        "Profile image",
        validators=[FileAllowed(["jpg", "jpeg", "png"], "JPG/PNG only")],
    )
    submit = SubmitField(
        "Save",
        render_kw={
            "class": "py-2 px-4 bg-green-500 text-white rounded hover:bg-green-600"
        },
    )


class ChangePasswordForm(BaseForm):
    current_password = password_field(
        "Current Password",
        placeholder="Current password",
        extra_validators=[DataRequired(), Length(min=8)],
    )
    new_password = password_field(
        "New Password",
        placeholder="New password",
        extra_validators=[DataRequired(), Length(min=8)],
    )
    confirm_new_password = password_field(
        "Confirm New Password",
        placeholder="Confirm new password",
        extra_validators=[EqualTo("new_password", message="Passwords must match")],
    )
    submit = SubmitField(
        "Change Password",
        render_kw={
            "class": "py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
        },
    )
