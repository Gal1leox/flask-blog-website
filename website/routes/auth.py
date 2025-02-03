import os

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from ..models import User
from website import db

load_dotenv()

admin_email = os.getenv("ADMIN_EMAIL")
admin_password = os.getenv("ADMIN_PASSWORD")
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
        return render_template("auth/user/pages/login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(request.url)

        user = User.query.filter(User.email == email).first()

        if (
            user
            and user.email == admin_email
            and check_password_hash(user.password_hash, admin_password)
        ):
            flash("Invalid credential. Please, try again.", "danger")
            return redirect(request.url)
        elif user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash("Access granted!", "success")
            return redirect(url_for("general.home"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(request.url)


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/user/pages/register.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(request.url)

        user = User.query.filter(User.email == email).first()

        if user:
            flash("A user with this email already exists.", "danger")
            return redirect(request.url)
        else:
            try:
                new_user = User(
                    username=email.split("@")[0],
                    email=email,
                    password_hash=generate_password_hash(password),
                )
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)
                flash("Access granted!", "success")
                return redirect(url_for("general.home"))

                print("Admin was created successfully!\n")
                print(user)
            except Exception as e:
                print(f"Error creating user:\n\n" f"{e}")


@auth_bp.route("/admin/login/", methods=["GET", "POST"])
def admin_login():
    if request.method == "GET":
        if request.args.get("token") != secret_key:
            return render_template("errors/pages/403.html")
        return render_template("auth/admin/pages/login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(request.url)

        admin = User.query.filter(User.email == admin_email).first()

        if admin and (
            admin.email == email and check_password_hash(admin.password_hash, password)
        ):
            login_user(admin)
            flash("Access granted!", "success")
            return redirect(url_for("general.home"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
            return redirect(request.url)
