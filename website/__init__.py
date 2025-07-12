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

load_dotenv(override=True)

def create_database_if_not_exists():
    # Connect to the default 'postgres' database to check/create the target database
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_LOGIN')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_SERVER')}:{os.getenv('DB_PORT', '5432')}/postgres"
        f"?sslmode=require",
        isolation_level="AUTOCOMMIT"
    )
    try:
        with engine.connect() as conn:
            # Use a DO block to conditionally create the database
            conn.execute(text("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :db_name) THEN
                        PERFORM 'CREATE DATABASE ' || quote_ident(:db_name);
                    END IF;
                END $$;
            """), {"db_name": os.getenv('DB_NAME')})
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        # If database creation fails (e.g., Render restricts access), proceed to table creation
        # This assumes the database already exists

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
