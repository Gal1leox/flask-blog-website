from datetime import datetime

from sqlalchemy import Integer, String, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from website import db
from .enums import NotificationType, NotificationStatus


class Notification(db.Model):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str] = mapped_column(String(40), nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user_notifications: Mapped[list["UserNotification"]] = relationship(
        "UserNotification", back_populates="notification"
    )

    def __repr__(self):
        return (
            f"Notification Info:\n"
            f"ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Type: {self.type}\n"
            f"Created At: {self.created_at}\n"
            f"Updated At: {self.updated_at}"
        )


class UserNotification(db.Model):
    __tablename__ = "user_notifications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    notification_id: Mapped[int] = mapped_column(
        ForeignKey("notifications.id"), primary_key=True
    )
    status: Mapped[NotificationStatus] = mapped_column(
        SQLEnum(NotificationStatus),
        nullable=False,
        default=NotificationStatus.UNREAD,
    )
    read_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notifications")
    notification: Mapped["Notification"] = relationship(
        "Notification", back_populates="user_notifications"
    )

    def __repr__(self):
        return (
            f"User Notification Info:\n"
            f"User ID: {self.user_id}\n"
            f"Notification ID: {self.notification_id}\n"
            f"Status: {self.status}\n"
            f"Read At: {self.read_at}"
        )
