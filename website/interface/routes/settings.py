from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user

from website import limiter
from website.config import Config
from website.domain.models import UserRole
from website.interface.forms import UpdateProfileForm, ChangePasswordForm
from website.application.services.settings_service import SettingsService

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings",
    template_folder="../templates/shared",
)

_service = SettingsService()


def _get_current_user():
    return current_user if current_user.is_authenticated else None


def _base_context(user):
    is_admin = bool(user and user.role == UserRole.ADMIN)
    return {
        "is_admin": is_admin,
        "avatar_url": user.avatar_url if user else "",
        "token": Config.SECRET_KEY if is_admin else "",
        "active_page": "Settings",
        "theme": user.theme.value if user else "system",
    }


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def profile_settings():
    user = _get_current_user()
    form = UpdateProfileForm()
    change_password_form = ChangePasswordForm()

    # Handle profile update (username + avatar)
    if request.method == "POST" and form.validate_on_submit():
        avatar_file = request.files.get("avatar")
        ok, msg = _service.update_profile(
            user,
            username=form.username.data,
            avatar_file=avatar_file,
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("settings.profile_settings"))

    # Pre-fill the form with existing values
    form.username.data = user.username
    form.email.data = user.email

    ctx = _base_context(user)
    ctx.update(
        {
            "form": form,
            "change_password_form": change_password_form,
            "show_change_password": bool(user.password_hash),
        }
    )
    return render_template("pages/shared/settings.html", **ctx)


@settings_bp.route("/delete-avatar", methods=["POST"])
@login_required
@limiter.limit("20/hour")
def delete_avatar():
    user = _get_current_user()
    ok, msg = _service.delete_avatar(user)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("settings.profile_settings"))


@settings_bp.route("/change-password", methods=["POST"])
@login_required
@limiter.limit("5/hour")
def change_password():
    user = _get_current_user()
    form = ChangePasswordForm()

    # Attempt to change password
    if form.validate_on_submit():
        ok, msg = _service.change_password(
            user,
            current_password=form.current_password.data,
            new_password=form.new_password.data,
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("settings.profile_settings"))

    # On error, re-render profile form + errorful change-password form
    profile_form = UpdateProfileForm(obj=user)
    profile_form.email.data = user.email  # ensure email field stays filled
    ctx = _base_context(user)
    ctx.update(
        {
            "form": profile_form,
            "change_password_form": form,
            "show_change_password": True,
        }
    )
    return render_template("pages/shared/settings.html", **ctx)


@settings_bp.route("/theme", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def set_theme():
    user = _get_current_user()
    data = request.get_json() or {}
    theme = data.get("theme")
    ok, msg = _service.set_theme(user, theme)
    if not ok:
        return msg, 400
    return "", 204


@settings_bp.route("/delete-account", methods=["POST"])
@login_required
@limiter.limit("1/day")
def delete_account():
    user = _get_current_user()

    ok, msg = _service.delete_account(user, is_admin=False)
    flash(msg, "success" if ok else "danger")

    # service.delete_account will also log the user out if successful
    redirect_to = "public.home" if ok else "settings.profile_settings"
    return redirect(url_for(redirect_to))
