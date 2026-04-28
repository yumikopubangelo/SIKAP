from flask import Blueprint, jsonify, request

from ..middleware.auth_middleware import inject_current_user
from ..services.jadwal_piket_service import (
    JadwalPiketServiceError,
    create_jadwal_piket,
    delete_jadwal_piket,
    list_jadwal_piket,
    update_jadwal_piket,
)
from ..utils.response import error_response, success_response
from ..utils.validators import validate_jadwal_piket_list_params, validate_jadwal_piket_payload


jadwal_piket_bp = Blueprint("jadwal_piket", __name__, url_prefix="/api/v1/jadwal-piket")


def _ensure_admin(current_user):
    if current_user.role != "admin":
        return error_response("Hanya admin yang dapat mengubah jadwal piket.", 403)
    return None


@jadwal_piket_bp.get("")
@inject_current_user
def list_jadwal_piket_route(current_user):
    params, errors = validate_jadwal_piket_list_params(request.args)
    if errors:
        return error_response("Parameter jadwal piket tidak valid.", 400, errors=errors)

    try:
        data, pagination = list_jadwal_piket(params, current_user)
    except JadwalPiketServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar jadwal piket berhasil diambil.",
                "data": data,
                "pagination": pagination,
            }
        ),
        200,
    )


@jadwal_piket_bp.post("")
@inject_current_user
def create_jadwal_piket_route(current_user):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_jadwal_piket_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload jadwal piket tidak valid.", 400, errors=errors)

    try:
        data = create_jadwal_piket(payload)
    except JadwalPiketServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Jadwal piket berhasil dibuat.", status_code=201)


@jadwal_piket_bp.put("/<int:jadwal_id>")
@inject_current_user
def update_jadwal_piket_route(current_user, jadwal_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_jadwal_piket_payload(request.get_json(silent=True), partial=True)
    if errors:
        return error_response("Payload update jadwal piket tidak valid.", 400, errors=errors)

    try:
        data = update_jadwal_piket(jadwal_id, payload)
    except JadwalPiketServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Jadwal piket berhasil diperbarui.")


@jadwal_piket_bp.delete("/<int:jadwal_id>")
@inject_current_user
def delete_jadwal_piket_route(current_user, jadwal_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    try:
        delete_jadwal_piket(jadwal_id)
    except JadwalPiketServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(message="Jadwal piket berhasil dihapus.")
