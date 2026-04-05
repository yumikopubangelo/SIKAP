from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.kelas_service import list_kelas, create_kelas, update_kelas, delete_kelas, KelasServiceError

kelas_bp = Blueprint("kelas", __name__, url_prefix="/api/v1/kelas")

@kelas_bp.get("")
@inject_current_user
def get_kelas(current_user):
    return success_response(data=list_kelas(), message="Data kelas")

@kelas_bp.post("")
@inject_current_user
def post_kelas(current_user):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        data = create_kelas(request.get_json(silent=True) or {})
        return success_response(data=data, status_code=201)
    except KelasServiceError as e: return error_response(e.message, getattr(e, "status_code", 400))

@kelas_bp.put("/<int:id_kelas>")
@inject_current_user
def put_kelas(current_user, id_kelas):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        data = update_kelas(id_kelas, request.get_json(silent=True) or {})
        return success_response(data=data)
    except KelasServiceError as e: return error_response(e.message, getattr(e, "status_code", 400))

@kelas_bp.delete("/<int:id_kelas>")
@inject_current_user
def del_kelas(current_user, id_kelas):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        delete_kelas(id_kelas)
        return success_response(data=None)
    except KelasServiceError as e: return error_response(e.message, getattr(e, "status_code", 400))
