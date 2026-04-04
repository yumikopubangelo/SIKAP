import os

from dotenv import load_dotenv
from flask import Flask, jsonify

from .extensions import cors, db, jwt, migrate
from .routes import register_blueprints
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

    with app.app_context():
        from .models import load_models

        load_models()

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db, directory="migrations")
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
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
        }


def register_jwt_handlers() -> None:
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
