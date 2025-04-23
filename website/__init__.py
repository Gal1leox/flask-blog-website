import os
from datetime import datetime

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
    init_markdown,
)

load_dotenv()


def timesince(dt, default="just now"):
    now = datetime.utcnow()
    diff = now - dt
    periods = [
        (diff.days // 365, "year"),
        ((diff.days % 365) // 30, "month"),
        ((diff.days % 30), "day"),
        (diff.seconds // 3600, "hour"),
        ((diff.seconds % 3600) // 60, "minute"),
        (diff.seconds % 60, "second"),
    ]
    for amount, name in periods:
        if amount:
            return f"{amount} {name}{'s ago' if amount > 1 else ''}"
    return default


def create_app():
    app = Flask(__name__)

    env = os.getenv("FLASK_ENV", "production")
    if env == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "danger"
    mail.init_app(app)
    limiter.init_app(app)
    oauth.init_app(app)
    init_markdown(app)

    app.jinja_env.filters["timesince"] = timesince

    @login_manager.user_loader
    def load_user(user_id):
        from website.domain.models import User

        with db.session() as session:
            return session.get(User, int(user_id))

    register_blueprints(app)
    register_error_handlers(app)

    with app.app_context():
        from website.domain import models

        db.create_all()

    schedule_jobs(app)

    return app
