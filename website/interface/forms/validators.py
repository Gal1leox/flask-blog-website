import re

from wtforms import ValidationError
from wtforms.validators import DataRequired, Email, Length, Regexp, StopValidation

# Precompiled regex patterns
GMAIL_PATTERN = re.compile(r"^[A-Za-z0-9_.+-]+@gmail\.com$")
PHONE_PATTERN = re.compile(r"^\+?[\d\s\-\(\)]+$")

# Composite Gmail-specific validators
gmail_validators = [
    DataRequired(message="Email is required."),
    Email(message="Invalid email address."),
    Length(min=6, max=100, message="Email must be between 6 and 100 characters."),
    Regexp(
        GMAIL_PATTERN,
        message="Email must be a Gmail address.",
    ),
]


def strip_filter(value: str) -> str:
    """
    Trim leading/trailing whitespace from input values.
    """
    return value.strip() if value else value


def validate_username(form, field):
    """
    Ensure username:
      - Starts with a letter
      - Ends with a letter or digit
      - Contains only lowercase letters, digits, '.' or '_'
    """
    username = (field.data or "").strip()
    if not username:
        raise ValidationError("Username is required.")

    if not username[0].isalpha():
        raise ValidationError("Username must start with a letter.")

    if not (username[-1].isalnum()):
        raise ValidationError("Username must end with a letter or digit.")

    for char in username:
        if char.isalpha() and not char.islower():
            raise ValidationError("Username must use only lowercase letters.")
        if not (char.islower() or char.isdigit() or char in "._"):
            raise ValidationError(
                "Username may only contain lowercase letters, digits, '.' or '_'."
            )


def validate_phone(form, field):
    """
    Validate optional phone number format.
    Accepts digits, spaces, parentheses, dashes, and optional leading '+'.
    """
    value = (field.data or "").strip()
    if not value:
        return
    if not PHONE_PATTERN.match(value):
        raise ValidationError("Invalid phone number format.")


def calculate_word_count(form, field):
    """
    Enforce a maximum of 300 words in a text field.
    """
    text = field.data or ""
    word_count = len(text.split())
    if word_count > 300:
        raise ValidationError("Cannot exceed 300 words.")


def validate_num_images(form, field):
    """
    Ensure at least one and at most five images,
    each no larger than 8MB.
    """
    files = getattr(field, "data", []) or []
    count = len(files)
    if count < 1:
        raise ValidationError("At least one image is required.")
    if count > 5:
        raise ValidationError("You can upload a maximum of 5 images.")

    for file in files:
        # Check file size
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        if size > 8 * 1024 * 1024:
            raise ValidationError(f"File '{file.filename}' exceeds the 8MB limit.")


class OptionalImages:
    """
    Skip image validators when editing an existing post.
    """

    def __call__(self, form, field):
        if getattr(form, "editing", False):
            raise StopValidation()
