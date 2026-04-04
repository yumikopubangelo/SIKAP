from flask import Blueprint, request

from ..middleware.auth_middleware import auth_required
from ..services.absensi_service import create_rfid_absensi, get_absensi_detail, list_absensi
from ..utils.response import error_response, success_response
from ..utils.validators import validate_absensi_query_params, validate_rfid_absensi_payload


absensi_bp = Blueprint("absensi", __name__, url_prefix="/api/v1/absensi")


@absensi_bp.post("")
def create_absensi():
    payload, errors = validate_rfid_absensi_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload absensi tidak valid.", 400, errors=errors)

    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return error_response("X-API-Key wajib diisi untuk perangkat RFID.", 401)

    try:
        absensi = create_rfid_absensi(
            uid_card=payload["uid_card"],
            device_id=payload["device_id"],
            api_key=api_key,
            timestamp=payload["timestamp"],
        )
    except PermissionError as exc:
        return error_response(str(exc), 401)
    except LookupError as exc:
        return error_response(str(exc), 404)
    except ValueError as exc:
        return error_response(str(exc), 400)

    return success_response(
        data=absensi.to_dict(),
        message="Absensi berhasil dicatat.",
        status_code=201,
    )


@absensi_bp.get("")
@auth_required
def get_absensi_list():
    filters, errors = validate_absensi_query_params(request.args)
    if errors:
        return error_response("Query absensi tidak valid.", 400, errors=errors)

    result = list_absensi(filters)
    return success_response(
        data=result["items"],
        message="Data absensi berhasil diambil.",
        status_code=200,
        pagination=result["pagination"],
    )


@absensi_bp.get("/<int:absensi_id>")
@auth_required
def get_absensi_by_id(absensi_id: int):
    absensi = get_absensi_detail(absensi_id)
    if absensi is None:
        return error_response("Data absensi tidak ditemukan.", 404)

    return success_response(
        data=absensi.to_dict(),
        message="Detail absensi berhasil diambil.",
    )
