from typing import Optional

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
