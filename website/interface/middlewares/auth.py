from functools import wraps

from flask import request, abort, render_template, redirect, url_for
from flask_login import current_user

from website.config import Config
from website.infrastructure.repositories import UserRepository
from website.infrastructure.repositories import (
    VerificationCodeRepository,
)


SECRET_KEY = Config.SECRET_KEY


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
        if token != SECRET_KEY:
            abort(403)
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return render_template("pages/errors/403.html"), 403

        user = UserRepository.get_by_id(current_user.id)
        if not user or user.role.name != "ADMIN":
            return render_template("pages/errors/403.html"), 403

        return f(*args, **kwargs)

    return decorated


def get_verification_code(token: str):
    """
    Retrieve a non-expired verification code by token, or return None.
    """
    vc = VerificationCodeRepository.get_by_token(token)
    if not vc or vc.is_valid:
        return None
    return vc
