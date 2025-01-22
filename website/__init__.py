from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getenv("DB_NAME")}"

    db.init_app(app)

    from .models.admin import Admin
    from .models.post import Post

    with app.app_context():
        db.create_all()

    return app
