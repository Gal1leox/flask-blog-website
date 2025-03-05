import os

from flask import Blueprint, request, redirect, url_for, render_template, abort
from flask_login import current_user
from dotenv import load_dotenv

from ..models import (
    User,
    UserRole,
    Post,
    Tag,
    Image,
    Comment,
    Notification,
    PostImage,
    PostTag,
    SavedPost,
    UserNotification,
    VerificationCode,
)

load_dotenv()

admin_email = os.getenv("ADMIN_EMAIL")
secret_key = os.getenv("SECRET_KEY")

admin_bp = Blueprint("admin", __name__, template_folder="../templates")


def get_model_columns(model_or_table):
    if hasattr(model_or_table, "__table__"):
        return [column.name for column in model_or_table.__table__.columns]
    elif hasattr(model_or_table, "columns"):
        return [column.name for column in model_or_table.columns]
    return []


TABLE_ATTRIBUTES = {
    "users": get_model_columns(User),
    "posts": get_model_columns(Post),
    "tags": get_model_columns(Tag),
    "comments": get_model_columns(Comment),
    "verification_codes": get_model_columns(VerificationCode),
    "images": get_model_columns(Image),
    "notifications": get_model_columns(Notification),
    "post_images": get_model_columns(PostImage),
    "post_tags": get_model_columns(PostTag),
    "saved_posts": get_model_columns(SavedPost),
    "user_notifications": get_model_columns(UserNotification),
}

TABLE_QUERIES = {
    "users": lambda: User.query.all(),
    "posts": lambda: Post.query.all(),
    "tags": lambda: Tag.query.all(),
    "comments": lambda: Comment.query.all(),
    "verification_codes": lambda: VerificationCode.query.all(),
    "images": lambda: Image.query.all(),
    "notifications": lambda: Notification.query.all(),
    "post_images": lambda: PostImage.query.all(),
    "post_tags": lambda: PostTag.query.all(),
    "saved_posts": lambda: SavedPost.query.all(),
    "user_notifications": lambda: UserNotification.query.all(),
}


def get_records(table):
    query = TABLE_QUERIES.get(table)
    return query() if query else []


def _redirect_to_referrer_or_home():
    """Redirect to the previous page URL if available, else home."""

    return redirect(request.referrer or url_for("general.home"))


@admin_bp.route("/database/")
def database():
    token = request.args.get("token")
    if token != secret_key:
        return abort(403)

    user = User.query.get(current_user.id) if current_user.is_authenticated else None
    is_admin = user and user.role == UserRole.ADMIN

    if not is_admin:
        return render_template("errors/pages/403.html")

    avatar_url = user.avatar_url if user else ""
    selected_table = request.args.get("table")

    tabs = [
        {"name": name, "link": url_for("admin.database", token=token, table=name)}
        for name in TABLE_QUERIES.keys()
    ]

    records = get_records(selected_table)
    attributes = TABLE_ATTRIBUTES[selected_table] if selected_table else []

    return render_template(
        "general/admin/pages/database.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        active_page="Database",
        tabs=tabs,
        records=records,
        attributes=attributes,
        selected_table=selected_table,
    )
