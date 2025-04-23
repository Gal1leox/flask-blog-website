# website/models/post.py

from datetime import datetime
from sqlalchemy import Integer, Text, String, DateTime, ForeignKey, event, inspect
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from website import db


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author = relationship(
        "User", back_populates="posts", lazy="joined", foreign_keys=[author_id]
    )
    images = relationship(
        "Image",
        secondary="post_images",
        back_populates="posts",
        lazy="subquery",
        order_by="Image.created_at",
    )
    saved_by = relationship(
        "SavedPost",
        back_populates="post",
        lazy="subquery",
        cascade="all, delete-orphan",
    )
    post_images = relationship(
        "PostImage",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments = relationship(
        "Comment",
        back_populates="post",
        cascade="all, delete, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Post id={self.id!r} created_at={self.created_at!r}>"


class Image(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author = relationship("User", back_populates="images", foreign_keys=[author_id])
    posts = relationship("Post", secondary="post_images", back_populates="images")
    post_images = relationship(
        "PostImage",
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"<Image id={self.id!r} url={self.image_url!r}>"


class SavedPost(db.Model):
    __tablename__ = "saved_posts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_posts")
    post = relationship("Post", back_populates="saved_by")

    def __repr__(self) -> str:
        return f"<SavedPost user_id={self.user_id!r} post_id={self.post_id!r}>"


class PostImage(db.Model):
    __tablename__ = "post_images"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id", ondelete="CASCADE"), primary_key=True
    )

    post = relationship("Post", back_populates="post_images")
    image = relationship("Image", back_populates="post_images")

    def __repr__(self) -> str:
        return f"<PostImage post_id={self.post_id!r} image_id={self.image_id!r}>"


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )

    # the _thread_ parent (top-level comment or NULL)
    parent_comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    # the exact comment you clicked “Reply” on (or NULL)
    reply_to_comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # — relationships —

    author = relationship(
        "User",
        back_populates="comments",
        foreign_keys=[author_id],
        lazy="joined",
        passive_deletes=True,
    )
    post = relationship(
        "Post",
        back_populates="comments",
        foreign_keys=[post_id],
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

    # the exact comment you clicked reply on
    reply_to = relationship(
        "Comment",
        remote_side=[id],
        foreign_keys=[reply_to_comment_id],
        lazy="joined",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        p = f", parent={self.parent_comment_id}" if self.parent_comment_id else ""
        r = f", reply_to={self.reply_to_comment_id}" if self.reply_to_comment_id else ""
        return (
            f"<Comment id={self.id}{p}{r} author={self.author_id} post={self.post_id}>"
        )


# ------------------------------------------------------------------------
# cleanup hooks


@event.listens_for(Session, "after_flush_postexec")
def delete_orphan_images(session: Session, _):
    for img in (
        session.query(Image).outerjoin(PostImage).filter(PostImage.image_id == None)
    ):
        session.delete(img)


@event.listens_for(Session, "after_flush_postexec")
def delete_orphan_posts(session: Session, _):
    for p in session.query(Post).outerjoin(PostImage).filter(PostImage.post_id == None):
        if not inspect(p).deleted:
            session.delete(p)


@event.listens_for(Post, "before_delete")
def delete_post_comments(mapper, connection, target):
    Session.object_session(target).query(Comment).filter_by(post_id=target.id).delete(
        synchronize_session=False
    )


@event.listens_for(Comment, "before_delete")
def delete_subcomments(mapper, connection, target):
    Session.object_session(target).query(Comment).filter_by(
        parent_comment_id=target.id
    ).delete(synchronize_session=False)


@event.listens_for(Session, "after_flush_postexec")
def delete_orphan_comments(session: Session, flush_context):
    """
    Wipe out any Comment whose parent_comment_id or reply_to_comment_id
    points at a non-existent Comment.
    """
    # collect all real comment IDs
    existing = session.query(Comment.id).subquery()

    # find comments with a parent that no longer exists
    bad_parents = (
        session.query(Comment)
        .filter(
            Comment.parent_comment_id.isnot(None),
            ~Comment.parent_comment_id.in_(existing),
        )
        .all()
    )

    # find comments with a reply_to that no longer exists
    bad_replies = (
        session.query(Comment)
        .filter(
            Comment.reply_to_comment_id.isnot(None),
            ~Comment.reply_to_comment_id.in_(existing),
        )
        .all()
    )

    for c in bad_parents + bad_replies:
        session.delete(c)
