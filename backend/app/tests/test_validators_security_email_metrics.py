import base64
import json
from datetime import date, datetime, time, timezone
from pathlib import Path
from urllib import error

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from app.extensions import db
from app.models import (
    Absensi,
    Kelas,
    Notifikasi,
    Perangkat,
    SesiSholat,
    Siswa,
    SuratPeringatan,
    User,
    WaktuSholat,
)
from app.routes import metrics as metrics_module
from app.security import (
    RfidSecurityError,
    _load_device_public_key,
    _parse_signature_timestamp,
    _verify_signature,
    build_rfid_signature_message,
    verify_rfid_signature,
)
from app.services import email_service
from app.utils import validators


def test_validators_cover_error_branches_and_aliases():
    payload, errors = validators.validate_register_payload(
        {"mode": "manual", "username": "u", "password": "12345678", "role": "wali", "full_name": "Nama"}
    )
    assert errors is None
    assert payload["role"] == "wali_kelas"

    _payload, errors = validators.validate_register_payload(
        {"mode": "invalid", "username": "", "password": "123", "role": "bad"}
    )
    assert "mode" in errors and "username" in errors and "password" in errors and "role" in errors

    _payload, errors = validators.validate_user_list_params({"role": "bad", "page": "0", "limit": "x"})
    assert "role" in errors and "page" in errors and "limit" in errors

    _payload, errors = validators.validate_user_update_payload({"password": "123"})
    assert "password" in errors

    _payload, errors = validators.validate_user_update_payload({})
    assert "payload" in errors

    _payload, errors = validators.validate_waktu_sholat_update_payload(
        {"waktu_adzan": "abc", "waktu_iqamah": "25:00", "waktu_selesai": ""}
    )
    assert "waktu_adzan" in errors and "waktu_iqamah" in errors and "waktu_selesai" in errors

    _payload, errors = validators.validate_kelas_payload({"tingkat": "XIII"}, partial=True)
    assert "tingkat" in errors

    _payload, errors = validators.validate_siswa_payload(
        {"nisn": "abc", "nama": "", "id_kelas": "x", "id_user": "y", "parent_user_id": "z"},
        partial=False,
    )
    assert "nisn" in errors and "nama" in errors and "id_kelas" in errors and "id_user" in errors and "parent_user_id" in errors

    _payload, errors = validators.validate_surat_peringatan_list_params({"siswa_id": "a", "kelas_id": "b", "jenis": "SP4"})
    assert "siswa_id" in errors and "kelas_id" in errors and "jenis" in errors

    _payload, errors = validators.validate_jadwal_piket_payload(
        {"user_id": "", "hari": "holiday", "jam_mulai": "09:00", "jam_selesai": "08:00"},
        partial=False,
    )
    assert "user_id" in errors and "hari" in errors and "jam_range" in errors


def test_security_helpers_and_signature_verification(app, tmp_path):
    with app.app_context():
        app.config["RFID_REQUIRE_SIGNATURE"] = False
        assert verify_rfid_signature({"device_id": "ESP-SEC", "uid_card": "CARD", "timestamp": None}, {}, None) == {
            "verified": False,
            "nonce": None,
        }

        try:
            _parse_signature_timestamp(None)
            assert False, "timestamp kosong seharusnya ditolak"
        except RfidSecurityError as exc:
            assert exc.status_code == 401

        try:
            _parse_signature_timestamp("bukan-timestamp")
            assert False, "timestamp invalid seharusnya ditolak"
        except RfidSecurityError as exc:
            assert exc.status_code == 401

        parsed = _parse_signature_timestamp("2026-04-28T12:00:00")
        assert parsed.tzinfo is not None

        perangkat = Perangkat(
            device_id="ESP-SEC-001",
            nama_device="Security Reader",
            lokasi="Masjid",
            api_key="sec-key",
            status="offline",
        )
        db.session.add(perangkat)
        db.session.commit()

        app.config["RFID_PUBLIC_KEY_DIR"] = str(tmp_path)
        try:
            _load_device_public_key(perangkat.device_id, perangkat)
            assert False, "public key yang belum ada seharusnya ditolak"
        except RfidSecurityError as exc:
            assert exc.status_code == 401

        perangkat.public_key = "INVALID-PEM"
        db.session.commit()
        try:
            _load_device_public_key(perangkat.device_id, perangkat)
            assert False, "public key invalid di database seharusnya ditolak"
        except RfidSecurityError as exc:
            assert exc.status_code == 500

        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        perangkat.public_key = public_key.decode("utf-8")
        perangkat.last_nonce = None
        db.session.commit()

        payload = {
            "device_id": perangkat.device_id,
            "uid_card": "CARD-SEC-001",
            "timestamp": datetime(2026, 4, 28, 12, 0, 0, tzinfo=timezone.utc),
        }
        signature_timestamp = datetime.now(timezone.utc).isoformat()
        message = build_rfid_signature_message(
            payload,
            datetime.fromisoformat(signature_timestamp.replace("Z", "+00:00")),
        )
        signature = base64.b64encode(private_key.sign(message)).decode("utf-8")

        app.config["RFID_REQUIRE_SIGNATURE"] = True
        app.config["RFID_SIGNATURE_TOLERANCE_SECONDS"] = 120

        verified = verify_rfid_signature(
            payload,
            {
                "X-RFID-Signature": signature,
                "X-RFID-Signature-Timestamp": signature_timestamp,
            },
            perangkat,
        )
        assert verified["verified"] is True
        assert verified["nonce"] is not None

        try:
            verify_rfid_signature(
                payload,
                {
                    "X-RFID-Signature": "not-base64",
                    "X-RFID-Signature-Timestamp": signature_timestamp,
                },
                perangkat,
            )
            assert False, "signature base64 invalid seharusnya ditolak"
        except RfidSecurityError as exc:
            assert exc.status_code == 401

        perangkat.last_nonce = verified["nonce"]
        db.session.commit()
        try:
            verify_rfid_signature(
                payload,
                {
                    "X-RFID-Signature": signature,
                    "X-RFID-Signature-Timestamp": signature_timestamp,
                },
                perangkat,
            )
            assert False, "replay nonce seharusnya ditolak"
        except RfidSecurityError as exc:
            assert exc.status_code == 401

        try:
            _verify_signature(object(), b"x", b"y")
            assert False, "jenis key unsupported seharusnya ditolak"
        except RfidSecurityError as exc:
            assert exc.status_code == 500


def test_email_service_helpers_and_send(app, tmp_path, monkeypatch):
    client_secret_path = tmp_path / "client_secret.json"
    token_path = tmp_path / "gmail_token.json"
    client_secret_path.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "client-id",
                    "client_secret": "client-secret",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost/callback"],
                }
            }
        ),
        encoding="utf-8",
    )

    with app.app_context():
        app.config["GMAIL_CLIENT_SECRET_PATH"] = str(client_secret_path)
        app.config["GMAIL_TOKEN_PATH"] = str(token_path)
        app.config["GMAIL_OAUTH_REDIRECT_URI"] = "http://localhost/callback"
        app.config["GMAIL_SENDER_EMAIL"] = "noreply@sikap.local"

        assert email_service._parse_iso_datetime(None) is None
        assert email_service._parse_iso_datetime("2026-04-28T12:00:00Z").tzinfo is not None

        url = email_service.build_gmail_authorization_url("state-123")
        assert "client_id=client-id" in url
        assert "state=state-123" in url

        monkeypatch.setattr(
            email_service,
            "_request_token",
            lambda token_uri, payload: {
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": email_service.GMAIL_SEND_SCOPE,
            },
        )
        exchanged = email_service.exchange_google_authorization_code("code-123")
        assert exchanged["refresh_token"] == "refresh-token"
        assert token_path.exists()

        fresh = email_service._refresh_access_token_if_needed()
        assert fresh["access_token"] == "access-token"

        token_path.write_text(
            json.dumps(
                {
                    "access_token": "old-token",
                    "refresh_token": "refresh-token",
                    "token_type": "Bearer",
                    "scope": email_service.GMAIL_SEND_SCOPE,
                    "expires_at": "2000-01-01T00:00:00+00:00",
                }
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(
            email_service,
            "_request_token",
            lambda token_uri, payload: {
                "access_token": "new-token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "scope": email_service.GMAIL_SEND_SCOPE,
            },
        )
        refreshed = email_service._refresh_access_token_if_needed()
        assert refreshed["access_token"] == "new-token"

        class DummyResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps({"id": "gmail-message-1"}).encode("utf-8")

        monkeypatch.setattr(email_service.request, "urlopen", lambda *args, **kwargs: DummyResponse())
        monkeypatch.setattr(
            email_service,
            "_refresh_access_token_if_needed",
            lambda: {"access_token": "send-token"},
        )

        result = email_service.send_gmail_email(
            recipient_email="tujuan@sikap.local",
            subject="Subjek Tes",
            body="Isi email tes",
        )
        assert result["id"] == "gmail-message-1"

        http_error = error.HTTPError(
            url="http://example.test",
            code=400,
            msg="Bad Request",
            hdrs=None,
            fp=None,
        )
        http_error.read = lambda: json.dumps({"error": {"message": "detail error"}}).encode("utf-8")
        message = email_service._build_http_error_message(http_error, "Prefix")
        assert "detail error" in message


def test_refresh_custom_metrics_updates_gauges_and_swallow_errors(app, monkeypatch):
    with app.app_context():
        admin = User(
            username="admin_metrics",
            full_name="Admin Metrics",
            email="admin.metrics@sikap.local",
            role="admin",
        )
        admin.set_password("admin12345")
        siswa_user = User(
            username="siswa_metrics",
            full_name="Siswa Metrics",
            email="siswa.metrics@sikap.local",
            role="siswa",
        )
        siswa_user.set_password("siswa12345")
        kelas = Kelas(
            nama_kelas="X MET 1",
            tingkat="X",
            jurusan="RPL",
            tahun_ajaran="2025/2026",
        )
        db.session.add_all([admin, siswa_user, kelas])
        db.session.flush()

        siswa = Siswa(
            id_user=siswa_user.id_user,
            nisn="7300000001",
            nama="Siswa Metrics",
            id_card="CARD-MET-001",
            id_kelas=kelas.id_kelas,
        )
        waktu = WaktuSholat(
            nama_sholat="Ashar",
            waktu_adzan=time(15, 0, 0),
            waktu_iqamah=time(15, 10, 0),
            waktu_selesai=time(15, 30, 0),
        )
        perangkat = Perangkat(
            device_id="ESP-MET-001",
            nama_device="Metrics Reader",
            lokasi="Masjid",
            api_key="met-key",
            status="online",
        )
        db.session.add_all([siswa, waktu, perangkat])
        db.session.flush()

        sesi = SesiSholat(id_waktu=waktu.id_waktu, tanggal=date.today(), status="aktif")
        db.session.add(sesi)
        db.session.flush()

        absensi = Absensi(
            id_siswa=siswa.id_siswa,
            id_sesi=sesi.id_sesi,
            timestamp=datetime.combine(date.today(), time(15, 5, 0)),
            status="tepat_waktu",
            device_id=perangkat.device_id,
        )
        notifikasi = Notifikasi(id_user=siswa_user.id_user, judul="Notif", pesan="Pesan", tipe="umum")
        sp = SuratPeringatan(
            id_siswa=siswa.id_siswa,
            sp_ke=1,
            tanggal=date.today(),
            jenis="SP1",
            id_pengirim=admin.id_user,
            alasan="Alpha",
        )
        db.session.add_all([absensi, notifikasi, sp])
        db.session.commit()

        metrics_module.refresh_custom_metrics(app)

        assert metrics_module.sikap_total_absensi._value.get() >= 1
        assert metrics_module.sikap_active_sessions._value.get() >= 1
        assert metrics_module.sikap_devices_online._value.get() >= 1
        assert metrics_module.sikap_total_siswa._value.get() >= 1
        assert metrics_module.sikap_total_kelas._value.get() >= 1
        assert metrics_module.sikap_total_notifikasi_unread._value.get() >= 1

        original_query = metrics_module.db.session.query

        def broken_query(*args, **kwargs):
            raise RuntimeError("query rusak")

        monkeypatch.setattr(metrics_module.db.session, "query", broken_query)
        metrics_module.refresh_custom_metrics(app)
        monkeypatch.setattr(metrics_module.db.session, "query", original_query)
