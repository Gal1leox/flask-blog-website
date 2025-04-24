import random
import time

from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
)
from flask_login import login_user, login_required, logout_user
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash

from website import db, mail, limiter
from website.config import Config
from website.init import google
from website.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from website.domain.models import User, VerificationCode
from website.utils import anonymous_required, get_verification_code, token_required

admin_email = Config.ADMIN_EMAIL
preferred_url_scheme = Config.PREFERRED_URL_SCHEME


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="../templates/auth",
)


@auth_bp.route("/google/login")
@anonymous_required
@limiter.limit("10/hour")
def google_login():
    redirect_uri = url_for(
        "auth.google_authorize",
        _external=True,
        _scheme=preferred_url_scheme,
    )

    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/authorize")
@anonymous_required
@limiter.limit("10/hour")
def google_authorize():
    token = google.authorize_access_token()

    info = google.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        token=token,
    ).json()

    email = info["email"]
    user = User.query.filter_by(email=email).first()

    if user:
        user.google_id = info["sub"]
        user.avatar_url = user.avatar_url or info.get("picture")
        message = f"Welcome back, {user.username}!"
    else:
        username = f"usr.{int(time.time() * 1000)}"
        user = User(
            username=username,
            email=email,
            avatar_url=info.get("picture"),
            google_id=info["sub"],
        )

        db.session.add(user)
        message = "Account created successfully!"

    db.session.commit()

    login_user(user)
    flash(message, "success")

    return redirect(url_for("home.home"))


@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/day", methods=["POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        user = User(
            username=f"usr.{int(time.time() * 1000)}",
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash("Account created!", "success")

        return redirect(url_for("home.home"))

    return render_template(
        "pages/auth/user/register.html",
        form=form,
        theme="system",
    )


@auth_bp.route("/login", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if (
            user
            and user.email != admin_email
            and user.password_hash
            and check_password_hash(user.password_hash, form.password.data)
        ):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")

            return redirect(url_for("home.home"))

        flash("Invalid credentials.", "danger")
        return redirect(url_for("auth.login"))

    return render_template(
        "pages/auth/user/login.html",
        form=form,
        theme="system",
    )


@auth_bp.route("/logout")
@login_required
@limiter.limit("20/hour")
def logout():
    logout_user()
    flash("Logged out successfully.", "success")

    return redirect(url_for("home.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or user.email == admin_email or not user.password_hash:
            flash("Invalid email for password reset.", "danger")
            return redirect(url_for("auth.forgot_password"))

        code = str(random.randint(1000, 9999))
        vc = VerificationCode(user.id, code)

        db.session.add(vc)
        db.session.commit()

        link = f"{request.host_url}auth/verify-code?token={vc.token}"
        msg = Message(
            "Password Reset Code",
            sender=admin_email,
            recipients=[user.email],
            html=render_template(
                "pages/auth/user/email_message.html",
                code=code,
                link=link,
                theme="system",
            ),
        )

        mail.send(msg)

        return redirect(url_for("auth.verify_code", token=vc.token))

    return render_template(
        "pages/auth/user/forgot_password.html",
        form=form,
        theme="system",
    )


@auth_bp.route("/verify-code", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def verify_code():
    token = request.args.get("token")
    vc = get_verification_code(token)

    if request.method == "POST":
        code = "".join(request.form.getlist("codefield"))

        if vc and check_password_hash(vc.code_hash, code):
            vc.is_valid = True
            db.session.commit()

            return redirect(url_for("auth.reset_password", token=token))

        return render_template(
            "pages/auth/user/verify_code.html",
            is_valid=False,
            theme="system",
        )

    if not vc:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    return render_template(
        "pages/auth/user/verify_code.html",
        theme="system",
    )


@auth_bp.route("/reset-password", methods=["GET", "POST"])
@limiter.limit("5/minute")
def reset_password():
    token = request.args.get("token")
    vc = get_verification_code(token)

    if not vc or not vc.is_valid:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.get(vc.user_id)
        user.password_hash = generate_password_hash(form.password.data)

        db.session.delete(vc)
        db.session.commit()

        flash("Password reset successfully.", "success")

        return redirect(url_for("auth.login"))

    return render_template(
        "pages/auth/user/reset_password.html",
        form=form,
        theme="system",
    )


@auth_bp.route("/admin/login", methods=["GET", "POST"])
@token_required
@limiter.limit("3/hour", methods=["POST"])
def admin_login():
    form = LoginForm()

    if form.validate_on_submit():
        admin = User.query.filter_by(email=admin_email).first()

        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            flash("Welcome, admin!", "success")

            return redirect(url_for("home.home"))

        flash("Invalid admin credentials.", "danger")
        return redirect(url_for("auth.admin_login"))

    return render_template(
        "pages/auth/admin/login.html",
        form=form,
        theme="system",
    )
