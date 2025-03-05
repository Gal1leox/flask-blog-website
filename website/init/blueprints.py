def register_blueprints(app):
    from website.routes import general_bp, auth_bp, admin_bp

    app.register_blueprint(general_bp, url_prefix="/")
    app.register_blueprint(auth_bp, url_prefix="/auth/")
    app.register_blueprint(admin_bp, url_prefix="/admin/")
