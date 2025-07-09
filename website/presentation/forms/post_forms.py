from wtforms import StringField, TextAreaField, SubmitField,IntegerField
from wtforms.validators import DataRequired, NumberRange
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


    overall_rating = IntegerField(
    "Overall Rating",
    validators=[DataRequired(), NumberRange(min=1, max=5)],
    render_kw={"class": "rating-input", "min": 1, "max": 5}
    )

    story_rating = IntegerField(
        "Story",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    gameplay_rating = IntegerField(
        "Gameplay",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    graphics_rating = IntegerField(
        "Graphics",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    sound_design_rating = IntegerField(
        "Sound Design",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    replay_value_rating = IntegerField(
        "Replay Value",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    difficulty_rating = IntegerField(
        "Difficulty",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    bug_free_rating = IntegerField(
        "Bug Free?",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    pc_requirements_rating = IntegerField(
        "PC Requirements",
        validators=[DataRequired(), NumberRange(min=1, max=5)],
        render_kw={"class": "rating-input"}
    )

    game_length_blocks = IntegerField(
        "Game Length",
        validators=[DataRequired(), NumberRange(min=1, max=10)],
        render_kw={"class": "rating-input"}
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
