from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Siswa, User
from .auth_service import find_student_candidate


class UserServiceError(Exception):
    def __init__(self, message: str, status_code: int, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def _serialize_student(student: Siswa | None):
    if student is None:
        return None

    return {
        "id_siswa": student.id_siswa,
        "nisn": student.nisn,
        "nama": student.nama,
        "id_card": student.id_card,
        "kelas": student.kelas.nama_kelas if student.kelas else None,
    }


def serialize_user(user: User, include_student: bool = True) -> dict:
    data = user.to_dict()
    if include_student:
        data["student"] = _serialize_student(user.siswa_profile)
    return data


def _user_query():
    return User.query.options(
        joinedload(User.siswa_profile).joinedload(Siswa.kelas),
    )


def _get_user_or_raise(user_id: int) -> User:
    user = _user_query().filter_by(id_user=user_id).first()
    if user is None:
        raise UserServiceError("User tidak ditemukan.", 404)
    return user


def _ensure_unique_identity_fields(
    *,
    username: str | None = None,
    email: str | None = None,
    exclude_user_id: int | None = None,
) -> None:
    if username:
        query = User.query.filter_by(username=username)
        if exclude_user_id is not None:
            query = query.filter(User.id_user != exclude_user_id)
        if query.first() is not None:
            raise UserServiceError("Username sudah digunakan.", 409)

    if email:
        query = User.query.filter_by(email=email)
        if exclude_user_id is not None:
            query = query.filter(User.id_user != exclude_user_id)
        if query.first() is not None:
            raise UserServiceError("Email sudah digunakan.", 409)


def _resolve_student_candidate(payload: dict, current_user: User | None = None) -> Siswa | None:
    if payload.get("role") != "siswa":
        return None

    student = find_student_candidate(
        nisn=payload.get("nisn"),
        id_card=payload.get("id_card"),
    )
    if student is None:
        raise UserServiceError("Data siswa tidak ditemukan.", 404)

    if student.id_user is not None and (current_user is None or student.id_user != current_user.id_user):
        raise UserServiceError("Data siswa tersebut sudah terhubung ke akun lain.", 409)

    return student


def list_users(params: dict) -> tuple[list[dict], dict]:
    query = _user_query()

    if params.get("role"):
        query = query.filter(User.role == params["role"])

    if params.get("search"):
        search_pattern = f"%{params['search']}%"
        query = query.filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            )
        )

    page = params["page"]
    limit = params["limit"]
    total_items = query.count()
    total_pages = max(1, (total_items + limit - 1) // limit)

    users = (
        query.order_by(User.created_at.desc(), User.id_user.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return (
        [serialize_user(user) for user in users],
        {
            "page": page,
            "limit": limit,
            "total_items": total_items,
            "total_pages": total_pages,
        },
    )


def get_user_detail(user_id: int) -> dict:
    user = _get_user_or_raise(user_id)
    return serialize_user(user)


def create_user(payload: dict) -> dict:
    _ensure_unique_identity_fields(username=payload["username"], email=payload.get("email"))
    student = _resolve_student_candidate(payload)

    user = User(
        username=payload["username"],
        full_name=payload["full_name"],
        email=payload.get("email"),
        no_telp=payload.get("no_telp"),
        role=payload["role"],
    )
    user.set_password(payload["password"])

    try:
        db.session.add(user)
        db.session.flush()

        if student is not None:
            student.id_user = user.id_user

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    created = _get_user_or_raise(user.id_user)
    return serialize_user(created)


def update_user(user_id: int, payload: dict) -> dict:
    user = _get_user_or_raise(user_id)

    next_username = payload.get("username", user.username)
    next_email = payload.get("email", user.email)
    next_role = payload.get("role", user.role)

    _ensure_unique_identity_fields(
        username=next_username,
        email=next_email,
        exclude_user_id=user.id_user,
    )

    if next_role != "siswa" and user.siswa_profile is not None:
        raise UserServiceError(
            "User yang sudah terhubung ke data siswa tidak bisa diubah ke role lain.",
            400,
        )

    student = None
    if next_role == "siswa" and user.siswa_profile is None:
        student = _resolve_student_candidate(
            {
                "role": next_role,
                "nisn": payload.get("nisn"),
                "id_card": payload.get("id_card"),
            },
            current_user=user,
        )
        if student is None:
            raise UserServiceError(
                "Role siswa wajib dikaitkan ke data siswa dengan NISN atau kartu.",
                400,
            )

    if "username" in payload:
        user.username = payload["username"]
    if "full_name" in payload:
        user.full_name = payload["full_name"]
    if "email" in payload:
        user.email = payload["email"]
    if "no_telp" in payload:
        user.no_telp = payload["no_telp"]
    if "role" in payload:
        user.role = payload["role"]
    if payload.get("password"):
        user.set_password(payload["password"])

    try:
        if student is not None:
            student.id_user = user.id_user

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    updated = _get_user_or_raise(user.id_user)
    return serialize_user(updated)


def delete_user(user_id: int, current_user: User) -> None:
    user = _get_user_or_raise(user_id)

    if user.id_user == current_user.id_user:
        raise UserServiceError("Akun Anda sendiri tidak dapat dihapus.", 400)

    if user.siswa_profile is not None:
        raise UserServiceError(
            "User yang terhubung ke data siswa tidak dapat dihapus dari menu ini.",
            400,
        )

    try:
        db.session.delete(user)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
