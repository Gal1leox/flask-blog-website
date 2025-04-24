import os

from flask import (
    Blueprint,
    render_template,
    request,
    url_for,
    flash,
    send_file,
    abort,
    jsonify,
)
from flask_login import current_user

from website import limiter
from website.config import Config
from website.application.services import AdminService
from website.interface.middlewares import (
    token_required,
    admin_required,
)

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="../templates/shared/admin",
)

_service = AdminService()


def get_current_user():
    return current_user if current_user.is_authenticated else None


def base_ctx(user, active_page=""):
    return {
        "is_admin": user and user.role.name == "ADMIN",
        "avatar_url": user.avatar_url if user else "",
        "token": Config.SECRET_KEY if user and user.role.name == "ADMIN" else "",
        "db_name": Config.DB_NAME,
        "active_page": active_page,
        "theme": user.theme.value if user else "system",
    }


@admin_bp.route("/database/", methods=["GET"])
@token_required
@admin_required
@limiter.limit("20/hour")
def database():
    user = get_current_user()
    table = request.args.get("table", "")
    tables = _service.list_tables()
    records, columns = _service.get_records(table)

    ctx = base_ctx(user, active_page="Database")
    ctx.update(
        {
            "tabs": [
                {"name": t, "link": url_for("admin.database", table=t)} for t in tables
            ],
            "table": table,
            "attributes": columns,
            "records": records,
        }
    )
    return render_template("pages/shared/admin/database.html", **ctx)


@admin_bp.route("/database/<table>/<int:record_id>", methods=["DELETE"])
@token_required
@admin_required
@limiter.limit("30/hour")
def delete_record(table, record_id):
    ok, msg, code = _service.delete_one(table, record_id)
    flash(msg, "success" if ok else "danger")
    return (jsonify(success=ok), code) if not ok else (jsonify(success=True), 200)


@admin_bp.route("/database/<table>/all", methods=["DELETE"])
@token_required
@admin_required
@limiter.limit("5/hour")
def delete_records(table):
    ok, msg, code, deleted = _service.delete_all(table)
    flash(msg, "success" if ok else "danger")
    return jsonify(success=ok, deleted=deleted), code


@admin_bp.route("/database/download", methods=["GET"])
@token_required
@admin_required
@limiter.limit("10/hour")
def download_db():
    path = _service.download_database()
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name=Config.DB_NAME)


@admin_bp.route("/database/restore", methods=["POST"])
@token_required
@admin_required
@limiter.limit("5/hour")
def restore_db():
    file = request.files.get("db_file")
    ok, msg = _service.restore_database(file)
    flash(msg, "success" if ok else "danger")
    status = 200 if ok else 400
    return jsonify(success=ok, error=None if ok else msg), status
