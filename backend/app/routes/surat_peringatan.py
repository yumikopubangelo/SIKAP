from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.sp_service import list_sp, generate_auto_sp, SPServiceError

sp_bp = Blueprint("surat_peringatan", __name__, url_prefix="/api/v1/surat-peringatan")

@sp_bp.get("")
@inject_current_user
def get_sp(current_user):
    return success_response(data=list_sp(), message="Data Surat Peringatan")

@sp_bp.post("/generate")
@inject_current_user
def post_generate_sp(current_user):
    if current_user.role not in ("admin", "kepsek"):
        return error_response("Unauthorized", 403)
    try:
        data = generate_auto_sp(current_user)
        return success_response(data=data, message="Automasi SP berhasil dieksekusi", status_code=201)
    except SPServiceError as e: 
        return error_response(e.message, getattr(e, "status_code", 400))
