import os

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from dotenv import load_dotenv
import cloudinary.uploader

from ..models import User, UserRole, Post, Image
from ..forms import CreatePostForm
from ..utils import token_required, admin_required
from website import db

load_dotenv()

posts_bp = Blueprint("posts", __name__, template_folder="../templates")


@posts_bp.route("/new", methods=["GET", "POST"])
@token_required
@admin_required
def new_post():
    form = CreatePostForm()
    user = User.query.get(current_user.id) if current_user.is_authenticated else None
    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN
    token = os.getenv("SECRET_KEY") if is_admin else ""

    if form.validate_on_submit():
        image_files = request.files.getlist("images")
        if not image_files or len(image_files) == 0:
            flash("At least one image is required.", "error")
            return render_template(
                "pages/shared/admin/new_post.html",
                is_admin=is_admin,
                avatar_url=avatar_url,
                token=token,
                active_page="",
                form=form,
            )

        new_post = Post(
            title=form.title.data, content=form.content.data, author_id=current_user.id
        )
        for file in image_files:
            if file:
                result = cloudinary.uploader.upload(
                    file, folder="posts", resource_type="image"
                )
                secure_url = result.get("secure_url")
                if secure_url:
                    new_image = Image(author_id=current_user.id, image_url=secure_url)
                    new_post.images.append(new_image)
                    db.session.add(new_image)

        db.session.add(new_post)
        db.session.commit()
        flash("Post created successfully!", "success")
        return redirect(url_for("home.home", token=token))

    return render_template(
        "pages/shared/admin/new_post.html",
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        active_page="",
        form=form,
    )
