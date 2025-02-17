from flask import Blueprint, render_template
from flask_login import current_user

from ..models import User, UserRole

general_bp = Blueprint("general", __name__, template_folder="../templates")


@general_bp.route("/")
def home():
    avatar_url = ""
    is_admin = False

    if current_user.is_authenticated:
        user = User.query.filter(User.id == current_user.id).first()
        avatar_url = user.avatar_url
        is_admin = user.role == UserRole.ADMIN

    return render_template(
        "general/pages/home.html", avatar_url=avatar_url, is_admin=is_admin
    )
