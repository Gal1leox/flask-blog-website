from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Integer,
    String,
    event,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from flask_login import UserMixin

from website import db
from .enums import UserRole, UserTheme


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    username: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), nullable=False, default=UserRole.USER
    )
    theme: Mapped[UserTheme] = mapped_column(
        SQLEnum(UserTheme), nullable=False, default=UserTheme.SYSTEM
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    images = relationship(
        "Image",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    posts = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    saved_posts = relationship(
        "SavedPost",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    verification_codes = relationship(
        "VerificationCode",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"User Info:\n"
            f"ID: {self.id}\n"
            f"Username: {self.username}\n"
            f"Email: {self.email}\n"
            f"Role: {self.role.value}\n"
            f"Theme: {self.theme.value}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


@event.listens_for(User, "before_delete")
def _cleanup_user_related(mapper, connection, target: User):
    session: Session = Session.object_session(target)

    from .comment import Comment
    from .image import Image
    from .post import Post, SavedPost
    from .verification_code import VerificationCode

    session.query(Comment).filter_by(author_id=target.id).delete(
        synchronize_session=False
    )
    session.query(Image).filter_by(author_id=target.id).delete(
        synchronize_session=False
    )
    session.query(Post).filter_by(author_id=target.id).delete(synchronize_session=False)
    session.query(SavedPost).filter_by(user_id=target.id).delete(
        synchronize_session=False
    )
    session.query(VerificationCode).filter_by(user_id=target.id).delete(
        synchronize_session=False
    )
