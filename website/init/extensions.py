import os
from dotenv import load_dotenv

# Flask Extensions
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Task Scheduling
from apscheduler.schedulers.background import BackgroundScheduler

# OAuth Integration
from authlib.integrations.flask_client import OAuth

# Cloudinary Integration
import cloudinary


# Markdown + Bleach Formatting
import bleach
import markdown as _md
from markupsafe import Markup

# -----------------------------------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------------------------------
load_dotenv()

# -----------------------------------------------------------------------------
# Initialize Flask Extensions
# -----------------------------------------------------------------------------
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
limiter = Limiter(get_remote_address)
scheduler = BackgroundScheduler()
oauth = OAuth()

# -----------------------------------------------------------------------------
# Configure Cloudinary
# -----------------------------------------------------------------------------
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_SECRET"),
)

# -----------------------------------------------------------------------------
# Register OAuth Providers
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
# Markdown + Bleach configuration
# -----------------------------------------------------------------------------

# Which HTML tags and attributes you’ll allow in posts
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
    "*": ["class"],  # allow Tailwind classes on any tag
    "a": ["href", "title", "rel", "target", "class"],
    "img": ["src", "alt", "title", "width", "height", "loading", "class"],
}

MD_EXTENSIONS = [
    "fenced_code",
    "tables",
    "codehilite",
    "attr_list",
]


def init_markdown(app):
    @app.template_filter("markdown")
    def render_md(text: str):
        # 1) convert Markdown→HTML (raw HTML is passed through)
        raw = _md.markdown(text or "", extensions=MD_EXTENSIONS, output_format="html5")
        # 2) sanitize any unwanted tags/attrs
        clean = bleach.clean(
            raw, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True
        )
        # 3) mark safe for Jinja
        return Markup(clean)
