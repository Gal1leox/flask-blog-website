import os

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

from ..models import User

load_dotenv()
secret_key = os.getenv("SECRET_KEY")

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("general.home"))


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/admin/pages/login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter(User.email == email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Access granted!", "success")
            return redirect(url_for("general.home"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(request.url)


@auth_bp.route("/admin/login/", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if request.args.get("token") != secret_key:
            return render_template("errors/pages/403.html")
        return render_template("auth/admin/pages/login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        admin = User.query.filter(User.email == email).first()

        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin)
            flash("Access granted!", "success")
            return redirect(url_for("general.home"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(request.url)
