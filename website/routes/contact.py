import os

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from dotenv import load_dotenv
from flask_mail import Message

from ..config import Config
from ..forms import ContactForm
from ..models import User, UserRole
from website import mail

load_dotenv()

admin_email = Config.ADMIN_EMAIL
secret_key = Config.SECRET_KEY

contact_bp = Blueprint("contact", __name__, template_folder="../templates")


@contact_bp.route("/", methods=["GET", "POST"])
@login_required
def contact():
    form = ContactForm()

    user = User.query.get(current_user.id) if current_user.is_authenticated else None

    if form.validate_on_submit():
        subject = (
            f"New Contact Message from {form.first_name.data} {form.last_name.data}"
        )
        html = render_template(
            "pages/shared/user/email_message.html", form=form, sender_email=user.email
        )
        message = Message(
            subject,
            html=html,
            sender=user.email,
            recipients=[admin_email],
        )
        try:
            mail.send(message)
            flash("Your message has been sent successfully!", "success")
        except Exception as error:
            flash(str(error), "danger")
        return redirect(url_for("home.home"))

    avatar_url = user.avatar_url if user else ""
    is_admin = user and user.role == UserRole.ADMIN
    token = secret_key if is_admin else ""

    return render_template(
        "pages/shared/user/contact.html",
        form=form,
        is_admin=is_admin,
        avatar_url=avatar_url,
        token=token,
        active_page="Contact Me",
    )
