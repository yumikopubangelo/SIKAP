from app.extensions import db
from app.models import Siswa, User


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


def login_as_admin(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    return response.get_json()["data"]["access_token"]


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


def test_admin_can_register_manual_student_account(client, app):
    with app.app_context():
        create_user()

    token = login_as_admin(client)
    response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "mode": "manual",
            "username": "siswa_manual",
            "password": "siswa123",
            "full_name": "Siswa Manual",
            "role": "siswa",
            "student": {
                "nisn": "2000000001",
                "nama": "Siswa Manual",
                "id_card": "RFID-MANUAL-001",
            },
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["data"]["user"]["username"] == "siswa_manual"
    assert body["data"]["student"]["nisn"] == "2000000001"


def test_admin_can_lookup_and_register_from_school_db(client, app):
    with app.app_context():
        create_user()
        db.session.add(
            Siswa(
                id_user=None,
                nisn="3000000001",
                nama="Siswa Sekolah",
                id_card="RFID-SEKOLAH-001",
            )
        )
        db.session.commit()

    token = login_as_admin(client)
    lookup_response = client.get(
        "/api/v1/auth/student-candidates?nisn=3000000001",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert lookup_response.status_code == 200
    assert lookup_response.get_json()["data"]["has_account"] is False

    register_response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "mode": "from_school_db",
            "username": "siswa_import",
            "password": "siswa123",
            "email": "siswa.import@sikap.local",
            "nisn": "3000000001",
        },
    )

    assert register_response.status_code == 201
    body = register_response.get_json()
    assert body["data"]["user"]["username"] == "siswa_import"
    assert body["data"]["student"]["id_user"] is not None


def test_non_admin_cannot_register_account(client, app):
    with app.app_context():
        user = User(
            username="siswa",
            full_name="Siswa Biasa",
            email="siswa@sikap.local",
            role="siswa",
        )
        user.set_password("siswa123")
        db.session.add(user)
        db.session.commit()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "siswa", "password": "siswa123"},
    )
    token = login_response.get_json()["data"]["access_token"]

    response = client.post(
        "/api/v1/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "mode": "manual",
            "username": "illegal_create",
            "password": "password123",
            "full_name": "Tidak Boleh",
            "role": "guru_piket",
        },
    )

    assert response.status_code == 403
