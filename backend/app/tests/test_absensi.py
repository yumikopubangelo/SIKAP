from datetime import date, datetime, time

from app.extensions import db
from app.models import Kelas, Perangkat, SesiSholat, Siswa, User, WaktuSholat


def seed_auth_and_absensi_base():
    admin = User(
        username="admin_absensi",
        full_name="Admin Absensi",
        email="admin.absensi@sikap.local",
        role="admin",
    )
    admin.set_password("admin123")
    db.session.add(admin)
    db.session.flush()

    kelas = Kelas(
        nama_kelas="X RPL 1",
        tingkat="X",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    db.session.add(kelas)
    db.session.flush()

    siswa_user = User(
        username="siswa_absen",
        full_name="Siswa Absen",
        email="siswa.absen@sikap.local",
        role="siswa",
    )
    siswa_user.set_password("siswa123")
    db.session.add(siswa_user)
    db.session.flush()

    siswa = Siswa(
        id_user=siswa_user.id_user,
        nisn="4000000001",
        nama="Siswa Absen",
        id_card="A3B2C1D4",
        id_kelas=kelas.id_kelas,
    )
    waktu = WaktuSholat(
        nama_sholat="Dzuhur",
        waktu_adzan=time(12, 0, 0),
        waktu_iqamah=time(12, 10, 0),
        waktu_selesai=time(12, 30, 0),
    )
    perangkat = Perangkat(
        device_id="ESP8266_MASJID_01",
        nama_device="RFID Reader Masjid",
        lokasi="Masjid",
        api_key="device-key-demo-001",
        status="online",
    )
    db.session.add_all([siswa, waktu, perangkat])
    db.session.commit()
    return admin, siswa, waktu, perangkat


def login_admin(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_absensi", "password": "admin123"},
    )
    return response.get_json()["data"]["access_token"]


def test_rfid_absensi_creates_tepat_waktu_record(client, app):
    with app.app_context():
        seed_auth_and_absensi_base()

    response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": "device-key-demo-001"},
        json={
            "uid_card": "A3B2C1D4",
            "device_id": "ESP8266_MASJID_01",
            "timestamp": "2026-04-04T12:05:00",
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["data"]["status"] == "tepat_waktu"
    assert body["data"]["siswa"]["nisn"] == "4000000001"


def test_rfid_absensi_marks_terlambat_after_iqamah(client, app):
    with app.app_context():
        seed_auth_and_absensi_base()

    response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": "device-key-demo-001"},
        json={
            "uid_card": "A3B2C1D4",
            "device_id": "ESP8266_MASJID_01",
            "timestamp": "2026-04-04T12:15:00",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["data"]["status"] == "terlambat"


def test_rfid_absensi_rejects_unknown_card(client, app):
    with app.app_context():
        seed_auth_and_absensi_base()

    response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": "device-key-demo-001"},
        json={
            "uid_card": "UNKNOWN-CARD",
            "device_id": "ESP8266_MASJID_01",
            "timestamp": "2026-04-04T12:05:00",
        },
    )

    assert response.status_code == 404


def test_rfid_absensi_rejects_duplicate_tap_for_same_session(client, app):
    with app.app_context():
        seed_auth_and_absensi_base()

    payload = {
        "uid_card": "A3B2C1D4",
        "device_id": "ESP8266_MASJID_01",
        "timestamp": "2026-04-04T12:05:00",
    }
    first_response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": "device-key-demo-001"},
        json=payload,
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": "device-key-demo-001"},
        json=payload,
    )
    assert second_response.status_code == 400


def test_admin_can_list_and_view_absensi_detail(client, app):
    with app.app_context():
        seed_auth_and_absensi_base()
        sesi = SesiSholat(
            id_waktu=1,
            tanggal=date(2026, 4, 4),
            status="aktif",
        )
        db.session.add(sesi)
        db.session.flush()
        from app.models import Absensi

        absensi = Absensi(
            id_siswa=1,
            id_sesi=sesi.id_sesi,
            timestamp=datetime(2026, 4, 4, 12, 5, 0),
            status="tepat_waktu",
            device_id="ESP8266_MASJID_01",
        )
        db.session.add(absensi)
        db.session.commit()

    token = login_admin(client)
    list_response = client.get(
        "/api/v1/absensi",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200

    detail_response = client.get(
        "/api/v1/absensi/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.get_json()["data"]["status"] == "tepat_waktu"
