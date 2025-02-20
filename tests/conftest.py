import pytest

from website import create_app, db


@pytest.fixture()
def app():
    app = create_app()
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()

    yield app
