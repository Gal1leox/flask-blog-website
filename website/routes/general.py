from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from dotenv import load_dotenv
import cloudinary.uploader

from ..forms.forms import UpdateProfileForm
from ..models import User, UserRole
from website import db

load_dotenv()

general_bp = Blueprint("general", __name__, template_folder="../templates")


@general_bp.route("/")
def home():
    user = User.query.get(current_user.id) if current_user.is_authenticated else None

    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN

    return render_template(
        "general/pages/home.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        active_page="Home",
    )


@general_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    form = UpdateProfileForm()
    user = User.query.get(current_user.id) if current_user.is_authenticated else None

    if request.method == "POST":
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

        if form.validate_on_submit() and user:
            user.username = form.username.data
            flash("Profile updated successfully", "success")

        db.session.commit()
        return redirect(url_for("general.settings"))

    if user:
        form.username.data = user.username

    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN

    return render_template(
        "general/pages/settings.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        active_page="",
        form=form,
    )


@general_bp.route("/settings/delete-avatar", methods=["POST"])
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

    return redirect(url_for("general.settings"))
