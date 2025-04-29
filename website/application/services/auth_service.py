import time
import random

from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, render_template
from flask_login import login_user, logout_user
from flask_mail import Message

from website.infrastructure.repositories import (
    UserRepository,
    VerificationCodeRepository,
)
from website.domain.models import User, VerificationCode
from website.extensions import google, mail
from website.utils import generate_username


class AuthService:
    def register(self, form) -> tuple[bool, str]:
        if UserRepository.get_by_email(form.email.data):
            return False, "This email is already registered."

        user = User(
            username=generate_username(),
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
        )

        UserRepository.save(user)
        login_user(user)

        return True, "Account created!"

    def login(self, form, admin_email: str) -> tuple[bool, str]:
        user = UserRepository.get_by_email(form.email.data)

        if (
            user
            and user.email != admin_email
            and user.password_hash
            and check_password_hash(user.password_hash, form.password.data)
        ):
            login_user(user)
            return True, f"Welcome back, {user.username}!"

        return False, "Invalid credentials. Please try again."

    def logout(self) -> str:
        logout_user()
        return "You have been logged out."

    def google_authorize(self, preferred_url_scheme: str) -> tuple[None, str]:
        token = google.authorize_access_token()
        info = google.get(
            "https://openidconnect.googleapis.com/v1/userinfo", token=token
        ).json()
        email = info["email"]

        user = UserRepository.get_by_email(email)

        if user:
            user.google_id = info["sub"]
            user.avatar_url = user.avatar_url or info.get("picture")
            message = f"Welcome back, {user.username}!"
        else:
            user = User(
                username=f"usr.{int(time.time() * 1000)}",
                email=email,
                avatar_url=info.get("picture"),
                google_id=info["sub"],
            )
            UserRepository.save(user)
            message = "Account created successfully!"

        login_user(user)

        return True, message

    def send_reset_code(self, form, admin_email: str) -> tuple[bool, str]:
        user = UserRepository.get_by_email(form.email.data)

        if not user or user.email == admin_email or not user.password_hash:
            return False, "Invalid credentials. Please try again."

        code = str(random.randint(1000, 9999))
        verification_code = VerificationCode(user.id, code)
        VerificationCodeRepository.create(verification_code)

        verification_link = (
            f"{request.host_url}auth/verify-code?token={verification_code.token}"
        )
        message = Message(
            "Password Reset Code",
            sender=admin_email,
            recipients=[user.email],
            html=render_template(
                "pages/auth/user/email_message.html",
                code=code,
                verification_link=verification_link,
                theme="system",
            ),
        )
        mail.send(message)

        return True, verification_code.token

    def verify_code(self, token: str, code: str) -> bool:
        verification_code = VerificationCodeRepository.get_by_token(token)
        if (
            verification_code
            and not verification_code.is_expired()
            and check_password_hash(verification_code.code_hash, code)
        ):
            VerificationCodeRepository.invalidate(verification_code)
            return True

        return False

    def reset_password(self, token: str, new_password: str) -> tuple[bool, str]:
        verification_code = VerificationCodeRepository.get_by_token(token)
        if not verification_code or verification_code.is_expired():
            return False, "The verification link is invalid or expired."

        user = UserRepository.get_by_id(verification_code.user_id)
        user.password_hash = generate_password_hash(new_password)
        UserRepository.save(user)

        VerificationCodeRepository.invalidate(verification_code)

        return True, "Password reset successfully."

    def admin_login(self, form, admin_email: str) -> tuple[bool, str]:
        admin = UserRepository.get_by_email(admin_email)

        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            return True, "Welcome back, boss!"

        return False, "Invalid admin credentials."
