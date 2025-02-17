import os

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from website import create_app, db
from website.models import User, UserRole

load_dotenv()

admin_email = os.getenv("ADMIN_EMAIL")
admin_username = os.getenv("ADMIN_USERNAME")
admin_password = os.getenv("ADMIN_PASSWORD")
admin_avatar_path = os.getenv("ADMIN_AVATAR_PATH")


def create_admin_if_not_exists():
    """Creates an admin in the database, ensuring only one admin exists."""

    admin = User.query.filter(User.role == UserRole.ADMIN).first()
    if admin is not None:
        print("Admin already exists!\n")
        print(admin)
    else:
        try:
            new_admin = User(
                username=admin_username,
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                role=UserRole.ADMIN,
            )
            db.session.add(new_admin)
            db.session.commit()

            print("Admin was created successfully!\n")
            print(new_admin)
        except Exception as e:
            print(f"Error creating admin:\n\n" f"{e}")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        create_admin_if_not_exists()
