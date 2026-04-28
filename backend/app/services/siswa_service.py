from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Kelas, OrangTua, Siswa, User


class SiswaServiceError(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def _siswa_query():
    return Siswa.query.options(
        joinedload(Siswa.kelas),
        joinedload(Siswa.user),
        joinedload(Siswa.orangtua).joinedload(OrangTua.user),
    )


def _serialize_siswa(siswa: Siswa) -> dict:
    parent_user = siswa.orangtua.user if getattr(siswa, "orangtua", None) and siswa.orangtua.user else None
    return {
        "id_siswa": siswa.id_siswa,
        "nisn": siswa.nisn,
        "nama": siswa.nama,
        "jenis_kelamin": siswa.jenis_kelamin,
        "alamat": siswa.alamat,
        "no_telp_ortu": siswa.no_telp_ortu,
        "id_card": siswa.id_card,
        "created_at": siswa.created_at.isoformat() if siswa.created_at else None,
        "kelas": (
            {
                "id_kelas": siswa.kelas.id_kelas,
                "nama_kelas": siswa.kelas.nama_kelas,
                "tingkat": siswa.kelas.tingkat,
                "jurusan": siswa.kelas.jurusan,
                "tahun_ajaran": siswa.kelas.tahun_ajaran,
            }
            if siswa.kelas
            else None
        ),
        "user": (
            {
                "id_user": siswa.user.id_user,
                "username": siswa.user.username,
                "full_name": siswa.user.full_name,
            }
            if siswa.user
            else None
        ),
        "orangtua": (
            {
                "id_ortu": siswa.orangtua.id_ortu,
                "id_user": parent_user.id_user if parent_user else None,
                "username": parent_user.username if parent_user else None,
                "full_name": parent_user.full_name if parent_user else None,
                "email": parent_user.email if parent_user else None,
                "no_telp": parent_user.no_telp if parent_user else None,
            }
            if getattr(siswa, "orangtua", None)
            else None
        ),
    }


def _get_siswa_or_raise(siswa_id: int) -> Siswa:
    siswa = _siswa_query().filter_by(id_siswa=siswa_id).first()
    if siswa is None:
        raise SiswaServiceError("Data siswa tidak ditemukan.", 404)
    return siswa


def _ensure_unique_nisn_or_raise(nisn: str, exclude_id: int | None = None):
    query = Siswa.query.filter_by(nisn=nisn)
    if exclude_id is not None:
        query = query.filter(Siswa.id_siswa != exclude_id)
    if query.first() is not None:
        raise SiswaServiceError("NISN sudah digunakan.", 409)


def _ensure_unique_card_or_raise(id_card: str | None, exclude_id: int | None = None):
    if not id_card:
        return
    query = Siswa.query.filter_by(id_card=id_card)
    if exclude_id is not None:
        query = query.filter(Siswa.id_siswa != exclude_id)
    if query.first() is not None:
        raise SiswaServiceError("UID kartu RFID sudah digunakan siswa lain.", 409)


def _ensure_kelas_exists_or_raise(kelas_id: int) -> Kelas:
    kelas = Kelas.query.filter_by(id_kelas=kelas_id).first()
    if kelas is None:
        raise SiswaServiceError("Kelas tidak ditemukan.", 404)
    return kelas


def _ensure_student_user_or_raise(user_id: int | None, current_student_id: int | None = None) -> User | None:
    if user_id is None:
        return None
    user = User.query.filter_by(id_user=user_id).first()
    if user is None:
        raise SiswaServiceError("User siswa tidak ditemukan.", 404)
    if user.role != "siswa":
        raise SiswaServiceError("User yang dipilih bukan akun siswa.", 400)

    existing_owner = Siswa.query.filter(Siswa.id_user == user_id)
    if current_student_id is not None:
        existing_owner = existing_owner.filter(Siswa.id_siswa != current_student_id)
    if existing_owner.first() is not None:
        raise SiswaServiceError("User siswa tersebut sudah terhubung ke siswa lain.", 409)
    return user


def _ensure_parent_user_or_raise(parent_user_id: int | None, current_student_id: int | None = None) -> User | None:
    if parent_user_id is None:
        return None
    user = User.query.filter_by(id_user=parent_user_id).first()
    if user is None:
        raise SiswaServiceError("User orang tua tidak ditemukan.", 404)
    if user.role != "orangtua":
        raise SiswaServiceError("User yang dipilih bukan akun orang tua.", 400)

    query = OrangTua.query.filter_by(id_user=parent_user_id)
    if current_student_id is not None:
        query = query.filter(OrangTua.id_siswa != current_student_id)
    if query.first() is not None:
        raise SiswaServiceError("User orang tua tersebut sudah terhubung ke siswa lain.", 409)
    return user


def _upsert_parent_relation(siswa: Siswa, parent_user_id: int | None):
    relation = getattr(siswa, "orangtua", None)
    if parent_user_id is None:
        if relation is not None:
            db.session.delete(relation)
            db.session.flush()
        return

    if relation is None:
        relation = OrangTua(id_user=parent_user_id, id_siswa=siswa.id_siswa)
        db.session.add(relation)
    else:
        relation.id_user = parent_user_id
    db.session.flush()


def list_siswa(params: dict) -> tuple[list[dict], dict]:
    query = _siswa_query()

    if params.get("kelas_id") is not None:
        query = query.filter(Siswa.id_kelas == params["kelas_id"])

    if params.get("parent_user_id") is not None:
        query = query.join(Siswa.orangtua).filter(OrangTua.id_user == params["parent_user_id"])

    if params.get("search"):
        search_pattern = f"%{params['search']}%"
        query = query.outerjoin(Siswa.kelas).outerjoin(Siswa.user).filter(
            or_(
                Siswa.nisn.ilike(search_pattern),
                Siswa.nama.ilike(search_pattern),
                Siswa.id_card.ilike(search_pattern),
                Kelas.nama_kelas.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            )
        )

    total_items = query.with_entities(func.count(Siswa.id_siswa.distinct())).scalar() or 0
    page = params["page"]
    limit = params["limit"]
    total_pages = max(1, (total_items + limit - 1) // limit)

    rows = (
        query.order_by(Siswa.nama.asc(), Siswa.nisn.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return (
        [_serialize_siswa(siswa) for siswa in rows],
        {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    )


def get_siswa_detail(siswa_id: int) -> dict:
    siswa = _get_siswa_or_raise(siswa_id)
    return _serialize_siswa(siswa)


def create_siswa(payload: dict) -> dict:
    _ensure_unique_nisn_or_raise(payload["nisn"])
    _ensure_unique_card_or_raise(payload.get("id_card"))
    _ensure_kelas_exists_or_raise(payload["id_kelas"])
    student_user = _ensure_student_user_or_raise(payload.get("id_user"))
    parent_user = _ensure_parent_user_or_raise(payload.get("parent_user_id"))

    siswa = Siswa(
        nisn=payload["nisn"],
        nama=payload["nama"],
        jenis_kelamin=payload.get("jenis_kelamin"),
        alamat=payload.get("alamat"),
        no_telp_ortu=payload.get("no_telp_ortu"),
        id_card=payload.get("id_card"),
        id_kelas=payload["id_kelas"],
        id_user=student_user.id_user if student_user else None,
    )
    db.session.add(siswa)
    db.session.flush()

    if parent_user is not None:
        _upsert_parent_relation(siswa, parent_user.id_user)

    db.session.commit()
    return get_siswa_detail(siswa.id_siswa)


def update_siswa(siswa_id: int, payload: dict) -> dict:
    siswa = _get_siswa_or_raise(siswa_id)
    next_nisn = payload.get("nisn", siswa.nisn)
    next_card = payload.get("id_card", siswa.id_card)

    _ensure_unique_nisn_or_raise(next_nisn, exclude_id=siswa.id_siswa)
    _ensure_unique_card_or_raise(next_card, exclude_id=siswa.id_siswa)

    if "id_kelas" in payload:
        _ensure_kelas_exists_or_raise(payload["id_kelas"])

    if "id_user" in payload:
        student_user = _ensure_student_user_or_raise(payload.get("id_user"), current_student_id=siswa.id_siswa)
        siswa.id_user = student_user.id_user if student_user else None

    if "parent_user_id" in payload:
        parent_user = _ensure_parent_user_or_raise(
            payload.get("parent_user_id"),
            current_student_id=siswa.id_siswa,
        )
        _upsert_parent_relation(siswa, parent_user.id_user if parent_user else None)

    if "nisn" in payload:
        siswa.nisn = payload["nisn"]
    if "nama" in payload:
        siswa.nama = payload["nama"]
    if "jenis_kelamin" in payload:
        siswa.jenis_kelamin = payload["jenis_kelamin"]
    if "alamat" in payload:
        siswa.alamat = payload["alamat"]
    if "no_telp_ortu" in payload:
        siswa.no_telp_ortu = payload["no_telp_ortu"]
    if "id_card" in payload:
        siswa.id_card = payload["id_card"]
    if "id_kelas" in payload:
        siswa.id_kelas = payload["id_kelas"]

    db.session.commit()
    return get_siswa_detail(siswa.id_siswa)


def delete_siswa(siswa_id: int) -> None:
    siswa = _get_siswa_or_raise(siswa_id)
    relation = getattr(siswa, "orangtua", None)
    if relation is not None:
        db.session.delete(relation)
        db.session.flush()
    db.session.delete(siswa)
    db.session.commit()
