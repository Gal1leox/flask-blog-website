from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.getenv("DB_NAME")}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = os.getenv("SECRET_KEY")

    @app.errorhandler(404)
    def not_found_page(error):
        return render_template("errors/404.html"), 404

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "admin_bp.login"

    @login_manager.user_loader
    def load_user(id):
        from .models import Admin

        return Admin.query.get(int(id))

    from .routes import home_bp, admin_bp

    app.register_blueprint(admin_bp, url_prefix="/admin/")
    app.register_blueprint(home_bp, url_prefix="/")

    with app.app_context():
        from .models import Admin, Post

        db.create_all()

    return app
