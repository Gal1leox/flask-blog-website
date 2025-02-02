from datetime import datetime

from sqlalchemy import (
    Integer,
    LargeBinary,
    Text,
    String,
    DateTime,
    ForeignKey,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from website import db


class Post(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author: Mapped["User"] = relationship("User", back_populates="posts")
    images: Mapped[list["Image"]] = relationship(
        "Image", secondary="post_images", back_populates="posts"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="post_tags",
        back_populates="posts",
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete"
    )
    saved_by: Mapped[list["SavedPost"]] = relationship(
        "SavedPost", back_populates="post"
    )

    def __repr__(self):
        return (
            f"Post Info:\n"
            f"ID: {self.id}\n"
            f"Title: {self.title}\n"
            f"Content: {self.content}\n"
            f"Images: {[image.filename for image in self.images]}\n"
            f"Tags: {[tag.name for tag in self.tags]}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


class Image(db.Model):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author: Mapped["User"] = relationship("User", back_populates="images")
    posts: Mapped[list("Post")] = relationship(
        "Post", secondary="post_images", back_populates="images"
    )

    def __repr__(self):
        return (
            f"Image Info:\n"
            f"ID: {self.id}\n"
            f"Filename: {self.filename}\n"
            f"Type: {self.file_type}\n"
            f"Size: {self.file_size} bytes\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author: Mapped["User"] = relationship("User", back_populates="tags")
    posts: Mapped[list["Post"]] = relationship(
        "Post", secondary="post_tags", back_populates="tags"
    )

    def __repr__(self):
        return (
            f"Tag Info:\n"
            f"ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Color: {self.color}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


class Comment(db.Model):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id"), nullable=True
    )
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    author: Mapped["User"] = relationship("User", back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    parent_comment: Mapped["Comment"] = relationship(
        "Comment", back_populates="replies", remote_side="Comment.id"
    )
    replies: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="parent_comment"
    )

    def __repr__(self):
        return (
            f"Comment Info:\n"
            f"ID: {self.id}\n"
            f"Content: {self.content}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


class SavedPost(db.Model):
    __tablename__ = "saved_posts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="saved_posts")
    post: Mapped["Post"] = relationship("Post", back_populates="saved_by")

    def __repr__(self):
        return (
            f"Saved Post Info:\n"
            f"User ID: {self.user_id}\n"
            f"Post ID: {self.post_id}\n"
            f"Saved At: {self.saved_at}"
        )


post_images = Table(
    "post_images",
    db.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("image_id", Integer, ForeignKey("images.id"), primary_key=True),
)

post_tags = Table(
    "post_tags",
    db.metadata,
    Column("post_id", Integer, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
