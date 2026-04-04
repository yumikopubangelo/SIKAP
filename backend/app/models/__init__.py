from ..extensions import db


def load_models() -> None:
    from .absensi import Absensi, StatusAbsensi
    from .audit_log import AuditLog
    from .kelas import Kelas
    from .laporan import Laporan
    from .perangkat import Perangkat
    from .siswa import Siswa
    from .user import User
    from .waktu_sholat import SesiSholat, WaktuSholat

    globals().update(
        {
            "User": User,
            "Kelas": Kelas,
            "Siswa": Siswa,
            "WaktuSholat": WaktuSholat,
            "SesiSholat": SesiSholat,
            "StatusAbsensi": StatusAbsensi,
            "Perangkat": Perangkat,
            "Absensi": Absensi,
            "AuditLog": AuditLog,
            "Laporan": Laporan,
        }
    )


load_models()

__all__ = [
    "db",
    "User",
    "Kelas",
    "Siswa",
    "WaktuSholat",
    "SesiSholat",
    "StatusAbsensi",
    "Perangkat",
    "Absensi",
    "AuditLog",
    "Laporan",
    "load_models",
]
