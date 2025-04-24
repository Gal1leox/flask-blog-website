from flask_wtf import FlaskForm

from .validators import strip_filter


class BaseForm(FlaskForm):
    class Meta:
        def bind_field(self, form, unbound_field, options):
            options.setdefault("filters", []).append(strip_filter)
            return unbound_field.bind(form=form, **options)
