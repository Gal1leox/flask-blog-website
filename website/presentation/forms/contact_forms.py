from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Optional
from flask_wtf import RecaptchaField

from .base import BaseForm
from .fields import textarea_field


class ContactForm(BaseForm):
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(r"^[A-Za-z]+$", message="First name must contain only letters"),
        ],
        render_kw={"placeholder": "First name"},
    )
    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(r"^[A-Za-z]+$", message="Last name must contain only letters"),
        ],
        render_kw={"placeholder": "Last name"},
    )
    inquiry_type = SelectField(
        "I am interested in",
        choices=[
            ("general inquiry", "General Inquiry"),
            ("collaboration inquiry", "Collaboration Inquiry"),
            ("hiring inquiry", "Hiring Inquiry"),
        ],
        validators=[DataRequired()],
    )
    phone = StringField(
        "Phone Number (optional)",
        validators=[
            Optional(),
            Regexp(r"^[+0-9 ()-]+$", message="Invalid phone number format"),
            Length(10, 20),
        ],
        render_kw={"placeholder": "+7 475 638 8929"},
    )
    message = textarea_field(
        "Message",
        extra_validators=[DataRequired(), Length(min=10, max=1000)],
        render_kw={"placeholder": "Your message", "rows": 4},
    )
    recaptcha = RecaptchaField()
    submit = SubmitField(
        "Submit",
        render_kw={
            "class": "py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
        },
    )
