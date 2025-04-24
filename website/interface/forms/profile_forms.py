from wtforms import StringField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_wtf.file import FileAllowed

from .base import BaseForm
from .fields import password_field
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
    submit = SubmitField("Save")


class ChangePasswordForm(BaseForm):
    current_password = password_field(
        "Current Password", extra_validators=[DataRequired(), Length(min=8)]
    )
    new_password = password_field(
        "New Password", extra_validators=[DataRequired(), Length(min=8)]
    )
    confirm_new = password_field(
        "Confirm New", extra_validators=[EqualTo("new_password", message="Must match.")]
    )
    submit = SubmitField("Change Password")
