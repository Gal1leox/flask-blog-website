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
from website.interface.forms import CreatePostForm, CommentForm
from website.application.services import PostService, CommentService

posts_bp = Blueprint(
    "posts",
    __name__,
    url_prefix="/posts",
    template_folder="../templates",
)

_post_svc = PostService()
_comment_svc = CommentService()


def _get_current_user():
    return current_user if current_user.is_authenticated else None


def _base_context(user, active_page="Posts"):
    return {
        "is_admin": bool(user and user.role.name == "ADMIN"),
        "avatar_url": user.avatar_url if user else "",
        "token": Config.SECRET_KEY if user and user.role.name == "ADMIN" else "",
        "theme": user.theme.value if user else "system",
        "active_page": active_page,
    }


@posts_bp.route("/", methods=["GET"])
@limiter.limit("60/minute")
def list_posts():
    user = _get_current_user()
    posts = _post_svc.list_posts()
    ctx = _base_context(user)
    ctx["posts"] = posts
    return render_template("pages/shared/posts/list.html", **ctx)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def new_post():
    form = CreatePostForm()
    user = _get_current_user()
    ctx = _base_context(user)
    ctx["form"] = form

    if form.validate_on_submit():
        images = [f for f in request.files.getlist("images") if f.filename]
        ok, msg = _post_svc.create_post(form.content.data, images, user.id)
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("public.home"))

    return render_template("pages/shared/admin/new_post.html", **ctx)


@posts_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def edit_post(post_id):
    user = _get_current_user()
    post = _post_svc.get_post(post_id)
    if not post or (post.author_id != user.id and user.role.name != "ADMIN"):
        flash("Unauthorized to edit this post.", "danger")
        return redirect(url_for("public.home"))

    form = CreatePostForm(obj=post)
    ctx = _base_context(user)
    ctx.update(
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
        ok, msg = _post_svc.edit_post(
            post, form.content.data, delete_ids, new_files, user.id
        )
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("public.home"))

    return render_template("pages/shared/admin/new_post.html", **ctx)


@posts_bp.route("/<int:post_id>", methods=["GET"])
@limiter.limit("60/minute")
def view_post(post_id):
    user = _get_current_user()
    post = _post_svc.get_post(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("posts.list_posts"))

    # prepare comment form + load comments
    form = CommentForm()
    comments = _comment_svc.list_comments(
        post_id, sort=request.args.get("sort", "oldest")
    )

    ctx = _base_context(user, active_page="")
    ctx.update(
        {
            "post": post,
            "comments": comments,
            "form": form,
            "is_authorized": bool(user),
        }
    )
    return render_template("pages/shared/posts/detail.html", **ctx)


@posts_bp.route("/toggle-save/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def toggle_save(post_id):
    user = _get_current_user()
    saved_flag = _post_svc.toggle_save(post_id, user.id)
    return jsonify({"saved": saved_flag}), 200


@posts_bp.route("/saved", methods=["GET"])
@login_required
@limiter.limit("20/minute")
def saved_posts():
    user = _get_current_user()
    posts = _post_svc.list_saved(user.id)
    ctx = _base_context(user)
    ctx["saved_posts"] = posts
    return render_template("pages/shared/posts/saved.html", **ctx)


@posts_bp.route("/delete/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("5/hour")
@admin_required
def delete_post(post_id):
    post = _post_svc.get_post(post_id)
    if not post:
        flash("Post not found.", "danger")
        return redirect(url_for("posts.list_posts"))

    ok, msg = _post_svc.delete_post(post)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("posts.list_posts"))
