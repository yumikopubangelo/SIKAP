import csv
import io
from dataclasses import dataclass

from ..extensions import db
from ..models import Kelas, OrangTua, Siswa, User


class SchoolImportServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


CSV_REQUIRED_HEADERS = {
    "nama_kelas",
    "tingkat",
    "jurusan",
    "tahun_ajaran",
    "nisn",
    "nama",
}


@dataclass(slots=True)
class ImportCounters:
    processed_rows: int = 0
    created_classes: int = 0
    updated_classes: int = 0
    created_students: int = 0
    updated_students: int = 0
    created_parent_users: int = 0
    linked_parent_relations: int = 0


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {str(key).strip().lower(): (value or "").strip() for key, value in row.items()}


def _generate_parent_username(row: dict[str, str]) -> str:
    if row.get("parent_username"):
        return row["parent_username"]
    return f"ortu_{row['nisn']}"


def _get_or_create_class(row: dict[str, str], counters: ImportCounters) -> Kelas:
    kelas = Kelas.query.filter_by(
        nama_kelas=row["nama_kelas"],
        tahun_ajaran=row["tahun_ajaran"],
    ).first()
    if kelas is None:
        kelas = Kelas(
            nama_kelas=row["nama_kelas"],
            tingkat=row["tingkat"].upper(),
            jurusan=row.get("jurusan") or None,
            tahun_ajaran=row["tahun_ajaran"],
        )
        db.session.add(kelas)
        db.session.flush()
        counters.created_classes += 1
        return kelas

    changed = False
    next_tingkat = row["tingkat"].upper()
    next_jurusan = row.get("jurusan") or None
    if kelas.tingkat != next_tingkat:
        kelas.tingkat = next_tingkat
        changed = True
    if kelas.jurusan != next_jurusan:
        kelas.jurusan = next_jurusan
        changed = True
    if changed:
        counters.updated_classes += 1
    return kelas


def _get_or_create_parent_user(row: dict[str, str], counters: ImportCounters) -> User | None:
    parent_email = row.get("parent_email") or None
    parent_phone = row.get("parent_phone") or None
    parent_name = row.get("parent_full_name") or None
    parent_username = _generate_parent_username(row)

    if not any([parent_email, parent_phone, parent_name, row.get("parent_username")]):
        return None

    user = None
    if row.get("parent_username"):
        user = User.query.filter_by(username=parent_username).first()
    if user is None and parent_email:
        user = User.query.filter_by(email=parent_email).first()

    if user is None:
        user = User(
            username=parent_username,
            full_name=parent_name or f"Orang Tua {row['nama']}",
            email=parent_email,
            no_telp=parent_phone,
            role="orangtua",
        )
        user.set_password("orangtua123")
        db.session.add(user)
        db.session.flush()
        counters.created_parent_users += 1
        return user

    if user.role != "orangtua":
        raise SchoolImportServiceError(
            f"User parent {user.username} ada tetapi role-nya bukan orangtua.",
            400,
        )

    if parent_name and user.full_name != parent_name:
        user.full_name = parent_name
    if parent_email and user.email != parent_email:
        user.email = parent_email
    if parent_phone and user.no_telp != parent_phone:
        user.no_telp = parent_phone
    return user


def _upsert_student(row: dict[str, str], kelas: Kelas, parent_user: User | None, counters: ImportCounters):
    siswa = Siswa.query.filter_by(nisn=row["nisn"]).first()
    creating = siswa is None

    if siswa is None:
        siswa = Siswa(
            nisn=row["nisn"],
            nama=row["nama"],
            jenis_kelamin=(row.get("jenis_kelamin") or "").upper() or None,
            alamat=row.get("alamat") or None,
            no_telp_ortu=row.get("parent_phone") or row.get("no_telp_ortu") or None,
            id_card=row.get("id_card") or None,
            id_kelas=kelas.id_kelas,
        )
        db.session.add(siswa)
        db.session.flush()
        counters.created_students += 1
    else:
        siswa.nama = row["nama"]
        siswa.jenis_kelamin = (row.get("jenis_kelamin") or "").upper() or None
        siswa.alamat = row.get("alamat") or None
        siswa.no_telp_ortu = row.get("parent_phone") or row.get("no_telp_ortu") or None
        siswa.id_kelas = kelas.id_kelas
        if row.get("id_card"):
            existing_card_owner = Siswa.query.filter(
                Siswa.id_card == row["id_card"],
                Siswa.id_siswa != siswa.id_siswa,
            ).first()
            if existing_card_owner is not None:
                raise SchoolImportServiceError(
                    f"UID kartu {row['id_card']} sudah dipakai siswa lain.",
                    409,
                )
            siswa.id_card = row["id_card"]
        counters.updated_students += 1

    if parent_user is not None:
        relation = OrangTua.query.filter_by(id_siswa=siswa.id_siswa).first()
        existing_parent_for_user = OrangTua.query.filter(
            OrangTua.id_user == parent_user.id_user,
            OrangTua.id_siswa != siswa.id_siswa,
        ).first()
        if existing_parent_for_user is not None:
            raise SchoolImportServiceError(
                f"User orang tua {parent_user.username} sudah terhubung ke siswa lain.",
                409,
            )
        if relation is None:
            relation = OrangTua(id_user=parent_user.id_user, id_siswa=siswa.id_siswa)
            db.session.add(relation)
            counters.linked_parent_relations += 1
        elif relation.id_user != parent_user.id_user:
            relation.id_user = parent_user.id_user
            counters.linked_parent_relations += 1

    return siswa, creating


def import_school_csv(file_storage) -> dict:
    if file_storage is None:
        raise SchoolImportServiceError("File CSV wajib diunggah.", 400)

    raw_bytes = file_storage.read()
    if not raw_bytes:
        raise SchoolImportServiceError("File CSV kosong.", 400)

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SchoolImportServiceError("File CSV harus memakai encoding UTF-8.", 400) from exc

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise SchoolImportServiceError("Header CSV tidak ditemukan.", 400)

    normalized_headers = {str(header).strip().lower() for header in reader.fieldnames}
    missing_headers = sorted(CSV_REQUIRED_HEADERS - normalized_headers)
    if missing_headers:
        raise SchoolImportServiceError(
            f"Header CSV kurang: {', '.join(missing_headers)}",
            400,
        )

    counters = ImportCounters()
    errors: list[dict] = []

    for row_number, raw_row in enumerate(reader, start=2):
        row = _normalize_row(raw_row)
        if not any(row.values()):
            continue

        try:
            kelas = _get_or_create_class(row, counters)
            parent_user = _get_or_create_parent_user(row, counters)
            _upsert_student(row, kelas, parent_user, counters)
            db.session.commit()
            counters.processed_rows += 1
        except SchoolImportServiceError as exc:
            db.session.rollback()
            errors.append({"row": row_number, "message": exc.message})
        except Exception as exc:
            db.session.rollback()
            errors.append({"row": row_number, "message": f"Gagal memproses baris: {exc}"})

    return {
        "processed_rows": counters.processed_rows,
        "created_classes": counters.created_classes,
        "updated_classes": counters.updated_classes,
        "created_students": counters.created_students,
        "updated_students": counters.updated_students,
        "created_parent_users": counters.created_parent_users,
        "linked_parent_relations": counters.linked_parent_relations,
        "errors": errors,
    }
