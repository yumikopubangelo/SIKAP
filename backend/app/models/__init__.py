from ..extensions import db


_MODEL_EXPORTS = {
    "Absensi": ".absensi",
    "StatusAbsensi": ".absensi",
    "Kelas": ".kelas",
    "Perangkat": ".perangkat",
    "Siswa": ".siswa",
    "User": ".user",
    "SesiSholat": ".waktu_sholat",
    "WaktuSholat": ".waktu_sholat",
}


def load_models() -> None:
    from .absensi import Absensi, StatusAbsensi
    from .kelas import Kelas
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
        }
    )

def __getattr__(name: str):
    module_name = _MODEL_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    load_models()
    return globals()[name]

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
    "load_models",
]
