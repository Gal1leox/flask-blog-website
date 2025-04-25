from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from flask_login import login_required, current_user

from website import limiter
from website.config import Config
from website.interface.middlewares import admin_required
from website.interface.forms import CreatePostForm
from website.application.services import PostService

posts_bp = Blueprint(
    "posts",
    __name__,
    url_prefix="/posts",
    template_folder="../templates/shared/posts",
)

_service = PostService()


def get_current_user():
    return current_user if current_user.is_authenticated else None


def base_context(user):
    return {
        "is_admin": bool(user and user.role.name == "ADMIN"),
        "avatar_url": user.avatar_url if user else "",
        "token": Config.SECRET_KEY if user and user.role.name == "ADMIN" else "",
        "theme": user.theme.value if user else "system",
        "active_page": "Posts",
    }


@posts_bp.route("/", methods=["GET"])
@limiter.limit("60/minute")
def list_posts():
    user = get_current_user()
    posts = _service.list_posts()
    context = base_context(user)
    context["posts"] = posts
    return render_template("pages/shared/posts/list.html", **context)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def new_post():
    form = CreatePostForm()
    user = get_current_user()
    context = base_context(user)
    context["form"] = form

    if form.validate_on_submit():
        images = [f for f in request.files.getlist("images") if f.filename]
        ok, msg = _service.create_post(form.content.data, images, user.id)
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("public.home"))

    return render_template("pages/shared/posts/new_post.html", **context)


@posts_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def edit_post(post_id):
    user = get_current_user()
    post = _service.get_post(post_id)
    if not post or (post.author_id != user.id and user.role.name != "ADMIN"):
        flash("Unauthorized to edit this post.", "danger")
        return redirect(url_for("public.home"))

    form = CreatePostForm(obj=post)
    context = base_context(user)
    context.update(
        {
            "form": form,
            "editing": True,
            "post": post,
            "max_images": PostService.MAX_IMAGES,
        }
    )

    if form.validate_on_submit():
        delete_ids = [
            int(i) for i in request.form.getlist("delete_images") if i.isdigit()
        ]
        new_files = [f for f in request.files.getlist("images") if f.filename]
        ok, msg = _service.edit_post(
            post, form.content.data, delete_ids, new_files, user.id
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("public.home"))

    return render_template("pages/shared/posts/new_post.html", **context)


@posts_bp.route("/toggle-save/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def toggle_save(post_id):
    user = get_current_user()
    saved_flag = _service.toggle_save(post_id, user.id)
    return jsonify({"saved": saved_flag}), 200


@posts_bp.route("/saved", methods=["GET"])
@login_required
@limiter.limit("20/minute")
def saved_posts():
    user = get_current_user()
    posts = _service.list_saved(user.id)
    context = base_context(user)
    context["saved_posts"] = posts
    return render_template("pages/shared/posts/saved.html", **context)


@posts_bp.route("/delete/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("5/hour")
@admin_required
def delete_post(post_id):
    post = _service.get_post(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("posts.list_posts"))

    ok, msg = _service.delete_post(post)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("posts.list_posts"))
