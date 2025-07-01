import os
from typing import Any, Dict, List, Tuple

import cloudinary.uploader
from flask import current_app
from sqlalchemy import text, Table, MetaData
from werkzeug.datastructures import FileStorage

from website import db
from website.config import Config
from website.domain.models import UserRole
from website.infrastructure.repositories.table_repository import TableRepository


class AdminService:
    def __init__(self) -> None:
        self.table_repository = TableRepository()

    def list_tables(self) -> List[str]:
        return self.table_repository.all_tables()

    def get_records(self, table_name: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        if not table_name or not table_name.isidentifier():
            return [], []

        try:
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=db.engine)
            column_names = [column.name for column in table.columns]
            records = db.session.execute(table.select()).mappings().all()
            record_list = [dict(row) for row in records]
            return record_list, column_names
        except Exception as e:
            print(f"Error fetching records for table {table_name}: {str(e)}")
            return [], []

    def delete_one(self, table_name: str, record_id: int) -> Tuple[bool, str, int]:
        forbidden_tables = ("post_tags", "saved_posts")
        if table_name in forbidden_tables:
            return False, "Deletion forbidden for this table.", 403

        table_query = self.table_repository.query_for(table_name)
        if not table_query:
            return False, f"Table '{table_name}' not found.", 404

        entity = table_query.get(record_id)
        if not entity:
            return False, f"Record {record_id} not found.", 404

        if table_name == "users" and getattr(entity, "role", None) == UserRole.ADMIN:
            return False, "Cannot delete admin user.", 403

        for attr_name in ("public_id", "avatar_public_id"):
            cloudinary_id = getattr(entity, attr_name, None)
            if cloudinary_id:
                try:
                    cloudinary.uploader.destroy(cloudinary_id, invalidate=True)
                except Exception:
                    return False, "Failed to destroy image.", 500

        related_images = getattr(entity, "images", None)
        if related_images:
            for image in related_images:
                image_public_id = getattr(image, "public_id", None)
                if image_public_id:
                    try:
                        cloudinary.uploader.destroy(image_public_id, invalidate=True)
                    except Exception:
                        return False, "Failed to destroy related post image.", 500

        self.table_repository.delete(entity)
        return True, f"Record {record_id} deleted from {table_name}.", 200

    def delete_all(self, table_name: str) -> Tuple[bool, str, int, int]:
        table_query = self.table_repository.query_for(table_name)
        if not table_query:
            return False, f"Table '{table_name}' not found.", 404, 0

        if table_name == "users":
            from website.domain.models.user import User

            table_query = table_query.filter(User.role != UserRole.ADMIN)

        entities_to_delete = table_query.all()
        for entity in entities_to_delete:
            for attr_name in ("public_id", "avatar_public_id"):
                cloudinary_id = getattr(entity, attr_name, None)
                if cloudinary_id:
                    try:
                        cloudinary.uploader.destroy(cloudinary_id, invalidate=True)
                    except Exception:
                        return False, "Failed to destroy image.", 500, 0

            related_images = getattr(entity, "images", None)
            if related_images:
                for image in related_images:
                    image_public_id = getattr(image, "public_id", None)
                    if image_public_id:
                        try:
                            cloudinary.uploader.destroy(
                                image_public_id, invalidate=True
                            )
                        except Exception:
                            return (
                                False,
                                "Failed to destroy related post image.",
                                500,
                                0,
                            )

        deleted_count = self.table_repository.bulk_delete(table_query)
        return True, f"Deleted {deleted_count} records.", 200, deleted_count

    def download_database(self) -> str:
        database_path = os.path.join(
            current_app.root_path,
            "..",
            "instance",
            Config.DB_NAME,
        )
        return os.path.abspath(database_path)

    def restore_database(self, backup_file: FileStorage) -> Tuple[bool, str]:
        if not backup_file or not backup_file.filename.endswith(".db"):
            return False, "Invalid file. Must be .db"

        target_path = os.path.join(
            current_app.root_path,
            "..",
            "instance",
            Config.DB_NAME,
        )
        backup_file.save(target_path)
        return True, "Database restored successfully."
