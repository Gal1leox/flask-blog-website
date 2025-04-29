from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Query

from website import db
from website.domain.models import (
    User,
    Post,
    Comment,
    VerificationCode,
    Image,
    PostImage,
    SavedPost,
)

TABLES: Dict[str, Dict[str, Any]] = {
    "users": {"table": User},
    "posts": {"table": Post},
    "comments": {"table": Comment},
    "verification_codes": {"table": VerificationCode},
    "images": {"table": Image},
    "post_images": {"table": PostImage},
    "saved_posts": {"table": SavedPost},
}


class TableRepository:
    @staticmethod
    def all_tables() -> List[str]:
        return list(TABLES.keys())

    @staticmethod
    def query_for(table_name: str) -> Optional[Query]:
        info = TABLES.get(table_name)
        return info["table"].query if info else None

    @staticmethod
    def get(table_name: str, record_id: int) -> Optional[Any]:
        qry = TableRepository.query_for(table_name)
        return qry.get(record_id) if qry else None

    @staticmethod
    def delete(record: Any) -> None:
        db.session.delete(record)
        db.session.commit()

    @staticmethod
    def bulk_delete(query: Query) -> int:
        objs = query.all()
        count = len(objs)

        for obj in objs:
            db.session.delete(obj)
        db.session.commit()

        return count

    @staticmethod
    def get_columns(table_name: str) -> List[str]:
        info = TABLES.get(table_name)
        model = info and info["table"]

        if model and hasattr(model, "__table__"):
            return [c.name for c in model.__table__.columns]

        return []
