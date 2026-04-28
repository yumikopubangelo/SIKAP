import os
from datetime import timedelta
from pathlib import Path


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def _get_csv(name: str, default: str = ""):
    value = os.getenv(name, default)
    if value.strip() == "*":
        return "*"
    return [item.strip() for item in value.split(",") if item.strip()]


def _get_int_list(name: str, default: str) -> tuple[int, ...]:
    raw_value = os.getenv(name, default)
    values: list[int] = []
    for item in raw_value.split(","):
        chunk = item.strip()
        if not chunk:
            continue
        try:
            number = int(chunk)
        except ValueError:
            continue
        if number > 0:
            values.append(number)
    return tuple(values)


def _parse_key_map(value: str) -> dict[str, str]:
    key_map: dict[str, str] = {}
    for item in (value or "").split(";"):
        chunk = item.strip()
        if not chunk or "=" not in chunk:
            continue
        key_id, secret = chunk.split("=", 1)
        key_id = key_id.strip()
        secret = secret.strip()
        if key_id and secret:
            key_map[key_id] = secret
    return key_map


def _build_jwt_secret_keys() -> dict[str, str]:
    active_kid = os.getenv("JWT_ACTIVE_KID", "v1")
    active_secret = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    secret_keys = {active_kid: active_secret}
    secret_keys.update(_parse_key_map(os.getenv("JWT_ADDITIONAL_SECRET_KEYS", "")))
    return secret_keys


def _build_database_uri() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("mysql://"):
            return database_url.replace("mysql://", "mysql+pymysql://", 1)
        return database_url

    db_user = os.getenv("DB_USER", "sikap_user")
    db_password = os.getenv("DB_PASSWORD", "sikap_pass_2025")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME", "sikap_db")
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_gmail_client_secret_path() -> str | None:
    repo_root = _repo_root()
    matches = sorted(repo_root.glob("client_secret_*.apps.googleusercontent.com.json"))
    if not matches:
        return None
    return str(matches[0])


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
    JWT_SECRET_KEYS = _build_jwt_secret_keys()
    JWT_ACTIVE_KID = os.getenv("JWT_ACTIVE_KID", "v1")
    JWT_LEGACY_KID = os.getenv("JWT_LEGACY_KID", JWT_ACTIVE_KID)
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }
    JSON_SORT_KEYS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=_get_int("JWT_ACCESS_TOKEN_HOURS", 12))
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_ALGORITHM = "HS256"
    CORS_ALLOWED_ORIGINS = _get_csv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:8081,http://127.0.0.1:8081,http://localhost:5173,http://127.0.0.1:5173",
    )
    RFID_REQUIRE_SIGNATURE = _get_bool("RFID_REQUIRE_SIGNATURE", False)
    RFID_SIGNATURE_TOLERANCE_SECONDS = _get_int("RFID_SIGNATURE_TOLERANCE_SECONDS", 120)
    RFID_PUBLIC_KEY_DIR = os.getenv("RFID_PUBLIC_KEY_DIR", "/app/keys/rfid_public")
    SECURITY_ENABLE_HSTS = _get_bool("SECURITY_ENABLE_HSTS", False)
    SP_AUTO_ENABLED = _get_bool("SP_AUTO_ENABLED", True)
    SP_CONSECUTIVE_ALPHA_THRESHOLDS = _get_int_list("SP_CONSECUTIVE_ALPHA_THRESHOLDS", "3,6,9")
    SP_EMAIL_ENABLED = _get_bool("SP_EMAIL_ENABLED", True)
    GMAIL_CLIENT_SECRET_PATH = os.getenv(
        "GMAIL_CLIENT_SECRET_PATH",
        _default_gmail_client_secret_path() or "",
    ) or None
    GMAIL_TOKEN_PATH = os.getenv(
        "GMAIL_TOKEN_PATH",
        str(Path(__file__).resolve().parent / "instance" / "gmail_token.json"),
    )
    GMAIL_OAUTH_REDIRECT_URI = os.getenv(
        "GMAIL_OAUTH_REDIRECT_URI",
        "http://127.0.0.1:8765/oauth2callback",
    )
    GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL") or None


class DevelopmentConfig(Config):
    DEBUG = _get_bool("FLASK_DEBUG", True)


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
