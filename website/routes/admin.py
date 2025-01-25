from flask import Blueprint, request, render_template, jsonify, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
import os

from website.models import Admin

load_dotenv()
secret_key = os.getenv("SECRET_KEY")

admin_bp = Blueprint("admin", __name__, template_folder="../templates")


@admin_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home.index"))


@admin_bp.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if request.args.get("token") != secret_key:
            return render_template("errors/403.html")
        return render_template("admin/login.html")
    elif request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")

        admin = Admin.query.filter_by(login=login).first()

        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            flash("Access granted!", "success")
            return redirect(url_for("home.index"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(request.url)
