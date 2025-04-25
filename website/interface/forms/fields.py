from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length
from werkzeug.datastructures import FileStorage
from flask_wtf.file import FileField

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


def textarea_field(label, extra_validators=None, render_kw=None, **kwargs):
    validators = []
    if extra_validators:
        validators.extend(extra_validators)

    options = {"validators": validators}
    if render_kw is not None:
        options["render_kw"] = render_kw
    # include any other kwargs (e.g. filters, default, etc.)
    options.update(kwargs)

    return TextAreaField(label, **options)


class MultiFileField(FileField):
    def process_formdata(self, valuelist):
        self.data = [
            f
            for f in valuelist
            if isinstance(f, FileStorage) and getattr(f, "filename", None)
        ]
