import os

import cloudinary.uploader
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from website import db, limiter
from website.interface.forms import UpdateProfileForm, ChangePasswordForm
from website.domain.models import User, UserRole, UserTheme

settings_bp = Blueprint(
    "settings",
    __name__,
    url_prefix="/settings",
    template_folder="../templates/shared",
)


def get_current_user():
    return User.query.get(current_user.id) if current_user.is_authenticated else None


def base_context(user):
    return {
        "is_admin": user and user.role == UserRole.ADMIN,
        "avatar_url": user.avatar_url if user else "",
        "token": (
            os.getenv("SECRET_KEY") if user and user.role == UserRole.ADMIN else ""
        ),
        "active_page": "",
        "theme": user.theme.value if user else "system",
    }


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def profile_settings():
    form = UpdateProfileForm()
    change_password_form = ChangePasswordForm()

    user = get_current_user()

    if request.method == "POST" and form.validate_on_submit():
        if "avatar" in request.files:
            file = request.files["avatar"]
            if file and file.filename:
                result = cloudinary.uploader.upload(file, resource_type="image")
                user.avatar_url = result.get("secure_url")
                flash("Avatar updated successfully.", "success")

        if form.username.data and form.username.data != user.username:
            user.username = form.username.data
            flash("Profile updated successfully.", "success")

        db.session.commit()

        return redirect(url_for("settings.profile_settings"))

    form.username.data = user.username
    form.email.data = user.email

    context = base_context(user)
    context.update(
        {
            "form": form,
            "change_password_form": change_password_form,
            "show_change_password": bool(user.password_hash),
        }
    )

    return render_template("pages/shared/settings.html", **context)


@settings_bp.route("/delete-avatar", methods=["POST"])
@login_required
@limiter.limit("20/hour")
def delete_avatar():
    user = get_current_user()

    if user:
        user.avatar_url = None
        db.session.commit()
        flash("Avatar deleted successfully.", "success")
    else:
        flash("User not found.", "danger")

    return redirect(url_for("settings.profile_settings"))


@settings_bp.route("/change-password", methods=["POST"])
@login_required
@limiter.limit("5/hour")
def change_password():
    form = ChangePasswordForm()
    user = get_current_user()

    if not (user and user.password_hash):
        flash("Password change is not available.", "danger")
        return redirect(url_for("settings.profile_settings"))

    if form.validate_on_submit():
        if not check_password_hash(user.password_hash, form.current_password.data):
            flash("Current password is incorrect.", "danger")
        else:
            user.password_hash = generate_password_hash(form.new_password.data)
            db.session.commit()
            flash("Password updated successfully.", "success")

            return redirect(url_for("settings.profile_settings"))

    profile_form = UpdateProfileForm()
    profile_form.username.data = user.username
    profile_form.email.data = user.email

    context = base_context(user)
    context.update(
        {
            "form": profile_form,
            "change_password_form": form,
            "show_change_password": True,
        }
    )

    return render_template("pages/shared/settings.html", **context)


@settings_bp.route("/theme", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def set_theme():
    data = request.get_json() or {}
    theme = data.get("theme")

    try:
        theme_enum = UserTheme(theme)
    except ValueError:
        return "Invalid theme", 400

    user = get_current_user()
    user.theme = theme_enum
    db.session.commit()

    return "", 204


@settings_bp.route("/delete-account", methods=["POST"])
@login_required
@limiter.limit("1/day")
def delete_account():
    user = get_current_user()

    if user.role == UserRole.ADMIN:
        flash("Cannot delete an admin user.", "danger")
        return redirect(url_for("home.home"))

    db.session.delete(user)
    db.session.commit()

    logout_user()
    flash("Your account has been deleted.", "success")

    return redirect(url_for("home.home"))
