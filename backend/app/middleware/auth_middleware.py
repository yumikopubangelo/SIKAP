from functools import wraps

from flask_jwt_extended import get_jwt_identity, jwt_required

from ..services.auth_service import get_user_by_identity
from ..utils.response import error_response


def auth_required(fn):
    @jwt_required()
    @wraps(fn)
    def decorated(*args, **kwargs):
        return fn(*args, **kwargs)

    return decorated


def get_current_user():
    identity = get_jwt_identity()
    if identity is None:
        return None
    return get_user_by_identity(identity)


def inject_current_user(fn):
    @jwt_required()
    @wraps(fn)
    def decorated(*args, **kwargs):
        current_user = get_current_user()
        if current_user is None:
            return error_response("User tidak ditemukan.", 404)
        return fn(current_user=current_user, *args, **kwargs)

    return decorated
