from typing import Tuple, Any

import cloudinary.uploader
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user

from website.domain.models.user import User, UserRole, UserTheme
from website.infrastructure.repositories.user_repository import UserRepository


class SettingsService:

    def update_profile(
        self,
        user: User,
        username: str = None,
        avatar: Any = None,
    ) -> Tuple[bool, str]:
        changes_made = False

        if avatar and avatar.filename:
            if user.avatar_public_id:
                try:
                    cloudinary.uploader.destroy(user.avatar_public_id, invalidate=True)
                except Exception:
                    pass

            upload_result = cloudinary.uploader.upload(avatar, resource_type="image")
            secure_url = upload_result.get("secure_url")
            public_id = upload_result.get("public_id")
            if secure_url and public_id:
                user.avatar_url = secure_url
                user.avatar_public_id = public_id
                changes_made = True

        if username and username != user.username:
            user.username = username
            changes_made = True

        if not changes_made:
            return False, "No changes made."

        UserRepository.save(user)
        return True, "Profile updated successfully."

    def delete_avatar(self, user: User) -> Tuple[bool, str]:
        if not user.avatar_url:
            return False, "No avatar to delete."

        if user.avatar_public_id:
            try:
                cloudinary.uploader.destroy(user.avatar_public_id, invalidate=True)
            except Exception:
                pass

        user.avatar_url = None
        user.avatar_public_id = None

        UserRepository.save(user)
        return True, "Avatar deleted successfully."

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> Tuple[bool, str]:
        if not user.password_hash:
            return False, "Password change is not available."

        if not check_password_hash(user.password_hash, current_password):
            return False, "Current password is incorrect."

        user.password_hash = generate_password_hash(new_password)
        UserRepository.save(user)
        return True, "Password updated successfully."

    def set_theme(self, user: User, theme_value: str) -> Tuple[bool, str]:
        try:
            selected_theme = UserTheme(theme_value)
        except ValueError:
            return False, "Invalid theme."

        user.theme = selected_theme
        UserRepository.save(user)
        return True, "Theme updated."

    def delete_account(self, user: User, is_admin: bool) -> Tuple[bool, str]:
        if is_admin or user.role == UserRole.ADMIN:
            return False, "Cannot delete an admin user."

        UserRepository.delete(user)
        logout_user()
        return True, "Your account has been deleted."
