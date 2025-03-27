import os

from flask import Blueprint, render_template
from flask_login import current_user
from dotenv import load_dotenv

from ..models import User, UserRole

load_dotenv()

general_bp = Blueprint("general", __name__, template_folder="../templates")


@general_bp.route("/")
def home():
    user = User.query.get(current_user.id) if current_user.is_authenticated else None

    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN
    token = os.getenv("SECRET_KEY") if is_admin else ""

    return render_template(
        "general/pages/home.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        active_page="Home",
    )
