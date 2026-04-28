from datetime import timedelta

from app.extensions import db
from app.models import Kelas, Perangkat, Siswa, User
from app.security import RfidSecurityError
from app.services import rfid_capture_service as capture_service


def seed_capture_data():
    admin = User(
        username="admin_capture",
        full_name="Admin Capture",
        email="admin.capture@sikap.local",
        role="admin",
    )
    admin.set_password("admin12345")

    kelas = Kelas(
        nama_kelas="X RFID 1",
        tingkat="X",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    db.session.add_all([admin, kelas])
    db.session.flush()

    siswa = Siswa(
        nisn="7100000001",
        nama="Siswa Capture",
        id_card=None,
        id_kelas=kelas.id_kelas,
    )
    perangkat = Perangkat(
        device_id="ESP-CAPTURE-001",
        nama_device="Capture Reader",
        lokasi="Ruang Admin",
        api_key="capture-secret",
        status="offline",
    )
    db.session.add_all([siswa, perangkat])
    db.session.commit()
    return admin, siswa, perangkat


def test_capture_session_basic_flow(app):
    with app.app_context():
        capture_service.reset_capture_state()
        admin, siswa, _perangkat = seed_capture_data()

        started = capture_service.start_capture_session(admin, {"student_id": siswa.id_siswa})
        assert started["status"] == "waiting_first_tap"
        assert started["student_id"] == siswa.id_siswa

        current = capture_service.get_capture_session(admin)
        assert current["session_id"] == started["session_id"]

        reset = capture_service.reset_capture_session(admin)
        assert reset["status"] == "waiting_first_tap"
        assert reset["first_uid"] is None

        capture_service.cancel_capture_session(admin)
        assert capture_service.get_capture_session(admin) is None


def test_capture_session_rejects_invalid_student_and_missing_session(app):
    with app.app_context():
        capture_service.reset_capture_state()
        admin, _siswa, _perangkat = seed_capture_data()

        try:
            capture_service.start_capture_session(admin, {"student_id": "abc"})
            assert False, "student_id non-angka seharusnya ditolak"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 400

        try:
            capture_service.start_capture_session(admin, {"student_id": 9999})
            assert False, "student_id yang tidak ada seharusnya ditolak"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 404

        try:
            capture_service.reset_capture_session(admin)
            assert False, "reset tanpa sesi aktif seharusnya ditolak"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 404


def test_record_capture_tap_requires_valid_session_and_device(app):
    with app.app_context():
        capture_service.reset_capture_state()
        _admin, _siswa, perangkat = seed_capture_data()
        payload = {"device_id": perangkat.device_id, "uid_card": "CARD-1", "timestamp": None}

        try:
            capture_service.record_capture_tap(payload, {"X-API-Key": perangkat.api_key})
            assert False, "tap tanpa sesi aktif seharusnya ditolak"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 409

        try:
            capture_service.record_capture_tap(payload, {})
            assert False, "tap tanpa API key seharusnya ditolak"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 401

        try:
            capture_service.record_capture_tap(payload, {"X-API-Key": "wrong-key"})
            assert False, "tap dengan API key salah seharusnya ditolak"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 401

        try:
            capture_service.record_capture_tap(
                {"device_id": "UNKNOWN-DEVICE", "uid_card": "CARD-1", "timestamp": None},
                {"X-API-Key": perangkat.api_key},
            )
            assert False, "tap dengan device tidak dikenal seharusnya ditolak"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 404


def test_record_capture_tap_confirms_uid_and_updates_device(app, monkeypatch):
    with app.app_context():
        capture_service.reset_capture_state()
        admin, siswa, perangkat = seed_capture_data()
        capture_service.start_capture_session(admin, {"student_id": siswa.id_siswa})

        monkeypatch.setattr(
            capture_service,
            "verify_rfid_signature",
            lambda payload, headers, perangkat=None: {"verified": False, "nonce": None},
        )

        first = capture_service.record_capture_tap(
            {"device_id": perangkat.device_id, "uid_card": "CARD-CONFIRM", "timestamp": None},
            {"X-API-Key": perangkat.api_key},
        )
        assert first["status"] == "waiting_second_tap"
        assert first["first_uid"] == "CARD-CONFIRM"
        assert first["confirmed_uid"] is None

        second = capture_service.record_capture_tap(
            {"device_id": perangkat.device_id, "uid_card": "CARD-CONFIRM", "timestamp": None},
            {"X-API-Key": perangkat.api_key},
        )
        assert second["status"] == "confirmed"
        assert second["confirmed_uid"] == "CARD-CONFIRM"
        assert second["tap_count"] == 2

        perangkat_refresh = db.session.get(Perangkat, perangkat.device_id)
        assert perangkat_refresh.status == "online"
        assert perangkat_refresh.last_ping is not None


def test_record_capture_tap_restarts_when_uid_changes_and_propagates_signature_errors(app, monkeypatch):
    with app.app_context():
        capture_service.reset_capture_state()
        admin, siswa, perangkat = seed_capture_data()
        capture_service.start_capture_session(admin, {"student_id": siswa.id_siswa})

        monkeypatch.setattr(
            capture_service,
            "verify_rfid_signature",
            lambda payload, headers, perangkat=None: {"verified": False, "nonce": None},
        )

        capture_service.record_capture_tap(
            {"device_id": perangkat.device_id, "uid_card": "CARD-A", "timestamp": None},
            {"X-API-Key": perangkat.api_key},
        )
        changed = capture_service.record_capture_tap(
            {"device_id": perangkat.device_id, "uid_card": "CARD-B", "timestamp": None},
            {"X-API-Key": perangkat.api_key},
        )
        assert changed["status"] == "waiting_second_tap"
        assert changed["first_uid"] == "CARD-B"
        assert changed["confirmed_uid"] is None

        def raise_signature(*_args, **_kwargs):
            raise RfidSecurityError("Signature gagal", 401, errors={"sig": "bad"})

        monkeypatch.setattr(capture_service, "verify_rfid_signature", raise_signature)
        try:
            capture_service.record_capture_tap(
                {"device_id": perangkat.device_id, "uid_card": "CARD-C", "timestamp": None},
                {"X-API-Key": perangkat.api_key},
            )
            assert False, "signature error seharusnya dipropagasi sebagai RfidCaptureServiceError"
        except capture_service.RfidCaptureServiceError as exc:
            assert exc.status_code == 401
            assert exc.errors == {"sig": "bad"}


def test_expired_capture_session_is_cleaned(app, monkeypatch):
    with app.app_context():
        capture_service.reset_capture_state()
        admin, siswa, _perangkat = seed_capture_data()
        started = capture_service.start_capture_session(admin, {"student_id": siswa.id_siswa})
        assert started["expires_in_seconds"] > 0

        future = capture_service._utcnow() + timedelta(seconds=capture_service.CAPTURE_SESSION_TTL_SECONDS + 1)
        monkeypatch.setattr(capture_service, "_utcnow", lambda: future)

        assert capture_service.has_active_capture_session() is False
        assert capture_service.get_capture_session(admin) is None
