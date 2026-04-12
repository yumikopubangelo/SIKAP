from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.izin_service import (
    list_izin, create_izin, resolve_izin, IzinServiceError
)

izin_bp = Blueprint("izin", __name__, url_prefix="/api/v1/izin")

@izin_bp.get("")
@inject_current_user
def get_izin_route(current_user):
    status = request.args.get("status")
    data = list_izin(status)
    return success_response(data=data, message="Berhasil mengambil data izin")

@izin_bp.post("")
@inject_current_user
def create_izin_route(current_user):
    payload = request.get_json(silent=True) or {}
    try:
        data = create_izin(payload, current_user)
        return success_response(data=data, message="Pengajuan izin berhasil dibuat", status_code=201)
    except IzinServiceError as e:
        return error_response(e.message, e.status_code)

@izin_bp.put("/<int:izin_id>/approve")
@inject_current_user
def approve_izin_route(current_user, izin_id):
    payload = request.get_json(silent=True) or {}
    action = payload.get("action")
    catatan = payload.get("catatan", "")
    
    if not action:
        return error_response("Field action (approve/reject) wajib diisi.", 400)
        
    try:
        data = resolve_izin(izin_id, action, catatan, current_user)
        return success_response(data=data, message=f"Pengajuan izin berhasil di-{action}")
    except IzinServiceError as e:
        return error_response(e.message, e.status_code)
