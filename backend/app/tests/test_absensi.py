from datetime import date, time

from app.extensions import db
from app.models import AuditLog, Kelas, Siswa, StatusAbsensi, User, WaktuSholat


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


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    body = response.get_json()
    return body["data"]["access_token"]


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
