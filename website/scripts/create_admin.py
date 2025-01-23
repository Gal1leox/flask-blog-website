import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from website import create_app
from website.models import Admin
from website.utils import convert_image_to_binary

load_dotenv()

admin_login = os.getenv("ADMIN_LOGIN")
admin_password = os.getenv("ADMIN_PASSWORD")
admin_avatar_path = os.getenv("ADMIN_AVATAR_PATH")

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        admin = Admin.query.first()
        if admin is not None:
            print("Admin already exists!\n\n", admin)
        else:
            try:
                avatar_data = convert_image_to_binary(admin_avatar_path)
                new_admin = Admin.create_admin(admin_login, admin_password, avatar_data)
                print("Admin was created successfully!\n\n", new_admin)
            except Exception as e:
                print(f"Error creating admin: {e}")
