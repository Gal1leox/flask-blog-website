from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from website import limiter
from website.domain.models import UserRole
from website.interface.forms import ContactForm
from website.application.services.public_service import PublicService

public_bp = Blueprint(
    "public", __name__, url_prefix="/", template_folder="../templates/shared"
)
_service = PublicService()


def _get_current_user():
    return current_user if current_user.is_authenticated else None


def _base_context(user, active_page=""):
    return {
        "is_admin": user and user.role == UserRole.ADMIN,
        "avatar_url": user.avatar_url if user else "",
        "theme": user.theme.value if user else "system",
        "active_page": active_page,
    }


@public_bp.route("", methods=["GET"])
@limiter.limit("60/minute")
def home():
    user = _get_current_user()
    ctx = _base_context(user, active_page="Home")
    ctx.update(_service.get_home_context(request.args.getlist("tag")))
    return render_template("pages/shared/home.html", **ctx)


@public_bp.route("contact", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def contact():
    user = _get_current_user()
    form = ContactForm()
    if form.validate_on_submit():
        ok, msg = _service.send_contact(user, form)
        flash(msg, "success" if ok else "danger")
        return redirect(url_for("public.home"))
    ctx = _base_context(user, active_page="Contact")
    ctx["form"] = form
    return render_template("pages/shared/user/contact.html", **ctx)
