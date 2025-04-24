from wtforms import TextAreaField, SubmitField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Length

from .base import BaseForm
from .validators import calculate_word_count, validate_num_images, OptionalImages


class CreatePostForm(BaseForm):
    content = TextAreaField(
        "Content",
        validators=[DataRequired(), calculate_word_count],
        render_kw={"rows": 10},
    )
    images = FileField(
        "Images",
        render_kw={"multiple": True},
        validators=[OptionalImages(), validate_num_images],
    )
    submit = SubmitField("Publish")


class CommentForm(BaseForm):
    content = TextAreaField(
        "Your Comment",
        validators=[DataRequired(), Length(4, 200), calculate_word_count],
        render_kw={"rows": 3},
    )
    submit = SubmitField("Comment")
