def validate_login_payload(payload):
    payload = payload or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    errors = {}
    if not username:
        errors["username"] = "Username wajib diisi."
    if not password:
        errors["password"] = "Password wajib diisi."

    if errors:
        return None, errors

    return {"username": username, "password": password}, None
