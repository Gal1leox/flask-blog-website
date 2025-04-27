from typing import List, Optional

from website import db
from website.domain.models import Comment


class CommentRepository:
    @staticmethod
    def get(comment_id: int) -> Optional[Comment]:
        return Comment.query.get(comment_id)

    @staticmethod
    def add(comment: Comment) -> None:
        db.session.add(comment)
        db.session.commit()

    @staticmethod
    def delete(comment: Comment) -> None:
        db.session.delete(comment)
        db.session.commit()

    @staticmethod
    def list_by_post(post_id: int, order: str = "asc") -> List[Comment]:
        query = Comment.query.filter_by(post_id=post_id)

        if order == "desc":
            query = query.order_by(Comment.created_at.desc())
        else:
            query = query.order_by(Comment.created_at.asc())

        return query.all()
