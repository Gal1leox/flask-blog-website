from flask import Blueprint, render_template
from flask_login import current_user

core_bp = Blueprint("core", __name__, template_folder="../templates/core")


@core_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html", user=current_user)
