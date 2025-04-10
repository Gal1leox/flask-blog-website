def register_blueprints(app):
    from website.routes import (
        home_bp,
        auth_bp,
        admin_bp,
        settings_bp,
        contact_bp,
        posts_bp,
    )

    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth/")
    app.register_blueprint(admin_bp, url_prefix="/admin/")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(contact_bp, url_prefix="/contact-me")
    app.register_blueprint(posts_bp, url_prefix="/posts")
