from wtforms import StringField, SelectField, SubmitField
from flask_wtf import RecaptchaField
from wtforms.validators import DataRequired, Length, Regexp, Optional

from .base import BaseForm
from .fields import textarea_field


class ContactForm(BaseForm):
    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(2, 50), Regexp(r"^[A-Za-z]+$")]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(2, 50), Regexp(r"^[A-Za-z]+$")]
    )
    inquiry_type = SelectField(
        "Inquiry",
        choices=[("general", "General"), ("hire", "Hiring")],
        validators=[DataRequired()],
    )
    phone = StringField(
        "Phone (opt)", validators=[Optional(), Regexp(r"^[+0-9 ()-]+$")]
    )
    message = textarea_field("Message", validators=[DataRequired(), Length(max=300)])
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit")
