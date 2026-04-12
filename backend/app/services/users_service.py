from typing import List, Optional, Tuple, Dict
from ..models import db, User
import logging

logger = logging.getLogger(__name__)

class UsersServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400, errors: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors

def list_users(role: Optional[str] = None) -> List[dict]:
    query = User.query
    if role:
        query = query.filter(User.role == role)
    users = query.all()
    return [user.to_dict() for user in users]

def get_user_by_id(user_id: int) -> dict:
    user = User.query.get(user_id)
    if not user:
        raise UsersServiceError("User tidak ditemukan", 404)
    return user.to_dict()

def create_user(payload: dict) -> dict:
    username = payload.get("username")
    email = payload.get("email")
    
    if User.query.filter_by(username=username).first():
        raise UsersServiceError("Username sudah terdaftar", 400)
    
    if email and User.query.filter_by(email=email).first():
        raise UsersServiceError("Email sudah terdaftar", 400)

    user = User(
        username=username,
        full_name=payload.get("full_name"),
        email=email,
        no_telp=payload.get("no_telp"),
        role=payload.get("role")
    )
    user.set_password(payload.get("password"))
    
    db.session.add(user)
    try:
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create user: {str(e)}")
        raise UsersServiceError("Gagal membuat user karena kesalahan sistem.", 500)

def update_user(user_id: int, payload: dict) -> dict:
    user = User.query.get(user_id)
    if not user:
        raise UsersServiceError("User tidak ditemukan", 404)
    
    if "full_name" in payload:
        user.full_name = payload["full_name"]
    if "email" in payload:
        user.email = payload["email"]
    if "no_telp" in payload:
        user.no_telp = payload["no_telp"]
    if "role" in payload:
        user.role = payload["role"]
    if "password" in payload and payload["password"]:
        user.set_password(payload["password"])
        
    try:
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update user: {str(e)}")
        raise UsersServiceError("Gagal memperbarui user.", 500)

def delete_user(user_id: int) -> None:
    user = User.query.get(user_id)
    if not user:
        raise UsersServiceError("User tidak ditemukan", 404)
    
    db.session.delete(user)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete user: {str(e)}")
        raise UsersServiceError("Gagal menghapus user. Data mungkin memiliki relasi yang tidak bisa dihapus.", 500)
