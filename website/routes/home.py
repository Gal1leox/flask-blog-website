from flask import Blueprint, render_template
from flask_login import current_user

home_bp = Blueprint("home", __name__, template_folder="../templates/home")


@home_bp.route("/", methods=["GET"])
def index():
    return render_template("index.html", user=current_user)
