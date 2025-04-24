from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length

from .validators import gmail_validators, strip_filter


def gmail_email_field(label, placeholder="user@gmail.com", extra_validators=None):
    validators = gmail_validators.copy()
    if extra_validators:
        validators.extend(extra_validators)
    return StringField(
        label,
        validators=validators,
        filters=[strip_filter],
        render_kw={"placeholder": placeholder},
    )


def password_field(label, placeholder="password", extra_validators=None):
    validators = [DataRequired(), Length(min=8)]
    if extra_validators:
        validators.extend(extra_validators)
    return PasswordField(
        label,
        validators=validators,
        filters=[strip_filter],
        render_kw={"placeholder": placeholder},
    )


def textarea_field(label, placeholder=None, rows=4, extra_validators=None):
    from .validators import calculate_word_count

    validators = extra_validators or [DataRequired(), calculate_word_count]
    render_kw = {"rows": rows}
    if placeholder:
        render_kw["placeholder"] = placeholder
    return TextAreaField(
        label, validators=validators, filters=[strip_filter], render_kw=render_kw
    )
