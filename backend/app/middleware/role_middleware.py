from functools import wraps

from flask_jwt_extended import get_jwt, jwt_required

from ..utils.response import error_response


def roles_required(*allowed_roles):
    def decorator(fn):
        @jwt_required()
        @wraps(fn)
        def decorated(*args, **kwargs):
            claims = get_jwt()
            current_role = claims.get("role")
            if current_role not in allowed_roles:
                return error_response("Anda tidak memiliki akses ke resource ini.", 403)
            return fn(*args, **kwargs)

        return decorated

    return decorator
