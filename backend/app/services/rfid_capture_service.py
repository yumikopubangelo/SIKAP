from __future__ import annotations

from datetime import datetime, timedelta
from threading import Lock
from uuid import uuid4

from ..extensions import db
from ..models import Perangkat, Siswa
from ..security import RfidSecurityError, verify_rfid_signature


CAPTURE_SESSION_TTL_SECONDS = 300

_capture_lock = Lock()
_active_capture_session: dict | None = None


class RfidCaptureServiceError(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def _utcnow() -> datetime:
    return datetime.utcnow()


def _serialize_student_brief(student: Siswa | None) -> dict | None:
    if student is None:
        return None

    return {
        "id_siswa": student.id_siswa,
        "id_user": student.id_user,
        "nisn": student.nisn,
        "nama": student.nama,
        "id_card": student.id_card,
    }


def _get_student_or_raise(student_id: int | None) -> Siswa | None:
    if student_id is None:
        return None

    student = Siswa.query.filter_by(id_siswa=student_id).first()
    if student is None:
        raise RfidCaptureServiceError("Data siswa tujuan tidak ditemukan.", 404)
    return student


def _cleanup_expired_session_locked() -> None:
    global _active_capture_session

    if _active_capture_session is None:
        return

    if _active_capture_session["expires_at"] <= _utcnow():
        _active_capture_session = None


def _find_session_for_admin_locked(admin_user_id: int) -> dict | None:
    _cleanup_expired_session_locked()
    if _active_capture_session is None:
        return None
    if _active_capture_session["admin_user_id"] != admin_user_id:
        return None
    return _active_capture_session


def _find_card_owner(id_card: str | None, target_student_id: int | None) -> Siswa | None:
    if not id_card:
        return None

    owner = Siswa.query.filter_by(id_card=id_card).first()
    if owner is None:
        return None
    if target_student_id is not None and owner.id_siswa == target_student_id:
        return None
    return owner


def _serialize_session(session: dict | None) -> dict | None:
    if session is None:
        return None

    owner = _find_card_owner(session.get("confirmed_uid") or session.get("first_uid"), session.get("student_id"))
    expires_in = max(0, int((session["expires_at"] - _utcnow()).total_seconds()))

    return {
        "session_id": session["session_id"],
        "student_id": session["student_id"],
        "student_name": session["student_name"],
        "nisn": session["nisn"],
        "current_id_card": session["current_id_card"],
        "first_uid": session["first_uid"],
        "confirmed_uid": session["confirmed_uid"],
        "status": session["status"],
        "message": session["message"],
        "tap_count": session["tap_count"],
        "device_id": session["device_id"],
        "started_at": session["started_at"].isoformat(),
        "updated_at": session["updated_at"].isoformat(),
        "expires_at": session["expires_at"].isoformat(),
        "expires_in_seconds": expires_in,
        "card_owner": _serialize_student_brief(owner),
    }


def _build_session(admin_user_id: int, student: Siswa | None) -> dict:
    now = _utcnow()
    return {
        "session_id": uuid4().hex,
        "admin_user_id": admin_user_id,
        "student_id": student.id_siswa if student else None,
        "student_name": student.nama if student else None,
        "nisn": student.nisn if student else None,
        "current_id_card": student.id_card if student else None,
        "first_uid": None,
        "confirmed_uid": None,
        "status": "waiting_first_tap",
        "message": "Tempelkan kartu RFID pertama untuk mulai verifikasi UID.",
        "tap_count": 0,
        "device_id": None,
        "started_at": now,
        "updated_at": now,
        "expires_at": now + timedelta(seconds=CAPTURE_SESSION_TTL_SECONDS),
    }


def reset_capture_state() -> None:
    global _active_capture_session
    with _capture_lock:
        _active_capture_session = None


def has_active_capture_session() -> bool:
    with _capture_lock:
        _cleanup_expired_session_locked()
        return _active_capture_session is not None


def start_capture_session(admin_user, payload: dict | None = None) -> dict:
    global _active_capture_session

    payload = payload or {}
    student_id_raw = payload.get("student_id")
    student_id = None
    if student_id_raw not in (None, ""):
        try:
            student_id = int(student_id_raw)
        except (TypeError, ValueError) as exc:
            raise RfidCaptureServiceError(
                "Student ID untuk sesi scan UID tidak valid.",
                400,
                errors={"student_id": "Gunakan angka ID siswa yang valid."},
            ) from exc

    student = _get_student_or_raise(student_id)

    with _capture_lock:
        _active_capture_session = _build_session(admin_user.id_user, student)
        return _serialize_session(_active_capture_session)


def get_capture_session(admin_user) -> dict | None:
    with _capture_lock:
        return _serialize_session(_find_session_for_admin_locked(admin_user.id_user))


def reset_capture_session(admin_user) -> dict:
    with _capture_lock:
        session = _find_session_for_admin_locked(admin_user.id_user)
        if session is None:
            raise RfidCaptureServiceError("Belum ada sesi scan UID yang aktif.", 404)

        session.update(
            {
                "first_uid": None,
                "confirmed_uid": None,
                "status": "waiting_first_tap",
                "message": "Scan diulang. Tempelkan kartu RFID pertama untuk mulai verifikasi UID.",
                "tap_count": 0,
                "device_id": None,
                "updated_at": _utcnow(),
                "expires_at": _utcnow() + timedelta(seconds=CAPTURE_SESSION_TTL_SECONDS),
            }
        )
        return _serialize_session(session)


def cancel_capture_session(admin_user) -> None:
    global _active_capture_session

    with _capture_lock:
        session = _find_session_for_admin_locked(admin_user.id_user)
        if session is None:
            return
        _active_capture_session = None


def _get_perangkat_or_raise(device_id: str, api_key: str | None) -> Perangkat:
    if not api_key:
        raise RfidCaptureServiceError(
            "API key perangkat wajib disertakan.",
            401,
            errors={"X-API-Key": "Header wajib diisi."},
        )

    perangkat = Perangkat.query.filter_by(device_id=device_id).first()
    if perangkat is None:
        raise RfidCaptureServiceError("Perangkat RFID tidak ditemukan.", 404)

    if (perangkat.api_key or "") != api_key:
        raise RfidCaptureServiceError(
            "API key perangkat tidak valid.",
            401,
            errors={"X-API-Key": "API key tidak cocok."},
        )

    return perangkat


def record_capture_tap(payload: dict, headers) -> dict:
    global _active_capture_session

    perangkat = _get_perangkat_or_raise(payload["device_id"], headers.get("X-API-Key"))

    try:
        signature_state = verify_rfid_signature(payload, headers, perangkat=perangkat)
    except RfidSecurityError as exc:
        raise RfidCaptureServiceError(exc.message, exc.status_code, errors=exc.errors) from exc

    with _capture_lock:
        _cleanup_expired_session_locked()
        if _active_capture_session is None:
            raise RfidCaptureServiceError("Belum ada sesi scan UID yang aktif untuk admin.", 409)

        session = _active_capture_session
        now = _utcnow()
        uid_card = payload["uid_card"]

        if session["confirmed_uid"] == uid_card:
            session["status"] = "confirmed"
            session["message"] = "UID kartu sudah terkonfirmasi."
            session["tap_count"] = 2
        elif not session["first_uid"] or session["first_uid"] != uid_card:
            session["first_uid"] = uid_card
            session["confirmed_uid"] = None
            session["status"] = "waiting_second_tap"
            session["message"] = "Tap pertama diterima. Tempelkan kartu yang sama sekali lagi untuk konfirmasi."
            session["tap_count"] = 1
        else:
            session["confirmed_uid"] = uid_card
            session["status"] = "confirmed"
            session["message"] = "UID kartu terkonfirmasi. Form user sekarang bisa disimpan."
            session["tap_count"] = 2

        session["device_id"] = perangkat.device_id
        session["updated_at"] = now
        session["expires_at"] = now + timedelta(seconds=CAPTURE_SESSION_TTL_SECONDS)
        serialized = _serialize_session(session)

    if signature_state["nonce"] is not None:
        perangkat.last_nonce = signature_state["nonce"]
    perangkat.status = "online"
    perangkat.last_ping = _utcnow()
    db.session.commit()

    return serialized
