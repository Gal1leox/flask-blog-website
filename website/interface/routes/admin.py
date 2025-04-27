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

from website.config import Config
from website.application.services import AdminService
from website.interface.middlewares import token_required, admin_required

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/admin",
    template_folder="../templates/shared/admin",
)

admin_service = AdminService()


def get_authenticated_user():
    return current_user if current_user.is_authenticated else None


def build_context(user, active_page=""):
    is_admin = bool(user and user.role.name == "ADMIN")

    return {
        "is_admin": is_admin,
        "avatar_url": user.avatar_url if user else "",
        "token": Config.SECRET_KEY if is_admin else "",
        "db_name": Config.DB_NAME,
        "active_page": active_page,
        "theme": user.theme.value if user else "system",
    }


@admin_bp.route("/database/", methods=["GET"])
@token_required
@admin_required
def view_database():
    user = get_authenticated_user()
    table = request.args.get("table", "")

    table_names = admin_service.list_tables()
    records, attributes = admin_service.get_records(table)

    context = build_context(user, active_page="Database")
    context.update(
        {
            "tabs": [
                {
                    "name": table,
                    "link": url_for(
                        "admin.view_database", table=table, token=context["token"]
                    ),
                }
                for table in table_names
            ],
            "table": table,
            "attributes": attributes,
            "records": records,
        }
    )

    return render_template("pages/shared/admin/database.html", **context)


@admin_bp.route("/database/<table>/<int:entry_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_single_record(table, entry_id):
    success, message, status_code = admin_service.delete_one(table, entry_id)
    flash(message, "success" if success else "danger")
    return jsonify(success=success), status_code


@admin_bp.route("/database/<table>/all", methods=["DELETE"])
@token_required
@admin_required
def delete_all_records(table):
    success, message, status_code, deleted_count = admin_service.delete_all(table)
    flash(message, "success" if success else "danger")
    return jsonify(success=success, deleted=deleted_count), status_code


@admin_bp.route("/database/download", methods=["GET"])
@token_required
@admin_required
def download_database_file():
    db_path = admin_service.download_database()

    if not os.path.exists(db_path):
        abort(404)

    return send_file(
        db_path,
        as_attachment=True,
        download_name=Config.DB_NAME,
    )


@admin_bp.route("/database/restore", methods=["POST"])
@token_required
@admin_required
def restore_database():
    upload = request.files.get("db_file")
    success, message = admin_service.restore_database(upload)

    flash(message, "success" if success else "danger")
    status_code = 200 if success else 400

    return jsonify(success=success, error=None if success else message), status_code
