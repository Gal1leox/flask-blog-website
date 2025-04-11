from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class UserTheme(Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"
