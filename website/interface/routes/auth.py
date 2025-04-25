from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required

from website.config import Config
from website.extensions import google
from website.interface.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from website.application.services import AuthService
from ..middlewares.auth import (
    anonymous_required,
    get_verification_code,
    token_required,
)
from website import limiter

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="../templates/auth",
)

_auth = AuthService()
_admin_email = Config.ADMIN_EMAIL
_scheme = Config.PREFERRED_URL_SCHEME


@auth_bp.route("/google")
@anonymous_required
@limiter.limit("10/hour")
def google_login():
    redirect_uri = url_for("auth.google_authorize", _external=True, _scheme=_scheme)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/authorize")
@anonymous_required
@limiter.limit("10/hour")
def google_authorize():
    _, message = _auth.google_authorize(_scheme)
    flash(message, "success")
    return redirect(url_for("public.home"))


@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/day", methods=["POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        ok, msg = _auth.register(form)
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("public.home") if ok else url_for("auth.register"))
    return render_template("pages/auth/user/register.html", form=form, theme="system")


@auth_bp.route("/login", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        ok, msg = _auth.login(form, _admin_email)
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("public.home") if ok else url_for("auth.login"))
    return render_template("pages/auth/user/login.html", form=form, theme="system")


@auth_bp.route("/logout")
@login_required
@limiter.limit("20/hour")
def logout():
    _auth.logout()
    flash("Logged out successfully.", "success")
    return redirect(url_for("public.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        ok, token = _auth.send_reset_code(form, _admin_email)
        if ok:
            return redirect(url_for("auth.verify_code", token=token))
        flash(token, "danger")
        return redirect(url_for("auth.forgot_password"))
    return render_template(
        "pages/auth/user/forgot_password.html", form=form, theme="system"
    )


@auth_bp.route("/verify-code", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def verify_code():
    token = request.args.get("token")
    if request.method == "POST":
        code = "".join(request.form.getlist("codefield"))
        if _auth.verify_code(token, code):
            return redirect(url_for("auth.reset_password", token=token))
        return render_template(
            "pages/auth/user/verify_code.html",
            is_valid=False,
            token=token,
            theme="system",
        )

    vc = get_verification_code(token)
    if not vc:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.forgot_password"))
    return render_template(
        "pages/auth/user/verify_code.html",
        token=token,
        theme="system",
    )


@auth_bp.route("/reset-password", methods=["GET", "POST"])
@limiter.limit("5/minute")
def reset_password():
    token = request.args.get("token")
    form = ResetPasswordForm()

    if form.validate_on_submit():
        if _auth.reset_password(token, form.password.data):
            flash("Password reset successfully.", "success")
            return redirect(url_for("auth.login"))
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    return render_template(
        "pages/auth/user/reset_password.html",
        form=form,
        token=token,  # ← add this
        theme="system",
    )


@auth_bp.route("/admin/login", methods=["GET", "POST"])
@token_required
@limiter.limit("3/hour", methods=["POST"])
def admin_login():
    form = LoginForm()
    token = request.args.get("token")
    if form.validate_on_submit():
        if _auth.admin_login(form, _admin_email):
            flash("Welcome, admin!", "success")
            return redirect(url_for("public.home"))
        flash("Invalid admin credentials.", "danger")
        return redirect(url_for("auth.admin_login", token=token))
    return render_template("pages/auth/admin/login.html", form=form, theme="system")
