from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..middleware.auth_middleware import inject_current_user
from ..services.auth_service import (
    authenticate_user,
    build_login_payload,
    revoke_token,
)
from ..utils.response import error_response, success_response
from ..utils.validators import validate_login_payload


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
