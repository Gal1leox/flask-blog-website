import os
from functools import wraps

from flask import request, abort, render_template
from flask_login import current_user
from dotenv import load_dotenv

from ..models import User, UserRole

load_dotenv()
secret_key = os.getenv("SECRET_KEY")


def require_admin_and_token():
    token = request.args.get("token")
    if token != secret_key:
        return abort(403)

    user = User.query.get(current_user.id) if current_user.is_authenticated else None
    if not (user and user.role == UserRole.ADMIN):
        return render_template("errors/pages/403.html")

    return None


def admin_and_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        result = require_admin_and_token()
        if result:
            return result
        return f(*args, **kwargs)

    return decorated
