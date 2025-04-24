import os

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from website import limiter
from website.domain.models import UserRole
from website.interface.forms import UpdateProfileForm, ChangePasswordForm
from website.application.services.settings_service import SettingsService

settings_bp = Blueprint(
    "settings", __name__, url_prefix="/settings", template_folder="../templates/shared"
)

_service = SettingsService()


def _get_current_user():
    return current_user if current_user.is_authenticated else None


def _base_context(user):
    return {
        "is_admin": bool(user and user.role == UserRole.ADMIN),
        "avatar_url": user.avatar_url if user else "",
        "token": (
            os.getenv("SECRET_KEY") if user and user.role == UserRole.ADMIN else ""
        ),
        "active_page": "Settings",
        "theme": user.theme.value if user else "system",
    }


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def profile_settings():
    user = _get_current_user()
    form = UpdateProfileForm()
    pwd_form = ChangePasswordForm()

    if request.method == "POST" and form.validate_on_submit():
        avatar = request.files.get("avatar")
        ok, msg = _service.update_profile(user, form.username.data, avatar)
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("settings.profile_settings"))

    form.username.data = user.username
    form.email.data = user.email

    ctx = _base_context(user)
    ctx.update(
        {
            "form": form,
            "change_password_form": pwd_form,
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
    if form.validate_on_submit():
        ok, msg = _service.change_password(
            user, form.current_password.data, form.new_password.data
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("settings.profile_settings"))
    # show errors
    ctx = _base_context(user)
    profile_form = UpdateProfileForm(obj=user)
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
    data = request.get_json() or {}
    ok, msg = _service.set_theme(_get_current_user(), data.get("theme"))
    if not ok:
        return msg, 400
    return "", 204


@settings_bp.route("/delete-account", methods=["POST"])
@login_required
@limiter.limit("1/day")
def delete_account():
    user = _get_current_user()
    ok, msg = _service.delete_account(user, False)
    flash(msg, "success" if ok else "danger")
    redirect_to = "home.home" if ok else "settings.profile_settings"
    return redirect(url_for(redirect_to))
