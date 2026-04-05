from flask import Flask

from .absensi import absensi_bp
from .auth import auth_bp
from .dashboard import dashboard_bp
from .laporan import laporan_bp
from .notifikasi import notifikasi_bp
from .rekapitulasi import rekapitulasi_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(absensi_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(laporan_bp)
    app.register_blueprint(notifikasi_bp)
    app.register_blueprint(rekapitulasi_bp)
