from flask import Blueprint, request

from ..middleware.auth_middleware import inject_current_user
from ..services.absensi_service import (
    AbsensiServiceError,
    create_manual_absensi,
    update_absensi,
)
from ..utils.response import error_response, success_response
from ..utils.validators import (
    validate_absensi_update_payload,
    validate_manual_absensi_payload,
)


absensi_bp = Blueprint("absensi", __name__, url_prefix="/api/v1/absensi")


def _ensure_guru_piket(current_user):
    if current_user.role != "guru_piket":
        return error_response("Hanya guru piket yang dapat mengakses endpoint ini.", 403)
    return None


@absensi_bp.post("/manual")
@inject_current_user
def create_manual(current_user):
    forbidden_response = _ensure_guru_piket(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_manual_absensi_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload absensi manual tidak valid.", 400, errors=errors)

    try:
        data, audit_log_id = create_manual_absensi(payload, current_user)
    except AbsensiServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(
        data=data | {"audit_log_id": audit_log_id},
        message="Absensi manual berhasil dicatat.",
        status_code=201,
    )


@absensi_bp.put("/<int:absensi_id>")
@inject_current_user
def update_absensi_route(current_user, absensi_id: int):
    forbidden_response = _ensure_guru_piket(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_absensi_update_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload update absensi tidak valid.", 400, errors=errors)

    try:
        data, audit_log_id = update_absensi(absensi_id, payload, current_user)
    except AbsensiServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(
        data=data | {"audit_log_id": audit_log_id},
        message="Absensi berhasil diperbarui.",
    )
