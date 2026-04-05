from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.perangkat_service import list_perangkat, create_perangkat, update_perangkat, delete_perangkat, PerangkatServiceError

perangkat_bp = Blueprint("perangkat", __name__, url_prefix="/api/v1/perangkat")

@perangkat_bp.get("")
@inject_current_user
def get_perangkat(current_user):
    if current_user.role != "admin" and current_user.role != "kepsek": 
        return error_response("Unauthorized", 403)
    return success_response(data=list_perangkat(), message="Data perangkat")

@perangkat_bp.post("")
@inject_current_user
def post_perangkat(current_user):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        data = create_perangkat(request.get_json(silent=True) or {})
        return success_response(data=data, status_code=201)
    except PerangkatServiceError as e: 
        return error_response(e.message, getattr(e, "status_code", 400))

@perangkat_bp.put("/<string:device_id>")
@inject_current_user
def put_perangkat(current_user, device_id):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        data = update_perangkat(device_id, request.get_json(silent=True) or {})
        return success_response(data=data)
    except PerangkatServiceError as e: 
        return error_response(e.message, getattr(e, "status_code", 400))

@perangkat_bp.delete("/<string:device_id>")
@inject_current_user
def del_perangkat(current_user, device_id):
    if current_user.role != "admin": return error_response("Unauthorized", 403)
    try:
        delete_perangkat(device_id)
        return success_response(data=None)
    except PerangkatServiceError as e: 
        return error_response(e.message, getattr(e, "status_code", 400))
