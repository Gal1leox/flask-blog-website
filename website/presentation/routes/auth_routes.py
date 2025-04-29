from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required

from website import limiter
from website.config import Config
from website.extensions import google
from website.presentation.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from website.infrastructure.repositories import VerificationCodeRepository
from website.presentation.middlewares import anonymous_required, token_required
from website.application.services import AuthService

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
    template_folder="../templates/auth",
)

auth_service = AuthService()
admin_email = Config.ADMIN_EMAIL
url_scheme = Config.PREFERRED_URL_SCHEME


@auth_bp.route("/google")
@anonymous_required
@limiter.limit("10/hour")
def initiate_google_login():
    redirect_uri = url_for(
        "auth.handle_google_authorize",
        _external=True,
        _scheme=url_scheme,
    )
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/google/authorize")
@anonymous_required
@limiter.limit("10/hour")
def handle_google_authorize():
    success, message = auth_service.google_authorize(url_scheme)
    flash(message, "success" if success else "danger")
    return redirect(url_for("public.home"))


@auth_bp.route("/register", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/day", methods=["POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        success, message = auth_service.register(form)
        flash(message, "success" if success else "danger")
        target = "public.home" if success else "auth.register_user"
        return redirect(url_for(target))

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
        success, message = auth_service.login(form, admin_email)
        flash(message, "success" if success else "danger")
        target = "public.home" if success else "auth.login"
        return redirect(url_for(target))

    return render_template(
        "pages/auth/user/login.html",
        form=form,
        theme="system",
    )


@auth_bp.route("/logout")
@login_required
@limiter.limit("20/hour")
def logout():
    message = auth_service.logout()
    flash(message, "success")
    return redirect(url_for("public.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        success, token_or_error = auth_service.send_reset_code(form, admin_email)
        if success:
            return redirect(url_for("auth.verify_code", token=token_or_error))

        flash(token_or_error, "danger")
        return redirect(url_for("auth.forgot_password"))

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
    if not token:
        flash("Invalid token. Please fill in your email.", "danger")
        return redirect(url_for("auth.forgot_password"))

    verification_code = VerificationCodeRepository.get_by_token(token)
    if not verification_code:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        digits = request.form.getlist("codefield")
        code = "".join(digits)
        if auth_service.verify_code(token, code):
            return redirect(url_for("auth.reset_password", token=token))

        return render_template(
            "pages/auth/user/verify_code.html",
            is_valid=False,
            token=token,
            theme="system",
        )

    return render_template(
        "pages/auth/user/verify_code.html", token=token, theme="system"
    )


@auth_bp.route("/reset-password", methods=["GET", "POST"])
@anonymous_required
@limiter.limit("5/minute", methods=["POST"])
def reset_password():
    token = request.args.get("token")
    if not token:
        flash("Invalid token. Please fill in your email.", "danger")
        return redirect(url_for("auth.forgot_password"))

    verification_code = VerificationCodeRepository.get_by_token(token)
    if not verification_code or verification_code.is_expired():
        flash(
            f"The verification link is invalid or expired.",
            "danger",
        )
        return redirect(url_for("auth.forgot_password"))

    if not verification_code.is_valid:
        flash("You must confirm verification code first.", "danger")
        return redirect(url_for("auth.verify_code", token=token))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        success, message = auth_service.reset_password(token, form.password.data)
        flash(message, "success" if success else "danger")

        if success:
            return redirect(url_for("auth.login"))

        return redirect(url_for("auth.reset_password", token=token))

    return render_template(
        "pages/auth/user/reset_password.html",
        form=form,
        token=token,
        theme="system",
    )


@auth_bp.route("/admin/login", methods=["GET", "POST"])
@token_required
@limiter.limit("3/hour", methods=["POST"])
def admin_login():
    form = LoginForm()
    token = request.args.get("token")

    if form.validate_on_submit():
        success, message = auth_service.admin_login(form, admin_email)
        flash(message, "success" if success else "danger")

        if success:
            return redirect(url_for("public.home"))

        return redirect(url_for("auth.admin_login", token=token))

    return render_template(
        "pages/auth/admin/login.html",
        form=form,
        theme="system",
    )
