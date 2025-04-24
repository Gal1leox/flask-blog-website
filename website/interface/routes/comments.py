from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user

from website import limiter
from website.interface.forms import CommentForm
from website.application.services import CommentService

comments_bp = Blueprint(
    "comments",
    __name__,
    url_prefix="/comments",
)

_service = CommentService()


def _redirect(post_id: int):
    return redirect(url_for("posts.view_post", post_id=post_id))


@comments_bp.route("/post/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("20/minute")
def add_comment(post_id):
    form = CommentForm()
    if not form.validate_on_submit():
        flash("Comment cannot be empty.", "danger")
        return _redirect(post_id)

    parent_id = request.form.get("parent_comment_id", type=int)
    ok, msg = _service.add_comment(
        post_id,
        form.content.data,
        current_user.id,
        parent_id,
    )
    flash(msg, "success" if ok else "danger")
    return _redirect(post_id)


@comments_bp.route("/<int:comment_id>/edit", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def edit_comment(comment_id):
    new_content = request.form.get("content", "")
    ok, msg = _service.edit_comment(
        comment_id,
        current_user.id,
        new_content,
    )
    flash(msg, "success" if ok else "danger")
    post_id = CommentRepository.get(comment_id).post_id
    return _redirect(post_id)


@comments_bp.route("/<int:comment_id>/delete", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def delete_comment(comment_id):
    ok, msg = _service.delete_comment(
        comment_id,
        current_user.id,
        current_user.role,
    )
    flash(msg, "success" if ok else "danger")
    post_id = CommentRepository.get(comment_id).post_id if ok else None
    return _redirect(post_id) if post_id else _redirect(request.args.get("post_id", 0))
