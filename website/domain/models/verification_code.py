import secrets
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from website import db


class VerificationCode(db.Model):
    __tablename__ = "verification_codes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    code_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        nullable=False,
    )
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="verification_codes",
        passive_deletes=True,
    )

    def __init__(self, user_id: int, code: str):
        self.user_id = user_id
        self.code_hash = generate_password_hash(code)
        self.token = secrets.token_urlsafe(16)
        self.is_valid = False
        self.expires_at = datetime.utcnow() + timedelta(minutes=2)

    def __repr__(self) -> str:
        return (
            f"VerificationCode:\n"
            f"ID: {self.id}\n"
            f"User ID: {self.user_id}\n"
            f"Token: {self.token}\n"
            f"Valid: {self.is_valid}\n"
            f"Expires At: {self.expires_at}"
        )

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @staticmethod
    def delete_expired() -> None:
        db.session.query(VerificationCode).filter(
            VerificationCode.expires_at < datetime.utcnow()
        ).delete()
        db.session.commit()
