from flask import Blueprint, jsonify, request

from ..middleware.auth_middleware import inject_current_user
from ..services.school_import_service import SchoolImportServiceError, import_school_csv
from ..services.siswa_service import (
    SiswaServiceError,
    create_siswa,
    delete_siswa,
    get_siswa_detail,
    list_siswa,
    update_siswa,
)
from ..utils.response import error_response, success_response
from ..utils.validators import validate_siswa_list_params, validate_siswa_payload


siswa_bp = Blueprint("siswa", __name__, url_prefix="/api/v1/siswa")


def _ensure_admin(current_user):
    if current_user.role != "admin":
        return error_response("Hanya admin yang dapat mengakses endpoint ini.", 403)
    return None


@siswa_bp.get("")
@inject_current_user
def list_siswa_route(current_user):
    params, errors = validate_siswa_list_params(request.args)
    if errors:
        return error_response("Parameter list siswa tidak valid.", 400, errors=errors)

    try:
        data, pagination = list_siswa(params)
    except SiswaServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar siswa berhasil diambil.",
                "data": data,
                "pagination": pagination,
            }
        ),
        200,
    )


@siswa_bp.post("")
@inject_current_user
def create_siswa_route(current_user):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_siswa_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload siswa tidak valid.", 400, errors=errors)

    try:
        data = create_siswa(payload)
    except SiswaServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Data siswa berhasil dibuat.", status_code=201)


@siswa_bp.post("/import-csv")
@inject_current_user
def import_siswa_csv_route(current_user):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    try:
        data = import_school_csv(request.files.get("file"))
    except SchoolImportServiceError as exc:
        return error_response(exc.message, exc.status_code)

    return success_response(data=data, message="Import CSV selesai diproses.", status_code=201)


@siswa_bp.get("/<int:siswa_id>")
@inject_current_user
def get_siswa_route(current_user, siswa_id: int):
    try:
        data = get_siswa_detail(siswa_id)
    except SiswaServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Detail siswa berhasil diambil.")


@siswa_bp.put("/<int:siswa_id>")
@inject_current_user
def update_siswa_route(current_user, siswa_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_siswa_payload(request.get_json(silent=True), partial=True)
    if errors:
        return error_response("Payload update siswa tidak valid.", 400, errors=errors)

    try:
        data = update_siswa(siswa_id, payload)
    except SiswaServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Data siswa berhasil diperbarui.")


@siswa_bp.delete("/<int:siswa_id>")
@inject_current_user
def delete_siswa_route(current_user, siswa_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    try:
        delete_siswa(siswa_id)
    except SiswaServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(message="Data siswa berhasil dihapus.")
