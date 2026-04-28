from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Kelas, Siswa, User


class KelasServiceError(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def _serialize_kelas(kelas: Kelas) -> dict:
    return {
        "id_kelas": kelas.id_kelas,
        "nama_kelas": kelas.nama_kelas,
        "tingkat": kelas.tingkat,
        "jurusan": kelas.jurusan,
        "tahun_ajaran": kelas.tahun_ajaran,
        "jumlah_siswa": len(kelas.siswa or []),
        "wali_kelas": (
            {
                "id_user": kelas.wali_kelas.id_user,
                "username": kelas.wali_kelas.username,
                "full_name": kelas.wali_kelas.full_name,
            }
            if kelas.wali_kelas
            else None
        ),
    }


def _kelas_query():
    return Kelas.query.options(
        joinedload(Kelas.wali_kelas),
        joinedload(Kelas.siswa),
    )


def _get_kelas_or_raise(kelas_id: int) -> Kelas:
    kelas = _kelas_query().filter_by(id_kelas=kelas_id).first()
    if kelas is None:
        raise KelasServiceError("Data kelas tidak ditemukan.", 404)
    return kelas


def _ensure_wali_kelas_or_raise(user_id: int | None) -> User | None:
    if user_id is None:
        return None
    user = User.query.filter_by(id_user=user_id).first()
    if user is None:
        raise KelasServiceError("User wali kelas tidak ditemukan.", 404)
    if user.role != "wali_kelas":
        raise KelasServiceError("User yang dipilih bukan wali kelas.", 400)
    return user


def _ensure_unique_kelas_or_raise(*, nama_kelas: str, tahun_ajaran: str, exclude_id: int | None = None):
    query = Kelas.query.filter_by(nama_kelas=nama_kelas, tahun_ajaran=tahun_ajaran)
    if exclude_id is not None:
        query = query.filter(Kelas.id_kelas != exclude_id)
    if query.first() is not None:
        raise KelasServiceError("Nama kelas pada tahun ajaran tersebut sudah ada.", 409)


def list_kelas(params: dict) -> tuple[list[dict], dict]:
    query = _kelas_query()

    if params.get("tingkat"):
        query = query.filter(Kelas.tingkat == params["tingkat"])

    if params.get("tahun_ajaran"):
        query = query.filter(Kelas.tahun_ajaran == params["tahun_ajaran"])

    if params.get("search"):
        search_pattern = f"%{params['search']}%"
        query = query.outerjoin(Kelas.wali_kelas).filter(
            or_(
                Kelas.nama_kelas.ilike(search_pattern),
                Kelas.jurusan.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            )
        )

    total_items = query.with_entities(func.count(Kelas.id_kelas.distinct())).scalar() or 0
    page = params["page"]
    limit = params["limit"]
    total_pages = max(1, (total_items + limit - 1) // limit)

    rows = (
        query.order_by(Kelas.tingkat.asc(), Kelas.nama_kelas.asc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return (
        [_serialize_kelas(kelas) for kelas in rows],
        {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    )


def get_kelas_detail(kelas_id: int) -> dict:
    kelas = _get_kelas_or_raise(kelas_id)
    data = _serialize_kelas(kelas)
    data["students"] = [
        {
            "id_siswa": siswa.id_siswa,
            "nisn": siswa.nisn,
            "nama": siswa.nama,
            "id_card": siswa.id_card,
        }
        for siswa in sorted(kelas.siswa or [], key=lambda item: (item.nama or "", item.nisn or ""))
    ]
    return data


def create_kelas(payload: dict) -> dict:
    _ensure_unique_kelas_or_raise(
        nama_kelas=payload["nama_kelas"],
        tahun_ajaran=payload["tahun_ajaran"],
    )
    wali_kelas = _ensure_wali_kelas_or_raise(payload.get("id_wali"))

    kelas = Kelas(
        nama_kelas=payload["nama_kelas"],
        tingkat=payload["tingkat"],
        jurusan=payload.get("jurusan"),
        tahun_ajaran=payload["tahun_ajaran"],
        id_wali=wali_kelas.id_user if wali_kelas else None,
    )
    db.session.add(kelas)
    db.session.commit()
    return get_kelas_detail(kelas.id_kelas)


def update_kelas(kelas_id: int, payload: dict) -> dict:
    kelas = _get_kelas_or_raise(kelas_id)
    next_nama_kelas = payload.get("nama_kelas", kelas.nama_kelas)
    next_tahun_ajaran = payload.get("tahun_ajaran", kelas.tahun_ajaran)

    _ensure_unique_kelas_or_raise(
        nama_kelas=next_nama_kelas,
        tahun_ajaran=next_tahun_ajaran,
        exclude_id=kelas.id_kelas,
    )

    if "id_wali" in payload:
        wali_kelas = _ensure_wali_kelas_or_raise(payload.get("id_wali"))
        kelas.id_wali = wali_kelas.id_user if wali_kelas else None

    if "nama_kelas" in payload:
        kelas.nama_kelas = payload["nama_kelas"]
    if "tingkat" in payload:
        kelas.tingkat = payload["tingkat"]
    if "jurusan" in payload:
        kelas.jurusan = payload["jurusan"]
    if "tahun_ajaran" in payload:
        kelas.tahun_ajaran = payload["tahun_ajaran"]

    db.session.commit()
    return get_kelas_detail(kelas.id_kelas)


def delete_kelas(kelas_id: int) -> None:
    kelas = _get_kelas_or_raise(kelas_id)
    if kelas.siswa:
        raise KelasServiceError("Kelas masih memiliki data siswa dan tidak dapat dihapus.", 400)

    db.session.delete(kelas)
    db.session.commit()
