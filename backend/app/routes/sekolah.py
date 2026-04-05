from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.sekolah_service import get_sekolah_info, update_sekolah_info, SekolahServiceError

sekolah_bp = Blueprint("sekolah", __name__, url_prefix="/api/v1/sekolah")

@sekolah_bp.get("")
def get_sekolah():
    data = get_sekolah_info()
    return success_response(data=data, message="Data profile sekolah")

@sekolah_bp.put("")
@inject_current_user
def update_sekolah(current_user):
    if current_user.role not in ("admin", "kepsek"):
        return error_response("Hanya Admin/Kepsek yang dapat mengedit profil sekolah.", 403)
        
    payload = request.get_json(silent=True) or {}
    try:
        data = update_sekolah_info(payload)
        return success_response(data=data, message="Profil sekolah berhasil diupdate")
    except SekolahServiceError as e:
        return error_response(e.message, e.status_code)
