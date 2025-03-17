import os

from flask import Blueprint, request, redirect, url_for, render_template, abort, flash
from flask_login import current_user
from dotenv import load_dotenv

from ..models import (
    User,
    UserRole,
)
from ..utils import (
    admin_and_token_required,
    TABLES,
    get_table_records,
)
from website import db

load_dotenv()

admin_email = os.getenv("ADMIN_EMAIL")
secret_key = os.getenv("SECRET_KEY")

admin_bp = Blueprint("admin", __name__, template_folder="../templates")


@admin_bp.route("/database/")
@admin_and_token_required
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
        "general/admin/pages/database.html",
        is_admin=True,
        avatar_url=avatar_url,
        tabs=tabs,
        table=table,
        attributes=attributes,
        records=records,
        token=secret_key,
        active_page="Database",
    )


@admin_bp.route("/database/<string:table>/<int:record_id>", methods=["DELETE"])
@admin_and_token_required
def delete_record(table, record_id):
    table_info = TABLES.get(table)
    if not table_info:
        abort(404)

    Table = table_info["table"]
    record = Table.query.get(record_id)
    if not record:
        abort(404)

    if table == "users" and record.role == UserRole.ADMIN:
        flash("Cannot delete an admin user.", "danger")
        return redirect(url_for("general.home"))

    db.session.delete(record)
    db.session.commit()
    flash(
        f"Successfully deleted the record with ID {record_id} from the {table} table.",
        "success",
    )
    return "", 204
