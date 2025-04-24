import os
from typing import Any, List, Tuple

from flask import current_app
from werkzeug.datastructures import FileStorage

from website.config import Config
from website.domain.models import UserRole
from website.infrastructure.repositories.table_repository import TableRepository, TABLES


class AdminService:
    """
    Service layer for admin operations on database tables and backups.
    """

    def __init__(self) -> None:
        self._repo = TableRepository()

    def list_tables(self) -> List[str]:
        """Return the names of all manageable tables."""
        return list(self._repo.all_tables().keys())

    def get_records(self, table: str) -> Tuple[List[Any], List[str]]:
        """
        Fetch all records and column names for a given table.
        Returns (records, columns).
        """
        if not table:
            return [], []

        query = self._repo.query_for(table)
        if not query:
            return [], []

        records = query.order_by().all()
        columns = TABLES.get(table, {}).get("columns", [])
        return records, columns

    def delete_one(self, table: str, record_id: int) -> Tuple[bool, str, int]:
        """
        Delete a single record by ID from the specified table.
        Returns (success, message, HTTP_status).
        """
        # Prevent dangerous removals
        if table in ("post_images", "post_tags", "saved_posts"):
            return False, "Deletion forbidden for this table.", 403

        query = self._repo.query_for(table)
        if not query:
            return False, f"Table '{table}' not found.", 404

        record = query.get(record_id)
        if not record:
            return False, f"Record {record_id} not found.", 404

        # Protect admin users
        if table == "users" and getattr(record, "role", None) == UserRole.ADMIN:
            return False, "Cannot delete admin user.", 403

        self._repo.delete(record)
        return True, f"Record {record_id} deleted from {table}.", 200

    def delete_all(self, table: str) -> Tuple[bool, str, int, int]:
        """
        Bulk delete all records in a table (excluding admin users).
        Returns (success, message, HTTP_status, deleted_count).
        """
        query = self._repo.query_for(table)
        if not query:
            return False, f"Table '{table}' not found.", 404, 0

        if table == "users":
            # skip admin accounts
            from website.domain.models.user import User

            query = query.filter(User.role != UserRole.ADMIN)

        count = self._repo.bulk_delete(query)
        return True, f"Deleted {count} records.", 200, count

    def download_database(self) -> str:
        """Return the absolute path to the SQLite database file."""
        db_path = os.path.join(
            current_app.root_path,
            "..",
            "instance",
            Config.DB_NAME,
        )
        return os.path.abspath(db_path)

    def restore_database(self, file: FileStorage) -> Tuple[bool, str]:
        """Replace the database file with an uploaded .db file."""
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
