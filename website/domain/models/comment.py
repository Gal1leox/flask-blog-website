from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Text,
    event,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from website import db


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
    )

    parent_comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
    )
    reply_to_comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    author = relationship(
        "User",
        back_populates="comments",
        lazy="joined",
        passive_deletes=True,
    )
    post = relationship(
        "Post",
        back_populates="comments",
        lazy="joined",
        passive_deletes=True,
    )

    parent = relationship(
        "Comment",
        back_populates="replies",
        remote_side=[id],
        foreign_keys=[parent_comment_id],
        passive_deletes=True,
    )
    replies = relationship(
        "Comment",
        back_populates="parent",
        foreign_keys=[parent_comment_id],
        lazy="subquery",
        cascade="all, delete-orphan",
    )
    reply_to = relationship(
        "Comment",
        remote_side=[id],
        foreign_keys=[reply_to_comment_id],
        lazy="joined",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        parts = [
            f"ID: {self.id}",
            f"Content: {self.content}",
            f"Author ID: {self.author_id}",
            f"Post ID: {self.post_id}",
        ]
        if self.parent_comment_id:
            parts.append(f"Parent ID: {self.parent_comment_id}")
        if self.reply_to_comment_id:
            parts.append(f"Reply-To ID: {self.reply_to_comment_id}")
        return "Comment:\n  " + "\n  ".join(parts)


@event.listens_for(Comment, "before_delete")
def _delete_subcomments(mapper, connection, target: Comment):
    Session.object_session(target).query(Comment).filter_by(
        parent_comment_id=target.id
    ).delete(synchronize_session=False)


@event.listens_for(Session, "after_flush_postexec")
def _delete_orphan_comments(session: Session, _):
    existing_ids = session.query(Comment.id).subquery()

    bad_parents = session.query(Comment).filter(
        Comment.parent_comment_id.isnot(None),
        ~Comment.parent_comment_id.in_(existing_ids),
    )
    bad_replies = session.query(Comment).filter(
        Comment.reply_to_comment_id.isnot(None),
        ~Comment.reply_to_comment_id.in_(existing_ids),
    )

    for c in bad_parents.union(bad_replies):
        session.delete(c)
