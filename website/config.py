import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration with default settings."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_NAME = os.getenv("DB_NAME")
    SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{os.getenv('DB_LOGIN')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_SERVER')}/{os.getenv('DB_NAME')}?"
    "driver=ODBC+Driver+17+for+SQL+Server"
)


    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
    MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("ADMIN_EMAIL")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME")
    RECAPTCHA_PUBLIC_KEY = os.getenv("RECAPTCHA_SITE_KEY")
    RECAPTCHA_PRIVATE_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
    RECAPTCHA_OPTIONS = {"theme": "light"}


class DevelopmentConfig(Config):
    """Development-specific configuration."""

    DEBUG = True
    DEVELOPMENT = True
    PREFERRED_URL_SCHEME = "http"


class ProductionConfig(Config):
    """Production-specific configuration."""

    DEBUG = False
    PREFERRED_URL_SCHEME = "https"




    # DB_NAME = os.getenv("DB_NAME")
    # DB_LOGIN = os.getenv("DB_LOGIN")
    # DB_PASSWORD = os.getenv("DB_PASSWORD")
    # DB_SERVER = os.getenv("DB_SERVER")
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_LOGIN}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False