from flask import Flask

from .absensi import absensi_bp
from .auth import auth_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(absensi_bp)
