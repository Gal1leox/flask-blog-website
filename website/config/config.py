import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration with default settings."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_NAME = os.getenv("DB_NAME")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("ADMIN_EMAIL")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME")


class DevelopmentConfig(Config):
    """Development-specific configuration."""

    DEBUG = True
    DEVELOPMENT = True
    PREFERRED_URL_SCHEME = "http"


class ProductionConfig(Config):
    """Production-specific configuration."""

    DEBUG = False
    PREFERRED_URL_SCHEME = "https"
