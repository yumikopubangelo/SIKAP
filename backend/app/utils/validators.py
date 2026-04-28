from datetime import date, datetime, time

from ..models.absensi import ABSENSI_STATUS_VALUES
from ..models.kelas import TINGKAT_VALUES
from ..models.siswa import JENIS_KELAMIN_VALUES
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


def _parse_int(value) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if not text.isdigit():
        return None
    return int(text)


def _validate_page_limit(params, *, default_limit: str = "20") -> tuple[int | None, int | None, dict]:
    page_raw = (params.get("page") or "1").strip()
    limit_raw = (params.get("limit") or default_limit).strip()
    errors = {}

    if not page_raw.isdigit() or int(page_raw) < 1:
        errors["page"] = "Page harus berupa angka >= 1."

    if not limit_raw.isdigit() or int(limit_raw) < 1:
        errors["limit"] = "Limit harus berupa angka >= 1."

    if errors:
        return None, None, errors

    return int(page_raw), min(int(limit_raw), 100), {}


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


def validate_rfid_absensi_payload(payload):
    payload = payload or {}
    uid_card = (payload.get("uid_card") or payload.get("id_card") or "").strip()
    device_id = (payload.get("device_id") or "").strip()
    timestamp_raw = (payload.get("timestamp") or "").strip()

    errors = {}
    if not uid_card:
        errors["uid_card"] = "UID kartu wajib diisi."

    if not device_id:
        errors["device_id"] = "Device ID wajib diisi."

    parsed_timestamp = None
    if timestamp_raw:
        parsed_timestamp = _parse_datetime(timestamp_raw)
        if parsed_timestamp is None:
            errors["timestamp"] = "Timestamp harus berformat ISO 8601."

    if errors:
        return None, errors

    return {
        "uid_card": uid_card,
        "device_id": device_id,
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


def validate_absensi_list_params(params):
    params = params or {}
    siswa_id_raw = (params.get("siswa_id") or "").strip()
    kelas_id_raw = (params.get("kelas_id") or "").strip()
    start_date_raw = (params.get("start_date") or "").strip()
    end_date_raw = (params.get("end_date") or "").strip()
    waktu_sholat = (params.get("waktu_sholat") or "").strip().lower() or None
    status = (params.get("status") or "").strip().lower() or None
    page_raw = (params.get("page") or "1").strip()
    limit_raw = (params.get("limit") or "50").strip()
    sort = (params.get("sort") or "desc").strip().lower()

    errors = {}

    siswa_id = None
    if siswa_id_raw:
        if not siswa_id_raw.isdigit():
            errors["siswa_id"] = "Siswa ID harus berupa angka."
        else:
            siswa_id = int(siswa_id_raw)

    kelas_id = None
    if kelas_id_raw:
        if not kelas_id_raw.isdigit():
            errors["kelas_id"] = "Kelas ID harus berupa angka."
        else:
            kelas_id = int(kelas_id_raw)

    start_date = None
    if start_date_raw:
        start_date = _parse_date(start_date_raw)
        if start_date is None:
            errors["start_date"] = "Start date harus berformat YYYY-MM-DD."

    end_date = None
    if end_date_raw:
        end_date = _parse_date(end_date_raw)
        if end_date is None:
            errors["end_date"] = "End date harus berformat YYYY-MM-DD."

    if start_date and end_date and start_date > end_date:
        errors["date_range"] = "Start date tidak boleh lebih besar dari end date."

    if status and status not in ABSENSI_STATUS_VALUES:
        errors["status"] = "Status absensi tidak dikenali."

    if sort not in ("asc", "desc"):
        errors["sort"] = "Sort harus bernilai asc atau desc."

    if not page_raw.isdigit() or int(page_raw) < 1:
        errors["page"] = "Page harus berupa angka >= 1."

    if not limit_raw.isdigit() or int(limit_raw) < 1:
        errors["limit"] = "Limit harus berupa angka >= 1."

    if errors:
        return None, errors

    return {
        "siswa_id": siswa_id,
        "kelas_id": kelas_id,
        "start_date": start_date,
        "end_date": end_date,
        "waktu_sholat": waktu_sholat,
        "status": status,
        "page": int(page_raw),
        "limit": min(int(limit_raw), 100),
        "sort": sort,
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


HARI_PIKET_VALUES = (
    "senin",
    "selasa",
    "rabu",
    "kamis",
    "jumat",
    "sabtu",
    "minggu",
)

SP_JENIS_VALUES = ("SP1", "SP2", "SP3")


def validate_kelas_list_params(params):
    params = params or {}
    search = (params.get("search") or "").strip()
    tingkat = (params.get("tingkat") or "").strip().upper() or None
    tahun_ajaran = (params.get("tahun_ajaran") or "").strip() or None
    page, limit, errors = _validate_page_limit(params)

    if tingkat and tingkat not in TINGKAT_VALUES:
        errors["tingkat"] = "Tingkat kelas tidak valid."

    if errors:
        return None, errors

    return {
        "search": search or None,
        "tingkat": tingkat,
        "tahun_ajaran": tahun_ajaran,
        "page": page,
        "limit": limit,
    }, None


def validate_kelas_payload(payload, *, partial: bool = False):
    payload = payload or {}
    updates = {}
    errors = {}

    if not partial or "nama_kelas" in payload:
        nama_kelas = (payload.get("nama_kelas") or "").strip()
        if not nama_kelas:
            errors["nama_kelas"] = "Nama kelas wajib diisi."
        else:
            updates["nama_kelas"] = nama_kelas

    if not partial or "tingkat" in payload:
        tingkat = (payload.get("tingkat") or "").strip().upper()
        if not tingkat:
            errors["tingkat"] = "Tingkat wajib diisi."
        elif tingkat not in TINGKAT_VALUES:
            errors["tingkat"] = "Tingkat kelas tidak valid."
        else:
            updates["tingkat"] = tingkat

    if "jurusan" in payload or not partial:
        updates["jurusan"] = (payload.get("jurusan") or "").strip() or None

    if not partial or "tahun_ajaran" in payload:
        tahun_ajaran = (payload.get("tahun_ajaran") or "").strip()
        if not tahun_ajaran:
            errors["tahun_ajaran"] = "Tahun ajaran wajib diisi."
        else:
            updates["tahun_ajaran"] = tahun_ajaran

    if "id_wali" in payload or not partial:
        raw_id_wali = payload.get("id_wali")
        if raw_id_wali in ("", None):
            updates["id_wali"] = None
        else:
            id_wali = _parse_int(raw_id_wali)
            if id_wali is None:
                errors["id_wali"] = "ID wali kelas harus berupa angka."
            else:
                updates["id_wali"] = id_wali

    if partial and not updates:
        errors["payload"] = "Minimal satu field perubahan wajib diisi."

    if errors:
        return None, errors

    return updates, None


def validate_siswa_list_params(params):
    params = params or {}
    search = (params.get("search") or "").strip()
    kelas_id = _parse_int(params.get("kelas_id"))
    parent_user_id = _parse_int(params.get("parent_user_id"))
    page, limit, errors = _validate_page_limit(params)

    if params.get("kelas_id") not in (None, "") and kelas_id is None:
        errors["kelas_id"] = "Kelas ID harus berupa angka."

    if params.get("parent_user_id") not in (None, "") and parent_user_id is None:
        errors["parent_user_id"] = "Parent user ID harus berupa angka."

    if errors:
        return None, errors

    return {
        "search": search or None,
        "kelas_id": kelas_id,
        "parent_user_id": parent_user_id,
        "page": page,
        "limit": limit,
    }, None


def validate_siswa_payload(payload, *, partial: bool = False):
    payload = payload or {}
    updates = {}
    errors = {}

    if not partial or "nisn" in payload:
        nisn = (payload.get("nisn") or "").strip()
        if not nisn:
            errors["nisn"] = "NISN wajib diisi."
        elif not nisn.isdigit():
            errors["nisn"] = "NISN harus berupa angka."
        else:
            updates["nisn"] = nisn

    if not partial or "nama" in payload:
        nama = (payload.get("nama") or "").strip()
        if not nama:
            errors["nama"] = "Nama siswa wajib diisi."
        else:
            updates["nama"] = nama

    if "jenis_kelamin" in payload or not partial:
        jenis_kelamin = (payload.get("jenis_kelamin") or "").strip().upper() or None
        if jenis_kelamin and jenis_kelamin not in JENIS_KELAMIN_VALUES:
            errors["jenis_kelamin"] = "Jenis kelamin harus L atau P."
        else:
            updates["jenis_kelamin"] = jenis_kelamin

    if "alamat" in payload or not partial:
        updates["alamat"] = (payload.get("alamat") or "").strip() or None

    if "no_telp_ortu" in payload or not partial:
        updates["no_telp_ortu"] = (payload.get("no_telp_ortu") or "").strip() or None

    if "id_card" in payload or not partial:
        updates["id_card"] = (payload.get("id_card") or "").strip() or None

    if not partial or "id_kelas" in payload:
        raw_id_kelas = payload.get("id_kelas")
        if raw_id_kelas in ("", None):
            errors["id_kelas"] = "Kelas wajib dipilih."
        else:
            id_kelas = _parse_int(raw_id_kelas)
            if id_kelas is None:
                errors["id_kelas"] = "ID kelas harus berupa angka."
            else:
                updates["id_kelas"] = id_kelas

    if "id_user" in payload or not partial:
        raw_id_user = payload.get("id_user")
        if raw_id_user in ("", None):
            updates["id_user"] = None
        else:
            id_user = _parse_int(raw_id_user)
            if id_user is None:
                errors["id_user"] = "ID user siswa harus berupa angka."
            else:
                updates["id_user"] = id_user

    if "parent_user_id" in payload or not partial:
        raw_parent_user_id = payload.get("parent_user_id")
        if raw_parent_user_id in ("", None):
            updates["parent_user_id"] = None
        else:
            parent_user_id = _parse_int(raw_parent_user_id)
            if parent_user_id is None:
                errors["parent_user_id"] = "ID user orang tua harus berupa angka."
            else:
                updates["parent_user_id"] = parent_user_id

    if partial and not updates:
        errors["payload"] = "Minimal satu field perubahan wajib diisi."

    if errors:
        return None, errors

    return updates, None


def validate_surat_peringatan_list_params(params):
    params = params or {}
    siswa_id = _parse_int(params.get("siswa_id"))
    kelas_id = _parse_int(params.get("kelas_id"))
    jenis = (params.get("jenis") or "").strip().upper() or None
    page, limit, errors = _validate_page_limit(params)

    if params.get("siswa_id") not in (None, "") and siswa_id is None:
        errors["siswa_id"] = "Siswa ID harus berupa angka."

    if params.get("kelas_id") not in (None, "") and kelas_id is None:
        errors["kelas_id"] = "Kelas ID harus berupa angka."

    if jenis and jenis not in SP_JENIS_VALUES:
        errors["jenis"] = "Jenis surat peringatan tidak valid."

    if errors:
        return None, errors

    return {
        "siswa_id": siswa_id,
        "kelas_id": kelas_id,
        "jenis": jenis,
        "page": page,
        "limit": limit,
    }, None


def validate_jadwal_piket_list_params(params):
    params = params or {}
    hari = (params.get("hari") or "").strip().lower() or None
    user_id = _parse_int(params.get("user_id"))
    page, limit, errors = _validate_page_limit(params)

    if hari and hari not in HARI_PIKET_VALUES:
        errors["hari"] = "Hari piket tidak valid."

    if params.get("user_id") not in (None, "") and user_id is None:
        errors["user_id"] = "User ID harus berupa angka."

    if errors:
        return None, errors

    return {
        "hari": hari,
        "user_id": user_id,
        "page": page,
        "limit": limit,
    }, None


def validate_jadwal_piket_payload(payload, *, partial: bool = False):
    payload = payload or {}
    updates = {}
    errors = {}

    if not partial or "user_id" in payload:
        user_id = _parse_int(payload.get("user_id"))
        if user_id is None:
            errors["user_id"] = "User guru piket wajib dipilih."
        else:
            updates["user_id"] = user_id

    if not partial or "hari" in payload:
        hari = (payload.get("hari") or "").strip().lower()
        if not hari:
            errors["hari"] = "Hari wajib diisi."
        elif hari not in HARI_PIKET_VALUES:
            errors["hari"] = "Hari piket tidak valid."
        else:
            updates["hari"] = hari

    if not partial or "jam_mulai" in payload:
        jam_mulai_raw = (payload.get("jam_mulai") or "").strip()
        jam_mulai = _parse_time(jam_mulai_raw) if jam_mulai_raw else None
        if jam_mulai is None:
            errors["jam_mulai"] = "Jam mulai wajib berformat HH:MM atau HH:MM:SS."
        else:
            updates["jam_mulai"] = jam_mulai

    if not partial or "jam_selesai" in payload:
        jam_selesai_raw = (payload.get("jam_selesai") or "").strip()
        jam_selesai = _parse_time(jam_selesai_raw) if jam_selesai_raw else None
        if jam_selesai is None:
            errors["jam_selesai"] = "Jam selesai wajib berformat HH:MM atau HH:MM:SS."
        else:
            updates["jam_selesai"] = jam_selesai

    if (
        "jam_mulai" in updates
        and "jam_selesai" in updates
        and updates["jam_mulai"] >= updates["jam_selesai"]
    ):
        errors["jam_range"] = "Jam mulai harus lebih kecil dari jam selesai."

    if partial and not updates:
        errors["payload"] = "Minimal satu field perubahan wajib diisi."

    if errors:
        return None, errors

    return updates, None
