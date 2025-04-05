import os
from functools import wraps

from flask import request, abort, render_template, redirect, url_for
from flask_login import current_user
from wtforms import ValidationError
from dotenv import load_dotenv

from ..models import User, UserRole, VerificationCode

load_dotenv()
secret_key = os.getenv("SECRET_KEY")


def anonymous_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("home.home"))
        return f(*args, **kwargs)

    return decorated


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get("token")
        if token != secret_key:
            return abort(403)
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return render_template("errors/pages/403.html")

        user = User.query.get(current_user.id)
        if not (user and user.role == UserRole.ADMIN):
            return render_template("errors/pages/403.html")
        return f(*args, **kwargs)

    return decorated


def get_verification_code(token):
    verification_code = VerificationCode.query.filter_by(token=token).first()
    if not verification_code or verification_code.is_expired():
        return None

    return verification_code


def validate_username(_, field):
    username = field.data or ""

    if not username[0].isalpha():
        raise ValidationError("Username must start with a letter.")

    if username[-1] in "._":
        raise ValidationError("Username must end with a letter or digit.")

    for char in username:
        if char.isalpha() and not char.islower():
            raise ValidationError("Username must use only lowercase letters.")
        if not (char.isdigit() or char.islower() or char in "._"):
            raise ValidationError(
                "Username may only contain lowercase letters, digits, '.' or '_'."
            )


def unique_username(form, field):
    user = User.query.filter_by(username=field.data).first()
    if user and user.id != current_user.id:
        raise ValidationError("This username is already taken.")
