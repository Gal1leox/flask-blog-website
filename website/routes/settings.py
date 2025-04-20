import os

import cloudinary.uploader
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required, logout_user
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

from ..forms.forms import UpdateProfileForm, ChangePasswordForm
from ..models import User, UserRole
from website import db

load_dotenv()

settings_bp = Blueprint("settings", __name__, template_folder="../templates")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
def settings():
    form = UpdateProfileForm()
    change_password_form = ChangePasswordForm()

    user = User.query.get(current_user.id) if current_user.is_authenticated else None
    theme = user.theme.value if user else "system"

    if request.method == "POST":
        if form.validate_on_submit():
            if "avatar" in request.files:
                file_to_upload = request.files["avatar"]
                if file_to_upload and file_to_upload.filename != "":
                    try:
                        upload_result = cloudinary.uploader.upload(
                            file_to_upload, resource_type="image"
                        )
                        user.avatar_url = upload_result.get("secure_url")
                        flash("Avatar updated successfully", "success")
                    except Exception as e:
                        flash("Error uploading image: " + str(e), "danger")

            if user and form.username.data != user.username:
                user.username = form.username.data
                flash("Profile updated successfully", "success")

            db.session.commit()
            return redirect(url_for("settings.settings"))

    if user:
        form.username.data = user.username
        form.email.data = user.email

    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN
    token = os.getenv("SECRET_KEY") if is_admin else ""
    show_change_password = True if user and user.password_hash else False

    return render_template(
        "pages/shared/settings.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        active_page="",
        form=form,
        change_password_form=change_password_form,
        show_change_password=show_change_password,
        theme=theme,
    )


@settings_bp.route("/delete-avatar", methods=["POST"])
@login_required
def delete_avatar():
    form = UpdateProfileForm()
    user = User.query.get(current_user.id) if current_user.is_authenticated else None
    if user:
        form.username.data = user.username

    if user:
        user.avatar_url = None
        db.session.commit()
        flash("Avatar deleted successfully", "success")
    else:
        flash("User not found", "error")

    return redirect(url_for("settings.settings"))


@settings_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    change_password_form = ChangePasswordForm()
    user = User.query.get(current_user.id) if current_user.is_authenticated else None
    theme = user.theme.value if user else "system"

    if not (user and user.password_hash):
        flash("Password change is not available for your account.", "danger")
        return redirect(url_for("settings.settings"))

    if change_password_form.validate_on_submit():
        if not check_password_hash(
            user.password_hash, change_password_form.current_password.data
        ):
            flash("Current password is incorrect.", "danger")
        else:
            user.password_hash = generate_password_hash(
                change_password_form.new_password.data
            )
            db.session.commit()
            flash("Password updated successfully.", "success")
            return redirect(url_for("settings.settings"))

    profile_form = UpdateProfileForm()
    profile_form.username.data = user.username
    profile_form.email.data = user.email
    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN
    token = os.getenv("SECRET_KEY") if is_admin else ""
    show_change_password = True if user and user.password_hash else False

    return render_template(
        "pages/shared/settings.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        active_page="",
        form=profile_form,
        change_password_form=change_password_form,
        show_change_password=show_change_password,
        theme=theme,
    )


@settings_bp.route("/delete-account", methods=["POST"])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    if user and user.role == UserRole.ADMIN:
        flash("Cannot delete an admin user.", "danger")
        return redirect(url_for("home.home"))

    db.session.delete(user)
    db.session.commit()

    logout_user()

    flash("Your account has been deleted.", "success")
    return redirect(url_for("home.home"))
