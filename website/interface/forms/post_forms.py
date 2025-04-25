from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

from .base import BaseForm
from .validators import calculate_word_count, validate_num_images, OptionalImages
from .fields import MultiFileField


class CreatePostForm(BaseForm):
    content = TextAreaField(
        "Content",
        validators=[DataRequired(), calculate_word_count],
        render_kw={"rows": 4},
    )
    images = MultiFileField(
        "Images",
        render_kw={"multiple": True, "required": True},
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
