import os

import pytest


@pytest.fixture()
def app():
    os.environ["TEST_DATABASE_URL"] = "sqlite:///:memory:"
    from app import create_app
    from app.extensions import db, token_blocklist

    app = create_app("testing")

    with app.app_context():
        token_blocklist.clear()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        token_blocklist.clear()


@pytest.fixture()
def client(app):
    return app.test_client()
