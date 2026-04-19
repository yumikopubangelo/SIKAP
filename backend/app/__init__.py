import os

from dotenv import load_dotenv
from flask import Flask, current_app, jsonify, request

from .extensions import cors, db, jwt, migrate
from .routes import register_blueprints
from .routes.metrics import refresh_custom_metrics
from .services.auth_service import is_token_revoked
from .utils.response import error_response


load_dotenv()

from config import DevelopmentConfig, _build_database_uri, config_by_name


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    selected_config = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_by_name.get(selected_config, DevelopmentConfig))
    if selected_config == "testing":
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = _build_database_uri()

    register_extensions(app)
    register_routes(app)
    register_shell_context(app)
    register_security_headers(app)
    register_prometheus(app)

    with app.app_context():
        from .models import load_models

        load_models()

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ALLOWED_ORIGINS"]}},
    )
    register_jwt_handlers()


def register_routes(app: Flask) -> None:
    register_blueprints(app)

    @app.get("/")
    def index():
        return jsonify(
            {
                "app": "SIKAP Backend",
                "status": "ok",
                "version": "BE-01",
            }
        )

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "healthy",
                "database_uri": app.config["SQLALCHEMY_DATABASE_URI"].split("@")[-1],
            }
        )


def register_shell_context(app: Flask) -> None:
    @app.shell_context_processor
    def shell_context():
        from .models import (
            Absensi,
            AuditLog,
            Kelas,
            Perangkat,
            SesiSholat,
            Siswa,
            StatusAbsensi,
            User,
            WaktuSholat,
        )

        return {
            "db": db,
            "User": User,
            "Kelas": Kelas,
            "Siswa": Siswa,
            "WaktuSholat": WaktuSholat,
            "SesiSholat": SesiSholat,
            "StatusAbsensi": StatusAbsensi,
            "Perangkat": Perangkat,
            "Absensi": Absensi,
            "AuditLog": AuditLog,
        }


def register_jwt_handlers() -> None:
    @jwt.additional_headers_loader
    def additional_headers_callback(_identity):
        return {"kid": current_app.config["JWT_ACTIVE_KID"]}

    @jwt.encode_key_loader
    def encode_key_callback(_identity):
        key_id = current_app.config["JWT_ACTIVE_KID"]
        return current_app.config["JWT_SECRET_KEYS"][key_id]

    @jwt.decode_key_loader
    def decode_key_callback(jwt_header, _jwt_payload):
        key_id = jwt_header.get("kid") or current_app.config["JWT_LEGACY_KID"]
        key_ring = current_app.config["JWT_SECRET_KEYS"]
        return key_ring.get(key_id, key_ring[current_app.config["JWT_ACTIVE_KID"]])

    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(_jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload)

    @jwt.invalid_token_loader
    def invalid_token_callback(message):
        return error_response(f"Token tidak valid: {message}", 401)

    @jwt.unauthorized_loader
    def unauthorized_callback(message):
        return error_response(f"Akses ditolak: {message}", 401)

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return error_response("Token sudah kedaluwarsa.", 401)

    @jwt.revoked_token_loader
    def revoked_token_callback(_jwt_header, _jwt_payload):
        return error_response("Token sudah logout dan tidak bisa dipakai lagi.", 401)


def register_security_headers(app: Flask) -> None:
    @app.after_request
    def apply_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        if app.config.get("SECURITY_ENABLE_HSTS"):
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return response


def register_prometheus(app: Flask) -> None:
    """Instrument Flask with Prometheus metrics + custom SIKAP gauges."""
    try:
        from prometheus_flask_exporter import NO_PREFIX, PrometheusMetrics

        def handler(req):
            return req.url_rule.rule if req.url_rule else "none"

        PrometheusMetrics(
            app,
            path="/metrics",
            defaults_prefix=NO_PREFIX,
            group_by=handler,
            excluded_paths=[r"^/health$"],
        )

        @app.before_request
        def _refresh_metrics_on_scrape():
            if request.path == "/metrics":
                refresh_custom_metrics(app)

    except Exception:
        # Jangan crash app jika prometheus belum terinstall di environment lokal.
        app.logger.warning(
            "prometheus-flask-exporter tidak tersedia. "
            "Endpoint /metrics tidak aktif."
        )
