from datetime import date, time

from app.extensions import db
from app.models import IzinPengajuan, Kelas, SengketaAbsensi, SesiSholat, Siswa, User, WaktuSholat
from app.services import izin_service, sengketa_service
from app.services.absensi_service import AbsensiServiceError


def seed_school_case():
    siswa_user = User(
        username="siswa_case",
        full_name="Siswa Case",
        email="siswa.case@sikap.local",
        role="siswa",
    )
    siswa_user.set_password("siswa12345")

    wali = User(
        username="wali_case",
        full_name="Wali Case",
        email="wali.case@sikap.local",
        role="wali_kelas",
    )
    wali.set_password("wali12345")

    kepsek = User(
        username="kepsek_case",
        full_name="Kepsek Case",
        email="kepsek.case@sikap.local",
        role="kepsek",
    )
    kepsek.set_password("kepsek12345")

    guru_piket = User(
        username="piket_case",
        full_name="Guru Piket Case",
        email="piket.case@sikap.local",
        role="guru_piket",
    )
    guru_piket.set_password("piket12345")

    kelas = Kelas(
        nama_kelas="XI CASE 1",
        tingkat="XI",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
        id_wali=None,
    )
    db.session.add_all([siswa_user, wali, kepsek, guru_piket, kelas])
    db.session.flush()
    kelas.id_wali = wali.id_user

    siswa = Siswa(
        id_user=siswa_user.id_user,
        nisn="7200000001",
        nama="Siswa Case",
        id_card="CARD-CASE-001",
        id_kelas=kelas.id_kelas,
    )
    waktu = WaktuSholat(
        nama_sholat="Dzuhur",
        waktu_adzan=time(12, 0, 0),
        waktu_iqamah=time(12, 10, 0),
        waktu_selesai=time(12, 30, 0),
    )
    db.session.add_all([siswa, waktu])
    db.session.flush()

    sesi_1 = SesiSholat(id_waktu=waktu.id_waktu, tanggal=date(2026, 4, 28), status="aktif")
    sesi_2 = SesiSholat(id_waktu=waktu.id_waktu, tanggal=date(2026, 4, 29), status="aktif")
    db.session.add_all([sesi_1, sesi_2])
    db.session.commit()

    return {
        "siswa_user": siswa_user,
        "wali": wali,
        "kepsek": kepsek,
        "guru_piket": guru_piket,
        "siswa": siswa,
        "sesi_1": sesi_1,
        "sesi_2": sesi_2,
    }


def login(client, username, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    return response.get_json()["data"]["access_token"]


def test_izin_service_validations_and_business_rules(app, monkeypatch):
    with app.app_context():
        data = seed_school_case()
        siswa_user = data["siswa_user"]
        wali = data["wali"]

        try:
            izin_service.create_izin({}, wali)
            assert False, "wali tidak boleh membuat izin"
        except izin_service.IzinServiceError as exc:
            assert exc.status_code == 403

        try:
            izin_service.create_izin({"tanggal_mulai": "2026/04/28", "tanggal_selesai": "2026-04-29", "alasan": "izin"}, siswa_user)
            assert False, "format tanggal salah seharusnya ditolak"
        except izin_service.IzinServiceError as exc:
            assert exc.status_code == 400

        try:
            izin_service.create_izin({"tanggal_mulai": "2026-04-28", "tanggal_selesai": "2026-04-29"}, siswa_user)
            assert False, "alasan kosong seharusnya ditolak"
        except izin_service.IzinServiceError as exc:
            assert exc.status_code == 400

        created = izin_service.create_izin(
            {"tanggal_mulai": "2026-04-28", "tanggal_selesai": "2026-04-29", "alasan": "Haid bulanan"},
            siswa_user,
        )
        assert created["status"] == "pending"

        calls = []

        def fake_create_manual_absensi(payload, current_user):
            calls.append((payload, current_user.id_user))
            return {"ok": True}, 1

        monkeypatch.setattr(izin_service, "create_manual_absensi", fake_create_manual_absensi)
        resolved = izin_service.resolve_izin(created["id_izin"], "approve", "Disetujui", wali)
        assert resolved["status"] == "disetujui"
        assert len(calls) == 2
        assert all(call[0]["status"] == "haid" for call in calls)

        second = izin_service.create_izin(
            {"tanggal_mulai": "2026-04-28", "tanggal_selesai": "2026-04-28", "alasan": "Izin sekolah"},
            siswa_user,
        )
        rejected = izin_service.resolve_izin(second["id_izin"], "reject", "Ditolak", wali)
        assert rejected["status"] == "ditolak"

        duplicate_status = db.session.get(IzinPengajuan, created["id_izin"])
        try:
            izin_service.resolve_izin(duplicate_status.id_izin, "approve", "Ulang", wali)
            assert False, "izin non-pending seharusnya ditolak"
        except izin_service.IzinServiceError as exc:
            assert exc.status_code == 400

        third = izin_service.create_izin(
            {"tanggal_mulai": "2026-04-28", "tanggal_selesai": "2026-04-28", "alasan": "Izin umum"},
            siswa_user,
        )
        try:
            izin_service.resolve_izin(third["id_izin"], "unknown", "Invalid", wali)
            assert False, "action tidak valid seharusnya ditolak"
        except izin_service.IzinServiceError as exc:
            assert exc.status_code == 400

        try:
            izin_service.resolve_izin(9999, "approve", "Tidak ada", wali)
            assert False, "izin yang tidak ada seharusnya ditolak"
        except izin_service.IzinServiceError as exc:
            assert exc.status_code == 404


def test_sengketa_service_validations_and_business_rules(app, monkeypatch):
    with app.app_context():
        data = seed_school_case()
        siswa_user = data["siswa_user"]
        guru_piket = data["guru_piket"]
        wali = data["wali"]
        sesi_1 = data["sesi_1"]

        try:
            sengketa_service.create_sengketa({}, wali)
            assert False, "wali tidak boleh membuat sengketa"
        except sengketa_service.SengketaServiceError as exc:
            assert exc.status_code == 403

        try:
            sengketa_service.create_sengketa({"id_sesi": sesi_1.id_sesi}, siswa_user)
            assert False, "alasan kosong seharusnya ditolak"
        except sengketa_service.SengketaServiceError as exc:
            assert exc.status_code == 400

        created = sengketa_service.create_sengketa(
            {"id_sesi": sesi_1.id_sesi, "alasan": "Saya hadir tetapi kartu gagal"},
            siswa_user,
        )
        assert created["status"] == "pending"

        monkeypatch.setattr(
            sengketa_service,
            "create_manual_absensi",
            lambda payload, current_user: (_ for _ in ()).throw(
                AbsensiServiceError("Duplicate", 409)
            ),
        )
        approved = sengketa_service.resolve_sengketa(created["id_sengketa"], "approve", "Diterima", guru_piket)
        assert approved["status"] == "disetujui"

        second = sengketa_service.create_sengketa(
            {"id_sesi": sesi_1.id_sesi, "alasan": "Klaim kedua"},
            siswa_user,
        )
        monkeypatch.setattr(
            sengketa_service,
            "create_manual_absensi",
            lambda payload, current_user: (_ for _ in ()).throw(
                AbsensiServiceError("Kesalahan lain", 500)
            ),
        )
        try:
            sengketa_service.resolve_sengketa(second["id_sengketa"], "approve", "Error", guru_piket)
            assert False, "error absensi selain duplikasi seharusnya diteruskan"
        except sengketa_service.SengketaServiceError as exc:
            assert exc.status_code == 500

        third = sengketa_service.create_sengketa(
            {"id_sesi": sesi_1.id_sesi, "alasan": "Klaim ketiga"},
            siswa_user,
        )
        rejected = sengketa_service.resolve_sengketa(third["id_sengketa"], "reject", "Ditolak", guru_piket)
        assert rejected["status"] == "ditolak"

        resolved_row = db.session.get(SengketaAbsensi, third["id_sengketa"])
        try:
            sengketa_service.resolve_sengketa(resolved_row.id_sengketa, "reject", "Ulang", guru_piket)
            assert False, "sengketa non-pending seharusnya ditolak"
        except sengketa_service.SengketaServiceError as exc:
            assert exc.status_code == 400

        fourth = sengketa_service.create_sengketa(
            {"id_sesi": sesi_1.id_sesi, "alasan": "Klaim keempat"},
            siswa_user,
        )
        try:
            sengketa_service.resolve_sengketa(fourth["id_sengketa"], "oops", "Invalid", guru_piket)
            assert False, "action tidak valid seharusnya ditolak"
        except sengketa_service.SengketaServiceError as exc:
            assert exc.status_code == 400

        try:
            sengketa_service.resolve_sengketa(9999, "approve", "Tidak ada", guru_piket)
            assert False, "sengketa yang tidak ada seharusnya ditolak"
        except sengketa_service.SengketaServiceError as exc:
            assert exc.status_code == 404


def test_izin_routes_cover_create_list_and_approve(client, app):
    with app.app_context():
        data = seed_school_case()

    siswa_token = login(client, "siswa_case", "siswa12345")
    wali_token = login(client, "wali_case", "wali12345")

    create_response = client.post(
        "/api/v1/izin",
        headers={"Authorization": f"Bearer {siswa_token}"},
        json={
            "tanggal_mulai": "2026-04-28",
            "tanggal_selesai": "2026-04-29",
            "alasan": "Izin route test",
        },
    )
    assert create_response.status_code == 201
    izin_id = create_response.get_json()["data"]["id_izin"]

    list_response = client.get(
        "/api/v1/izin?status=pending",
        headers={"Authorization": f"Bearer {wali_token}"},
    )
    assert list_response.status_code == 200
    assert any(item["id_izin"] == izin_id for item in list_response.get_json()["data"])

    missing_action_response = client.put(
        f"/api/v1/izin/{izin_id}/approve",
        headers={"Authorization": f"Bearer {wali_token}"},
        json={},
    )
    assert missing_action_response.status_code == 400

    approve_response = client.put(
        f"/api/v1/izin/{izin_id}/approve",
        headers={"Authorization": f"Bearer {wali_token}"},
        json={"action": "reject", "catatan": "Route reject"},
    )
    assert approve_response.status_code == 200
    assert approve_response.get_json()["data"]["status"] == "ditolak"
