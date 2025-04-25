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
from website.domain.models.user import User
from website.domain.models.verification_code import VerificationCode
from website.extensions import google, mail


class AuthService:
    def register(self, form) -> tuple[bool, str]:
        if UserRepository.get_by_email(form.email.data):
            return False, "Email already registered."

        user = User(
            username=f"usr.{int(time.time() * 1000)}",
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

        return False, "Invalid credentials."

    def logout(self) -> None:
        logout_user()

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

        return None, message

    def send_reset_code(self, form, admin_email: str) -> tuple[bool, str]:
        user = UserRepository.get_by_email(form.email.data)

        if not user or user.email == admin_email or not user.password_hash:
            return False, "Invalid email for password reset."

        code = str(random.randint(1000, 9999))
        vc = VerificationCode(user.id, code)
        VerificationCodeRepository.create(vc)

        link = f"{request.host_url}auth/verify-code?token={vc.token}"
        msg = Message(
            "Password Reset Code",
            sender=admin_email,
            recipients=[user.email],
            html=render_template(
                "pages/auth/user/email_message.html",
                code=code,
                link=link,
                theme="system",
            ),
        )
        mail.send(msg)

        return True, vc.token

    def verify_code(self, token: str, code_input: str) -> bool:
        vc = VerificationCodeRepository.get_by_token(token)

        if vc and check_password_hash(vc.code_hash, code_input):
            VerificationCodeRepository.invalidate(vc)
            return True

        return False

    def reset_password(self, token: str, new_password: str) -> bool:
        vc = VerificationCodeRepository.get_by_token(token)

        if not vc or not vc.is_valid:
            return False

        user = UserRepository.get_by_id(vc.user_id)
        user.password_hash = generate_password_hash(new_password)

        VerificationCodeRepository.delete(vc)
        UserRepository.save(user)

        return True

    def admin_login(self, form, admin_email: str) -> bool:
        admin = UserRepository.get_by_email(admin_email)

        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin)
            return True

        return False
