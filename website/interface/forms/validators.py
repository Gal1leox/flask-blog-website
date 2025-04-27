import re

from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, StopValidation
from flask_login import current_user

from website.infrastructure.repositories import UserRepository

# Patterns
gmail_re = re.compile(r"^[\w.+-]+@gmail\.com$")
phone_re = re.compile(r"^\+?[\d\s\-()]+$")

# Gmail field validators
gmail_validators = [
    DataRequired("Email is required."),
    Email("Invalid email address."),
    Length(6, 100, "Email must be between 6 and 100 characters."),
    Regexp(gmail_re, "Email must be a Gmail address."),
]


def strip_filter(value):
    if isinstance(value, str):
        return value.strip()
    return value


def validate_username(_, field):
    name = (field.data or "").strip()
    if not name:
        raise ValidationError("Username is required.")
    if not name[0].isalpha() or not name[-1].isalnum():
        raise ValidationError(
            "Username must start with a letter and end with a letter or digit."
        )
    if not re.fullmatch(r"[a-z0-9._]+", name):
        raise ValidationError("Use only lowercase letters, digits, '.' or '_'.")


def unique_username(_, field):
    """
    Ensure username is unique (excluding current user).
    """
    existing = UserRepository.get_by_username(field.data)
    if existing and existing.id != current_user.id:
        raise ValidationError("This username is already taken.")


def validate_phone(_, field):
    val = (field.data or "").strip()
    if val and not phone_re.match(val):
        raise ValidationError("Invalid phone number format.")


def validate_num_images(form, field):
    files = field.data or []
    # server must see a list now
    if not isinstance(files, (list, tuple)):
        raise ValidationError("Invalid upload data.")

    if not (1 <= len(files) <= 5):
        raise ValidationError("Please upload between 1 and 5 images.")

    for f in files:
        # enforce size ≤ 8 MB
        f.seek(0, 2)
        size = f.tell()
        f.seek(0)
        if size > 8 * 1024 * 1024:
            raise ValidationError(f"'{f.filename}' exceeds 8 MB.")


class OptionalImages:
    def __call__(self, form, field):
        if getattr(form, "editing", False):
            raise StopValidation()
