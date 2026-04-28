from flask import Blueprint, jsonify, request

from ..middleware.auth_middleware import inject_current_user
from ..services.kelas_service import (
    KelasServiceError,
    create_kelas,
    delete_kelas,
    get_kelas_detail,
    list_kelas,
    update_kelas,
)
from ..utils.response import error_response, success_response
from ..utils.validators import validate_kelas_list_params, validate_kelas_payload


kelas_bp = Blueprint("kelas", __name__, url_prefix="/api/v1/kelas")


def _ensure_admin(current_user):
    if current_user.role != "admin":
        return error_response("Hanya admin yang dapat mengakses endpoint ini.", 403)
    return None


@kelas_bp.get("")
@inject_current_user
def list_kelas_route(current_user):
    params, errors = validate_kelas_list_params(request.args)
    if errors:
        return error_response("Parameter list kelas tidak valid.", 400, errors=errors)

    try:
        data, pagination = list_kelas(params)
    except KelasServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar kelas berhasil diambil.",
                "data": data,
                "pagination": pagination,
            }
        ),
        200,
    )


@kelas_bp.post("")
@inject_current_user
def create_kelas_route(current_user):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_kelas_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload kelas tidak valid.", 400, errors=errors)

    try:
        data = create_kelas(payload)
    except KelasServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Kelas berhasil dibuat.", status_code=201)


@kelas_bp.get("/<int:kelas_id>")
@inject_current_user
def get_kelas_route(current_user, kelas_id: int):
    try:
        data = get_kelas_detail(kelas_id)
    except KelasServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Detail kelas berhasil diambil.")


@kelas_bp.put("/<int:kelas_id>")
@inject_current_user
def update_kelas_route(current_user, kelas_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_kelas_payload(request.get_json(silent=True), partial=True)
    if errors:
        return error_response("Payload update kelas tidak valid.", 400, errors=errors)

    try:
        data = update_kelas(kelas_id, payload)
    except KelasServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Kelas berhasil diperbarui.")


@kelas_bp.delete("/<int:kelas_id>")
@inject_current_user
def delete_kelas_route(current_user, kelas_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    try:
        delete_kelas(kelas_id)
    except KelasServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(message="Kelas berhasil dihapus.")
