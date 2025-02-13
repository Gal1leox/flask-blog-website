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


def _redirect_to_referrer_or_home():
    """Redirect to the previous page URL if available, else home."""

    return redirect(request.referrer or url_for("general.home"))


def _get_verification_code(token):
    """
    Retrieve a valid verification code using token.
    If invalid or expired, flash an error and return None.

    :param token: The query parameter token.
    """

    verification_code = VerificationCode.query.filter_by(token=token).first()

    if not verification_code or verification_code.is_expired():
        flash(
            f"The verification link is invalid or expired.",
            "danger",
        )
        return None

    return verification_code


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_to_referrer_or_home()

    if request.method == "GET":
        return render_template("auth/user/pages/register.html")

    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not email or not password:
        flash("Email and password are required.", "danger")
        return redirect(request.url)

    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(request.url)

    user = User.query.filter_by(email=email).first()

    if user:
        flash("A user with this email already exists.", "danger")
        return redirect(request.url)

    try:
        new_user = User(
            email=f"{email.split("@")[0]}_{random.randint(1000000,9999999)}",
            password_hash=generate_password_hash(password),
        )
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Access granted!", "success")

        print("User was created successfully!\n")
        print(user)

        return redirect(url_for("general.home"))
    except Exception as e:
        print(f"Error creating a user:\n\n" f"{e}")


@auth_bp.route("/login/", methods=["GET"])
def login_page():
    if current_user.is_authenticated:
        return _redirect_to_referrer_or_home()
    return render_template("auth/user/pages/login.html")


@auth_bp.route("/login/", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return _redirect_to_referrer_or_home()

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required.", "danger")
        return redirect(request.url)

    user = User.query.filter_by(email=email).first()

    if (
        user
        and user.email != admin_email
        and check_password_hash(user.password_hash, password)
    ):
        login_user(user)
        flash("Access granted!", "success")
        return redirect(url_for("general.home"))
    else:
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(request.url)


@auth_bp.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("general.home"))


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

    user = User.query.filter_by(email=email).first()
    admin = User.query.filter_by(email=admin_email).first()

    if user and user.email != admin.email:
        code = f"{random.randint(1000, 9999)}"
        verification_code = VerificationCode(user.id, code)
        db.session.add(verification_code)
        db.session.commit()

        token = verification_code.token
        verification_link = f"{request.host_url}auth/verify-code?token={token}"

        message = Message(
            "Verify Your Email with This Code",
            html=render_template(
                "auth/user/pages/email_message.html",
                code=code,
                verification_link=verification_link,
            ),
            sender=os.getenv("ADMIN_EMAIL"),
            recipients=[email],
        )

        try:
            mail.send(message)
            return redirect(f"/auth/verify-code?token={token}")
        except Exception as error:
            flash(str(error), "danger")
            return redirect(request.url)
    else:
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(request.url)


@auth_bp.route("/verify-code/", methods=["GET"])
def get_verify_code_page():
    token = request.args.get("token")

    if not token:
        flash("Invalid token. Please fill in your email.", "danger")
        return redirect(url_for("auth.forgot_password_page"))

    if not _get_verification_code(token):
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

    verification_code = _get_verification_code(token)

    if not verification_code:
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

    verification_code = _get_verification_code(token)
    if not verification_code:
        flash(
            f"The verification link is invalid or expired.",
            "danger",
        )
        return redirect(url_for("auth.forgot_password_page"))

    if not verification_code.is_valid:
        flash("You didn't confirm this token!", "danger")
        return redirect(url_for("auth.get_verify_code_page", token=token))

    if request.method == "GET":
        return render_template("auth/user/pages/reset_password.html")

    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(request.url)

    verification_code = _get_verification_code(token)

    user = User.query.filter_by(id=verification_code.user_id).first()
    user.password_hash = generate_password_hash(password)
    db.session.delete(verification_code)
    db.session.commit()

    flash("Password reset successfully.", "success")
    return redirect(url_for("auth.login_page"))


# --- Admin Routes ---


@auth_bp.route("/admin/login/", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated:
        return _redirect_to_referrer_or_home()

    if request.args.get("token") != secret_key:
        return render_template("errors/pages/403.html")

    if request.method == "GET":
        return render_template("auth/admin/pages/login.html")

    email = request.form.get("email")
    password = request.form.get("password")

    if not email or not password:
        flash("Email and password are required.", "danger")
        return redirect(request.url)

    admin = User.query.filter_by(email=admin_email).first()

    if admin and (check_password_hash(admin.password_hash, password)):
        login_user(admin)
        flash("Access granted!", "success")
        return redirect(url_for("general.home"))
    else:
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(request.url)
