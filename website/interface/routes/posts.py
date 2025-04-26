from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
)
from flask_login import current_user, login_required

from website import limiter
from website.config import Config
from website.interface.middlewares import admin_required, token_required
from website.interface.forms import CreatePostForm
from website.application.services import PostService

posts_bp = Blueprint(
    "posts",
    __name__,
    url_prefix="/posts",
    template_folder="../templates",
)

_post_svc = PostService()


def _get_current_user():
    return current_user if current_user.is_authenticated else None


def _base_context(user, active_page=""):
    """
    Build the same context you had before: avatar_url, is_admin,
    token, theme, active_page.
    """
    is_admin = bool(user and user.role.name == "ADMIN")
    return {
        "is_admin": is_admin,
        "avatar_url": user.avatar_url if user else "",
        "token": Config.SECRET_KEY if is_admin else "",
        "theme": user.theme.value if user else "system",
        "active_page": active_page,
    }


@posts_bp.route("/", methods=["GET"])
@token_required
@limiter.limit("60/minute")
def list_posts():
    user = _get_current_user()
    posts = _post_svc.list_posts()

    ctx = _base_context(user, active_page="Posts")
    ctx["posts"] = posts

    return render_template("pages/shared/posts/list.html", **ctx)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def new_post():
    user = _get_current_user()
    form = CreatePostForm()

    ctx = _base_context(user, active_page="")
    ctx["form"] = form

    if form.validate_on_submit():
        image_files = [f for f in request.files.getlist("images") if f.filename]
        ok, msg = _post_svc.create_post(
            content=form.content.data,
            images=image_files,
            author_id=user.id,
        )
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
        flash("You are not authorized to edit this post.", "danger")
        return redirect(url_for("public.home"))

    form = CreatePostForm(obj=post)
    form.editing = True
    ctx = _base_context(user, active_page="")
    ctx.update(
        {
            "form": form,
            "editing": True,
            "post": post,
            "post_images": post.images,
            "max_images": PostService.MAX_IMAGES,
        }
    )

    if form.validate_on_submit():
        delete_ids = [
            int(i) for i in request.form.getlist("delete_images") if i.isdigit()
        ]
        new_files = [f for f in request.files.getlist("images") if f.filename]

        ok, msg = _post_svc.edit_post(
            post=post,
            content=form.content.data,
            delete_ids=delete_ids,
            new_files=new_files,
            author_id=user.id,
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

    # prepare a CommentForm for the “add comment” box
    from website.interface.forms import CommentForm

    form = CommentForm()

    # load comments via your CommentService
    from website.application.services import CommentService

    comments = CommentService().list_comments(
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
    saved_posts = _post_svc.list_saved(user.id)

    ctx = _base_context(user, active_page="")
    ctx["saved_posts"] = saved_posts

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

    user = _get_current_user()
    ctx = _base_context(user, active_page="Posts")

    ok, msg = _post_svc.delete_post(post)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("posts.list_posts", **ctx))
