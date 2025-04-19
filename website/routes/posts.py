import os

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from dotenv import load_dotenv
import cloudinary.uploader

from ..models import User, UserRole, Post, Image, SavedPost
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

        new_post = Post(content=form.content.data, author_id=current_user.id)
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


@posts_bp.route("/toggle-save/<int:post_id>", methods=["POST"])
@login_required
def toggle_save(post_id):
    user = User.query.get(current_user.id)

    existing = SavedPost.query.filter_by(user_id=user.id, post_id=post_id).first()
    try:
        if existing:
            db.session.delete(existing)
            saved = False
        else:
            new = SavedPost(user_id=user.id, post_id=post_id)
            db.session.add(new)
            saved = True

        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Something went wrong while saving the post.", "danger")
        return "", 500

    return jsonify({"saved": saved}), 200


@posts_bp.route("/saved")
@login_required
def saved_posts():
    user = User.query.get(current_user.id)

    saved = (
        db.session.query(SavedPost)
        .filter_by(user_id=user.id)
        .join(Post)
        .order_by(SavedPost.saved_at.desc())
        .all()
    )

    saved_posts = [s.post for s in saved]

    return render_template(
        "pages/shared/saved_posts.html",
        saved_posts=saved_posts,
        avatar_url=user.avatar_url,
        is_admin=user.role == UserRole.ADMIN,
        token=os.getenv("SECRET_KEY"),
        active_page="",
    )


@posts_bp.route("<int:post_id>")
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    user = User.query.get(current_user.id)

    return render_template(
        "pages/shared/selected_post.html",
        post=post,
        avatar_url=user.avatar_url if user else "",
        is_admin=user.role == UserRole.ADMIN if user else False,
        token=os.getenv("SECRET_KEY") if user else "",
        active_page="",
    )
