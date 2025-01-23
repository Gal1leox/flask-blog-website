from website import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model, UserMixin):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.LargeBinary, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", cascade="all")

    def __repr__(self):
        return f"Admin Info:\n" f"ID: {self.id}\n" f"Created At: {self.created_at}"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def create_admin(login, password, avatar):
        """
        Creates an admin in the database, ensuring only one admin exists.

        :param login: The login username for the admin account.
        :param password: The password for the admin account, which will be hashed before storage.
        :param avatar: The file path of the admin's avatar image.
        :return: The created Admin object.
        """

        if not login:
            raise ValueError("The login is required.")
        elif not password:
            raise ValueError("The password is required.")
        elif not avatar:
            raise ValueError("The avatar is required.")

        admin = Admin(login=login, avatar=avatar)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()

        return admin
