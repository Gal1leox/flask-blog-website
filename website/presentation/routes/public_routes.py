from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from website import limiter
from website.utils import get_current_user, build_context
from website.presentation.forms import ContactForm
from website.application.services import PublicService

public_bp = Blueprint(
    "public",
    __name__,
    url_prefix="/",
    template_folder="../templates",
)

public_service = PublicService()


@public_bp.route("/", methods=["GET"])
@limiter.limit("60/minute")
def home():
    user = get_current_user()
    selected_tags = request.args.getlist("tag")

    context = build_context(user, active_page="Home")
    context.update(public_service.get_home_context(selected_tags))

    return render_template("pages/shared/home.html", **context)


@public_bp.route("/contact-me", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def contact():
    user = get_current_user()
    form = ContactForm()

    if form.validate_on_submit():
        success, message = public_service.send_contact(user, form)
        flash(message, "success" if success else "danger")
        return redirect(url_for("public.home"))

    context = build_context(user, active_page="Contact Me")
    context["form"] = form

    return render_template("pages/shared/user/contact.html", **context)
