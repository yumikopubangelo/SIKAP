import base64
import tempfile
from datetime import date, datetime, time, timezone
from pathlib import Path

from app.extensions import db
from app.models import AuditLog, Kelas, Perangkat, Siswa, StatusAbsensi, User, WaktuSholat
from app.security import build_rfid_signature_message
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


def seed_absensi_manual_data():
    statuses = [
        StatusAbsensi(kode="tepat_waktu", deskripsi="Tepat Waktu"),
        StatusAbsensi(kode="terlambat", deskripsi="Terlambat"),
        StatusAbsensi(kode="alpha", deskripsi="Alpha"),
        StatusAbsensi(kode="haid", deskripsi="Haid"),
        StatusAbsensi(kode="izin", deskripsi="Izin"),
        StatusAbsensi(kode="sakit", deskripsi="Sakit"),
    ]
    db.session.add_all(statuses)

    guru_piket = User(
        username="piket_manual",
        full_name="Guru Piket",
        email="piket.manual@sikap.local",
        role="guru_piket",
    )
    guru_piket.set_password("piket123")

    admin = User(
        username="admin_manual",
        full_name="Admin Manual",
        email="admin.manual@sikap.local",
        role="admin",
    )
    admin.set_password("admin123")

    siswa_user = User(
        username="siswa_manual",
        full_name="Siswa Manual",
        email="siswa.manual@sikap.local",
        role="siswa",
    )
    siswa_user.set_password("siswa123")

    db.session.add_all([guru_piket, admin, siswa_user])
    db.session.flush()

    kelas = Kelas(
        nama_kelas="XI RPL 2",
        tingkat="XI",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    db.session.add(kelas)
    db.session.flush()

    siswa = Siswa(
        id_user=siswa_user.id_user,
        nisn="5000000010",
        nama="Siswa Manual",
        id_card="CARD-MANUAL-001",
        id_kelas=kelas.id_kelas,
    )
    waktu_sholat = WaktuSholat(
        nama_sholat="Dzuhur",
        waktu_adzan=time(12, 0, 0),
        waktu_iqamah=time(12, 10, 0),
        waktu_selesai=time(12, 30, 0),
    )

    db.session.add_all([siswa, waktu_sholat])
    db.session.commit()
    return {
        "siswa_id": siswa.id_siswa,
    }


def seed_absensi_rfid_data():
    statuses = [
        StatusAbsensi(kode="tepat_waktu", deskripsi="Tepat Waktu"),
        StatusAbsensi(kode="terlambat", deskripsi="Terlambat"),
        StatusAbsensi(kode="alpha", deskripsi="Alpha"),
        StatusAbsensi(kode="haid", deskripsi="Haid"),
        StatusAbsensi(kode="izin", deskripsi="Izin"),
        StatusAbsensi(kode="sakit", deskripsi="Sakit"),
    ]
    db.session.add_all(statuses)

    admin = User(
        username="admin_rfid",
        full_name="Admin RFID",
        email="admin.rfid@sikap.local",
        role="admin",
    )
    admin.set_password("admin123")

    siswa_user_1 = User(
        username="siswa_rfid_1",
        full_name="Siswa RFID 1",
        email="siswa.rfid1@sikap.local",
        role="siswa",
    )
    siswa_user_1.set_password("siswa123")

    siswa_user_2 = User(
        username="siswa_rfid_2",
        full_name="Siswa RFID 2",
        email="siswa.rfid2@sikap.local",
        role="siswa",
    )
    siswa_user_2.set_password("siswa123")

    db.session.add_all([admin, siswa_user_1, siswa_user_2])
    db.session.flush()

    kelas = Kelas(
        nama_kelas="XI RPL 3",
        tingkat="XI",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
        id_wali=admin.id_user,
    )
    db.session.add(kelas)
    db.session.flush()

    siswa_1 = Siswa(
        id_user=siswa_user_1.id_user,
        nisn="5000000111",
        nama="Siswa RFID 1",
        id_card="CARD-RFID-001",
        id_kelas=kelas.id_kelas,
    )
    siswa_2 = Siswa(
        id_user=siswa_user_2.id_user,
        nisn="5000000222",
        nama="Siswa RFID 2",
        id_card="CARD-RFID-002",
        id_kelas=kelas.id_kelas,
    )
    waktu_sholat = WaktuSholat(
        nama_sholat="Dzuhur",
        waktu_adzan=time(12, 0, 0),
        waktu_iqamah=time(12, 10, 0),
        waktu_selesai=time(12, 30, 0),
    )
    perangkat = Perangkat(
        device_id="ESP-001",
        nama_device="Gerbang Masjid",
        lokasi="Masjid Utama",
        api_key="device-secret",
        status="offline",
    )

    db.session.add_all([siswa_1, siswa_2, waktu_sholat, perangkat])
    db.session.commit()
    return {
        "device_id": perangkat.device_id,
        "api_key": perangkat.api_key,
        "uid_card_1": siswa_1.id_card,
        "uid_card_2": siswa_2.id_card,
    }


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    body = response.get_json()
    return body["data"]["access_token"]


def test_rfid_device_can_create_absensi(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": seeded["api_key"]},
        json={
            "uid_card": seeded["uid_card_1"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T12:05:00",
        },
    )

    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["status"] == "tepat_waktu"
    assert body["device_id"] == seeded["device_id"]
    assert body["color"] == "green"
    assert body["verified_by_guru_piket"] is False
    assert body["signature_verified"] is False
    assert body["audit_log_id"] >= 1

    with app.app_context():
        perangkat = db.session.get(Perangkat, seeded["device_id"])
        assert perangkat.status == "online"
        assert perangkat.last_ping is not None
        assert AuditLog.query.count() == 1


def test_rfid_device_rejects_duplicate_absensi_in_same_session(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    first_payload = {
        "uid_card": seeded["uid_card_1"],
        "device_id": seeded["device_id"],
        "timestamp": f"{date.today().isoformat()}T12:05:00",
    }
    headers = {"X-API-Key": seeded["api_key"]}

    first_response = client.post("/api/v1/absensi", headers=headers, json=first_payload)
    assert first_response.status_code == 201

    duplicate_response = client.post(
        "/api/v1/absensi",
        headers=headers,
        json={**first_payload, "timestamp": f"{date.today().isoformat()}T12:06:00"},
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.get_json()["message"] == "Siswa sudah tercatat hadir untuk sesi ini."


def test_rfid_device_requires_valid_api_key(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": "wrong-key"},
        json={
            "uid_card": seeded["uid_card_1"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T12:05:00",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Perangkat tidak valid atau API key salah."


def test_rfid_device_can_use_public_key_signature_when_enabled(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, f"{seeded['device_id']}.pem").write_bytes(public_key)
        app.config["RFID_REQUIRE_SIGNATURE"] = True
        app.config["RFID_PUBLIC_KEY_DIR"] = temp_dir
        app.config["RFID_SIGNATURE_TOLERANCE_SECONDS"] = 120

        signature_timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "uid_card": seeded["uid_card_1"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T12:05:00",
        }
        message = build_rfid_signature_message(
            payload,
            datetime.fromisoformat(signature_timestamp.replace("Z", "+00:00")),
        )
        signature = base64.b64encode(private_key.sign(message)).decode("utf-8")

        response = client.post(
            "/api/v1/absensi",
            headers={
                "X-API-Key": seeded["api_key"],
                "X-RFID-Signature": signature,
                "X-RFID-Signature-Timestamp": signature_timestamp,
            },
            json=payload,
        )

    assert response.status_code == 201
    assert response.get_json()["data"]["signature_verified"] is True


def test_rfid_signature_is_required_when_enforced(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    app.config["RFID_REQUIRE_SIGNATURE"] = True

    response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": seeded["api_key"]},
        json={
            "uid_card": seeded["uid_card_1"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T12:05:00",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "Tanda tangan RFID wajib disertakan."


def test_rfid_signature_rejects_replay_timestamp(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, f"{seeded['device_id']}.pem").write_bytes(public_key)
        app.config["RFID_REQUIRE_SIGNATURE"] = True
        app.config["RFID_PUBLIC_KEY_DIR"] = temp_dir
        app.config["RFID_SIGNATURE_TOLERANCE_SECONDS"] = 120

        signature_timestamp = datetime.now(timezone.utc).isoformat()
        payload = {
            "uid_card": seeded["uid_card_1"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T12:05:00",
        }
        message = build_rfid_signature_message(
            payload,
            datetime.fromisoformat(signature_timestamp.replace("Z", "+00:00")),
        )
        signature = base64.b64encode(private_key.sign(message)).decode("utf-8")

        first_response = client.post(
            "/api/v1/absensi",
            headers={
                "X-API-Key": seeded["api_key"],
                "X-RFID-Signature": signature,
                "X-RFID-Signature-Timestamp": signature_timestamp,
            },
            json=payload,
        )

        second_response = client.post(
            "/api/v1/absensi",
            headers={
                "X-API-Key": seeded["api_key"],
                "X-RFID-Signature": signature,
                "X-RFID-Signature-Timestamp": signature_timestamp,
            },
            json={
                "uid_card": seeded["uid_card_2"],
                "device_id": seeded["device_id"],
                "timestamp": f"{date.today().isoformat()}T12:06:00",
            },
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 401
    assert second_response.get_json()["message"] == "Permintaan RFID terdeteksi sebagai replay atau urutan timestamp mundur."


def test_rfid_device_rejects_tap_outside_active_session(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    response = client.post(
        "/api/v1/absensi",
        headers={"X-API-Key": seeded["api_key"]},
        json={
            "uid_card": seeded["uid_card_1"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T10:00:00",
        },
    )

    assert response.status_code == 409
    assert response.get_json()["message"] == "Tidak ada sesi sholat aktif untuk timestamp ini."


def test_absensi_list_is_available_and_scoped_by_role(client, app):
    with app.app_context():
        seeded = seed_absensi_rfid_data()

    headers = {"X-API-Key": seeded["api_key"]}
    response_1 = client.post(
        "/api/v1/absensi",
        headers=headers,
        json={
            "uid_card": seeded["uid_card_1"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T12:05:00",
        },
    )
    assert response_1.status_code == 201

    response_2 = client.post(
        "/api/v1/absensi",
        headers=headers,
        json={
            "uid_card": seeded["uid_card_2"],
            "device_id": seeded["device_id"],
            "timestamp": f"{date.today().isoformat()}T12:15:00",
        },
    )
    assert response_2.status_code == 201

    admin_token = login(client, "admin_rfid", "admin123")
    admin_response = client.get(
        "/api/v1/absensi?status=terlambat",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert admin_response.status_code == 200
    admin_body = admin_response.get_json()
    assert admin_body["pagination"]["total_items"] == 1
    assert len(admin_body["data"]) == 1
    assert admin_body["data"][0]["status"] == "terlambat"

    siswa_token = login(client, "siswa_rfid_1", "siswa123")
    siswa_response = client.get(
        "/api/v1/absensi",
        headers={"Authorization": f"Bearer {siswa_token}"},
    )

    assert siswa_response.status_code == 200
    siswa_body = siswa_response.get_json()
    assert siswa_body["pagination"]["total_items"] == 1
    assert len(siswa_body["data"]) == 1
    assert siswa_body["data"][0]["siswa"]["nisn"] == "5000000111"


def test_guru_piket_can_create_manual_absensi(client, app):
    with app.app_context():
        seeded = seed_absensi_manual_data()

    token = login(client, "piket_manual", "piket123")
    response = client.post(
        "/api/v1/absensi/manual",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "siswa_id": seeded["siswa_id"],
            "tanggal": date.today().isoformat(),
            "waktu_sholat": "dzuhur",
            "status": "tepat_waktu",
            "keterangan": "Kartu siswa tertinggal, diinput manual.",
        },
    )

    assert response.status_code == 201
    body = response.get_json()["data"]
    assert body["status"] == "tepat_waktu"
    assert body["verified_by_guru_piket"] is True
    assert body["audit_log_id"] >= 1
    assert len(body["audit_log"]) == 1

    with app.app_context():
        assert AuditLog.query.count() == 1


def test_guru_piket_can_update_absensi_and_audit_is_appended(client, app):
    with app.app_context():
        seeded = seed_absensi_manual_data()

    token = login(client, "piket_manual", "piket123")
    create_response = client.post(
        "/api/v1/absensi/manual",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "siswa_id": seeded["siswa_id"],
            "tanggal": date.today().isoformat(),
            "waktu_sholat": "dzuhur",
            "status": "tepat_waktu",
            "keterangan": "Input awal guru piket.",
        },
    )
    absensi_id = create_response.get_json()["data"]["id_absensi"]

    update_response = client.put(
        f"/api/v1/absensi/{absensi_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "status": "sakit",
            "keterangan": "Diperbarui setelah siswa menyerahkan izin sakit.",
        },
    )

    assert update_response.status_code == 200
    body = update_response.get_json()["data"]
    assert body["status"] == "sakit"
    assert body["audit_log_id"] >= 2
    assert len(body["audit_log"]) == 2
    assert body["audit_log"][0]["aksi"] == "UPDATE"

    with app.app_context():
        assert AuditLog.query.count() == 2


def test_non_guru_piket_cannot_create_manual_absensi(client, app):
    with app.app_context():
        seeded = seed_absensi_manual_data()

    token = login(client, "admin_manual", "admin123")
    response = client.post(
        "/api/v1/absensi/manual",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "siswa_id": seeded["siswa_id"],
            "tanggal": date.today().isoformat(),
            "waktu_sholat": "dzuhur",
            "status": "tepat_waktu",
        },
    )

    assert response.status_code == 403
