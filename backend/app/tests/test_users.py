from app.extensions import db
from app.models import Kelas, Perangkat, Siswa, User


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


def seed_student_without_card():
    kelas = Kelas(
        nama_kelas="XII RPL 7",
        tingkat="XII",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    siswa = Siswa(
        nisn="5000000399",
        nama="Siswa Tanpa Kartu",
        id_card=None,
        kelas=kelas,
    )
    db.session.add_all([kelas, siswa])
    db.session.commit()
    return siswa


def seed_student_user_without_card():
    kelas = Kelas(
        nama_kelas="XI TKJ 2",
        tingkat="XI",
        jurusan="TKJ",
        tahun_ajaran="2025/2026",
    )
    user = User(
        username="siswa_target",
        full_name="Siswa Target",
        email="siswa.target@sikap.local",
        role="siswa",
    )
    user.set_password("target12345")
    siswa = Siswa(
        nisn="5000000499",
        nama="Siswa Target",
        id_card=None,
        kelas=kelas,
        user=user,
    )
    db.session.add_all([kelas, user, siswa])
    db.session.commit()
    return user, siswa


def seed_rfid_device():
    perangkat = Perangkat(
        device_id="ESP-USERS-001",
        nama_device="RFID User Management",
        lokasi="Ruang Admin",
        api_key="device-secret-users",
        status="offline",
    )
    db.session.add(perangkat)
    db.session.commit()
    return perangkat


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


def test_admin_can_capture_and_assign_confirmed_rfid_uid_to_new_student_user(client, app):
    with app.app_context():
        admin = seed_admin()
        siswa = seed_student_without_card()
        perangkat = seed_rfid_device()
        student_id = siswa.id_siswa
        nisn = siswa.nisn
        device_id = perangkat.device_id
        api_key = perangkat.api_key

    token = login(client, "admin_users", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    start_response = client.post(
        "/api/v1/users/rfid-capture/session",
        headers=headers,
        json={"student_id": student_id},
    )
    assert start_response.status_code == 201

    tap_one_response = client.post(
        "/api/v1/rfid/capture",
        headers={"X-API-Key": api_key},
        json={"device_id": device_id, "uid_card": "CARD-NEW-001"},
    )
    assert tap_one_response.status_code == 201
    tap_one_body = tap_one_response.get_json()["data"]
    assert tap_one_body["first_uid"] == "CARD-NEW-001"
    assert tap_one_body["confirmed_uid"] is None
    assert tap_one_body["status"] == "waiting_second_tap"

    tap_two_response = client.post(
        "/api/v1/rfid/capture",
        headers={"X-API-Key": api_key},
        json={"device_id": device_id, "uid_card": "CARD-NEW-001"},
    )
    assert tap_two_response.status_code == 201
    tap_two_body = tap_two_response.get_json()["data"]
    assert tap_two_body["confirmed_uid"] == "CARD-NEW-001"
    assert tap_two_body["status"] == "confirmed"

    create_response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "username": "siswa.scanbaru",
            "full_name": "Siswa Scan Baru",
            "email": "siswa.scanbaru@sikap.local",
            "role": "siswa",
            "password": "password123",
            "nisn": nisn,
            "id_card": "CARD-NEW-001",
        },
    )

    assert create_response.status_code == 201
    create_body = create_response.get_json()["data"]
    assert create_body["student"]["nisn"] == nisn
    assert create_body["student"]["id_card"] == "CARD-NEW-001"


def test_admin_can_transfer_and_revoke_rfid_uid_from_student_user(client, app):
    with app.app_context():
        seed_admin()
        _donor_user, donor_student = seed_student_with_account()
        target_user, target_student = seed_student_user_without_card()
        perangkat = seed_rfid_device()
        donor_card = donor_student.id_card
        target_user_id = target_user.id_user
        target_student_id = target_student.id_siswa
        device_id = perangkat.device_id
        api_key = perangkat.api_key

    token = login(client, "admin_users", "admin123")
    headers = {"Authorization": f"Bearer {token}"}

    start_response = client.post(
        "/api/v1/users/rfid-capture/session",
        headers=headers,
        json={"student_id": target_student_id},
    )
    assert start_response.status_code == 201

    for _ in range(2):
        tap_response = client.post(
            "/api/v1/rfid/capture",
            headers={"X-API-Key": api_key},
            json={"device_id": device_id, "uid_card": donor_card},
        )
        assert tap_response.status_code == 201

    transfer_response = client.put(
        f"/api/v1/users/{target_user_id}",
        headers=headers,
        json={"id_card": donor_card},
    )
    assert transfer_response.status_code == 200
    transfer_body = transfer_response.get_json()["data"]
    assert transfer_body["student"]["id_card"] == donor_card

    with app.app_context():
        donor_refresh = Siswa.query.filter_by(nisn="5000000299").first()
        target_refresh = Siswa.query.filter_by(nisn="5000000499").first()
        assert donor_refresh.id_card is None
        assert target_refresh.id_card == donor_card

    revoke_response = client.put(
        f"/api/v1/users/{target_user_id}",
        headers=headers,
        json={"id_card": ""},
    )
    assert revoke_response.status_code == 200
    assert revoke_response.get_json()["data"]["student"]["id_card"] is None
