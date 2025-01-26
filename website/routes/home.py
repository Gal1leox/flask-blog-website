import base64
from flask import Blueprint, render_template
from flask_login import current_user
from ..models import Admin

home_bp = Blueprint("home", __name__, template_folder="../templates/home")


@home_bp.route("/", methods=["GET"])
def index():
    avatar_data = None
    if current_user.is_authenticated:
        admin = Admin.query.filter_by(created_at=current_user.created_at).first()
        if admin and admin.avatar:
            avatar_data = base64.b64encode(admin.avatar).decode("utf-8")
    return render_template("index.html", avatar_data=avatar_data)
