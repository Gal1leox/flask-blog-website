import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration with default settings."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Development-specific configuration."""

    DEBUG = True
    DEVELOPMENT = True


class ProductionConfig(Config):
    """Production-specific configuration."""

    DEBUG = False
