from ..extensions import db


def load_models() -> None:
    from .absensi import Absensi, StatusAbsensi
    from .audit_log import AuditLog
    from .guru import Guru
    from .izin_pengajuan import IzinPengajuan
    from .jadwal_piket import JadwalPiket
    from .kelas import Kelas
    from .laporan import Laporan
    from .notifikasi import Notifikasi
    from .orangtua import OrangTua
    from .password_reset_token import PasswordResetToken
    from .perangkat import Perangkat
    from .sekolah import SekolahInfo
    from .sengketa_absensi import SengketaAbsensi
    from .siswa import Siswa
    from .surat_peringatan import SuratPeringatan
    from .user import User
    from .waktu_sholat import SesiSholat, WaktuSholat

    globals().update(
        {
            "Absensi": Absensi,
            "AuditLog": AuditLog,
            "Guru": Guru,
            "IzinPengajuan": IzinPengajuan,
            "JadwalPiket": JadwalPiket,
            "Kelas": Kelas,
            "Laporan": Laporan,
            "Notifikasi": Notifikasi,
            "OrangTua": OrangTua,
            "PasswordResetToken": PasswordResetToken,
            "Perangkat": Perangkat,
            "SekolahInfo": SekolahInfo,
            "SengketaAbsensi": SengketaAbsensi,
            "SesiSholat": SesiSholat,
            "Siswa": Siswa,
            "StatusAbsensi": StatusAbsensi,
            "SuratPeringatan": SuratPeringatan,
            "User": User,
            "WaktuSholat": WaktuSholat,
        }
    )


load_models()

__all__ = [
    "db",
    "Absensi",
    "AuditLog",
    "Guru",
    "IzinPengajuan",
    "JadwalPiket",
    "Kelas",
    "Laporan",
    "Notifikasi",
    "OrangTua",
    "PasswordResetToken",
    "Perangkat",
    "SekolahInfo",
    "SengketaAbsensi",
    "SesiSholat",
    "Siswa",
    "StatusAbsensi",
    "SuratPeringatan",
    "User",
    "WaktuSholat",
    "load_models",
]
