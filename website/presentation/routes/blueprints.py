def register_blueprints(app):
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .public_routes import public_bp
    from .settings_routes import settings_bp
    from .post_routes import posts_bp
    from .comment_routes import comments_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(public_bp, url_prefix="/")
    app.register_blueprint(settings_bp, url_prefix="/settings")
    app.register_blueprint(posts_bp, url_prefix="/posts")
    app.register_blueprint(comments_bp, url_prefix="/comments")
