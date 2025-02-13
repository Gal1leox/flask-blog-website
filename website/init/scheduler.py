import atexit
from .extensions import scheduler, db


def schedule_jobs(app):
    def cleanup_expired_codes():
        from website.models import VerificationCode

        with app.app_context():
            VerificationCode.delete_expired()
            db.session.commit()

    if not scheduler.get_jobs():
        scheduler.add_job(cleanup_expired_codes, "interval", minutes=5)
        scheduler.start()
        atexit.register(lambda: scheduler.shutdown())
