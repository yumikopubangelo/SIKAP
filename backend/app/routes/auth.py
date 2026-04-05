from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..middleware.auth_middleware import inject_current_user
from ..middleware.role_middleware import roles_required
from ..services.auth_service import (
    authenticate_user,
    build_login_payload,
    find_student_candidate,
    register_user_from_school_db,
    register_user_manual,
    revoke_token,
)
from ..utils.response import error_response, success_response
from ..utils.validators import (
    validate_login_payload,
    validate_register_payload,
    validate_student_lookup_params,
)


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/login")
def login():
    payload, errors = validate_login_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload login tidak valid.", 400, errors=errors)

    user = authenticate_user(payload["username"], payload["password"])
    if user is None:
        return error_response("Username atau password salah.", 401)

    return success_response(
        data=build_login_payload(user),
        message="Login berhasil.",
    )


@auth_bp.post("/logout")
@inject_current_user
def logout(current_user):
    revoke_token(get_jwt()["jti"])
    return success_response(
        data={"user_id": current_user.id_user},
        message="Logout berhasil.",
    )


@auth_bp.get("/me")
@inject_current_user
def me(current_user):
    return success_response(
        data=current_user.to_dict(),
        message="Profil user berhasil diambil.",
    )


@auth_bp.get("/student-candidates")
@roles_required("admin")
def student_candidates():
    params, errors = validate_student_lookup_params(request.args)
    if errors:
        return error_response("Parameter pencarian tidak valid.", 400, errors=errors)

    student = find_student_candidate(
        nisn=params.get("nisn"),
        id_card=params.get("id_card"),
    )
    if student is None:
        return error_response("Data siswa tidak ditemukan.", 404)

    return success_response(
        data={
            "student": student.to_dict(),
            "has_account": student.id_user is not None,
        },
        message="Data siswa berhasil ditemukan.",
    )


@auth_bp.post("/register")
@roles_required("admin")
def register():
    payload, errors = validate_register_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload registrasi tidak valid.", 400, errors=errors)

    try:
        if payload["mode"] == "manual":
            user, student = register_user_manual(payload)
        else:
            user, student = register_user_from_school_db(payload)
    except LookupError as exc:
        return error_response(str(exc), 404)
    except ValueError as exc:
        return error_response(str(exc), 400)

    return success_response(
        data={
            "user": user.to_dict(),
            "student": student.to_dict() if student else None,
        },
        message="Registrasi akun berhasil.",
        status_code=201,
    )
