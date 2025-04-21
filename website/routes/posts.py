import os
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from dotenv import load_dotenv
import cloudinary.uploader

from ..models import User, UserRole, Post, Image, SavedPost, Comment
from ..forms import CreatePostForm, CommentForm
from ..utils import token_required, admin_required
from website import db

load_dotenv()

posts_bp = Blueprint("posts", __name__, template_folder="../templates")


@posts_bp.route("/", methods=["GET"])
@token_required
@admin_required
def all_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    user = User.query.get(current_user.id)
    theme = user.theme.value if user else "system"

    return render_template(
        "pages/shared/posts/list.html",
        posts=posts,
        avatar_url=user.avatar_url if user else "",
        is_admin=user.role == UserRole.ADMIN if user else False,
        token=os.getenv("SECRET_KEY") if user else "",
        active_page="",
        theme=theme,
    )


@posts_bp.route("/new", methods=["GET", "POST"])
@token_required
@admin_required
def new_post():
    form = CreatePostForm()
    user = User.query.get(current_user.id)
    avatar_url = user.avatar_url if user else ""
    is_admin = user.role == UserRole.ADMIN if user else False
    token = os.getenv("SECRET_KEY") if is_admin else ""
    theme = user.theme.value if user else "system"

    if form.validate_on_submit():
        image_files = request.files.getlist("images")
        image_files = [f for f in image_files if f and f.filename]  # remove empty

        if not image_files:
            flash("At least one image is required.", "danger")
            return render_template(
                "pages/shared/admin/new_post.html",
                is_admin=is_admin,
                avatar_url=avatar_url,
                token=token,
                active_page="",
                form=form,
                theme=theme,
            )

        new_post = Post(content=form.content.data, author_id=current_user.id)
        for file in image_files:
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
        theme=theme,
    )


@posts_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@token_required
@admin_required
def edit_post(post_id):
    MAX_IMAGES = 5

    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id and current_user.role != UserRole.ADMIN:
        flash("You are not authorized to edit this post.", "danger")
        return redirect(url_for("home.home"))

    form = CreatePostForm(obj=post)
    form.editing = True
    user = User.query.get(current_user.id)
    avatar_url = user.avatar_url if user else ""
    is_admin = user.role == UserRole.ADMIN if user else False
    token = os.getenv("SECRET_KEY") if is_admin else ""
    theme = user.theme.value if user else "system"

    existing_count = len(post.images)

    if form.validate_on_submit():
        delete_ids = [
            int(i) for i in request.form.getlist("delete_images") if i.isdigit()
        ]
        if delete_ids:
            for img in post.images[:]:
                if img.id in delete_ids:
                    post.images.remove(img)
                    db.session.delete(img)
            db.session.flush()
            existing_count = len(post.images)

        new_files = [f for f in request.files.getlist("images") if f and f.filename]
        new_count = len(new_files)

        if existing_count + new_count == 0:
            flash("At least one image is required.", "danger")
            return render_template(
                "pages/shared/admin/new_post.html",
                form=form,
                is_admin=is_admin,
                avatar_url=avatar_url,
                token=token,
                editing=True,
                post_id=post.id,
                post_images=post.images,
                existing_count=existing_count,
                max_images=MAX_IMAGES,
                theme=theme,
            )

        if existing_count + new_count > MAX_IMAGES:
            flash(
                f"A post can't have more than {MAX_IMAGES} images.",
                "danger",
            )
            return render_template(
                "pages/shared/admin/new_post.html",
                form=form,
                is_admin=is_admin,
                avatar_url=avatar_url,
                token=token,
                editing=True,
                post_id=post.id,
                post_images=post.images,
                existing_count=existing_count,
                max_images=MAX_IMAGES,
                theme=theme,
            )

        if form.content.data != post.content:
            post.content = form.content.data

        for file in new_files:
            result = cloudinary.uploader.upload(
                file, folder="posts", resource_type="image"
            )
            url = result.get("secure_url")
            if url:
                img = Image(author_id=current_user.id, image_url=url)
                post.images.append(img)
                db.session.add(img)

        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("home.home", token=token))

    return render_template(
        "pages/shared/admin/new_post.html",
        form=form,
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        editing=True,
        post_id=post.id,
        post_images=post.images,
        existing_count=existing_count,
        max_images=MAX_IMAGES,
        theme=theme,
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
    theme = user.theme.value if user else "system"

    saved = (
        db.session.query(SavedPost)
        .filter_by(user_id=user.id)
        .join(Post)
        .order_by(SavedPost.saved_at.desc())
        .all()
    )

    saved_posts = [s.post for s in saved]

    return render_template(
        "pages/shared/posts/saved.html",
        saved_posts=saved_posts,
        avatar_url=user.avatar_url,
        is_admin=user.role == UserRole.ADMIN,
        token=os.getenv("SECRET_KEY"),
        active_page="",
        theme=theme,
    )


@posts_bp.route("/<int:post_id>", methods=["GET", "POST"])
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            author_id=current_user.id,
            post_id=post.id,
            created_at=datetime.utcnow(),
        )
        db.session.add(comment)
        db.session.commit()
        flash("Your comment has been posted.", "success")
        return redirect(url_for("posts.view_post", post_id=post.id))

    comments = (
        Comment.query.filter_by(post_id=post.id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    user = User.query.get(current_user.id)
    return render_template(
        "pages/shared/posts/detail.html",
        post=post,
        comments=comments,
        form=form,
        avatar_url=user.avatar_url if user else "",
        is_admin=(user.role == UserRole.ADMIN) if user else False,
        token=os.getenv("SECRET_KEY") if user else "",
        active_page="",
        theme=user.theme.value if user else "system",
    )


@posts_bp.route("/comment/<int:comment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.id != comment.author_id and current_user.role != UserRole.ADMIN:
        flash("Not authorized", "danger")
        return redirect(url_for("posts.view_post", post_id=comment.post_id))
    form = CommentForm(obj=comment)
    if form.validate_on_submit():
        comment.content = form.content.data
        db.session.commit()
        flash("Comment updated", "success")
        return redirect(url_for("posts.view_post", post_id=comment.post_id))
    user = User.query.get(current_user.id)
    return render_template(
        "pages/shared/posts/comment_edit.html",
        form=form,
        comment=comment,
        avatar_url=user.avatar_url if user else "",
        theme=user.theme.value if user else "system",
    )


@posts_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user.id != comment.author_id and current_user.role != UserRole.ADMIN:
        flash("Not authorized", "danger")
        return redirect(url_for("posts.view_post", post_id=comment.post_id))
    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted", "success")
    return redirect(url_for("posts.view_post", post_id=post_id))


@posts_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    try:
        SavedPost.query.filter_by(post_id=post.id).delete()

        db.session.delete(post)
        db.session.commit()
        flash(f"Post with id {post.id} was deleted successfully.", "success")
    except Exception:
        db.session.rollback()
        flash("An error occurred while deleting the post.", "danger")

    return redirect(url_for("posts.all_posts", token=os.getenv("SECRET_KEY")))
