def register_blueprints(app):
    from website.interface.routes import (
        auth_bp,
        admin_bp,
        public_bp,
        settings_bp,
        posts_bp,
        comments_bp,
    )

    app.register_blueprint(auth_bp, url_prefix="/auth/")
    app.register_blueprint(admin_bp, url_prefix="/admin/")
    app.register_blueprint(public_bp, url_prefix="/")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(posts_bp, url_prefix="/posts")
    app.register_blueprint(comments_bp, url_prefix="/comments")
