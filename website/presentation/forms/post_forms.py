from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileRequired

from .base import BaseForm
from .validators import (
    validate_num_images,
    OptionalImages,
    Length,
)
from .fields import MultiFileField


class CreatePostForm(BaseForm):
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(1, 150)],
        render_kw={
            "placeholder": "Title of your post",
            "class": "w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600",
        },
    )
    content = TextAreaField(
        "Content",
        validators=[DataRequired(), Length(4, 7000)],
        render_kw={
            "placeholder": "Content of a new post",
            "rows": 10,
            "class": "w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600",
        },
    )
    images = MultiFileField(
        "Upload Images",
        validators=[
            OptionalImages(),
            FileRequired(message="At least one image is required"),
            validate_num_images,
            FileAllowed(["jpg", "jpeg", "png"], "Only JPG and PNG allowed."),
        ],
        render_kw={"multiple": True, "id": "dropzone-file"},
    )
    submit = SubmitField(
        "Publish",
        render_kw={
            "class": "py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
        },
    )


class CommentForm(BaseForm):
    content = TextAreaField(
        "Your Comment",
        validators=[DataRequired("Please write something."), Length(4, 1500)],
        render_kw={
            "placeholder": "What do you think…",
            "rows": 3,
            "class": "w-full p-2 border rounded dark:bg-gray-700 dark:border-gray-600",
        },
    )
    submit = SubmitField(
        "Comment",
        render_kw={"class": "mt-2 px-4 py-2 bg-blue-600 text-white rounded"},
    )
