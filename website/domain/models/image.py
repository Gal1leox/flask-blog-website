from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    event,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from website import db
from .post import Post, PostImage


class Image(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    public_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    author = relationship(
        "User",
        back_populates="images",
        lazy="joined",
        passive_deletes=True,
    )
    posts = relationship(
        "Post",
        secondary="post_images",
        back_populates="images",
        lazy="subquery",
        overlaps="post,post_images"
    )
    post_images = relationship(
        "PostImage",
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="images"
    )

    def __repr__(self) -> str:
        return (
            f"Image:\n"
            f"ID: {self.id}\n"
            f"URL: {self.url!r}\n"
            f"Author ID: {self.author_id}\n"
            f"Created At: {self.created_at}"
        )


@event.listens_for(Session, "after_flush_postexec")
def cleanup_orphaned(session: Session, _):
    orphaned_images = (
        session.query(Image)
        .outerjoin(PostImage)
        .filter(PostImage.image_id.is_(None))
        .all()
    )
    for image in orphaned_images:
        session.delete(image)

    orphaned_posts = (
        session.query(Post)
        .outerjoin(PostImage)
        .filter(PostImage.post_id.is_(None))
        .all()
    )
    for post in orphaned_posts:
        session.delete(post)
