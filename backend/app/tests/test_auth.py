from app.extensions import db
from app.models import User


def create_user():
    user = User(
        username="admin",
        full_name="Administrator",
        email="admin@sikap.local",
        role="admin",
    )
    user.set_password("admin123")
    db.session.add(user)
    db.session.commit()
    return user


def test_login_and_me_flow(client, app):
    with app.app_context():
        create_user()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )

    assert login_response.status_code == 200
    body = login_response.get_json()
    assert body["success"] is True
    access_token = body["data"]["access_token"]
    assert body["data"]["user"]["role"] == "admin"

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert me_response.status_code == 200
    assert me_response.get_json()["data"]["username"] == "admin"


def test_logout_revokes_token(client, app):
    with app.app_context():
        create_user()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    access_token = login_response.get_json()["data"]["access_token"]

    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert logout_response.status_code == 200

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 401


def test_login_rejects_invalid_password(client, app):
    with app.app_context():
        create_user()

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "salah"},
    )

    assert response.status_code == 401
    assert response.get_json()["success"] is False
