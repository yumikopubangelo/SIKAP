from datetime import date, datetime, time

from app.extensions import db
from app.models import Absensi, Kelas, Perangkat, SesiSholat, Siswa, User, WaktuSholat


def seed_dashboard_data():
    admin = User(
        username="admin_dash",
        full_name="Admin Dashboard",
        email="admin.dashboard@sikap.local",
        role="admin",
        no_telp="081200001000",
    )
    admin.set_password("admin123")

    kepsek = User(
        username="kepsek_dash",
        full_name="Kepsek Dashboard",
        email="kepsek.dashboard@sikap.local",
        role="kepsek",
    )
    kepsek.set_password("kepsek123")

    wali = User(
        username="wali_dash",
        full_name="Wali Dashboard",
        email="wali.dashboard@sikap.local",
        role="wali_kelas",
    )
    wali.set_password("wali12345")

    piket = User(
        username="piket_dash",
        full_name="Piket Dashboard",
        email="piket.dashboard@sikap.local",
        role="guru_piket",
    )
    piket.set_password("piket123")

    siswa_user = User(
        username="siswa_dash",
        full_name="Siswa Dashboard",
        email="siswa.dashboard@sikap.local",
        role="siswa",
    )
    siswa_user.set_password("siswa123")

    ortu = User(
        username="ortu_dash",
        full_name="Orang Tua Dashboard",
        email="ortu.dashboard@sikap.local",
        role="orangtua",
        no_telp="081300001111",
    )
    ortu.set_password("ortu123")

    db.session.add_all([admin, kepsek, wali, piket, siswa_user, ortu])
    db.session.flush()

    kelas = Kelas(
        nama_kelas="XI RPL 1",
        tingkat="XI",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
        id_wali=wali.id_user,
    )
    db.session.add(kelas)
    db.session.flush()

    siswa = Siswa(
        id_user=siswa_user.id_user,
        nisn="5000000001",
        nama="Siswa Dashboard",
        id_card="CARD-DASH-001",
        id_kelas=kelas.id_kelas,
        no_telp_ortu="081300001111",
    )
    db.session.add(siswa)

    waktu = WaktuSholat(
        nama_sholat="Dzuhur",
        waktu_adzan=time(12, 0, 0),
        waktu_iqamah=time(12, 10, 0),
        waktu_selesai=time(12, 30, 0),
    )
    perangkat = Perangkat(
        device_id="ESP-DASH-001",
        nama_device="Perangkat Dashboard",
        lokasi="Masjid",
        api_key="dash-key-001",
        status="online",
    )
    db.session.add_all([waktu, perangkat])
    db.session.flush()

    sesi = SesiSholat(
        id_waktu=waktu.id_waktu,
        tanggal=date.today(),
        status="aktif",
    )
    db.session.add(sesi)
    db.session.flush()

    absensi = Absensi(
        id_siswa=siswa.id_siswa,
        id_sesi=sesi.id_sesi,
        timestamp=datetime.combine(date.today(), time(12, 5, 0)),
        status="tepat_waktu",
        device_id=perangkat.device_id,
    )
    db.session.add(absensi)
    db.session.commit()


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_admin_dashboard_returns_cards_and_rows(client, app):
    with app.app_context():
        seed_dashboard_data()

    token = login(client, "admin_dash", "admin123")
    response = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["role"] == "admin"
    assert len(body["cards"]) >= 4
    assert len(body["primary_table"]["rows"]) >= 1
    assert len(body["charts"]["attendance_trend"]["rows"]) == 7
    assert any(row["total"] >= 1 for row in body["charts"]["attendance_trend"]["rows"])
    assert body["charts"]["status_distribution"]["rows"][0]["status"] == "tepat_waktu"


def test_wali_dashboard_returns_owned_students(client, app):
    with app.app_context():
        seed_dashboard_data()

    token = login(client, "wali_dash", "wali12345")
    response = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    rows = response.get_json()["data"]["primary_table"]["rows"]
    assert rows[0]["nisn"] == "5000000001"


def test_siswa_dashboard_returns_history(client, app):
    with app.app_context():
        seed_dashboard_data()

    token = login(client, "siswa_dash", "siswa123")
    response = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["role"] == "siswa"
    assert body["primary_table"]["rows"][0]["status"] == "tepat_waktu"
    assert len(body["charts"]["attendance_trend"]["rows"]) == 7
    assert body["charts"]["status_distribution"]["rows"][0]["label"] == "Tepat Waktu"


def test_orangtua_dashboard_maps_child_from_phone(client, app):
    with app.app_context():
        seed_dashboard_data()

    token = login(client, "ortu_dash", "ortu123")
    response = client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.get_json()["data"]
    assert body["role"] == "orangtua"
    assert body["student"]["nisn"] == "5000000001"
