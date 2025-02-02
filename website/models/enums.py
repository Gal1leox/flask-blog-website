from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class UserTheme(Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class NotificationType(Enum):
    COMMENT = "comment"
    MENTION = "mention"
    RELEASE = "release"


class NotificationStatus(Enum):
    UNREAD = "unread"
    READ = "read"
