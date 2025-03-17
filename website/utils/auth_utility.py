import os
from functools import wraps

from flask import request, abort, render_template, redirect, url_for
from flask_login import current_user
from dotenv import load_dotenv

from ..models import User, UserRole, VerificationCode

load_dotenv()
secret_key = os.getenv("SECRET_KEY")


def anonymous_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("general.home"))
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
