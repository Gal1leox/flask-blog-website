from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from flask_mail import Message

from website import limiter, mail
from website.config import Config
from website.domain.models import User, UserRole, Post
from website.interface.forms import ContactForm

public_bp = Blueprint(
    "public",
    __name__,
    url_prefix="/",
    template_folder="../templates/shared",
)


def get_current_user():
    return User.query.get(current_user.id) if current_user.is_authenticated else None


def base_context(user, active_page=""):
    return {
        "is_admin": bool(user and user.role == UserRole.ADMIN),
        "token": Config.SECRET_KEY if user and user.role == UserRole.ADMIN else "",
        "avatar_url": user.avatar_url if user else "",
        "theme": user.theme.value if user else "system",
        "active_page": active_page,
    }


@public_bp.route("", methods=["GET"])
@limiter.limit("60/minute")
def home():
    user = get_current_user()
    selected_tags = request.args.getlist("tag")

    query = Post.query
    for tag in selected_tags:
        query = query.filter(Post.content.ilike(f"%#{tag}%"))

    posts = query.order_by(Post.created_at.desc()).all()

    context = base_context(user, active_page="Home")
    context.update(
        {
            "posts": posts,
            "selected_tags": selected_tags,
        }
    )

    return render_template("pages/shared/home.html", **context)


@public_bp.route("contact", methods=["GET", "POST"])
@login_required
@limiter.limit("10/hour", methods=["POST"])
def contact():
    user = get_current_user()
    form = ContactForm()

    if form.validate_on_submit():
        subject = (
            f"New Contact Message from {form.first_name.data} {form.last_name.data}"
        )

        html_body = render_template(
            "pages/shared/user/email_message.html",
            form=form,
            sender_email=user.email,
        )

        msg = Message(
            subject,
            sender=user.email,
            recipients=[Config.ADMIN_EMAIL],
            html=html_body,
        )

        try:
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash(str(e), "danger")

        return redirect(url_for("public.home"))

    context = base_context(user, active_page="Contact")
    context.update({"form": form})

    return render_template("pages/shared/user/contact.html", **context)
