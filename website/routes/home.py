import os

from flask import Blueprint, render_template
from flask_login import current_user
from dotenv import load_dotenv

from ..models import User, UserRole, Post

load_dotenv()

home_bp = Blueprint("home", __name__, template_folder="../templates")


@home_bp.route("/")
def home():
    user = User.query.get(current_user.id) if current_user.is_authenticated else None

    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN
    token = os.getenv("SECRET_KEY") if is_admin else ""
    theme = user.theme.value if user else "system"

    posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template(
        "pages/shared/home.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        active_page="Home",
        posts=posts,
        theme=theme,
    )
