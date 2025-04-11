import os

from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    render_template,
    abort,
    flash,
    current_app,
    send_file,
    jsonify,
)
from flask_login import current_user

from ..config import Config
from ..models import (
    User,
    UserRole,
)
from ..utils import (
    token_required,
    admin_required,
    TABLES,
    get_table_records,
)
from website import db

secret_key = Config.SECRET_KEY
db_name = Config.DB_NAME
admin_email = Config.ADMIN_EMAIL

admin_bp = Blueprint("admin", __name__, template_folder="../templates")


@admin_bp.route("/database/")
@token_required
@admin_required
def database():
    user = User.query.get(current_user.id)

    avatar_url = user.avatar_url if user else ""
    table = request.args.get("table")

    tabs = [
        {
            "name": table,
            "link": url_for("admin.database", token=secret_key, table=table),
        }
        for table in TABLES.keys()
    ]

    records = get_table_records(table)
    attributes = TABLES[table]["columns"] if table else []

    return render_template(
        "pages/shared/admin/database.html",
        is_admin=True,
        avatar_url=avatar_url,
        db_name=db_name,
        tabs=tabs,
        table=table,
        attributes=attributes,
        records=records,
        token=secret_key,
        active_page="Database",
    )


@admin_bp.route("/database/<string:table>/<int:record_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_record(table, record_id):
    if table in ["post_images", "post_tags", "saved_posts"]:
        flash("Deletion is not allowed for this table.", "danger")
        return jsonify(success=False, error="Deletion not allowed"), 403

    table_info = TABLES.get(table)
    if not table_info:
        flash(f"Table '{table}' not found.", "danger")
        return "", 404

    Table = table_info["table"]
    record = Table.query.get(record_id)
    if not record:
        flash(
            f"Record with id '{record_id}' from the table '{table}' not found.",
            "danger",
        )
        return "", 404

    if table == "users" and record.role == UserRole.ADMIN:
        flash("Cannot delete an admin user.", "danger")
        return redirect(url_for("home.home"))

    db.session.delete(record)
    db.session.commit()
    flash(
        f"Successfully deleted the record with ID {record_id} from the {table} table.",
        "success",
    )
    return (
        jsonify(
            success=True,
            message=f"Successfully deleted the record with ID {record_id} from the {table} table.",
        ),
        200,
    )


@admin_bp.route("/database/<string:table>/all", methods=["DELETE"])
@token_required
@admin_required
def delete_records(table):
    if table in ["post_images", "post_tags", "saved_posts"]:
        flash("Bulk deletion is not allowed for this table.", "danger")
        return jsonify(success=False, error="Deletion not allowed"), 403

    table_info = TABLES.get(table)
    if not table_info:
        flash(f"Table '{table}' not found.", "danger")
        return "", 404

    Table = table_info["table"]
    if Table.__tablename__ == "users":
        db.session.query(Table).filter(Table.role != UserRole.ADMIN).delete(
            synchronize_session=False
        )
    else:
        db.session.query(Table).delete(synchronize_session=False)

    db.session.commit()
    flash(
        f"Successfully deleted all records from the {table} table.",
        "success",
    )

    return (
        jsonify(
            success=True,
            message=f"Successfully deleted all records from the {table} table.",
        ),
        200,
    )


@admin_bp.route("/database/download-db")
@token_required
@admin_required
def download_db():
    db_path = os.path.abspath(
        os.path.join(current_app.root_path, "..", "instance", Config.DB_NAME)
    )
    if not os.path.exists(db_path):
        abort(404)

    return send_file(db_path, as_attachment=True, download_name=db_name)


@admin_bp.route("/database/restore-db", methods=["POST"])
@token_required
@admin_required
def restore_db():
    if "db_file" not in request.files:
        flash("No file uploaded. Please choose a .db file to restore.", "danger")
        return jsonify(success=False, error="No file uploaded"), 400

    file = request.files["db_file"]
    if file.filename == "":
        flash("No file uploaded. Please choose a .db file to restore.", "danger")
        return jsonify(success=False, error="No file selected"), 400
    if not file.filename or not file.filename.endswith(".db"):
        flash("Invalid file selected. Please upload a .db file.", "danger")
        return (
            jsonify(
                success=False, error="Invalid file selected. Please upload a .db file."
            ),
            400,
        )

    db_path = os.path.abspath(
        os.path.join(current_app.root_path, "..", "instance", Config.DB_NAME)
    )

    try:
        file.save(db_path)
        flash("Database restored successfully.", "success")
        return jsonify(success=True, message="Database restored successfully"), 200
    except Exception as e:
        flash(f"Failed to restore database: {str(e)}", "danger")
        return jsonify(success=False, error=str(e)), 500
