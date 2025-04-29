import os
import re
import atexit
import urllib.parse

from authlib.integrations.flask_client import OAuth
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

import bleach
import markdown as _md
from markupsafe import Markup

import cloudinary

# -----------------------------------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------------------------------
load_dotenv()

# -----------------------------------------------------------------------------
# Flask Extensions
# -----------------------------------------------------------------------------
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
limiter = Limiter(key_func=get_remote_address)
scheduler = BackgroundScheduler()
oauth = OAuth()

# -----------------------------------------------------------------------------
# Cloudinary Configuration
# -----------------------------------------------------------------------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_SECRET"),
)

# -----------------------------------------------------------------------------
# OAuth Providers
# -----------------------------------------------------------------------------
google = oauth.register(
    name="google",
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    refresh_token_url="https://oauth2.googleapis.com/token",
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
)

# -----------------------------------------------------------------------------
# Markdown + Bleach Configuration
# -----------------------------------------------------------------------------
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    "p",
    "pre",
    "code",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "a",
    "img",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "div",
    "span",
    "br",
    "strong",
    "em",
}
ALLOWED_ATTRS = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "*": ["class"],  # allow Tailwind classes
    "a": ["href", "title", "rel", "target", "class"],
    "img": ["src", "alt", "title", "width", "height", "loading", "class"],
}
MD_EXTENSIONS = ["fenced_code", "tables", "codehilite", "attr_list"]


def init_markdown(app):
    @app.template_filter("markdown")
    def render_markdown(markdown_text: str):
        html_output = _md.markdown(
            markdown_text or "", extensions=MD_EXTENSIONS, output_format="html5"
        )
        sanitized_output = bleach.clean(
            html_output, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
        )
        return Markup(sanitized_output)

    @app.template_filter("link_hashtags")
    def link_hashtags(text: str):
        current_path = request.path
        selected_tags = request.args.getlist("tag")

        def replace_hashtag(match_obj):
            hashtag_text = match_obj.group(1)
            tag_text = hashtag_text.lstrip("#")
            updated_tags = selected_tags.copy()

            if tag_text in updated_tags:
                updated_tags.remove(tag_text)
            else:
                updated_tags.append(tag_text)

            query_string = urllib.parse.urlencode(
                [("tag", t) for t in updated_tags], doseq=True
            )
            link_url = (
                f"{current_path}?{query_string}" if query_string else current_path
            )
            active_css = "underline" if tag_text in selected_tags else ""

            return (
                f'<a href="{link_url}" '
                f'class="text-blue-500 hover:underline {active_css}">'
                f"{hashtag_text}</a>"
            )

        linked_text = re.sub(r"(#\w+)", replace_hashtag, text)
        return Markup(linked_text)


def schedule_jobs(app):
    def cleanup_expired_codes():
        from website.domain.models import VerificationCode

        with app.app_context():
            VerificationCode.delete_expired()
            db.session.commit()

    if not scheduler.get_jobs():
        scheduler.add_job(cleanup_expired_codes, "interval", minutes=2)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())


@login_manager.user_loader
def load_user(user_id: str):
    from website.domain.models import User

    with db.session() as session:
        return session.get(User, int(user_id))
