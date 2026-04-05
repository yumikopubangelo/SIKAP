from flask import Blueprint, request
from ..middleware.auth_middleware import inject_current_user
from ..utils.response import success_response, error_response
from ..services.users_service import (
    list_users, get_user_by_id, create_user, update_user, delete_user, UsersServiceError
)

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")

def _ensure_admin(current_user):
    if current_user.role not in ("admin", "kepsek"):
        return error_response("Hanya Admin/Kepsek yang dapat mengelola users.", 403)
    return None

@users_bp.get("")
@inject_current_user
def get_users_route(current_user):
    forbidden = _ensure_admin(current_user)
    if forbidden: return forbidden
    role = request.args.get("role")
    return success_response(data=list_users(role), message="Berhasil mengambil data users")

@users_bp.post("")
@inject_current_user
def create_user_route(current_user):
    forbidden = _ensure_admin(current_user)
    if forbidden: return forbidden
    
    payload = request.get_json(silent=True) or {}
    required_fields = ["username", "password", "full_name", "role"]
    for field in required_fields:
        if not payload.get(field):
            return error_response(f"Field {field} wajib diisi.", 400)
            
    try:
        data = create_user(payload)
        return success_response(data=data, message="User berhasil dibuat", status_code=201)
    except UsersServiceError as e:
        return error_response(e.message, e.status_code, errors=e.errors)

@users_bp.get("/<int:user_id>")
@inject_current_user
def get_user_route(current_user, user_id):
    forbidden = _ensure_admin(current_user)
    if forbidden: return forbidden
    
    try:
        data = get_user_by_id(user_id)
        return success_response(data=data)
    except UsersServiceError as e:
        return error_response(e.message, e.status_code)

@users_bp.put("/<int:user_id>")
@inject_current_user
def update_user_route(current_user, user_id):
    forbidden = _ensure_admin(current_user)
    if forbidden: return forbidden
    
    payload = request.get_json(silent=True) or {}
    try:
        data = update_user(user_id, payload)
        return success_response(data=data, message="User berhasil diperbarui")
    except UsersServiceError as e:
        return error_response(e.message, e.status_code)

@users_bp.delete("/<int:user_id>")
@inject_current_user
def delete_user_route(current_user, user_id):
    forbidden = _ensure_admin(current_user)
    if forbidden: return forbidden
    
    try:
        delete_user(user_id)
        return success_response(data=None, message="User berhasil dihapus")
    except UsersServiceError as e:
        return error_response(e.message, e.status_code)
