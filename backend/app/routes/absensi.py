from flask import Blueprint, jsonify, request

from ..middleware.auth_middleware import inject_current_user
from ..services.absensi_service import (
    AbsensiServiceError,
    create_rfid_absensi,
    list_absensi,
    create_manual_absensi,
    update_absensi,
)
from ..services.rfid_capture_service import (
    RfidCaptureServiceError,
    has_active_capture_session,
    record_capture_tap,
)
from ..utils.response import error_response, success_response
from ..utils.validators import (
    validate_absensi_list_params,
    validate_absensi_update_payload,
    validate_manual_absensi_payload,
    validate_rfid_absensi_payload,
)


absensi_bp = Blueprint("absensi", __name__, url_prefix="/api/v1/absensi")


def _ensure_guru_piket(current_user):
    if current_user.role != "guru_piket":
        return error_response("Hanya guru piket yang dapat mengakses endpoint ini.", 403)
    return None


@absensi_bp.post("")
def create_rfid():
    payload, errors = validate_rfid_absensi_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload absensi RFID tidak valid.", 400, errors=errors)

    if has_active_capture_session():
        try:
            data = record_capture_tap(payload, request.headers)
        except RfidCaptureServiceError as exc:
            if exc.status_code != 409:
                return error_response(exc.message, exc.status_code, errors=exc.errors)
        else:
            return success_response(
                data=data,
                message="Tap RFID dialihkan ke mode konfirmasi UID kartu.",
                status_code=201,
            )

    try:
        data, audit_log_id = create_rfid_absensi(
            payload,
            request.headers,
        )
    except AbsensiServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(
        data=data | {"audit_log_id": audit_log_id},
        message="Absensi RFID berhasil dicatat.",
        status_code=201,
    )


@absensi_bp.get("")
@inject_current_user
def list_absensi_route(current_user):
    params, errors = validate_absensi_list_params(request.args)
    if errors:
        return error_response("Parameter list absensi tidak valid.", 400, errors=errors)

    try:
        data, pagination = list_absensi(params, current_user)
    except AbsensiServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return (
        jsonify(
            {
                "success": True,
                "message": "Daftar absensi berhasil diambil.",
                "data": data,
                "pagination": pagination,
            }
        ),
        200,
    )


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
