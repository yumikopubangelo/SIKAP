import os
from datetime import date, datetime, time

from app.extensions import db
from app.models import Absensi, Kelas, Perangkat, SesiSholat, Siswa, User, WaktuSholat


def seed_laporan_data():
    wali = User(
        username="wali_laporan",
        full_name="Wali Laporan",
        email="wali.laporan@sikap.local",
        role="wali_kelas",
    )
    wali.set_password("wali12345")
    db.session.add(wali)
    db.session.flush()

    kelas = Kelas(
        nama_kelas="X RPL 1",
        tingkat="X",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
        id_wali=wali.id_user,
    )
    db.session.add(kelas)
    db.session.flush()

    siswa = Siswa(
        id_user=None,
        nisn="5000000002",
        nama="Siswa Laporan",
        id_card="CARD-LAP-001",
        id_kelas=kelas.id_kelas,
    )
    db.session.add(siswa)

    waktu = WaktuSholat(
        nama_sholat="Ashar",
        waktu_adzan=time(15, 0, 0),
        waktu_iqamah=time(15, 10, 0),
        waktu_selesai=time(15, 30, 0),
    )
    perangkat = Perangkat(
        device_id="ESP-LAP-001",
        nama_device="Perangkat Laporan",
        lokasi="Masjid",
        api_key="lap-key-001",
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
        timestamp=datetime.combine(date.today(), time(15, 5, 0)),
        status="tepat_waktu",
        device_id=perangkat.device_id,
    )
    db.session.add(absensi)
    db.session.commit()
    return wali, kelas


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_generate_laporan_pdf_success(client, app):
    with app.app_context():
        wali, kelas = seed_laporan_data()
        kelas_id = kelas.id_kelas

    token = login(client, "wali_laporan", "wali12345")

    response = client.post(
        "/api/v1/laporan/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jenis": "kelas",
            "format": "pdf",
            "filter_id": kelas_id,
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["format"] == "pdf"
    assert "id_laporan" in body["data"]

    # Verify download works
    laporan_id = body["data"]["id_laporan"]
    download_res = client.get(
        f"/api/v1/laporan/download/{laporan_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert download_res.status_code == 200
    assert download_res.headers["Content-Type"] == "application/pdf"
    assert int(download_res.headers["Content-Length"]) > 0


def test_generate_laporan_excel_success(client, app):
    with app.app_context():
        wali,_ = seed_laporan_data()

    token = login(client, "wali_laporan", "wali12345")

    response = client.post(
        "/api/v1/laporan/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "jenis": "sekolah",
            "format": "excel",
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["format"] == "excel"

    laporan_id = body["data"]["id_laporan"]
    download_res = client.get(
        f"/api/v1/laporan/download/{laporan_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert download_res.status_code == 200
    # excel content type
    assert "spreadsheet" in download_res.headers["Content-Type"]


def test_generate_laporan_invalid_jenis_format(client, app):
    with app.app_context():
        wali, _ = seed_laporan_data()

    token = login(client, "wali_laporan", "wali12345")

    # Invalid jenis
    res1 = client.post("/api/v1/laporan/generate", headers={"Authorization": f"Bearer {token}"}, json={"jenis": "invalid", "format": "pdf"})
    assert res1.status_code == 400

    # Invalid format
    res2 = client.post("/api/v1/laporan/generate", headers={"Authorization": f"Bearer {token}"}, json={"jenis": "kelas", "format": "word"})
    assert res2.status_code == 400

    # Missing filter_id for kelas
    res3 = client.post("/api/v1/laporan/generate", headers={"Authorization": f"Bearer {token}"}, json={"jenis": "kelas", "format": "pdf"})
    assert res3.status_code == 400
