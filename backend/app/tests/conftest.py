import os
import tempfile

import pytest


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    os.environ["TEST_DATABASE_URL"] = f"sqlite:///{db_path}"
    from app import create_app
    from app.extensions import db, token_blocklist
    from app.services.rfid_capture_service import reset_capture_state

    app = create_app("testing")

    with app.app_context():
        token_blocklist.clear()
        reset_capture_state()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        token_blocklist.clear()
        reset_capture_state()
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture()
def client(app):
    return app.test_client()
