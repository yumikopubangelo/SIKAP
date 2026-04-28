from datetime import date, time, timedelta

from app.extensions import db
from app.models import Kelas, Notifikasi, OrangTua, StatusAbsensi, SuratPeringatan, Siswa, User, WaktuSholat


def seed_sp_data(parent_email="pgaurdian45@gmail.com"):
    statuses = [
        StatusAbsensi(kode="tepat_waktu", deskripsi="Tepat Waktu"),
        StatusAbsensi(kode="terlambat", deskripsi="Terlambat"),
        StatusAbsensi(kode="alpha", deskripsi="Alpha"),
        StatusAbsensi(kode="haid", deskripsi="Haid"),
        StatusAbsensi(kode="izin", deskripsi="Izin"),
        StatusAbsensi(kode="sakit", deskripsi="Sakit"),
    ]
    db.session.add_all(statuses)

    guru = User(
        username="guru_sp",
        full_name="Guru SP",
        email="guru.sp@sikap.local",
        role="guru_piket",
    )
    guru.set_password("guru12345")

    parent_user = User(
        username="ortu_sp",
        full_name="Orang Tua SP",
        email=parent_email,
        role="orangtua",
    )
    parent_user.set_password("orangtua123")

    siswa_user = User(
        username="siswa_sp",
        full_name="Siswa SP",
        email="siswa.sp@sikap.local",
        role="siswa",
    )
    siswa_user.set_password("siswa12345")
    db.session.add_all([guru, parent_user, siswa_user])
    db.session.flush()

    kelas = Kelas(
        nama_kelas="XI RPL SP",
        tingkat="XI",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    db.session.add(kelas)
    db.session.flush()

    siswa = Siswa(
        id_user=siswa_user.id_user,
        nisn="5000000999",
        nama="Siswa SP",
        id_card="CARD-SP-001",
        id_kelas=kelas.id_kelas,
    )
    db.session.add(siswa)
    db.session.flush()

    db.session.add(
        OrangTua(
            id_user=parent_user.id_user,
            id_siswa=siswa.id_siswa,
        )
    )
    db.session.add(
        WaktuSholat(
            nama_sholat="Dzuhur",
            waktu_adzan=time(12, 0, 0),
            waktu_iqamah=time(12, 10, 0),
            waktu_selesai=time(12, 30, 0),
        )
    )
    db.session.commit()
    return {
        "guru": guru,
        "siswa_id": siswa.id_siswa,
        "parent_id": parent_user.id_user,
    }


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_three_consecutive_alpha_creates_sp_and_parent_notification(client, app, monkeypatch):
    with app.app_context():
        seeded = seed_sp_data()

    app.config["SP_CONSECUTIVE_ALPHA_THRESHOLDS"] = (3, 6, 9)
    app.config["SP_EMAIL_ENABLED"] = True
    sent_messages = []

    def fake_send_email(**kwargs):
        sent_messages.append(kwargs)
        return {"id": "gmail-message-id"}

    monkeypatch.setattr("app.services.sp_service.send_gmail_email", fake_send_email)

    token = login(client, "guru_sp", "guru12345")
    headers = {"Authorization": f"Bearer {token}"}

    for day_offset in range(2, -1, -1):
        response = client.post(
            "/api/v1/absensi/manual",
            headers=headers,
            json={
                "siswa_id": seeded["siswa_id"],
                "tanggal": (date.today() - timedelta(days=day_offset)).isoformat(),
                "waktu_sholat": "dzuhur",
                "status": "alpha",
                "keterangan": "Pengujian SP otomatis.",
            },
        )
        assert response.status_code == 201

    with app.app_context():
        assert SuratPeringatan.query.count() == 1
        sp = SuratPeringatan.query.first()
        assert sp.jenis == "SP1"
        assert sp.status_kirim == "terkirim"
        notification = Notifikasi.query.filter_by(id_user=seeded["parent_id"]).first()
        assert notification is not None
        assert "SP1" in notification.judul

    assert len(sent_messages) == 1
    assert sent_messages[0]["recipient_email"] == "pgaurdian45@gmail.com"


def test_sp_marks_without_email_when_parent_has_no_email(client, app, monkeypatch):
    with app.app_context():
        seeded = seed_sp_data(parent_email=None)

    app.config["SP_CONSECUTIVE_ALPHA_THRESHOLDS"] = (3, 6, 9)
    app.config["SP_EMAIL_ENABLED"] = True

    def fail_if_called(**_kwargs):
        raise AssertionError("send_gmail_email tidak boleh dipanggil bila email orang tua kosong.")

    monkeypatch.setattr("app.services.sp_service.send_gmail_email", fail_if_called)

    token = login(client, "guru_sp", "guru12345")
    headers = {"Authorization": f"Bearer {token}"}

    for day_offset in range(2, -1, -1):
        response = client.post(
            "/api/v1/absensi/manual",
            headers=headers,
            json={
                "siswa_id": seeded["siswa_id"],
                "tanggal": (date.today() - timedelta(days=day_offset)).isoformat(),
                "waktu_sholat": "dzuhur",
                "status": "alpha",
                "keterangan": "Pengujian SP tanpa email.",
            },
        )
        assert response.status_code == 201

    with app.app_context():
        sp = SuratPeringatan.query.first()
        assert sp is not None
        assert sp.status_kirim == "tanpa_email"
