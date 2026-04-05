from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.waktu_sholat_service import list_waktu_sholat, update_waktu_sholat, WaktuSholatServiceError

waktu_sholat_bp = Blueprint("waktu_sholat", __name__, url_prefix="/api/v1/waktu-sholat")

@waktu_sholat_bp.get("")
def get_waktus():
    data = list_waktu_sholat()
    return success_response(data=data, message="Jadwal sholat berhasil dimuat")

@waktu_sholat_bp.put("/<int:waktu_id>")
@inject_current_user
def update_waktu(current_user, waktu_id):
    if current_user.role != "admin":
        return error_response("Hanya Admin yang dapat mengatur jadwal.", 403)
        
    payload = request.get_json(silent=True) or {}
    try:
        data = update_waktu_sholat(waktu_id, payload)
        return success_response(data=data, message="Jadwal sholat berhasil disimpan")
    except WaktuSholatServiceError as e:
        return error_response(e.message, e.status_code)
