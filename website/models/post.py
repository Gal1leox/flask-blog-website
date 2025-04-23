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

    author: Mapped["User"] = relationship("User", lazy="joined", back_populates="posts")
    images: Mapped[list["Image"]] = relationship(
        "Image", lazy="subquery", secondary="post_images", back_populates="posts"
    )
    saved_by: Mapped[list["SavedPost"]] = relationship(
        "SavedPost",
        lazy="subquery",
        back_populates="post",
        cascade="all, delete-orphan",
    )
    post_images: Mapped[list["PostImage"]] = relationship(
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

    def __repr__(self):
        return (
            f"Post Info:\n"
            f"ID: {self.id}\n"
            f"Content: {self.content}\n"
            f"Images: {[image.image_url for image in self.images]}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


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

    author: Mapped["User"] = relationship("User", back_populates="images")
    posts: Mapped[list["Post"]] = relationship(
        "Post", secondary="post_images", back_populates="images"
    )
    post_images: Mapped[list["PostImage"]] = relationship(
        "PostImage",
        back_populates="image",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"Image Info:\n"
            f"ID: {self.id}\n"
            f"Image URL: {self.image_url}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


class SavedPost(db.Model):
    __tablename__ = "saved_posts"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="saved_posts")
    post: Mapped["Post"] = relationship(
        "Post", back_populates="saved_by", passive_deletes=False
    )

    def __repr__(self):
        return (
            f"Saved Post Info:\n"
            f"User ID: {self.user_id}\n"
            f"Post ID: {self.post_id}\n"
            f"Saved At: {self.saved_at}"
        )


class PostImage(db.Model):
    __tablename__ = "post_images"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    image_id: Mapped[int] = mapped_column(
        ForeignKey("images.id", ondelete="CASCADE"), primary_key=True
    )

    post: Mapped["Post"] = relationship(
        "Post", back_populates="post_images", passive_deletes=True
    )
    image: Mapped["Image"] = relationship(
        "Image", back_populates="post_images", passive_deletes=True
    )

    def __repr__(self):
        return f"PostImage Info:\nPost ID: {self.post_id}\nImage ID: {self.image_id}"


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

    # The flattened parent for threading (always top-level comment or None)
    parent_comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    # The exact comment you clicked "Reply" on
    reply_to_comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    # Convenience field for grouping threads (same as parent_comment_id here)
    root_comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # -- relationships --
    author: Mapped["User"] = relationship(
        "User", lazy="joined", back_populates="comments"
    )
    post: Mapped["Post"] = relationship(
        "Post", back_populates="comments", passive_deletes=True
    )

    parent: Mapped["Comment"] = relationship(
        "Comment",
        back_populates="replies",
        remote_side=[id],
        foreign_keys=[parent_comment_id],
        passive_deletes=True,
    )

    replies: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        foreign_keys=[parent_comment_id],
        lazy="subquery",
        cascade="all, delete-orphan",
    )

    reply_to: Mapped["Comment"] = relationship(
        "Comment",
        foreign_keys=[reply_to_comment_id],
        remote_side=[id],
        lazy="joined",
    )

    root_comment: Mapped["Comment"] = relationship(
        "Comment",
        remote_side=[id],
        foreign_keys=[root_comment_id],
        lazy="joined",
    )

    def __repr__(self):
        parent = f", parent={self.parent_comment_id}" if self.parent_comment_id else ""
        replyto = (
            f", reply_to={self.reply_to_comment_id}" if self.reply_to_comment_id else ""
        )
        root = f", root={self.root_comment_id}" if self.root_comment_id else ""
        return (
            f"Comment(id={self.id}{parent}{replyto}{root}, "
            f"author={self.author_id}, post={self.post_id})"
        )


@event.listens_for(Session, "after_flush_postexec")
def delete_orphan_images(session: Session, _):
    orphan_images = (
        session.query(Image)
        .outerjoin(PostImage)
        .filter(PostImage.image_id == None)
        .all()
    )
    for image in orphan_images:
        session.delete(image)


@event.listens_for(Session, "after_flush_postexec")
def delete_orphan_posts(session: Session, _):
    orphan_posts = (
        session.query(Post).outerjoin(PostImage).filter(PostImage.post_id == None).all()
    )
    for post in orphan_posts:
        state = inspect(post)
        if state.deleted:
            continue
        try:
            session.delete(post)
        except Exception as e:
            print(f"Error deleting post {post.id}: {e}")


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
