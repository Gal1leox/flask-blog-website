import os
import random

from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from ..models import User, VerificationCode
from website import db, mail, limiter

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


@auth_bp.route("/login/", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return redirect(request.referrer or url_for("general.home"))
    if request.method == "GET":
        return render_template("auth/user/pages/login.html")


@auth_bp.route("/login/", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(request.referrer or url_for("general.home"))

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
    if current_user.is_authenticated:
        return redirect(request.referrer or url_for("general.home"))
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
    if request.args.get("token") != secret_key:
        return render_template("errors/pages/403.html")
    if current_user.is_authenticated:
        return redirect(request.referrer or url_for("general.home"))
    if request.method == "GET":
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


@auth_bp.route("/forgot-password/", methods=["GET"])
def forgot_password_page():
    return render_template("auth/user/pages/forgot_password.html")


@auth_bp.route("/forgot-password/", methods=["POST"])
@limiter.limit("2 per minute")
def forgot_password():
    email = request.form.get("email")

    if not email:
        flash("Invalid email. Please fill in your email.", "danger")
        return redirect(url_for("auth.forgot_password_page"))

    user = User.query.filter(User.email == email).first()
    admin = User.query.filter(User.email == admin_email).first()

    if user and user.email != admin.email:
        code = f"{random.randint(1000, 9999)}"
        verification_code = VerificationCode(user.id, code)
        db.session.add(verification_code)
        db.session.commit()

        token = verification_code.token
        verification_link = f"{request.host_url}auth/verify-code?token={token}"

        message = Message(
            "Verify Your Email with This Code",
            html=f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333; text-align: center;">
                        <h2 style="color: #3B82F6;">Email Verification</h2>
                        <p style="font-size: 16px;">Use the code below to verify your email:</p>
                        <p style="font-size: 24px; font-weight: bold; color: #3B82F6; background-color: #f8f8f8; padding: 10px; display: inline-block; border-radius: 5px;">
                            {code}
                        </p>
                        <p style="font-size: 14px; color: #777;">
                            If you were not redirected, click on this 
                            <a href="{verification_link}">link</a>.
                        </p>
                        <p style="font-size: 14px; color: #ff0000; margin-bottom: 3rem;">Don't delay, the token will expire in two minutes.</p>
                        <p style="font-size: 14px;">best, <br> <strong>Kalts Daniil’s</strong> personal blog >_<</p>
                    </body>
                </html>
            """,
            sender=os.getenv("ADMIN_EMAIL"),
            recipients=[email],
        )

        try:
            mail.send(message)
            return redirect(f"/auth/verify-code?token={token}")
        except Exception as error:
            flash(str(error), "danger")
    else:
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(request.url)


@auth_bp.route("/verify-code/", methods=["GET"])
def get_verify_code_page():
    token = request.args.get("token")

    if not token:
        flash("Invalid token. Please fill in your email.", "danger")
        return redirect(url_for("auth.forgot_password_page"))

    verification_code = VerificationCode.query.filter(
        VerificationCode.token == token
    ).first()

    if not verification_code or verification_code.is_expired():
        flash(
            f"The verification link is invalid or expired.",
            "danger",
        )

        return redirect(url_for("auth.forgot_password_page"))

    return render_template("auth/user/pages/verify_code.html")


@auth_bp.route("/verify-code/", methods=["POST"])
@limiter.limit("5 per minute", methods=["POST"])
def verify_code():
    token = request.args.get("token")

    if not token:
        flash("Invalid token. Please fill in your email.", "danger")
        return redirect(url_for("auth.forgot_password_page"))

    verification_code = VerificationCode.query.filter(
        VerificationCode.token == token
    ).first()

    if not verification_code or verification_code.is_expired():
        flash(
            f"The verification link is invalid or expired.",
            "danger",
        )

        return redirect(url_for("auth.forgot_password_page"))

    user_code = "".join([request.form.get(f"codefield_{idx}") for idx in range(4)])

    if check_password_hash(verification_code.code_hash, user_code):
        verification_code.is_valid = True
        db.session.commit()

        return redirect(url_for("auth.reset_password", token=token))
    else:
        return render_template(
            "auth/user/pages/verify_code.html",
            is_valid=False,
        )


@auth_bp.route("/reset-password/", methods=["GET", "POST"])
def reset_password():
    token = request.args.get("token")

    if not token:
        flash("Invalid token. Please fill in your email.", "danger")
        return redirect(url_for("auth.forgot_password_page"))

    verification_code = VerificationCode.query.filter(
        VerificationCode.token == token
    ).first()

    if not verification_code or verification_code.is_expired():
        flash(
            f"The verification link is invalid or expired.",
            "danger",
        )
        return redirect(url_for("auth.forgot_password_page"))

    if not verification_code.is_valid:
        flash("You didn't confirm this token!", "danger")
        return redirect(f"/auth/verify-code?token={token}")

    if request.method == "GET":
        return render_template("auth/user/pages/reset_password.html")
    elif request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(request.url)

        verification_code = VerificationCode.query.filter(
            VerificationCode.token == token
        ).first()

        user = User.query.filter(User.id == verification_code.user_id).first()
        user.password_hash = generate_password_hash(password)
        db.session.delete(verification_code)
        db.session.commit()

        return redirect(url_for("auth.login_page"))
