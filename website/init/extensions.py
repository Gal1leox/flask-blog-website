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
