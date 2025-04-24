from typing import Any, Dict, Optional

from sqlalchemy.orm import Query

from website import db
from website.utils import TABLES


class TableRepository:
    @staticmethod
    def all_tables() -> Dict[str, Any]:
        return TABLES

    @staticmethod
    def query_for(table_name: str) -> Optional[Query]:
        table_info = TABLES.get(table_name)
        model = table_info.get("table") if table_info else None
        return model.query if model else None

    @staticmethod
    def get(table_name: str, record_id: int) -> Optional[Any]:
        table_info = TABLES.get(table_name)
        model = table_info.get("table") if table_info else None
        return model.query.get(record_id) if model else None

    @staticmethod
    def delete(record: Any) -> None:
        db.session.delete(record)
        db.session.commit()

    @staticmethod
    def bulk_delete(query: Query) -> int:
        deleted = query.delete(synchronize_session=False)
        db.session.commit()
        return deleted
