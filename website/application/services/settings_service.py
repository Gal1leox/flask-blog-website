import cloudinary.uploader
from typing import Tuple

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user

from website.domain.models.user import User, UserRole, UserTheme
from website.infrastructure.repositories.user_repository import UserRepository


class SettingsService:
    def update_profile(
        self, user: User, username: str = None, avatar_file=None
    ) -> Tuple[bool, str]:
        updated = False
        if avatar_file and avatar_file.filename:
            result = cloudinary.uploader.upload(avatar_file, resource_type="image")
            url = result.get("secure_url")
            if url:
                user.avatar_url = url
                updated = True
        if username and username != user.username:
            user.username = username
            updated = True
        if not updated:
            return False, "No changes made."
        UserRepository.save(user)
        return True, "Profile updated successfully."

    def delete_avatar(self, user: User) -> Tuple[bool, str]:
        if not user.avatar_url:
            return False, "No avatar to delete."
        user.avatar_url = None
        UserRepository.save(user)
        return True, "Avatar deleted successfully."

    def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> Tuple[bool, str]:
        if not user.password_hash:
            return False, "Password change is not available."
        if not check_password_hash(user.password_hash, current_password):
            return False, "Current password is incorrect."
        user.password_hash = generate_password_hash(new_password)
        UserRepository.save(user)
        return True, "Password updated successfully."

    def set_theme(self, user: User, theme_str: str) -> Tuple[bool, str]:
        try:
            theme_enum = UserTheme(theme_str)
        except ValueError:
            return False, "Invalid theme."
        user.theme = theme_enum
        UserRepository.save(user)
        return True, "Theme updated."

    def delete_account(self, user: User, is_admin: bool) -> Tuple[bool, str]:
        if is_admin or user.role == UserRole.ADMIN:
            return False, "Cannot delete an admin user."
        UserRepository.delete(user)
        logout_user()
        return True, "Your account has been deleted."
