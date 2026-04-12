from flask import Blueprint, jsonify, request

from ..middleware.auth_middleware import inject_current_user
from ..services.user_service import (
    UserServiceError,
    create_user,
    delete_user,
    get_user_detail,
    list_users,
    update_user,
)
from ..utils.response import error_response, success_response
from ..utils.validators import (
    validate_user_create_payload,
    validate_user_list_params,
    validate_user_update_payload,
)


users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")


def _ensure_admin(current_user):
    if current_user.role != "admin":
        return error_response("Hanya admin yang dapat mengakses endpoint ini.", 403)
    return None


@users_bp.get("")
@inject_current_user
def list_users_route(current_user):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    params, errors = validate_user_list_params(request.args)
    if errors:
        return error_response("Parameter user management tidak valid.", 400, errors=errors)

    try:
        data, pagination = list_users(params)
    except UserServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar user berhasil diambil.",
                "data": data,
                "pagination": pagination,
            }
        ),
        200,
    )


@users_bp.get("/<int:user_id>")
@inject_current_user
def get_user_route(current_user, user_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    try:
        data = get_user_detail(user_id)
    except UserServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(
        data=data,
        message="Detail user berhasil diambil.",
    )


@users_bp.post("")
@inject_current_user
def create_user_route(current_user):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_user_create_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload create user tidak valid.", 400, errors=errors)

    try:
        data = create_user(payload)
    except UserServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(
        data=data,
        message="User berhasil dibuat.",
        status_code=201,
    )


@users_bp.put("/<int:user_id>")
@inject_current_user
def update_user_route(current_user, user_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_user_update_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload update user tidak valid.", 400, errors=errors)

    try:
        data = update_user(user_id, payload)
    except UserServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(
        data=data,
        message="User berhasil diupdate.",
    )


@users_bp.delete("/<int:user_id>")
@inject_current_user
def delete_user_route(current_user, user_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    try:
        delete_user(user_id, current_user)
    except UserServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(message="User berhasil dihapus.")
