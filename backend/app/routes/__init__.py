from flask import Flask

from .absensi import absensi_bp
from .auth import auth_bp
from .dashboard import dashboard_bp
from .laporan import laporan_bp
from .notifikasi import notifikasi_bp
from .rekapitulasi import rekapitulasi_bp
from .users import users_bp
from .waktu_sholat import waktu_sholat_bp
from .izin import izin_bp
from .sengketa import sengketa_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(absensi_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(laporan_bp)
    app.register_blueprint(notifikasi_bp)
    app.register_blueprint(rekapitulasi_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(waktu_sholat_bp)
    app.register_blueprint(izin_bp)
    app.register_blueprint(sengketa_bp)
