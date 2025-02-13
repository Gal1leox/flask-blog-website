from flask import render_template


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found_page(error):
        return render_template("errors/pages/404.html"), 404

    @app.errorhandler(429)
    def rate_limit_page(error):
        return render_template("errors/pages/429.html"), 429
