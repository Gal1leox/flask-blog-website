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
    def render_md(text: str):
        raw_html = _md.markdown(
            text or "", extensions=MD_EXTENSIONS, output_format="html5"
        )
        clean_html = bleach.clean(
            raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
        )
        return Markup(clean_html)

    @app.template_filter("link_hashtags")
    def link_hashtags(text: str):
        path = request.path
        current_tags = request.args.getlist("tag")

        def _replace(match):
            hashtag = match.group(1)
            tag = hashtag.lstrip("#")
            tags = current_tags.copy()

            if tag in tags:
                tags.remove(tag)
            else:
                tags.append(tag)

            qs = urllib.parse.urlencode([("tag", t) for t in tags], doseq=True)
            href = f"{path}?{qs}" if qs else path
            css = "underline" if tag in current_tags else ""

            return f'<a href="{href}" class="text-blue-500 hover:underline {css}">{hashtag}</a>'

        linked = re.sub(r"(#\w+)", _replace, text)
        return Markup(linked)


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
