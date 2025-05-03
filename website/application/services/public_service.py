from typing import List, Tuple

from flask import render_template

from website.config import Config
from website.infrastructure.repositories.post_repository import PostRepository


class PublicService:
    def get_home_context(self, selected_tags: List[str]) -> dict:
        posts = PostRepository.get_posts_by_tags(selected_tags)
        return {"posts": posts, "selected_tags": selected_tags}

    def send_contact(self, user, form) -> Tuple[bool, str]:
        subject = (
            f"New Contact Message from {form.first_name.data} {form.last_name.data}"
        )
        html = render_template(
            "pages/shared/user/email_message.html",
            form=form,
            sender_email=user.email,
        )

        from .mailjet_service import MailjetService

        mailjet = MailjetService()

        try:
            mailjet.send_email(to=Config.ADMIN_EMAIL, subject=subject, html_body=html)
            return True, "Your message has been sent successfully!"
        except Exception as e:
            return False, str(e)
