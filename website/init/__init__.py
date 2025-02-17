from .blueprints import register_blueprints
from .errors import register_error_handlers
from .extensions import db, login_manager, mail, limiter, oauth, google
from .scheduler import schedule_jobs
