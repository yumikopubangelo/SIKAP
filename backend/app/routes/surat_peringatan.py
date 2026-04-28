from flask import Blueprint, jsonify, request

from ..middleware.auth_middleware import inject_current_user
from ..services.surat_peringatan_service import (
    SuratPeringatanServiceError,
    get_surat_peringatan_detail,
    list_surat_peringatan,
)
from ..utils.response import error_response, success_response
from ..utils.validators import validate_surat_peringatan_list_params


surat_peringatan_bp = Blueprint("surat_peringatan", __name__, url_prefix="/api/v1/surat-peringatan")


@surat_peringatan_bp.get("")
@inject_current_user
def list_surat_peringatan_route(current_user):
    params, errors = validate_surat_peringatan_list_params(request.args)
    if errors:
        return error_response("Parameter surat peringatan tidak valid.", 400, errors=errors)

    try:
        data, pagination = list_surat_peringatan(params, current_user)
    except SuratPeringatanServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar surat peringatan berhasil diambil.",
                "data": data,
                "pagination": pagination,
            }
        ),
        200,
    )


@surat_peringatan_bp.get("/<int:sp_id>")
@inject_current_user
def get_surat_peringatan_route(current_user, sp_id: int):
    try:
        data = get_surat_peringatan_detail(sp_id, current_user)
    except SuratPeringatanServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(data=data, message="Detail surat peringatan berhasil diambil.")
