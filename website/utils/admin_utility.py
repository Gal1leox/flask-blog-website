from website.models import (
    User,
    Post,
    Tag,
    Image,
    Comment,
    Notification,
    PostImage,
    PostTag,
    SavedPost,
    UserNotification,
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
    "tags": {
        "table": Tag,
        "columns": get_table_columns(Tag),
        "query": lambda: Tag.query.all(),
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
    "notifications": {
        "table": Notification,
        "columns": get_table_columns(Notification),
        "query": lambda: Notification.query.all(),
    },
    "post_images": {
        "table": PostImage,
        "columns": get_table_columns(PostImage),
        "query": lambda: PostImage.query.all(),
    },
    "post_tags": {
        "table": PostTag,
        "columns": get_table_columns(PostTag),
        "query": lambda: PostTag.query.all(),
    },
    "saved_posts": {
        "table": SavedPost,
        "columns": get_table_columns(SavedPost),
        "query": lambda: SavedPost.query.all(),
    },
    "user_notifications": {
        "table": UserNotification,
        "columns": get_table_columns(UserNotification),
        "query": lambda: UserNotification.query.all(),
    },
}


def get_table_records(table):
    """Return all records for a given table name."""

    table_info = TABLES.get(table)
    if table_info:
        return table_info["query"]()
    return []
