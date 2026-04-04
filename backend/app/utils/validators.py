from datetime import datetime


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


def validate_student_lookup_params(args):
    nisn = (args.get("nisn") or "").strip()
    id_card = (args.get("id_card") or args.get("student_identifier") or "").strip()

    if not nisn and not id_card:
        return None, {
            "nisn": "Isi nisn atau id_card untuk mencari siswa.",
            "id_card": "Isi nisn atau id_card untuk mencari siswa.",
        }

    return {"nisn": nisn or None, "id_card": id_card or None}, None


def validate_register_payload(payload):
    payload = payload or {}
    mode = (payload.get("mode") or "manual").strip()
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    role = (payload.get("role") or "siswa").strip()
    email = (payload.get("email") or "").strip() or None
    no_telp = (payload.get("no_telp") or "").strip() or None

    errors = {}
    if mode not in {"manual", "from_school_db"}:
        errors["mode"] = "Mode registrasi harus 'manual' atau 'from_school_db'."
    if not username:
        errors["username"] = "Username wajib diisi."
    if not password or len(password) < 6:
        errors["password"] = "Password minimal 6 karakter."

    result = {
        "mode": mode,
        "username": username,
        "password": password,
        "email": email,
        "no_telp": no_telp,
    }

    if mode == "manual":
        full_name = (payload.get("full_name") or "").strip()
        if not full_name:
            errors["full_name"] = "Nama lengkap wajib diisi."
        if role not in {"admin", "kepsek", "wali_kelas", "guru_piket", "siswa", "orangtua"}:
            errors["role"] = "Role tidak valid."
        result["role"] = role
        result["full_name"] = full_name

        student = payload.get("student") or {}
        if role == "siswa":
            nisn = (student.get("nisn") or "").strip()
            if not nisn:
                errors["student.nisn"] = "NISN wajib diisi untuk akun siswa."
            result["student"] = {
                "nisn": nisn,
                "nama": (student.get("nama") or full_name).strip(),
                "jenis_kelamin": (student.get("jenis_kelamin") or "").strip() or None,
                "alamat": student.get("alamat"),
                "no_telp_ortu": (student.get("no_telp_ortu") or "").strip() or None,
                "id_card": (student.get("id_card") or "").strip() or None,
                "id_kelas": student.get("id_kelas"),
            }
    else:
        nisn = (payload.get("nisn") or payload.get("student", {}).get("nisn") or "").strip()
        id_card = (
            payload.get("id_card")
            or payload.get("student_identifier")
            or payload.get("student", {}).get("id_card")
            or ""
        ).strip()
        if not nisn and not id_card:
            errors["identifier"] = "Isi nisn atau id_card untuk mengambil data dari database sekolah."
        result["nisn"] = nisn or None
        result["id_card"] = id_card or None
        result["role"] = "siswa"

    if errors:
        return None, errors

    return result, None


def _parse_datetime_value(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_rfid_absensi_payload(payload):
    payload = payload or {}
    uid_card = (payload.get("uid_card") or payload.get("id_card") or "").strip()
    device_id = (payload.get("device_id") or "").strip()
    timestamp_value = (payload.get("timestamp") or "").strip()

    errors = {}
    if not uid_card:
        errors["uid_card"] = "UID kartu wajib diisi."
    if not device_id:
        errors["device_id"] = "Device ID wajib diisi."

    parsed_timestamp = None
    if timestamp_value:
        parsed_timestamp = _parse_datetime_value(timestamp_value)
        if parsed_timestamp is None:
            errors["timestamp"] = "Format timestamp tidak valid."

    if errors:
        return None, errors

    return {
        "uid_card": uid_card,
        "device_id": device_id,
        "timestamp": parsed_timestamp,
    }, None


def validate_absensi_query_params(args):
    filters = {
        "siswa_id": (args.get("siswa_id") or "").strip() or None,
        "kelas_id": (args.get("kelas_id") or "").strip() or None,
        "status": (args.get("status") or "").strip() or None,
        "waktu_sholat": (args.get("waktu_sholat") or "").strip() or None,
        "start_date": (args.get("start_date") or "").strip() or None,
        "end_date": (args.get("end_date") or "").strip() or None,
        "sort": (args.get("sort") or "desc").strip().lower(),
    }

    errors = {}
    try:
        page = int(args.get("page", 1))
        limit = int(args.get("limit", 50))
    except ValueError:
        return None, {"pagination": "page dan limit harus berupa angka."}

    if page < 1:
        errors["page"] = "page minimal 1."
    if limit < 1 or limit > 100:
        errors["limit"] = "limit harus antara 1 sampai 100."
    if filters["sort"] not in {"asc", "desc"}:
        errors["sort"] = "sort harus asc atau desc."

    for key in ("siswa_id", "kelas_id"):
        if filters[key] is not None:
            try:
                filters[key] = int(filters[key])
            except ValueError:
                errors[key] = f"{key} harus berupa angka."

    for key in ("start_date", "end_date"):
        value = filters[key]
        if value:
            try:
                filters[key] = datetime.fromisoformat(value).date()
            except ValueError:
                errors[key] = f"{key} harus berformat YYYY-MM-DD."

    if errors:
        return None, errors

    filters["page"] = page
    filters["limit"] = limit
    return filters, None
