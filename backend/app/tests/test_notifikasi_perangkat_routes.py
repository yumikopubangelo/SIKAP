from app.extensions import db
from app.models import Notifikasi, Perangkat, User


def seed_notification_and_device_data():
    admin = User(
        username="admin_notif",
        full_name="Admin Notif",
        email="admin.notif@sikap.local",
        role="admin",
    )
    admin.set_password("admin12345")

    siswa = User(
        username="siswa_notif",
        full_name="Siswa Notif",
        email="siswa.notif@sikap.local",
        role="siswa",
    )
    siswa.set_password("siswa12345")

    perangkat = Perangkat(
        device_id="ESP-NOTIF-001",
        nama_device="Reader Notif",
        lokasi="Masjid",
        api_key="notif-secret",
        status="offline",
    )
    db.session.add_all([admin, siswa, perangkat])
    db.session.commit()
    return admin, siswa, perangkat


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_notifikasi_routes_cover_send_list_read_and_read_all(client, app):
    with app.app_context():
        _admin, siswa, _perangkat = seed_notification_and_device_data()
        siswa_id = siswa.id_user

    token = login(client, "siswa_notif", "siswa12345")

    missing_payload = client.post(
        "/api/v1/notifikasi/send",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert missing_payload.status_code == 400

    create_1 = client.post(
        "/api/v1/notifikasi/send",
        headers={"Authorization": f"Bearer {token}"},
        json={"id_user": siswa_id, "judul": "Notif 1", "pesan": "Pesan 1", "tipe": "sistem"},
    )
    assert create_1.status_code == 201
    notif_id = create_1.get_json()["data"]["id_notifikasi"]

    create_2 = client.post(
        "/api/v1/notifikasi/send",
        headers={"Authorization": f"Bearer {token}"},
        json={"id_user": siswa_id, "judul": "Notif 2", "pesan": "Pesan 2", "tipe": "sp"},
    )
    assert create_2.status_code == 201

    list_response = client.get(
        "/api/v1/notifikasi?only_unread=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    list_body = list_response.get_json()["data"]
    assert list_body["unread_count"] == 2
    assert len(list_body["notifikasi"]) == 2

    not_found = client.put(
        "/api/v1/notifikasi/9999/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert not_found.status_code == 404

    read_response = client.put(
        f"/api/v1/notifikasi/{notif_id}/read",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert read_response.status_code == 200
    assert read_response.get_json()["data"]["is_read"] is True

    read_all_response = client.put(
        "/api/v1/notifikasi/read-all",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert read_all_response.status_code == 200

    with app.app_context():
        assert Notifikasi.get_unread_count(siswa_id) == 0


def test_perangkat_ping_route_covers_missing_invalid_success_and_error(client, app, monkeypatch):
    with app.app_context():
        _admin, _siswa, perangkat = seed_notification_and_device_data()
        device_id = perangkat.device_id
        api_key = perangkat.api_key

    missing_credentials = client.post("/api/v1/perangkat/ping", json={"status": "online"})
    assert missing_credentials.status_code == 401

    invalid_credentials = client.post(
        "/api/v1/perangkat/ping",
        headers={"X-Device-Id": device_id, "X-Api-Key": "wrong-secret"},
        json={"status": "online"},
    )
    assert invalid_credentials.status_code == 401

    success_response = client.post(
        "/api/v1/perangkat/ping",
        headers={"X-Device-Id": device_id, "X-Api-Key": api_key},
        json={"status": "online"},
    )
    assert success_response.status_code == 200

    with app.app_context():
        perangkat_refresh = db.session.get(Perangkat, device_id)
        assert perangkat_refresh.status == "online"
        assert perangkat_refresh.last_ping is not None

    original_commit = db.session.commit

    def broken_commit():
        raise RuntimeError("commit gagal")

    monkeypatch.setattr(db.session, "commit", broken_commit)
    error_response = client.post(
        "/api/v1/perangkat/ping",
        headers={"X-Device-Id": device_id, "X-Api-Key": api_key},
        json={"status": "online"},
    )
    monkeypatch.setattr(db.session, "commit", original_commit)

    assert error_response.status_code == 500
    assert error_response.get_json()["message"] == "Database error"
