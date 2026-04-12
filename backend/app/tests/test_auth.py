from app.extensions import db
from app.models import Kelas, Siswa, User


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


def create_guru_piket_and_student():
    guru_piket = User(
        username="guru.piket",
        full_name="Guru Piket",
        email="guru.piket@sikap.local",
        role="guru_piket",
    )
    guru_piket.set_password("piket123")

    kelas = Kelas(
        nama_kelas="XI RPL 1",
        tingkat="XI",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )

    siswa = Siswa(
        nisn="5000000099",
        nama="Siti Aminah",
        id_card="CARD-0099",
        kelas=kelas,
    )

    db.session.add_all([guru_piket, kelas, siswa])
    db.session.commit()
    return guru_piket, siswa


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


def test_guru_piket_can_lookup_student_candidate_by_nisn(client, app):
    with app.app_context():
        create_guru_piket_and_student()

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "guru.piket", "password": "piket123"},
    )
    access_token = login_response.get_json()["data"]["access_token"]

    response = client.get(
        "/api/v1/auth/student-candidates?nisn=5000000099",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["student"]["nisn"] == "5000000099"
    assert body["student"]["nama"] == "Siti Aminah"
    assert body["student"]["kelas"] == "XI RPL 1"
    assert body["has_account"] is False
