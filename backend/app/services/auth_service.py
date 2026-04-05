from flask_jwt_extended import create_access_token, decode_token

from ..extensions import db, token_blocklist
from ..models import Siswa, User


ROLE_ALIASES = {
    "wali": "wali_kelas",
    "piket": "guru_piket",
    "ortu": "orangtua",
}


def authenticate_user(username: str, password: str):
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    if user is None or not user.check_password(password):
        return None
    return user


def build_access_token(user: User) -> str:
    additional_claims = {
        "role": user.role,
        "username": user.username,
        "full_name": user.full_name,
    }
    return create_access_token(
        identity=str(user.id_user),
        additional_claims=additional_claims,
    )


def build_login_payload(user: User) -> dict:
    access_token = build_access_token(user)
    decoded = decode_token(access_token)
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_at": decoded["exp"],
        "user": user.to_dict(),
    }


def revoke_token(jti: str) -> None:
    token_blocklist.add(jti)


def is_token_revoked(jwt_payload: dict) -> bool:
    jti = jwt_payload.get("jti")
    return jti in token_blocklist


def get_user_by_identity(identity: str | int):
    return db.session.get(User, int(identity))


def _normalize_role(role: str) -> str:
    cleaned = (role or "").strip().lower()
    return ROLE_ALIASES.get(cleaned, cleaned)


def find_student_candidate(nisn: str | None = None, id_card: str | None = None):
    query = Siswa.query
    if nisn:
        student = query.filter_by(nisn=nisn.strip()).first()
        if student is not None:
            return student

    if id_card:
        student = query.filter_by(id_card=id_card.strip()).first()
        if student is not None:
            return student

    return None


def _assert_unique_user(username: str, email: str | None):
    if User.query.filter_by(username=username).first():
        raise ValueError("Username sudah digunakan.")

    if email and User.query.filter_by(email=email).first():
        raise ValueError("Email sudah digunakan.")


def register_user_manual(payload: dict):
    username = payload["username"]
    password = payload["password"]
    role = _normalize_role(payload["role"])
    full_name = payload["full_name"]
    email = payload.get("email")
    no_telp = payload.get("no_telp")

    _assert_unique_user(username, email)

    user = User(
        username=username,
        full_name=full_name,
        email=email,
        no_telp=no_telp,
        role=role,
    )
    user.set_password(password)

    student = None
    if role == "siswa":
        student = find_student_candidate(
            nisn=payload.get("nisn"),
            id_card=payload.get("id_card"),
        )
        if student is None:
            raise LookupError("Data siswa tidak ditemukan untuk role siswa.")
        if student.id_user is not None:
            raise ValueError("Siswa sudah memiliki akun.")

    try:
        db.session.add(user)
        db.session.flush()
        if student is not None:
            student.id_user = user.id_user
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return user, student


def register_user_from_school_db(payload: dict):
    student = find_student_candidate(
        nisn=payload.get("nisn"),
        id_card=payload.get("id_card"),
    )
    if student is None:
        raise LookupError("Data siswa tidak ditemukan.")
    if student.id_user is not None:
        raise ValueError("Siswa sudah memiliki akun.")

    username = payload.get("username") or f"siswa{student.nisn}"
    password = payload["password"]
    role = _normalize_role(payload.get("role") or "siswa")
    full_name = payload.get("full_name") or student.nama
    email = payload.get("email")
    no_telp = payload.get("no_telp")

    _assert_unique_user(username, email)

    user = User(
        username=username,
        full_name=full_name,
        email=email,
        no_telp=no_telp,
        role=role,
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.flush()
        student.id_user = user.id_user
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return user, student
