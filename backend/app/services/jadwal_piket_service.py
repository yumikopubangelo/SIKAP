from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import JadwalPiket, User


class JadwalPiketServiceError(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def _query():
    return JadwalPiket.query.options(joinedload(JadwalPiket.user))


def _serialize(item: JadwalPiket) -> dict:
    return {
        "id_jadwal": item.id_jadwal,
        "hari": item.hari,
        "jam_mulai": item.jam_mulai.isoformat() if item.jam_mulai else None,
        "jam_selesai": item.jam_selesai.isoformat() if item.jam_selesai else None,
        "user": (
            {
                "id_user": item.user.id_user,
                "username": item.user.username,
                "full_name": item.user.full_name,
            }
            if item.user
            else None
        ),
    }


def _get_or_raise(jadwal_id: int) -> JadwalPiket:
    item = _query().filter_by(id_jadwal=jadwal_id).first()
    if item is None:
        raise JadwalPiketServiceError("Jadwal piket tidak ditemukan.", 404)
    return item


def _ensure_guru_piket_or_raise(user_id: int) -> User:
    user = User.query.filter_by(id_user=user_id).first()
    if user is None:
        raise JadwalPiketServiceError("User guru piket tidak ditemukan.", 404)
    if user.role != "guru_piket":
        raise JadwalPiketServiceError("User yang dipilih bukan guru piket.", 400)
    return user


def _ensure_no_overlap_or_raise(*, user_id: int, hari: str, jam_mulai, jam_selesai, exclude_id: int | None = None):
    query = JadwalPiket.query.filter(
        JadwalPiket.id_user == user_id,
        JadwalPiket.hari == hari,
    )
    if exclude_id is not None:
        query = query.filter(JadwalPiket.id_jadwal != exclude_id)

    rows = query.all()
    for item in rows:
        if jam_mulai < item.jam_selesai and jam_selesai > item.jam_mulai:
            raise JadwalPiketServiceError("Jadwal piket bentrok dengan jadwal lain pada hari yang sama.", 409)


def list_jadwal_piket(params: dict, current_user) -> tuple[list[dict], dict]:
    query = _query()

    if current_user.role == "guru_piket":
        query = query.filter(JadwalPiket.id_user == current_user.id_user)
    elif current_user.role != "admin":
        raise JadwalPiketServiceError("Akses jadwal piket ditolak.", 403)

    if params.get("hari") is not None:
        query = query.filter(JadwalPiket.hari == params["hari"])

    if params.get("user_id") is not None:
        query = query.filter(JadwalPiket.id_user == params["user_id"])

    total_items = query.count()
    page = params["page"]
    limit = params["limit"]
    total_pages = max(1, (total_items + limit - 1) // limit)
    rows = (
        query.order_by(JadwalPiket.hari.asc(), JadwalPiket.jam_mulai.asc(), JadwalPiket.id_jadwal.asc())
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


def create_jadwal_piket(payload: dict) -> dict:
    user = _ensure_guru_piket_or_raise(payload["user_id"])
    if payload["jam_mulai"] >= payload["jam_selesai"]:
        raise JadwalPiketServiceError("Jam mulai harus lebih kecil dari jam selesai.", 400)
    _ensure_no_overlap_or_raise(
        user_id=user.id_user,
        hari=payload["hari"],
        jam_mulai=payload["jam_mulai"],
        jam_selesai=payload["jam_selesai"],
    )

    item = JadwalPiket(
        id_user=user.id_user,
        hari=payload["hari"],
        jam_mulai=payload["jam_mulai"],
        jam_selesai=payload["jam_selesai"],
    )
    db.session.add(item)
    db.session.commit()
    return _serialize(_get_or_raise(item.id_jadwal))


def update_jadwal_piket(jadwal_id: int, payload: dict) -> dict:
    item = _get_or_raise(jadwal_id)

    next_user_id = payload.get("user_id", item.id_user)
    next_hari = payload.get("hari", item.hari)
    next_jam_mulai = payload.get("jam_mulai", item.jam_mulai)
    next_jam_selesai = payload.get("jam_selesai", item.jam_selesai)

    if next_jam_mulai >= next_jam_selesai:
        raise JadwalPiketServiceError("Jam mulai harus lebih kecil dari jam selesai.", 400)

    _ensure_guru_piket_or_raise(next_user_id)
    _ensure_no_overlap_or_raise(
        user_id=next_user_id,
        hari=next_hari,
        jam_mulai=next_jam_mulai,
        jam_selesai=next_jam_selesai,
        exclude_id=item.id_jadwal,
    )

    item.id_user = next_user_id
    item.hari = next_hari
    item.jam_mulai = next_jam_mulai
    item.jam_selesai = next_jam_selesai
    db.session.commit()
    return _serialize(_get_or_raise(item.id_jadwal))


def delete_jadwal_piket(jadwal_id: int) -> None:
    item = _get_or_raise(jadwal_id)
    db.session.delete(item)
    db.session.commit()
