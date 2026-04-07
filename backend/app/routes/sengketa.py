from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.sengketa_service import (
    list_sengketa, create_sengketa, resolve_sengketa, SengketaServiceError
)

sengketa_bp = Blueprint("sengketa", __name__, url_prefix="/api/v1/sengketa")

@sengketa_bp.get("")
@inject_current_user
def get_sengketa_route(current_user):
    status = request.args.get("status")
    # TBD: Filtering by role (siswa views their own) but for now just general list
    data = list_sengketa(status)
    return success_response(data=data, message="Berhasil mengambil data sengketa")

@sengketa_bp.post("")
@inject_current_user
def create_sengketa_route(current_user):
    payload = request.get_json(silent=True) or {}
    try:
        data = create_sengketa(payload, current_user)
        return success_response(data=data, message="Sengketa berhasil diajukan", status_code=201)
    except SengketaServiceError as e:
        return error_response(e.message, e.status_code)

@sengketa_bp.put("/<int:sengketa_id>/resolve")
@inject_current_user
def resolve_sengketa_route(current_user, sengketa_id):
    payload = request.get_json(silent=True) or {}
    action = payload.get("action")
    catatan = payload.get("catatan", "")
    
    if not action:
        return error_response("Field action (approve/reject) wajib diisi.", 400)
        
    try:
        data = resolve_sengketa(sengketa_id, action, catatan, current_user)
        return success_response(data=data, message=f"Sengketa berhasil {action}")
    except SengketaServiceError as e:
        return error_response(e.message, e.status_code)
