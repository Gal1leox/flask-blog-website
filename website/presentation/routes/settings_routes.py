from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from website import limiter
from website.utils import get_current_user, build_context
from website.application.services import SettingsService
from website.presentation.forms import UpdateProfileForm, ChangePasswordForm

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings",
    template_folder="../templates/shared",
)

settings_service = SettingsService()


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def profile_settings():
    user = get_current_user()
    profile_form = UpdateProfileForm()
    password_form = ChangePasswordForm()

    if request.method == "POST" and profile_form.validate_on_submit():
        avatar = request.files.get("avatar")
        success, message = settings_service.update_profile(
            user,
            username=profile_form.username.data,
            avatar=avatar,
        )
        flash(message, "success" if success else "danger")
        return redirect(url_for("settings.profile_settings"))

    profile_form.username.data = user.username
    profile_form.email.data = user.email

    context = build_context(user)
    context.update(
        {
            "form": profile_form,
            "change_password_form": password_form,
            "show_change_password": bool(user.password_hash),
        }
    )
    return render_template("pages/shared/settings.html", **context)


@settings_bp.route("/delete-avatar", methods=["POST"])
@login_required
@limiter.limit("20/hour")
def delete_avatar():
    user = get_current_user()
    success, message = settings_service.delete_avatar(user)

    flash(message, "success" if success else "danger")
    return redirect(url_for("settings.profile_settings"))


@settings_bp.route("/change-password", methods=["POST"])
@login_required
@limiter.limit("5/hour")
def change_password():
    user = get_current_user()
    password_form = ChangePasswordForm()

    if password_form.validate_on_submit():
        success, message = settings_service.change_password(
            user,
            current_password=password_form.current_password.data,
            new_password=password_form.new_password.data,
        )
        flash(message, "success" if success else "danger")
        return redirect(url_for("settings.profile_settings"))

    profile_form = UpdateProfileForm(obj=user)
    profile_form.email.data = user.email
    context = build_context(user)
    context.update(
        {
            "form": profile_form,
            "change_password_form": password_form,
            "show_change_password": True,
        }
    )
    return render_template("pages/shared/settings.html", **context)


@settings_bp.route("/theme", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def set_theme():
    user = get_current_user()
    data = request.get_json() or {}
    theme = data.get("theme")
    success, message = settings_service.set_theme(user, theme)

    if not success:
        return message, 400

    return "", 204


@settings_bp.route("/delete-account", methods=["POST"])
@login_required
@limiter.limit("1/day")
def delete_account():
    user = get_current_user()
    success, message = settings_service.delete_account(user, is_admin=False)

    flash(message, "success" if success else "danger")
    target = "public.home" if success else "settings.profile_settings"

    return redirect(url_for(target))
