from website import db
from datetime import datetime

post_image = db.Table(
    "post_image",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("image_id", db.Integer, db.ForeignKey("images.id"), primary_key=True),
)

post_tag = db.Table(
    "post_tag",
    db.Column("post_id", db.Integer, db.ForeignKey("posts.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    title = db.Column(db.String(40), unique=True, nullable=False)
    content = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship("Image", secondary=post_image, cascade="all")
    tags = db.relationship(
        "Tag",
        secondary=post_tag,
        backref=db.backref("posts"),
        cascade="all",
    )

    def __repr__(self):
        return (
            f"Post Info:\n"
            f"ID: {self.id}\n"
            f"Title: {self.title}\n"
            f"Content: {self.content}\n"
            f"Images: {[image.filename for image in self.images]}\n"
            f"Tags: {[tag.name for tag in self.tags]}\n"
            f"Created At: {self.created_at}"
        )


class Image(db.Model):
    __tablename__ = "images"

    id = db.Column(db.Integer, primary_key=True)
    image_data = db.Column(db.LargeBinary, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"Image Info:\n"
            f"ID: {self.id}\n"
            f"Filename: {self.filename}\n"
            f"Type: {self.file_type}\n"
            f"Size: {self.file_size} bytes\n"
            f"Created At: {self.created_at}"
        )


class Tag(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(40), unique=True, nullable=False)
    color = db.Column(db.String(7), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"Tag Info:\n"
            f"ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Color: {self.color}\n"
            f"Created At: {self.created_at}"
        )
