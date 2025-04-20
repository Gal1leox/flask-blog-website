import os

from flask import Blueprint, render_template, request
from flask_login import current_user
from dotenv import load_dotenv

from ..models import User, UserRole, Post

load_dotenv()

home_bp = Blueprint("home", __name__, template_folder="../templates")


@home_bp.route("/")
def home():
    user = User.query.get(current_user.id) if current_user.is_authenticated else None

    is_admin = user and user.role == UserRole.ADMIN
    token = os.getenv("SECRET_KEY") if is_admin else ""
    theme = user.theme.value if user else "system"

    selected_tags = request.args.getlist("tag")

    post = Post.query
    for tag in selected_tags:
        post = post.filter(Post.content.ilike(f"%#{tag}%"))
    posts = post.order_by(Post.created_at.desc()).all()

    return render_template(
        "pages/shared/home.html",
        is_admin=is_admin,
        token=token,
        posts=posts,
        theme=theme,
        selected_tags=selected_tags,
    )
