from app.extensions import db
from app.models import Kelas, Siswa, User


def seed_admin():
    admin = User(
        username="admin_users",
        full_name="Admin Users",
        email="admin.users@sikap.local",
        role="admin",
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.commit()
    return admin


def seed_non_admin():
    guru = User(
        username="guru_users",
        full_name="Guru Users",
        email="guru.users@sikap.local",
        role="guru_piket",
    )
    guru.set_password("guru12345")
    db.session.add(guru)
    db.session.commit()
    return guru


def seed_student_without_account():
    kelas = Kelas(
        nama_kelas="X RPL 9",
        tingkat="X",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    siswa = Siswa(
        nisn="5000000199",
        nama="Siswa Tanpa Akun",
        id_card="CARD-0199",
        kelas=kelas,
    )
    db.session.add_all([kelas, siswa])
    db.session.commit()
    return siswa


def seed_student_with_account():
    kelas = Kelas(
        nama_kelas="XI RPL 8",
        tingkat="XI",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    user = User(
        username="siswa_user",
        full_name="Siswa User",
        email="siswa.user@sikap.local",
        role="siswa",
    )
    user.set_password("siswa12345")
    siswa = Siswa(
        nisn="5000000299",
        nama="Siswa Dengan Akun",
        id_card="CARD-0299",
        kelas=kelas,
        user=user,
    )
    db.session.add_all([kelas, user, siswa])
    db.session.commit()
    return user, siswa


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_admin_can_create_list_update_and_delete_user(client, app):
    with app.app_context():
        seed_admin()

    token = login(client, "admin_users", "admin123")

    create_response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "wali.rpl",
            "full_name": "Wali RPL",
            "email": "wali.rpl@sikap.local",
            "no_telp": "081234567890",
            "role": "wali_kelas",
            "password": "password123",
        },
    )

    assert create_response.status_code == 201
    created = create_response.get_json()["data"]
    assert created["username"] == "wali.rpl"
    assert created["role"] == "wali_kelas"
    user_id = created["id_user"]

    list_response = client.get(
        "/api/v1/users?search=wali",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    list_body = list_response.get_json()
    assert list_body["pagination"]["total_items"] >= 1
    assert any(item["id_user"] == user_id for item in list_body["data"])

    detail_response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["email"] == "wali.rpl@sikap.local"

    update_response = client.put(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Wali RPL Update",
            "email": "wali.rpl.update@sikap.local",
        },
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["full_name"] == "Wali RPL Update"

    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200


def test_admin_can_create_student_user_by_nisn(client, app):
    with app.app_context():
        seed_admin()
        seed_student_without_account()

    token = login(client, "admin_users", "admin123")

    response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "username": "siswa.linked",
            "full_name": "Siswa Linked",
            "email": "siswa.linked@sikap.local",
            "role": "siswa",
            "password": "password123",
            "nisn": "5000000199",
        },
    )

    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["role"] == "siswa"
    assert body["student"]["nisn"] == "5000000199"
    assert body["student"]["nama"] == "Siswa Tanpa Akun"


def test_delete_rejects_user_linked_to_student(client, app):
    with app.app_context():
        seed_admin()
        user, _student = seed_student_with_account()
        linked_user_id = user.id_user

    token = login(client, "admin_users", "admin123")

    response = client.delete(
        f"/api/v1/users/{linked_user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert "data siswa" in response.get_json()["message"].lower()


def test_non_admin_cannot_access_user_management(client, app):
    with app.app_context():
        seed_non_admin()

    token = login(client, "guru_users", "guru12345")

    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
