from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.siswa_service import list_siswa, create_siswa, update_siswa, delete_siswa, SiswaServiceError

siswa_bp = Blueprint("siswa", __name__, url_prefix="/api/v1/siswa")

@siswa_bp.get("")
@inject_current_user
def get_siswa(current_user):
    id_k = request.args.get("id_kelas", type=int)
    return success_response(data=list_siswa(id_k), message="Data Siswa")

@siswa_bp.post("")
@inject_current_user
def post_siswa(current_user):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        data = create_siswa(request.get_json(silent=True) or {})
        return success_response(data=data, status_code=201)
    except SiswaServiceError as e: return error_response(e.message, getattr(e, "status_code", 400))

@siswa_bp.put("/<int:id_siswa>")
@inject_current_user
def put_siswa(current_user, id_siswa):
    if current_user.role not in ("admin", "wali_kelas", "kepsek"): return error_response("Unauthorized", 403)
    try:
        data = update_siswa(id_siswa, request.get_json(silent=True) or {})
        return success_response(data=data)
    except SiswaServiceError as e: return error_response(e.message, getattr(e, "status_code", 400))

@siswa_bp.delete("/<int:id_siswa>")
@inject_current_user
def del_siswa(current_user, id_siswa):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        delete_siswa(id_siswa)
        return success_response(data=None)
    except SiswaServiceError as e: return error_response(e.message, getattr(e, "status_code", 400))
