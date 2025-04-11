import secrets
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

from sqlalchemy import Integer, Enum as SQLEnum, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_login import UserMixin

from website import db
from .enums import UserRole, UserTheme


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=True)
    google_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole), nullable=False, default=UserRole.USER
    )
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)
    theme: Mapped[str] = mapped_column(
        SQLEnum(UserTheme), nullable=False, default=UserTheme.SYSTEM
    )
    is_banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Add missing images relationship to match the back_populates in Image model.
    images: Mapped[list["Image"]] = relationship(
        "Image",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="author",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    saved_posts: Mapped[list["SavedPost"]] = relationship(
        "SavedPost",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return (
            f"User Info:\n"
            f"ID: {self.id}\n"
            f"Role: {self.role}\n"
            f"Theme: {self.theme}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


class VerificationCode(db.Model):
    __tablename__ = "verification_codes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    code_hash: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    def __init__(self, user_id: int, code: str):
        self.user_id = user_id
        self.code_hash = generate_password_hash(code)
        self.token = secrets.token_urlsafe(16)
        self.is_valid = False
        self.expires_at = datetime.utcnow() + timedelta(minutes=2)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def delete_expired():
        db.session.query(VerificationCode).filter(
            VerificationCode.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()
