import os
from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
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

def create_database_if_not_exists():
    db_login = os.getenv("DB_LOGIN")
    db_password = os.getenv("DB_PASSWORD")
    db_server = os.getenv("DB_SERVER")
    db_name = os.getenv("DB_NAME")

    engine = create_engine(
        f"mssql+pyodbc://{db_login}:{db_password}@{db_server}/master?driver=ODBC+Driver+17+for+SQL+Server",
        isolation_level="AUTOCOMMIT"
    )


    create_db_sql = f"""
    IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{db_name}')
    BEGIN
        CREATE DATABASE [{db_name}];
    END
    """

    with engine.connect() as conn:
        conn.execute(text(create_db_sql))

def create_app():
    create_database_if_not_exists()
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
