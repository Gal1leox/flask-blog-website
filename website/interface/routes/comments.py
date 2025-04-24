from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user

from website import db, limiter
from website.domain.models import (
    Comment,
    User,
    UserRole,
)
from website.interface.forms import CommentForm

comments_bp = Blueprint(
    "comments",
    __name__,
    url_prefix="/comments",
)


def get_current_user():
    return User.query.get(current_user.id) if current_user.is_authenticated else None


@comments_bp.route("/post/<int:post_id>", methods=["POST"])
@login_required
@limiter.limit("20/minute")
def add_comment(post_id):
    form = CommentForm()

    if not form.validate_on_submit():
        flash("Comment cannot be empty.", "danger")
        return redirect(url_for("posts.view_post", post_id=post_id))

    parent_id = request.form.get("parent_comment_id", type=int)

    if parent_id:
        parent = Comment.query.get(parent_id)
        thread_parent = parent.parent_comment_id or parent.id
    else:
        thread_parent = None

    comment = Comment(
        content=form.content.data,
        author_id=current_user.id,
        post_id=post_id,
        parent_comment_id=thread_parent,
        reply_to_comment_id=parent_id,
    )
    db.session.add(comment)
    db.session.commit()

    flash(
        "Reply posted." if parent_id else "Comment posted.",
        "success",
    )
    return redirect(url_for("posts.view_post", post_id=post_id))


@comments_bp.route("/<int:comment_id>/edit", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if current_user.id != comment.author_id:
        flash("Cannot edit others' comments.", "danger")
        return redirect(url_for("posts.view_post", post_id=comment.post_id))

    content = request.form.get("content", "").strip()
    if content:
        comment.content = content
        db.session.commit()
        flash("Comment edited successfully.", "success")
    else:
        flash("Comment cannot be empty.", "danger")

    return redirect(url_for("posts.view_post", post_id=comment.post_id))


@comments_bp.route("/<int:comment_id>/delete", methods=["POST"])
@login_required
@limiter.limit("30/minute")
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if current_user.id != comment.author_id and current_user.role != UserRole.ADMIN:
        flash("Not authorized to delete.", "danger")
        return redirect(url_for("posts.view_post", post_id=comment.post_id))

    post_id = comment.post_id
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted.", "success")

    return redirect(url_for("posts.view_post", post_id=post_id))
