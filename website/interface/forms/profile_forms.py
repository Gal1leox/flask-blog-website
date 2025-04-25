from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Optional
from flask_wtf.file import FileAllowed

from .base import BaseForm
from .fields import password_field, gmail_email_field
from .validators import validate_username, unique_username


class UpdateProfileForm(BaseForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(2, 20), validate_username, unique_username],
    )
    profile_image = FileField(
        "Profile image",
        validators=[FileAllowed(["jpg", "png"], "JPG/PNG only")],
    )
    email = StringField(
        "Email address",
        validators=[Optional()],
        render_kw={"disabled": True},
    )
    submit = SubmitField("Save")


class ChangePasswordForm(BaseForm):
    current_password = password_field(
        "Current Password", extra_validators=[DataRequired(), Length(min=8)]
    )
    new_password = password_field(
        "New Password", extra_validators=[DataRequired(), Length(min=8)]
    )
    confirm_new_password = password_field(
        "Confirm New Password",
        extra_validators=[EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Change Password")
