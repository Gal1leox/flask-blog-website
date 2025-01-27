from flask import Blueprint, render_template

from flask_login import current_user

from ..models import Admin
from ..utils import convert_binary_to_image

general_bp = Blueprint("general", __name__, template_folder="../templates")


@general_bp.route("/")
def home():
    avatar_data = None

    if current_user.is_authenticated:
        admin = Admin.query.filter_by(created_at=current_user.created_at).first()
        if admin and admin.avatar:
            avatar_data = convert_binary_to_image(admin.avatar)

    return render_template("general/pages/home.html", avatar_data=avatar_data)
