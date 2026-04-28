from flask import Flask

from .absensi import absensi_bp
from .auth import auth_bp
from .dashboard import dashboard_bp
from .jadwal_piket import jadwal_piket_bp
from .laporan import laporan_bp
from .kelas import kelas_bp
from .notifikasi import notifikasi_bp
from .rekapitulasi import rekapitulasi_bp
from .rfid import rfid_bp
from .sekolah import school_bp
from .users import users_bp
from .waktu_sholat import waktu_sholat_bp
from .izin import izin_bp
from .sengketa import sengketa_bp
from .perangkat import perangkat_bp
from .siswa import siswa_bp
from .surat_peringatan import surat_peringatan_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(absensi_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(laporan_bp)
    app.register_blueprint(notifikasi_bp)
    app.register_blueprint(rekapitulasi_bp)
    app.register_blueprint(rfid_bp)
    app.register_blueprint(school_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(waktu_sholat_bp)
    app.register_blueprint(izin_bp)
    app.register_blueprint(sengketa_bp)
    app.register_blueprint(perangkat_bp)
    app.register_blueprint(kelas_bp)
    app.register_blueprint(siswa_bp)
    app.register_blueprint(surat_peringatan_bp)
    app.register_blueprint(jadwal_piket_bp)
