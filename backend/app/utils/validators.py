from datetime import date, datetime, time

from ..models.absensi import ABSENSI_STATUS_VALUES
from ..models.user import ROLE_VALUES


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


def _parse_time(value: str) -> time | None:
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
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


ROLE_ALIASES = {
    "wali": "wali_kelas",
    "piket": "guru_piket",
    "ortu": "orangtua",
}


def _normalize_role(role: str) -> str:
    cleaned = (role or "").strip().lower()
    return ROLE_ALIASES.get(cleaned, cleaned)


def validate_student_lookup_params(params):
    params = params or {}
    nisn = (params.get("nisn") or "").strip()
    id_card = (params.get("id_card") or "").strip()

    errors = {}
    if not nisn and not id_card:
        errors["query"] = "Minimal isi salah satu: nisn atau id_card."

    if errors:
        return None, errors

    return {
        "nisn": nisn or None,
        "id_card": id_card or None,
    }, None


def validate_register_payload(payload):
    payload = payload or {}

    mode = (payload.get("mode") or "manual").strip().lower()
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip() or None
    no_telp = (payload.get("no_telp") or "").strip() or None
    role = _normalize_role(payload.get("role") or "siswa")
    nisn = (payload.get("nisn") or "").strip() or None
    id_card = (payload.get("id_card") or "").strip() or None

    errors = {}
    if mode not in ("manual", "school_db"):
        errors["mode"] = "Mode registrasi tidak valid."

    if not username:
        errors["username"] = "Username wajib diisi."

    if not password:
        errors["password"] = "Password wajib diisi."
    elif len(password) < 8:
        errors["password"] = "Password minimal 8 karakter."

    if role not in ROLE_VALUES:
        errors["role"] = "Role tidak valid."

    if mode == "manual" and not full_name:
        errors["full_name"] = "Nama lengkap wajib diisi untuk mode manual."

    if mode == "school_db" and not nisn and not id_card:
        errors["student_lookup"] = "Mode school_db wajib menyertakan nisn atau id_card."

    if role == "siswa" and not nisn and not id_card:
        errors["student_lookup"] = "Role siswa wajib menyertakan nisn atau id_card."

    if errors:
        return None, errors

    return {
        "mode": mode,
        "username": username,
        "password": password,
        "full_name": full_name if full_name else username,
        "email": email,
        "no_telp": no_telp,
        "role": role,
        "nisn": nisn,
        "id_card": id_card,
    }, None


def validate_user_list_params(params):
    params = params or {}
    role_raw = (params.get("role") or "").strip()
    search = (params.get("search") or "").strip()
    page_raw = (params.get("page") or "1").strip()
    limit_raw = (params.get("limit") or "20").strip()

    errors = {}
    role = None
    if role_raw:
      role = _normalize_role(role_raw)
      if role not in ROLE_VALUES:
          errors["role"] = "Role tidak valid."

    if not page_raw.isdigit() or int(page_raw) < 1:
        errors["page"] = "Page harus berupa angka >= 1."

    if not limit_raw.isdigit() or int(limit_raw) < 1:
        errors["limit"] = "Limit harus berupa angka >= 1."

    if errors:
        return None, errors

    return {
        "role": role,
        "search": search or None,
        "page": int(page_raw),
        "limit": min(int(limit_raw), 100),
    }, None


def validate_user_create_payload(payload):
    payload = payload or {}

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip() or None
    no_telp = (payload.get("no_telp") or "").strip() or None
    role = _normalize_role(payload.get("role") or "")
    nisn = (payload.get("nisn") or "").strip() or None
    id_card = (payload.get("id_card") or "").strip() or None

    errors = {}
    if not username:
        errors["username"] = "Username wajib diisi."

    if not full_name:
        errors["full_name"] = "Nama lengkap wajib diisi."

    if not password:
        errors["password"] = "Password wajib diisi."
    elif len(password) < 8:
        errors["password"] = "Password minimal 8 karakter."

    if role not in ROLE_VALUES:
        errors["role"] = "Role tidak valid."

    if role == "siswa" and not nisn and not id_card:
        errors["student_lookup"] = "Role siswa wajib menyertakan nisn atau id_card."

    if errors:
        return None, errors

    return {
        "username": username,
        "password": password,
        "full_name": full_name,
        "email": email,
        "no_telp": no_telp,
        "role": role,
        "nisn": nisn,
        "id_card": id_card,
    }, None


def validate_user_update_payload(payload):
    payload = payload or {}

    updates = {}
    errors = {}

    if "username" in payload:
        username = (payload.get("username") or "").strip()
        if not username:
            errors["username"] = "Username wajib diisi."
        else:
            updates["username"] = username

    if "full_name" in payload:
        full_name = (payload.get("full_name") or "").strip()
        if not full_name:
            errors["full_name"] = "Nama lengkap wajib diisi."
        else:
            updates["full_name"] = full_name

    if "email" in payload:
        updates["email"] = (payload.get("email") or "").strip() or None

    if "no_telp" in payload:
        updates["no_telp"] = (payload.get("no_telp") or "").strip() or None

    if "role" in payload:
        role = _normalize_role(payload.get("role") or "")
        if role not in ROLE_VALUES:
            errors["role"] = "Role tidak valid."
        else:
            updates["role"] = role

    if "password" in payload:
        password = payload.get("password") or ""
        if password and len(password) < 8:
            errors["password"] = "Password minimal 8 karakter."
        elif password:
            updates["password"] = password

    if "nisn" in payload:
        updates["nisn"] = (payload.get("nisn") or "").strip() or None

    if "id_card" in payload:
        updates["id_card"] = (payload.get("id_card") or "").strip() or None

    if not updates:
        errors["payload"] = "Minimal satu field perubahan wajib diisi."

    if errors:
        return None, errors

    return updates, None


def validate_waktu_sholat_update_payload(payload):
    payload = payload or {}

    waktu_adzan_raw = (payload.get("waktu_adzan") or "").strip()
    waktu_iqamah_raw = (payload.get("waktu_iqamah") or "").strip()
    waktu_selesai_raw = (payload.get("waktu_selesai") or "").strip()

    errors = {}
    if not waktu_adzan_raw:
        errors["waktu_adzan"] = "Waktu adzan wajib diisi."
    if not waktu_iqamah_raw:
        errors["waktu_iqamah"] = "Waktu iqamah wajib diisi."
    if not waktu_selesai_raw:
        errors["waktu_selesai"] = "Waktu selesai wajib diisi."

    waktu_adzan = _parse_time(waktu_adzan_raw) if waktu_adzan_raw else None
    waktu_iqamah = _parse_time(waktu_iqamah_raw) if waktu_iqamah_raw else None
    waktu_selesai = _parse_time(waktu_selesai_raw) if waktu_selesai_raw else None

    if waktu_adzan_raw and waktu_adzan is None:
        errors["waktu_adzan"] = "Format waktu adzan harus HH:MM atau HH:MM:SS."
    if waktu_iqamah_raw and waktu_iqamah is None:
        errors["waktu_iqamah"] = "Format waktu iqamah harus HH:MM atau HH:MM:SS."
    if waktu_selesai_raw and waktu_selesai is None:
        errors["waktu_selesai"] = "Format waktu selesai harus HH:MM atau HH:MM:SS."

    if errors:
        return None, errors

    return {
        "waktu_adzan": waktu_adzan,
        "waktu_iqamah": waktu_iqamah,
        "waktu_selesai": waktu_selesai,
    }, None
