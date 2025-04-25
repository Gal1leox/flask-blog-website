import os
from typing import Any, Dict, List, Tuple

from flask import current_app
from sqlalchemy import text
from werkzeug.datastructures import FileStorage

from website import db
from website.config import Config
from website.domain.models import UserRole
from website.infrastructure.repositories.table_repository import TableRepository


class AdminService:
    """
    Service layer for admin operations on database tables and backups.
    """

    def __init__(self) -> None:
        self._repo = TableRepository()

    def list_tables(self) -> List[str]:
        return self._repo.all_tables()

    def get_records(self, table_name: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        if not table_name:
            return [], []

        # 1) grab all rows as dicts
        sql = text(f"SELECT * FROM {table_name}")
        result = db.session.execute(sql).mappings().all()

        # 2) if no rows, still need column names
        if not result:
            pragma = db.session.execute(text(f"PRAGMA table_info({table_name})")).all()
            cols = [col_row[1] for col_row in pragma]  # PRAGMA returns (cid, name, ...)
            return [], cols

        # 3) otherwise, keys() are your column names
        cols = list(result[0].keys())
        records = [dict(r) for r in result]
        return records, cols

    def delete_one(self, table: str, record_id: int) -> Tuple[bool, str, int]:
        if table in ("post_images", "post_tags", "saved_posts"):
            return False, "Deletion forbidden for this table.", 403

        query = self._repo.query_for(table)
        if not query:
            return False, f"Table '{table}' not found.", 404

        record = query.get(record_id)
        if not record:
            return False, f"Record {record_id} not found.", 404

        if table == "users" and getattr(record, "role", None) == UserRole.ADMIN:
            return False, "Cannot delete admin user.", 403

        self._repo.delete(record)
        return True, f"Record {record_id} deleted from {table}.", 200

    def delete_all(self, table: str) -> Tuple[bool, str, int, int]:
        query = self._repo.query_for(table)
        if not query:
            return False, f"Table '{table}' not found.", 404, 0

        if table == "users":
            from website.domain.models.user import User

            query = query.filter(User.role != UserRole.ADMIN)

        count = self._repo.bulk_delete(query)
        return True, f"Deleted {count} records.", 200, count

    def download_database(self) -> str:
        db_path = os.path.join(
            current_app.root_path,
            "..",
            "instance",
            Config.DB_NAME,
        )
        return os.path.abspath(db_path)

    def restore_database(self, file: FileStorage) -> Tuple[bool, str]:
        if not file or not file.filename.endswith(".db"):
            return False, "Invalid file. Must be .db"

        target = os.path.join(
            current_app.root_path,
            "..",
            "instance",
            Config.DB_NAME,
        )
        file.save(target)
        return True, "Database restored."
