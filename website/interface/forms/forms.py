from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileRequired, FileField
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    TextAreaField,
    ValidationError,
)
from flask_wtf.recaptcha import RecaptchaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional, Regexp

from .validators import (
    gmail_validators,
    strip_filter,
    validate_username,
    calculate_word_count,
    validate_phone,
    validate_num_images,
    OptionalImages,
)
from website.domain.models import User


class BaseForm(FlaskForm):
    """
    Base form that applies strip_filter to all fields automatically.
    """

    class Meta:
        def bind_field(self, form, unbound_field, options):
            filters = options.pop("filters", [])
            filters.append(strip_filter)
            options["filters"] = filters
            return unbound_field.bind(form=form, **options)


def gmail_email_field(label, placeholder="user@gmail.com", extra_validators=None):
    """
    Reusable email field with Gmail-specific validators.
    """
    validators = gmail_validators.copy()
    if extra_validators:
        validators.extend(extra_validators)
    return StringField(
        label,
        validators=validators,
        render_kw={"placeholder": placeholder},
    )


def password_field(label, placeholder="password", extra_validators=None):
    """
    Reusable password field with basic length requirement.
    """
    validators = [DataRequired(), Length(min=8)]
    if extra_validators:
        validators.extend(extra_validators)
    return PasswordField(
        label,
        validators=validators,
        render_kw={"placeholder": placeholder},
    )


def textarea_field(label, placeholder=None, rows=4, extra_validators=None):
    """
    Reusable textarea field with word count and optional custom validators.
    """
    validators = extra_validators or [DataRequired(), calculate_word_count]
    render_kw = {"rows": rows}
    if placeholder:
        render_kw["placeholder"] = placeholder
    return TextAreaField(label, validators=validators, render_kw=render_kw)


def unique_username(_, field):
    """
    Ensure the username is unique (ignoring the current user).
    """
    existing = User.query.filter_by(username=field.data).first()
    if existing and existing.id != current_user.id:
        raise ValidationError("This username is already taken.")


class RegisterForm(BaseForm):
    email = gmail_email_field("Your email")
    password = password_field("Password")
    confirm_password = password_field(
        "Confirm password",
        extra_validators=[EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Sign up")


class LoginForm(BaseForm):
    email = gmail_email_field("Your email")
    password = password_field("Password")
    submit = SubmitField("Sign in")


class ForgotPasswordForm(BaseForm):
    email = gmail_email_field("Your registered email")
    submit = SubmitField("Submit")


class ResetPasswordForm(BaseForm):
    password = password_field("Password")
    confirm_password = password_field(
        "Confirm password",
        extra_validators=[EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Reset")


class UpdateProfileForm(BaseForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=2, max=20),
            validate_username,
            unique_username,
        ],
        render_kw={"placeholder": "username"},
    )
    email = gmail_email_field("Email address")
    email.render_kw.update({"disabled": True})
    profile_image = FileField(
        "Profile image",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png"], "Profile image must be a JPG or PNG file."
            )
        ],
    )
    submit = SubmitField("Save")


class ChangePasswordForm(BaseForm):
    current_password = password_field(
        "Current Password", placeholder="Current password"
    )
    new_password = password_field("New Password", placeholder="New password")
    confirm_new_password = password_field(
        "Confirm New Password",
        placeholder="Confirm new password",
        extra_validators=[EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Change Password")


class ContactForm(BaseForm):
    first_name = StringField(
        "First Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(r"^[A-Za-z]+$", message="First name must contain only letters."),
        ],
        render_kw={"placeholder": "First name"},
    )
    last_name = StringField(
        "Last Name",
        validators=[
            DataRequired(),
            Length(min=2, max=50),
            Regexp(r"^[A-Za-z]+$", message="Last name must contain only letters."),
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
        validators=[Optional(), validate_phone],
        render_kw={"placeholder": "+7 475 638 8929"},
    )
    message = textarea_field(
        "Message",
        placeholder="Your message (max 300 words)",
        rows=4,
    )
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit")


class FileListField(FileField):
    """
    Handle multiple file inputs as a list.
    """

    def process_formdata(self, valuelist):
        self.data = valuelist or []


class CreatePostForm(BaseForm):
    content = textarea_field(
        "Content",
        placeholder="Content of a new post",
        rows=10,
    )
    images = FileListField(
        "Upload Images",
        validators=[
            OptionalImages(),
            FileRequired(message="At least one image is required."),
            validate_num_images,
            FileAllowed(["jpg", "jpeg", "png"], "Only JPG and PNG images are allowed."),
        ],
        render_kw={"multiple": True, "id": "dropzone-file"},
    )
    submit = SubmitField("Publish")


class CommentForm(BaseForm):
    content = textarea_field(
        "Your Comment",
        rows=3,
        extra_validators=[DataRequired(), Length(min=4, max=200)],
        placeholder="What do you think..",
    )
    content.render_kw.update(
        {"class": "w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600"}
    )
    submit = SubmitField(
        "Comment",
        render_kw={"class": "mt-2 px-4 py-2 bg-blue-600 text-white rounded"},
    )
