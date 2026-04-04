from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from flask_jwt_extended import create_access_token, decode_token

from ..extensions import db, token_blocklist
from ..models import Siswa, User


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


def _find_user_by_username_or_email(username: str, email: str | None):
    filters = [User.username == username]
    if email:
        filters.append(User.email == email)
    return User.query.filter(or_(*filters)).first()


def find_student_candidate(nisn: str | None = None, id_card: str | None = None):
    query = Siswa.query
    if nisn:
        query = query.filter(Siswa.nisn == nisn)
    elif id_card:
        query = query.filter(Siswa.id_card == id_card)
    else:
        return None
    return query.first()


def register_user_manual(payload: dict) -> tuple[User | None, Siswa | None]:
    existing_user = _find_user_by_username_or_email(
        payload["username"],
        payload.get("email"),
    )
    if existing_user:
        raise ValueError("Username atau email sudah digunakan.")

    user = User(
        username=payload["username"],
        full_name=payload["full_name"],
        email=payload.get("email"),
        no_telp=payload.get("no_telp"),
        role=payload["role"],
    )
    user.set_password(payload["password"])
    db.session.add(user)
    db.session.flush()

    siswa = None
    if payload["role"] == "siswa":
        student_data = payload.get("student") or {}
        siswa = Siswa(
            id_user=user.id_user,
            nisn=student_data["nisn"],
            nama=student_data.get("nama") or user.full_name,
            jenis_kelamin=student_data.get("jenis_kelamin"),
            alamat=student_data.get("alamat"),
            no_telp_ortu=student_data.get("no_telp_ortu"),
            id_card=student_data.get("id_card"),
            id_kelas=student_data.get("id_kelas"),
        )
        db.session.add(siswa)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Data registrasi bentrok dengan data yang sudah ada.")
    return user, siswa


def register_user_from_school_db(payload: dict) -> tuple[User, Siswa]:
    student = find_student_candidate(
        nisn=payload.get("nisn"),
        id_card=payload.get("id_card"),
    )
    if student is None:
        raise LookupError("Data siswa tidak ditemukan di database sekolah.")
    if student.id_user is not None:
        raise ValueError("Siswa tersebut sudah memiliki akun.")

    existing_user = _find_user_by_username_or_email(
        payload["username"],
        payload.get("email"),
    )
    if existing_user:
        raise ValueError("Username atau email sudah digunakan.")

    user = User(
        username=payload["username"],
        full_name=student.nama,
        email=payload.get("email"),
        no_telp=payload.get("no_telp"),
        role="siswa",
    )
    user.set_password(payload["password"])
    db.session.add(user)
    db.session.flush()

    student.id_user = user.id_user
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise ValueError("Data registrasi bentrok dengan data yang sudah ada.")
    return user, student
