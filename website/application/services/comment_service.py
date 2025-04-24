from typing import Optional, Tuple

from website.domain.models.comment import Comment
from website.domain.models.user import UserRole
from website.infrastructure.repositories.comment_repository import CommentRepository
from website import db


class CommentService:
    def add_comment(
        self,
        post_id: int,
        content: str,
        author_id: int,
        parent_id: Optional[int] = None,
    ) -> Tuple[bool, str]:
        if not content.strip():
            return False, "Comment cannot be empty."

        thread_parent = None
        reply_to = None
        if parent_id:
            parent = CommentRepository.get(parent_id)
            if not parent:
                return False, "Parent comment not found."
            thread_parent = parent.parent_comment_id or parent.id
            reply_to = parent_id

        comment = Comment(
            content=content,
            author_id=author_id,
            post_id=post_id,
            parent_comment_id=thread_parent,
            reply_to_comment_id=reply_to,
        )
        CommentRepository.add(comment)
        return True, "Reply posted." if parent_id else "Comment posted."

    def edit_comment(
        self, comment_id: int, user_id: int, new_content: str
    ) -> Tuple[bool, str]:
        comment = CommentRepository.get(comment_id)
        if not comment:
            return False, "Comment not found."
        if comment.author_id != user_id:
            return False, "Cannot edit others' comments."
        if not new_content.strip():
            return False, "Comment cannot be empty."

        comment.content = new_content.strip()
        db.session.commit()
        return True, "Comment edited successfully."

    def delete_comment(
        self, comment_id: int, user_id: int, user_role: UserRole
    ) -> Tuple[bool, str]:
        comment = CommentRepository.get(comment_id)
        if not comment:
            return False, "Comment not found."
        if comment.author_id != user_id and user_role != UserRole.ADMIN:
            return False, "Not authorized to delete."

        CommentRepository.delete(comment)
        return True, "Comment deleted."
