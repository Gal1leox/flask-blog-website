from flask import render_template


def register_error_handlers(app):
    @app.errorhandler(403)
    def not_found_page(error):
        return render_template("pages/errors/403.html"), 403

    @app.errorhandler(404)
    def not_found_page(error):
        return render_template("pages/errors/404.html"), 404

    @app.errorhandler(429)
    def rate_limit_page(error):
        return (
            render_template(
                "pages/errors/429.html", time_span=" ".join(str(error).split()[-2:])
            ),
            429,
        )

    @app.errorhandler(500)
    def not_found_page(error):
        return render_template("pages/errors/500.html"), 500
