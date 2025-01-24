from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os

from website.models import Admin

load_dotenv()
secret_key = os.getenv("SECRET_KEY")

admin_bp = Blueprint("admin", __name__, template_folder="../templates/admin")


@admin_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for("core.index"))


@admin_bp.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if request.args.get("token") != secret_key:
            return (
                "<h1 style='color: red; text-align: center; margin-top: 20%;'>You have no access to this page! 🔪</h1>",
                403,
            )
        return render_template("login.html")
    elif request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        admin = Admin.query.filter_by(login=login).first()

        if not admin:
            return jsonify({"message": "The admin doesn't have this login."})
        elif check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for("core.index"))
        else:
            return jsonify({"message": "Something is wrong with the credentials."})
