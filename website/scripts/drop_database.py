import os

from dotenv import load_dotenv
from flask import Flask

load_dotenv()


def drop_database(app):
    db_path = os.path.join(app.instance_path, os.getenv("DB_NAME"))
    if os.path.exists(db_path):
        os.remove(db_path)


if __name__ == "__main__":
    app = Flask(__name__)

    with app.app_context():
        drop_database(app)
