import cloudinary.uploader

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import current_user, login_required

from website import db, limiter
from website.config import Config
from website.domain.models import User, UserRole, Post, Image, SavedPost
from website.forms import CreatePostForm

posts_bp = Blueprint(
    "posts",
    __name__,
    url_prefix="/posts",
    template_folder="../templates/shared/admin",
)


def get_current_user():
    return User.query.get(current_user.id) if current_user.is_authenticated else None


def base_context(user):
    return {
        "is_admin": bool(user and user.role == UserRole.ADMIN),
        "avatar_url": user.avatar_url if user else "",
        "token": Config.SECRET_KEY if user and user.role == UserRole.ADMIN else "",
        "theme": user.theme.value if user else "system",
        "active_page": "Posts",
    }


@posts_bp.route("/", methods=["GET"])
@limiter.limit("60/minute")
def list_posts():
    user = get_current_user()
    posts = Post.query.order_by(Post.created_at.desc()).all()

    context = base_context(user)
    context.update({"posts": posts})

    return render_template("pages/shared/posts/list.html", **context)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def new_post():
    form = CreatePostForm()
    user = get_current_user()
    context = base_context(user)
    context.update({"form": form})

    if form.validate_on_submit():
        images = [f for f in request.files.getlist("images") if f.filename]
        if not images:
            flash("At least one image is required.", "danger")
            return render_template("pages/shared/admin/new_post.html", **context)

        post = Post(content=form.content.data, author_id=user.id)
        for img in images:
            res = cloudinary.uploader.upload(img, folder="posts", resource_type="image")
            url = res.get("secure_url")
            if url:
                image = Image(author_id=user.id, image_url=url)
                post.images.append(image)
                db.session.add(image)

        db.session.add(post)
        db.session.commit()

        flash("Post created successfully!", "success")
        return redirect(url_for("home.home"))

    return render_template("pages/shared/admin/new_post.html", **context)


@posts_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def edit_post(post_id):
    MAX_IMAGES = 5
    user = get_current_user()
    post = Post.query.get_or_404(post_id)

    if post.author_id != user.id and user.role != UserRole.ADMIN:
        flash("Unauthorized to edit this post.", "danger")
        return redirect(url_for("home.home"))

    form = CreatePostForm(obj=post)
    context = base_context(user)
    context.update(
        {
            "form": form,
            "editing": True,
            "post_id": post.id,
            "post_images": post.images,
            "max_images": MAX_IMAGES,
        }
    )

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

        new_files = [f for f in request.files.getlist("images") if f.filename]
        if existing_count + len(new_files) == 0:
            flash("At least one image is required.", "danger")
            return render_template("pages/shared/admin/new_post.html", **context)

        if existing_count + len(new_files) > MAX_IMAGES:
            flash(f"Max {MAX_IMAGES} images allowed.", "danger")
            return render_template("pages/shared/admin/new_post.html", **context)

        if form.content.data != post.content:
            post.content = form.content.data

        for img in new_files:
            res = cloudinary.uploader.upload(img, folder="posts", resource_type="image")
            url = res.get("secure_url")
            if url:
                new_img = Image(author_id=user.id, image_url=url)
                post.images.append(new_img)
                db.session.add(new_img)

        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for("home.home"))

    return render_template("pages/shared/admin/new_post.html", **context)


@posts_bp.route("/toggle-save/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def toggle_save():
    user = get_current_user()
    saved = SavedPost.query.filter_by(user_id=user.id, post_id=post_id).first()

    try:
        if saved:
            db.session.delete(saved)
            saved_flag = False
        else:
            db.session.add(SavedPost(user_id=user.id, post_id=post_id))
            saved_flag = True

        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Error saving post.", "danger")
        return "", 500

    return jsonify({"saved": saved_flag}), 200


@posts_bp.route("/saved", methods=["GET"])
@login_required
@limiter.limit("20/minute")
def saved_posts():
    user = get_current_user()
    saved_items = (
        SavedPost.query.filter_by(user_id=user.id)
        .join(Post)
        .order_by(SavedPost.saved_at.desc())
        .all()
    )
    posts = [s.post for s in saved_items]

    context = base_context(user)
    context.update({"saved_posts": posts})

    return render_template("pages/shared/posts/saved.html", **context)


@posts_bp.route("/delete/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("5/hour")
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    try:
        SavedPost.query.filter_by(post_id=post.id).delete()
        db.session.delete(post)
        db.session.commit()
        flash(f"Post {post.id} deleted.", "success")
    except Exception:
        db.session.rollback()
        flash("Error deleting post.", "danger")

    return redirect(url_for("posts.list_posts"))
