def register_blueprints(app):
    from website.routes import home_bp, auth_bp, admin_bp, settings_bp

    app.register_blueprint(home_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth/")
    app.register_blueprint(admin_bp, url_prefix="/admin/")
    app.register_blueprint(settings_bp, url_prefix="/settings")
