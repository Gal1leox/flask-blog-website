import os

from dotenv import load_dotenv

from website import create_app
from website.models import Admin
from website.utils import convert_image_to_binary

load_dotenv()

admin_login = os.getenv("ADMIN_LOGIN")
admin_password = os.getenv("ADMIN_PASSWORD")
admin_avatar_path = os.getenv("ADMIN_AVATAR_PATH")


def validate_env_variables():
    """Ensures all required environment variables are set."""

    if not admin_login:
        raise ValueError("You have missed admin login variable.")
    elif not admin_password:
        raise ValueError("You have missed admin password variable.")
    elif not admin_avatar_path:
        raise ValueError("You have missed admin avatar variable.")


def create_admin_if_not_exists():
    """Creates an admin in the database, ensuring only one admin exists."""

    admin = Admin.query.first()
    if admin is not None:
        print("Admin already exists!\n")
        print(admin)
    else:
        try:
            avatar_data = convert_image_to_binary(admin_avatar_path)
            new_admin = Admin.create_admin(admin_login, admin_password, avatar_data)
            print("Admin was created successfully!\n")
            print(new_admin)
        except Exception as e:
            print(f"Error creating admin: {e}")


if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        create_admin_if_not_exists()
