from website.domain.models import (
    User,
    Post,
    Image,
    PostImage,
    SavedPost,
    Comment,
    VerificationCode,
)


def get_table_columns(table):
    """Return a list of column names for the given SQLAlchemy model."""

    if hasattr(table, "__table__"):
        return [column.name for column in table.__table__.columns]
    elif hasattr(table, "columns"):
        return [column.name for column in table.columns]
    return []


TABLES = {
    "users": {
        "table": User,
        "columns": get_table_columns(User),
        "query": lambda: User.query.all(),
    },
    "posts": {
        "table": Post,
        "columns": get_table_columns(Post),
        "query": lambda: Post.query.all(),
    },
    "comments": {
        "table": Comment,
        "columns": get_table_columns(Comment),
        "query": lambda: Comment.query.all(),
    },
    "verification_codes": {
        "table": VerificationCode,
        "columns": get_table_columns(VerificationCode),
        "query": lambda: VerificationCode.query.all(),
    },
    "images": {
        "table": Image,
        "columns": get_table_columns(Image),
        "query": lambda: Image.query.all(),
    },
    "post_images": {
        "table": PostImage,
        "columns": get_table_columns(PostImage),
        "query": lambda: PostImage.query.all(),
    },
    "saved_posts": {
        "table": SavedPost,
        "columns": get_table_columns(SavedPost),
        "query": lambda: SavedPost.query.all(),
    },
}


def get_table_records(table):
    """Return all records for a given table name."""

    table_info = TABLES.get(table)
    if table_info:
        return table_info["query"]()
    return []
