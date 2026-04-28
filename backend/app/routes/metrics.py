"""
Prometheus custom metrics untuk SIKAP.
Endpoint /metrics di-handle oleh prometheus-flask-exporter.
Modul ini mendefinisikan business metrics kustom yang di-update secara periodik.
"""

from prometheus_client import Gauge

from ..extensions import db

# ---------------------------------------------------------------------------
# Custom Gauges
# ---------------------------------------------------------------------------
sikap_total_absensi = Gauge(
    "sikap_total_absensi",
    "Total record absensi dalam database",
)

sikap_active_sessions = Gauge(
    "sikap_active_sessions",
    "Jumlah sesi sholat yang sedang aktif",
)

sikap_total_users = Gauge(
    "sikap_total_users",
    "Jumlah user terdaftar per role",
    ["role"],
)

sikap_devices_online = Gauge(
    "sikap_devices_online",
    "Jumlah perangkat IoT yang berstatus online",
)

sikap_total_siswa = Gauge(
    "sikap_total_siswa",
    "Jumlah siswa terdaftar",
)

sikap_total_kelas = Gauge(
    "sikap_total_kelas",
    "Jumlah kelas terdaftar",
)

sikap_total_notifikasi_unread = Gauge(
    "sikap_total_notifikasi_unread",
    "Total notifikasi yang belum dibaca",
)

sikap_total_surat_peringatan = Gauge(
    "sikap_total_surat_peringatan",
    "Total surat peringatan yang diterbitkan",
    ["jenis"],
)


def refresh_custom_metrics(app):
    """
    Membaca data terkini dari database dan mengupdate semua custom gauge.
    Dipanggil sebelum setiap scrape oleh Prometheus melalui
    callback `before_request` pada endpoint /metrics, atau secara periodik.
    """
    with app.app_context():
        try:
            from ..models.absensi import Absensi
            from ..models.kelas import Kelas
            from ..models.notifikasi import Notifikasi
            from ..models.perangkat import Perangkat
            from ..models.siswa import Siswa
            from ..models.surat_peringatan import SuratPeringatan
            from ..models.user import User
            from ..models.waktu_sholat import SesiSholat

            # Total absensi
            sikap_total_absensi.set(db.session.query(Absensi).count())

            # Sesi aktif
            sikap_active_sessions.set(
                db.session.query(SesiSholat)
                .filter(SesiSholat.status == "aktif")
                .count()
            )

            # Users per role
            roles = ["admin", "kepsek", "wali_kelas", "guru_piket", "siswa", "orangtua"]
            for role in roles:
                count = db.session.query(User).filter(User.role == role).count()
                sikap_total_users.labels(role=role).set(count)

            # Devices online
            sikap_devices_online.set(
                db.session.query(Perangkat)
                .filter(Perangkat.status == "online")
                .count()
            )

            # Total siswa
            sikap_total_siswa.set(db.session.query(Siswa).count())

            # Total kelas
            sikap_total_kelas.set(db.session.query(Kelas).count())

            # Notifikasi unread
            sikap_total_notifikasi_unread.set(
                db.session.query(Notifikasi)
                .filter(Notifikasi.is_read == False)  # noqa: E712
                .count()
            )

            # Surat peringatan per jenis
            for jenis in ["SP1", "SP2", "SP3"]:
                count = (
                    db.session.query(SuratPeringatan)
                    .filter(SuratPeringatan.jenis == jenis)
                    .count()
                )
                sikap_total_surat_peringatan.labels(jenis=jenis).set(count)

        except Exception:
            # Jangan crash endpoint /metrics jika ada query error.
            pass
