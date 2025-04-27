from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user

from website import limiter
from website.interface.forms import CommentForm
from website.application.services import CommentService
from website.infrastructure.repositories import CommentRepository

comments_bp = Blueprint(
    "comments",
    __name__,
    url_prefix="/comments",
)

comment_service = CommentService()


def redirect_to_post(post_id: int):
    return redirect(url_for("posts.view_post", post_id=post_id))


@comments_bp.route("/post/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("20/minute")
def add_comment(post_id):
    form = CommentForm()

    if not form.validate_on_submit():
        flash("Comment cannot be empty.", "danger")
        return redirect_to_post(post_id)

    parent_comment_id = request.form.get("parent_comment_id", type=int)
    success, message = comment_service.add_comment(
        post_id=post_id,
        content=form.content.data,
        author_id=current_user.id,
        parent_id=parent_comment_id,
    )
    flash(message, "success" if success else "danger")
    return redirect_to_post(post_id)


@comments_bp.route("/<int:comment_id>/edit", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def edit_comment(comment_id):
    updated_text = request.form.get("content", "")
    success, message = comment_service.edit_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        new_content=updated_text,
    )

    flash(message, "success" if success else "danger")

    post_id = CommentRepository.get(comment_id).post_id
    return redirect_to_post(post_id)


@comments_bp.route("/<int:comment_id>/delete", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def delete_comment(comment_id):
    comment = CommentRepository.get(comment_id)
    post_id = comment.post_id if comment else request.args.get("post_id", type=int) or 0

    success, message = comment_service.delete_comment(
        comment_id=comment_id,
        user_id=current_user.id,
        user_role=current_user.role,
    )
    flash(message, "success" if success else "danger")

    return redirect_to_post(post_id)
