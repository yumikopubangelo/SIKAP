import os
from datetime import date, datetime, time, timedelta

from app.extensions import db
from app.models import Absensi, Kelas, Perangkat, SesiSholat, Siswa, User, WaktuSholat
from app.models.absensi import StatusAbsensi

def seed_rekap_data():
    for kode, desc in [("tepat_waktu", "Tepat Waktu"), ("terlambat", "Terlambat"), ("alpha", "Alpha"), ("izin", "Izin"), ("sakit", "Sakit"), ("haid", "Haid")]:
        db.session.add(StatusAbsensi(kode=kode, deskripsi=desc))

    wali = User(
        username="wali_rekap",
        full_name="Wali Rekap",
        email="wali.rekap@sikap.local",
        role="wali_kelas",
    )
    wali.set_password("wali123")
    db.session.add(wali)
    db.session.flush()

    kelas = Kelas(
        nama_kelas="X RPL 2",
        tingkat="X",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
        id_wali=wali.id_user,
    )
    db.session.add(kelas)
    db.session.flush()

    siswa1 = Siswa(
        id_user=None,
        nisn="5000000010",
        nama="Siswa Rajin",
        id_card="CARD-REKAP-001",
        id_kelas=kelas.id_kelas,
    )
    siswa2 = Siswa(
        id_user=None,
        nisn="5000000011",
        nama="Siswa Bolos",
        id_card="CARD-REKAP-002",
        id_kelas=kelas.id_kelas,
    )
    siswa3 = Siswa(
        id_user=None,
        nisn="5000000012",
        nama="Siswa Sakit",
        id_card="CARD-REKAP-003",
        id_kelas=kelas.id_kelas,
    )
    db.session.add_all([siswa1, siswa2, siswa3])
    db.session.flush()

    waktu = WaktuSholat(
        nama_sholat="Maghrib",
        waktu_adzan=time(18, 0, 0),
        waktu_iqamah=time(18, 10, 0),
        waktu_selesai=time(18, 30, 0),
    )
    perangkat = Perangkat(
        device_id="ESP-REKAP-001",
        nama_device="Perangkat Rekap",
        lokasi="Masjid",
        api_key="rek-key-001",
        status="online",
    )
    db.session.add_all([waktu, perangkat])
    db.session.flush()

    # Create 3 sessions (3 days)
    today = date.today()
    sesi1 = SesiSholat(id_waktu=waktu.id_waktu, tanggal=today, status="aktif")
    sesi2 = SesiSholat(id_waktu=waktu.id_waktu, tanggal=today - timedelta(days=1), status="aktif")
    sesi3 = SesiSholat(id_waktu=waktu.id_waktu, tanggal=today - timedelta(days=2), status="aktif")
    db.session.add_all([sesi1, sesi2, sesi3])
    db.session.flush()

    # Siswa 1: 3 hadir (tepat waktu)
    db.session.add(Absensi(id_siswa=siswa1.id_siswa, id_sesi=sesi1.id_sesi, timestamp=datetime.now(), status="tepat_waktu"))
    db.session.add(Absensi(id_siswa=siswa1.id_siswa, id_sesi=sesi2.id_sesi, timestamp=datetime.now(), status="tepat_waktu"))
    db.session.add(Absensi(id_siswa=siswa1.id_siswa, id_sesi=sesi3.id_sesi, timestamp=datetime.now(), status="terlambat"))

    # Siswa 2: 1 hadir, 2 alpha
    db.session.add(Absensi(id_siswa=siswa2.id_siswa, id_sesi=sesi1.id_sesi, timestamp=datetime.now(), status="terlambat"))
    db.session.add(Absensi(id_siswa=siswa2.id_siswa, id_sesi=sesi2.id_sesi, timestamp=datetime.now(), status="alpha"))
    db.session.add(Absensi(id_siswa=siswa2.id_siswa, id_sesi=sesi3.id_sesi, timestamp=datetime.now(), status="alpha"))

    # Siswa 3: 1 hadir, 1 izin, 1 sakit (izin dan sakit tidak mempengaruhi total yang menghitung persentase)
    db.session.add(Absensi(id_siswa=siswa3.id_siswa, id_sesi=sesi1.id_sesi, timestamp=datetime.now(), status="tepat_waktu"))
    db.session.add(Absensi(id_siswa=siswa3.id_siswa, id_sesi=sesi2.id_sesi, timestamp=datetime.now(), status="izin"))
    db.session.add(Absensi(id_siswa=siswa3.id_siswa, id_sesi=sesi3.id_sesi, timestamp=datetime.now(), status="sakit"))

    db.session.commit()
    return wali, kelas, siswa1, siswa2, siswa3

def login(client, username, password):
    res = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    return res.get_json()["data"]["access_token"]

def test_rekapitulasi_siswa(client, app):
    with app.app_context():
        wali, _, s1, s2, s3 = seed_rekap_data()
        s1_id = s1.id_siswa
        s2_id = s2.id_siswa
        s3_id = s3.id_siswa

    token = login(client, "wali_rekap", "wali123")
    
    # Test Siswa 1 (2 tepat waktu, 1 terlambat -> 3 hadir / 3 total -> 100%)
    res1 = client.get(f"/api/v1/rekapitulasi/siswa/{s1_id}", headers={"Authorization": f"Bearer {token}"})
    assert res1.status_code == 200
    data1 = res1.get_json()["data"]
    assert data1["tepat_waktu"] == 2
    assert data1["terlambat"] == 1
    assert data1["persentase"] == 100.0

    # Test Siswa 2 (1 terlambat, 2 alpha -> 1 hadir / 3 total -> 33.33%)
    res2 = client.get(f"/api/v1/rekapitulasi/siswa/{s2_id}", headers={"Authorization": f"Bearer {token}"})
    assert res2.status_code == 200
    data2 = res2.get_json()["data"]
    assert data2["terlambat"] == 1
    assert data2["alpha"] == 2
    assert data2["persentase"] == 33.33

    # Test Siswa 3 (1 tepat waktu, 1 izin, 1 sakit -> valid=1, hadir=1 -> 100%)
    res3 = client.get(f"/api/v1/rekapitulasi/siswa/{s3_id}", headers={"Authorization": f"Bearer {token}"})
    assert res3.status_code == 200
    data3 = res3.get_json()["data"]
    assert data3["tepat_waktu"] == 1
    assert data3["izin"] == 1
    assert data3["sakit"] == 1
    assert data3["persentase"] == 100.0

def test_rekapitulasi_kelas(client, app):
    with app.app_context():
        wali, kelas, _, _, _ = seed_rekap_data()
        k_id = kelas.id_kelas

    token = login(client, "wali_rekap", "wali123")
    res = client.get(f"/api/v1/rekapitulasi/kelas/{k_id}", headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 200
    body = res.get_json()
    assert len(body["data"]) == 3
    
    # Sort to verify specific students
    data = sorted(body["data"], key=lambda x: x["nisn"])
    # Siswa 1
    assert data[0]["persentase"] == 100.0
    # Siswa 2 
    assert data[1]["persentase"] == 33.33
    # Siswa 3
    assert data[2]["persentase"] == 100.0

def test_rekapitulasi_sekolah(client, app):
    with app.app_context():
        seed_rekap_data()

    token = login(client, "wali_rekap", "wali123")
    # Actually, wali shouldn't be restricted logically here unless middleware says so, let's just use wali
    token = login(client, "wali_rekap", "wali123")
    res = client.get("/api/v1/rekapitulasi/sekolah", headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 200
    body = res.get_json()
    assert "summary" in body["data"]
    assert "kelas" in body["data"]
    
    summary = body["data"]["summary"]
    # Total Tepat Waktu = 2 (s1) + 1 (s3) = 3
    # Total Terlambat = 1 (s1) + 1 (s2) = 2
    # Total Alpha = 2 (s2)
    # Total Valid = 3 + 2 + 2 = 7
    # Hadir = 3 + 2 = 5
    # Persentase = 5 / 7 * 100 = 71.43
    assert summary["tepat_waktu"] == 3
    assert summary["terlambat"] == 2
    assert summary["alpha"] == 2
    assert summary["persentase"] == 71.43
