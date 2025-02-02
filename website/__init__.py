from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from .config import DevelopmentConfig

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "admin_bp.login"

    @login_manager.user_loader
    def load_admin(user_id):
        from .models import User

        with db.session() as session:
            return session.get(User, int(user_id))

    from .routes import general_bp, auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth/")
    app.register_blueprint(general_bp, url_prefix="/")

    with app.app_context():
        from . import models

        db.create_all()

    @app.errorhandler(404)
    def not_found_page(error):
        return render_template("errors/pages/404.html"), 404

    return app
