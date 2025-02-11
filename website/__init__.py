import atexit

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from apscheduler.schedulers.background import BackgroundScheduler

from .config import DevelopmentConfig

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
limiter = Limiter(get_remote_address)
scheduler = BackgroundScheduler()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "admin_bp.login"
    mail.init_app(app)
    limiter.init_app(app)

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

    @app.errorhandler(429)
    def rate_limit_page(error):
        return render_template("errors/pages/429.html"), 429

    def cleanup_expired_codes():
        from .models import VerificationCode

        with app.app_context():
            VerificationCode.delete_expired()
            db.session.commit()

    if scheduler.state == 0:
        scheduler.add_job(cleanup_expired_codes, "interval", minutes=5)
        scheduler.start()

        atexit.register(lambda: scheduler.shutdown())

    if not scheduler.running:
        scheduler.add_job(cleanup_expired_codes, "interval", minutes=5)
        scheduler.start()

        atexit.register(lambda: scheduler.shutdown())

    return app
