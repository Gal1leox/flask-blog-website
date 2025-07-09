from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required

from website import limiter
from website.utils import get_current_user, build_context
from website.presentation.forms import CreatePostForm, CommentForm
from website.presentation.middlewares import admin_required, token_required
from website.application.services import PostService, CommentService

posts_bp = Blueprint(
    "posts",
    __name__,
    url_prefix="/posts",
    template_folder="../templates",
)

post_service = PostService()




@posts_bp.route("/", methods=["GET"])
@token_required
def list_posts():
    user = get_current_user()
    posts = post_service.list_posts()

    context = build_context(user, active_page="Posts")
    context["posts"] = posts

    return render_template("pages/shared/posts/list.html", **context)


@posts_bp.route("/new", methods=["GET", "POST"])
@login_required
@limiter.limit("5/hour", methods=["POST"])
def add_post():
    user = get_current_user()
    form = CreatePostForm()
    context = build_context(user)
    context["form"] = form

    if form.validate_on_submit():
        images = [f for f in request.files.getlist("images") if f.filename]
        success, message = post_service.create_post(
            title=form.title.data,
            content=form.content.data,
            images=images,
            author_id=user.id,
            overall_rating=form.overall_rating.data,
            story_rating=form.story_rating.data,
            gameplay_rating=form.gameplay_rating.data,
            graphics_rating=form.graphics_rating.data,
            sound_design_rating=form.sound_design_rating.data,
            replay_value_rating=form.replay_value_rating.data,
            difficulty_rating=form.difficulty_rating.data,
            bug_free_rating=form.bug_free_rating.data,
            pc_requirements_rating=form.pc_requirements_rating.data,
            game_length_blocks=form.game_length_blocks.data,
        )
        flash(message, "success" if success else "danger")
        return redirect(url_for("public.home"))

    return render_template("pages/shared/admin/new_post.html", **context)


@posts_bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def edit_post(post_id):
    user = get_current_user()
    post, _ = post_service.get_post(post_id)
    if not post or (post.author_id != user.id and user.role.name != "ADMIN"):
        flash("You are not authorized to edit this post.", "danger")
        return redirect(url_for("public.home"))

    form = CreatePostForm(obj=post)
    form.editing = True

    context = build_context(user)
    context.update(
        {
            "form": form,
            "editing": True,
            "post": post,
            "post_images": post.images,
            "max_images": PostService.MAX_IMAGES,
            "title": post.title,
            "overall_rating": post.overall_rating,
            "story_rating": post.story_rating,
            "gameplay_rating": post.gameplay_rating,
            "graphics_rating": post.graphics_rating,
            "sound_design_rating": post.sound_design_rating,
            "replay_value_rating": post.replay_value_rating,
            "difficulty_rating": post.difficulty_rating,
            "bug_free_rating": post.bug_free_rating,
            "pc_requirements_rating": post.pc_requirements_rating,
            "game_length_blocks": post.game_length_blocks,
        }
    )

    if form.validate_on_submit():
        delete_ids = [
            int(i) for i in request.form.getlist("delete_images") if i.isdigit()
        ]
        new_images = [f for f in request.files.getlist("images") if f.filename]
        success, message = post_service.edit_post(
            post=post,
            title=form.title.data,
            content=form.content.data,
            delete_ids=delete_ids,
            new_files=new_images,
            author_id=user.id,
            overall_rating=form.overall_rating.data,
            story_rating=form.story_rating.data,
            gameplay_rating=form.gameplay_rating.data,
            graphics_rating=form.graphics_rating.data,
            sound_design_rating=form.sound_design_rating.data,
            replay_value_rating=form.replay_value_rating.data,
            difficulty_rating=form.difficulty_rating.data,
            bug_free_rating=form.bug_free_rating.data,
            pc_requirements_rating=form.pc_requirements_rating.data,
            game_length_blocks=form.game_length_blocks.data,
        )
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for("posts.view_post", post_id=post_id))
        else:
            return redirect(url_for("posts.edit_post"))

    return render_template("pages/shared/admin/new_post.html", **context)


@posts_bp.route("/<int:post_id>", methods=["GET"])
def view_post(post_id):
    user = get_current_user()
    post, error = post_service.get_post(post_id)
    if not post:
        flash(error, "danger")
        return redirect(url_for("public.home"))

    form = CommentForm()
    comments = CommentService().list_comments(
        post_id=post_id,
        sort=request.args.get("sort", "oldest"),
    )

    context = build_context(user)
    context.update(
        {
            "post": post,
            "comments": comments,
            "form": form,
            "is_authorized": bool(user),
        }
    )

    return render_template("pages/shared/posts/detail.html", **context)


@posts_bp.route("/toggle-save/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def toggle_save(post_id):
    user = get_current_user()
    saved = post_service.toggle_save(post_id, user.id)
    return jsonify({"saved": saved}), 200


@posts_bp.route("/saved", methods=["GET"])
@login_required
def list_saved_posts():
    user = get_current_user()
    saved_posts = post_service.list_saved(user.id)

    context = build_context(user)
    context["saved_posts"] = saved_posts

    return render_template("pages/shared/posts/saved.html", **context)


@posts_bp.route("/delete/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("5/hour")
@admin_required
def delete_post(post_id):
    post, error = post_service.get_post(post_id)
    if not post:
        flash(error, "danger")
        return redirect(url_for("posts.list_posts"))

    user = get_current_user()
    context = build_context(user)

    success, message = post_service.delete_post(post)
    flash(message, "success" if success else "danger")
    return redirect(url_for("posts.list_posts", token=context["token"]))
