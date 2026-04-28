from sqlalchemy.orm import joinedload

from ..models import Kelas, OrangTua, SuratPeringatan, Siswa


class SuratPeringatanServiceError(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def _query():
    return SuratPeringatan.query.options(
        joinedload(SuratPeringatan.siswa).joinedload(Siswa.kelas),
        joinedload(SuratPeringatan.pengirim),
        joinedload(SuratPeringatan.siswa).joinedload(Siswa.orangtua).joinedload(OrangTua.user),
    )


def _serialize(item: SuratPeringatan) -> dict:
    siswa = item.siswa
    parent_user = siswa.orangtua.user if siswa and getattr(siswa, "orangtua", None) and siswa.orangtua.user else None
    return {
        "id_sp": item.id_sp,
        "sp_ke": item.sp_ke,
        "jenis": item.jenis,
        "tanggal": item.tanggal.isoformat() if item.tanggal else None,
        "status_kirim": item.status_kirim,
        "alasan": item.alasan,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "siswa": (
            {
                "id_siswa": siswa.id_siswa,
                "nisn": siswa.nisn,
                "nama": siswa.nama,
                "kelas": siswa.kelas.nama_kelas if siswa.kelas else None,
            }
            if siswa
            else None
        ),
        "orangtua": (
            {
                "id_user": parent_user.id_user,
                "full_name": parent_user.full_name,
                "email": parent_user.email,
                "no_telp": parent_user.no_telp,
            }
            if parent_user
            else None
        ),
        "pengirim": (
            {
                "id_user": item.pengirim.id_user,
                "full_name": item.pengirim.full_name,
                "role": item.pengirim.role,
            }
            if item.pengirim
            else None
        ),
    }


def _scoped_query(current_user):
    query = _query().join(SuratPeringatan.siswa)

    if current_user.role in ("admin", "kepsek", "guru_piket"):
        return query

    if current_user.role == "wali_kelas":
        return query.join(Siswa.kelas).filter(Kelas.id_wali == current_user.id_user)

    if current_user.role == "siswa" and current_user.siswa_profile is not None:
        return query.filter(SuratPeringatan.id_siswa == current_user.siswa_profile.id_siswa)

    if current_user.role == "orangtua":
        parent_relation = getattr(current_user, "orangtua_profile", None)
        if parent_relation is not None:
            return query.filter(SuratPeringatan.id_siswa == parent_relation.id_siswa)

        if current_user.no_telp:
            return query.filter(Siswa.no_telp_ortu == current_user.no_telp)

    return query.filter(SuratPeringatan.id_sp == -1)


def list_surat_peringatan(params: dict, current_user) -> tuple[list[dict], dict]:
    query = _scoped_query(current_user)

    if params.get("siswa_id") is not None:
        query = query.filter(SuratPeringatan.id_siswa == params["siswa_id"])

    if params.get("kelas_id") is not None:
        query = query.filter(Siswa.id_kelas == params["kelas_id"])

    if params.get("jenis") is not None:
        query = query.filter(SuratPeringatan.jenis == params["jenis"])

    total_items = query.count()
    page = params["page"]
    limit = params["limit"]
    total_pages = max(1, (total_items + limit - 1) // limit)
    rows = (
        query.order_by(SuratPeringatan.tanggal.desc(), SuratPeringatan.id_sp.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return (
        [_serialize(item) for item in rows],
        {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    )


def get_surat_peringatan_detail(sp_id: int, current_user) -> dict:
    item = _scoped_query(current_user).filter(SuratPeringatan.id_sp == sp_id).first()
    if item is None:
        raise SuratPeringatanServiceError("Surat peringatan tidak ditemukan.", 404)
    return _serialize(item)
