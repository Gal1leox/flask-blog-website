import os

from flask import Flask
from dotenv import load_dotenv

from website.config import DevelopmentConfig, ProductionConfig
from website.utils import timesince
from website.extensions import (
    db,
    login_manager,
    mail,
    limiter,
    schedule_jobs,
    oauth,
    init_markdown,
)
from website.presentation.routes import (
    register_blueprints,
)
from website.errors import (
    register_error_handlers,
)

load_dotenv()


def create_app():
    app = Flask(
        __name__,
        static_folder="presentation/static",
        template_folder="presentation/templates",
    )
    app.url_map.strict_slashes = False
    app.jinja_env.filters["timesince"] = timesince

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

    register_blueprints(app)
    register_error_handlers(app)

    with app.app_context():
        from website.domain import models

        db.create_all()

    schedule_jobs(app)

    return app
