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

    author: Mapped["User"] = relationship("User", back_populates="posts")
    images: Mapped[list["Image"]] = relationship(
        "Image", secondary="post_images", back_populates="posts"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag", secondary="post_tags", back_populates="posts"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="post", cascade="all, delete", passive_deletes=True
    )
    saved_by: Mapped[list["SavedPost"]] = relationship(
        "SavedPost",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    post_images: Mapped[list["PostImage"]] = relationship(
        "PostImage",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    post_tags: Mapped[list["PostTag"]] = relationship(
        "PostTag",
        back_populates="post",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"Post Info:\n"
            f"ID: {self.id}\n"
            f"Content: {self.content}\n"
            f"Images: {[image.image_url for image in self.images]}\n"
            f"Tags: {[tag.name for tag in self.tags]}\n"
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


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
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
    post_tags: Mapped[list["PostTag"]] = relationship(
        "PostTag",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
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
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    parent_comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
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
        "Comment",
        back_populates="parent_comment",
        cascade="all, delete-orphan",
        passive_deletes=True,
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

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    saved_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="saved_posts")
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="saved_by",
        passive_deletes=True,
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


class PostTag(db.Model):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    post: Mapped["Post"] = relationship(
        "Post", back_populates="post_tags", passive_deletes=True
    )
    tag: Mapped["Tag"] = relationship(
        "Tag", back_populates="post_tags", passive_deletes=True
    )

    def __repr__(self):
        return f"PostTag Info:\nPost ID: {self.post_id}\nTag ID: {self.tag_id}"


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
