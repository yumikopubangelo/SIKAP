from datetime import date, datetime

from ..models.absensi import ABSENSI_STATUS_VALUES


def validate_login_payload(payload):
    payload = payload or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    errors = {}
    if not username:
        errors["username"] = "Username wajib diisi."
    if not password:
        errors["password"] = "Password wajib diisi."

    if errors:
        return None, errors

    return {"username": username, "password": password}, None


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_datetime(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_manual_absensi_payload(payload):
    payload = payload or {}
    siswa_id = payload.get("siswa_id") or payload.get("id_siswa")
    tanggal_raw = (payload.get("tanggal") or "").strip()
    waktu_sholat = (payload.get("waktu_sholat") or "").strip().lower()
    status = (payload.get("status") or "").strip().lower()
    keterangan = (payload.get("keterangan") or "").strip() or None
    timestamp_raw = (payload.get("timestamp") or "").strip()

    errors = {}
    if not siswa_id:
        errors["siswa_id"] = "Siswa wajib dipilih."
    elif not str(siswa_id).isdigit():
        errors["siswa_id"] = "Siswa tidak valid."

    tanggal = _parse_date(tanggal_raw) if tanggal_raw else None
    if tanggal is None:
        errors["tanggal"] = "Tanggal wajib diisi dengan format YYYY-MM-DD."

    if not waktu_sholat:
        errors["waktu_sholat"] = "Waktu sholat wajib diisi."

    if not status:
        errors["status"] = "Status absensi wajib diisi."
    elif status not in ABSENSI_STATUS_VALUES:
        errors["status"] = "Status absensi tidak dikenali."

    parsed_timestamp = None
    if timestamp_raw:
        parsed_timestamp = _parse_datetime(timestamp_raw)
        if parsed_timestamp is None:
            errors["timestamp"] = "Timestamp harus berformat ISO 8601."

    if errors:
        return None, errors

    return {
        "siswa_id": int(siswa_id),
        "tanggal": tanggal,
        "waktu_sholat": waktu_sholat,
        "status": status,
        "keterangan": keterangan,
        "timestamp": parsed_timestamp,
    }, None


def validate_absensi_update_payload(payload):
    payload = payload or {}
    status = (payload.get("status") or "").strip().lower()
    keterangan = (payload.get("keterangan") or "").strip()

    errors = {}
    if not status:
        errors["status"] = "Status absensi wajib diisi."
    elif status not in ABSENSI_STATUS_VALUES:
        errors["status"] = "Status absensi tidak dikenali."

    if not keterangan:
        errors["keterangan"] = "Keterangan wajib diisi saat absensi diubah."

    if errors:
        return None, errors

    return {
        "status": status,
        "keterangan": keterangan,
    }, None
