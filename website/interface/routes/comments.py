from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user

from website import limiter
from website.interface.forms import CommentForm
from website.application.services import CommentService
from website.infrastructure.repositories.comment_repository import CommentRepository

comments_bp = Blueprint(
    "comments",
    __name__,
    url_prefix="/comments",
)

_comment_svc = CommentService()


def _redirect_to_post(post_id: int):
    return redirect(url_for("posts.view_post", post_id=post_id))


@comments_bp.route("/post/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("20/minute")
def add_comment(post_id):
    form = CommentForm()
    if not form.validate_on_submit():
        flash("Comment cannot be empty.", "danger")
        return _redirect_to_post(post_id)

    parent_id = request.form.get("parent_comment_id", type=int)
    ok, msg = _comment_svc.add_comment(
        post_id,
        form.content.data,
        current_user.id,
        parent_id,
    )
    flash(msg, "success" if ok else "danger")
    return _redirect_to_post(post_id)


@comments_bp.route("/<int:comment_id>/edit", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def edit_comment(comment_id):
    new_content = request.form.get("content", "")
    ok, msg = _comment_svc.edit_comment(
        comment_id,
        current_user.id,
        new_content,
    )
    flash(msg, "success" if ok else "danger")

    # grab post_id so we can bounce back
    post_id = CommentRepository.get(comment_id).post_id
    return _redirect_to_post(post_id)


@comments_bp.route("/<int:comment_id>/delete", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def delete_comment(comment_id):
    ok, msg = _comment_svc.delete_comment(
        comment_id,
        current_user.id,
        current_user.role,
    )
    flash(msg, "success" if ok else "danger")

    # if delete succeeded, get post_id, else fallback to query string
    if ok:
        post_id = CommentRepository.get(comment_id).post_id
    else:
        post_id = request.args.get("post_id", type=int) or 0

    return _redirect_to_post(post_id)
