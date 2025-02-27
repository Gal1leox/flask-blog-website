import os

from flask import Flask
from dotenv import load_dotenv

from website.config import DevelopmentConfig, ProductionConfig
from website.init import (
    db,
    login_manager,
    mail,
    limiter,
    register_blueprints,
    register_error_handlers,
    schedule_jobs,
    oauth,
)

load_dotenv()


def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "production")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin_bp.login"
    mail.init_app(app)
    limiter.init_app(app)
    oauth.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from .models import User

        with db.session() as session:
            return session.get(User, int(user_id))

    register_blueprints(app)
    register_error_handlers(app)

    with app.app_context():
        from . import models

        db.create_all()

    schedule_jobs(app)

    return app
