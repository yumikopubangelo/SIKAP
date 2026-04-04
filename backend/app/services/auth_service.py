from flask_jwt_extended import create_access_token, decode_token

from ..extensions import db, token_blocklist
from ..models import User


def authenticate_user(username: str, password: str):
    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()
    if user is None or not user.check_password(password):
        return None
    return user


def build_access_token(user: User) -> str:
    additional_claims = {
        "role": user.role,
        "username": user.username,
        "full_name": user.full_name,
    }
    return create_access_token(
        identity=str(user.id_user),
        additional_claims=additional_claims,
    )


def build_login_payload(user: User) -> dict:
    access_token = build_access_token(user)
    decoded = decode_token(access_token)
    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_at": decoded["exp"],
        "user": user.to_dict(),
    }


def revoke_token(jti: str) -> None:
    token_blocklist.add(jti)


def is_token_revoked(jwt_payload: dict) -> bool:
    jti = jwt_payload.get("jti")
    return jti in token_blocklist


def get_user_by_identity(identity: str | int):
    return db.session.get(User, int(identity))
