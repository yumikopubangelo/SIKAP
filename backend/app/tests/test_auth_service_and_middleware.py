from flask_jwt_extended import create_access_token

from app.extensions import db, token_blocklist
from app.models import Kelas, Siswa, User
from app.services.auth_service import (
    authenticate_user,
    build_login_payload,
    find_student_candidate,
    get_user_by_identity,
    is_token_revoked,
    register_user_from_school_db,
    register_user_manual,
    revoke_token,
)


def seed_auth_data():
    admin = User(
        username="admin_auth_service",
        full_name="Admin Auth Service",
        email="admin.auth.service@sikap.local",
        role="admin",
    )
    admin.set_password("admin12345")

    kelas = Kelas(
        nama_kelas="X AUTH 1",
        tingkat="X",
        jurusan="RPL",
        tahun_ajaran="2025/2026",
    )
    db.session.add_all([admin, kelas])
    db.session.flush()

    siswa = Siswa(
        nisn="7000000001",
        nama="Siswa Auth",
        id_card="CARD-AUTH-001",
        id_kelas=kelas.id_kelas,
    )
    db.session.add(siswa)
    db.session.commit()
    return admin, siswa


def test_authenticate_user_supports_username_and_email_and_rejects_wrong_password(app):
    with app.app_context():
        admin, _siswa = seed_auth_data()

        assert authenticate_user("admin_auth_service", "admin12345").id_user == admin.id_user
        assert authenticate_user("admin.auth.service@sikap.local", "admin12345").id_user == admin.id_user
        assert authenticate_user("admin_auth_service", "wrong-password") is None
        assert authenticate_user("unknown-user", "admin12345") is None


def test_build_login_payload_revoke_token_and_get_user_by_identity(app):
    with app.app_context():
        admin, _siswa = seed_auth_data()

        payload = build_login_payload(admin)
        assert payload["token_type"] == "Bearer"
        assert payload["user"]["username"] == "admin_auth_service"
        assert payload["expires_at"] > 0

        revoke_token("jti-auth-service")
        assert is_token_revoked({"jti": "jti-auth-service"}) is True
        assert is_token_revoked({"jti": "other-jti"}) is False
        assert get_user_by_identity(str(admin.id_user)).username == "admin_auth_service"

        token_blocklist.clear()


def test_find_student_candidate_and_register_user_manual(app):
    with app.app_context():
        _admin, siswa = seed_auth_data()

        assert find_student_candidate(nisn="7000000001").id_siswa == siswa.id_siswa
        assert find_student_candidate(id_card="CARD-AUTH-001").id_siswa == siswa.id_siswa
        assert find_student_candidate(nisn="9999999999", id_card="NOT-FOUND") is None

        wali_user, linked_student = register_user_manual(
            {
                "username": "wali.alias",
                "password": "password123",
                "role": "wali",
                "full_name": "Wali Alias",
                "email": "wali.alias@sikap.local",
            }
        )
        assert wali_user.role == "wali_kelas"
        assert linked_student is None

        siswa_user, linked_student = register_user_manual(
            {
                "username": "siswa.auth",
                "password": "password123",
                "role": "siswa",
                "full_name": "Siswa Auth User",
                "email": "siswa.auth@sikap.local",
                "nisn": "7000000001",
            }
        )
        assert siswa_user.role == "siswa"
        assert linked_student.id_siswa == siswa.id_siswa
        assert linked_student.id_user == siswa_user.id_user


def test_register_user_manual_rejects_duplicate_and_existing_student(app):
    with app.app_context():
        admin, siswa = seed_auth_data()

        duplicate_username_payload = {
            "username": admin.username,
            "password": "password123",
            "role": "admin",
            "full_name": "Admin Baru",
            "email": "admin.baru@sikap.local",
        }
        try:
            register_user_manual(duplicate_username_payload)
            assert False, "register_user_manual seharusnya menolak username duplikat"
        except ValueError as exc:
            assert "Username sudah digunakan" in str(exc)

        duplicate_email_payload = {
            "username": "email.duplikat",
            "password": "password123",
            "role": "admin",
            "full_name": "Email Duplikat",
            "email": admin.email,
        }
        try:
            register_user_manual(duplicate_email_payload)
            assert False, "register_user_manual seharusnya menolak email duplikat"
        except ValueError as exc:
            assert "Email sudah digunakan" in str(exc)

        existing_student_user = User(
            username="existing.student",
            full_name="Existing Student",
            email="existing.student@sikap.local",
            role="siswa",
        )
        existing_student_user.set_password("password123")
        db.session.add(existing_student_user)
        db.session.flush()
        siswa.id_user = existing_student_user.id_user
        db.session.commit()

        try:
            register_user_manual(
                {
                    "username": "siswa.duplikat",
                    "password": "password123",
                    "role": "siswa",
                    "full_name": "Siswa Duplikat",
                    "email": "siswa.duplikat@sikap.local",
                    "nisn": siswa.nisn,
                }
            )
            assert False, "register_user_manual seharusnya menolak siswa yang sudah punya akun"
        except ValueError as exc:
            assert "Siswa sudah memiliki akun" in str(exc)

        try:
            register_user_manual(
                {
                    "username": "siswa.tidak.ada",
                    "password": "password123",
                    "role": "siswa",
                    "full_name": "Siswa Tidak Ada",
                    "email": "siswa.tidak.ada@sikap.local",
                    "nisn": "7000000099",
                }
            )
            assert False, "register_user_manual seharusnya menolak siswa yang tidak ada"
        except LookupError as exc:
            assert "Data siswa tidak ditemukan" in str(exc)


def test_register_user_from_school_db_uses_defaults(app):
    with app.app_context():
        _admin, siswa = seed_auth_data()

        user, linked_student = register_user_from_school_db(
            {
                "password": "password123",
                "nisn": siswa.nisn,
            }
        )

        assert user.username == f"siswa{siswa.nisn}"
        assert user.full_name == siswa.nama
        assert user.role == "siswa"
        assert linked_student.id_user == user.id_user


def test_auth_middleware_returns_404_for_valid_token_with_missing_user(client, app):
    with app.app_context():
        token = create_access_token(
            identity="999999",
            additional_claims={
                "role": "admin",
                "username": "ghost",
                "full_name": "Ghost User",
            },
        )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.get_json()["message"] == "User tidak ditemukan."
