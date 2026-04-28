import argparse
import os
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed 3 alpha berturut-turut untuk menguji SP otomatis dan email orang tua.",
    )
    parser.add_argument(
        "--recipient-email",
        default="pgaurdian45@gmail.com",
        help="Email orang tua penerima pengujian.",
    )
    return parser.parse_args()


def ensure_statuses(db, StatusAbsensi) -> None:
    defaults = {
        "tepat_waktu": "Tepat Waktu",
        "terlambat": "Terlambat",
        "alpha": "Alpha",
        "haid": "Haid",
        "izin": "Izin",
        "sakit": "Sakit",
    }
    for code, label in defaults.items():
        if not StatusAbsensi.query.filter_by(kode=code).first():
            db.session.add(StatusAbsensi(kode=code, deskripsi=label))
    db.session.commit()


def main() -> int:
    args = parse_args()

    os.environ.setdefault("SP_AUTO_ENABLED", "1")
    os.environ.setdefault("SP_CONSECUTIVE_ALPHA_THRESHOLDS", "3,6,9")
    os.environ.setdefault("SP_EMAIL_ENABLED", "1")
    os.environ.setdefault("GMAIL_CLIENT_SECRET_PATH", str(_detect_client_secret()))
    os.environ.setdefault("GMAIL_TOKEN_PATH", str(BACKEND_DIR / "instance" / "gmail_token.json"))
    os.environ.setdefault("GMAIL_OAUTH_REDIRECT_URI", "http://127.0.0.1:8765/oauth2callback")

    from app import create_app
    from app.extensions import db
    from app.models import Kelas, OrangTua, Siswa, StatusAbsensi, User, WaktuSholat
    from app.services.absensi_service import create_manual_absensi

    app = create_app("development")

    with app.app_context():
        ensure_statuses(db, StatusAbsensi)

        unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S")

        guru = User(
            username=f"guru_sp_test_{unique_suffix}",
            full_name="Guru Piket SP Test",
            email=f"guru.sp.test.{unique_suffix}@sikap.local",
            role="guru_piket",
        )
        guru.set_password("guru12345")
        orangtua = User(
            username=f"ortu_sp_test_{unique_suffix}",
            full_name="Orang Tua SP Test",
            email=args.recipient_email,
            role="orangtua",
        )
        orangtua.set_password("orangtua123")
        siswa_user = User(
            username=f"siswa_sp_test_{unique_suffix}",
            full_name="Siswa SP Test",
            email=f"siswa.sp.test.{unique_suffix}@sikap.local",
            role="siswa",
        )
        siswa_user.set_password("siswa12345")
        db.session.add_all([guru, orangtua, siswa_user])
        db.session.flush()

        kelas = Kelas(
            nama_kelas=f"XI-SP-{unique_suffix[-2:]}",
            tingkat="XI",
            jurusan="RPL",
            tahun_ajaran="2025/2026",
        )
        db.session.add(kelas)
        db.session.flush()

        siswa = Siswa(
            id_user=siswa_user.id_user,
            nisn=f"99{unique_suffix}",
            nama="Siswa Pengujian SP",
            id_card=f"TEST-SP-{unique_suffix}",
            id_kelas=kelas.id_kelas,
        )
        db.session.add(siswa)
        db.session.flush()

        relasi_ortu = OrangTua(
            id_user=orangtua.id_user,
            id_siswa=siswa.id_siswa,
        )
        waktu_sholat = WaktuSholat.query.filter_by(nama_sholat="Dzuhur").first()
        if waktu_sholat is None:
            waktu_sholat = WaktuSholat(
                nama_sholat="Dzuhur",
                waktu_adzan=time(12, 0, 0),
                waktu_iqamah=time(12, 10, 0),
                waktu_selesai=time(12, 30, 0),
            )
            db.session.add(waktu_sholat)

        db.session.add(relasi_ortu)
        db.session.commit()

        created_sp = []
        for day_offset in range(2, -1, -1):
            target_date = date.today() - timedelta(days=day_offset)
            payload = {
                "siswa_id": siswa.id_siswa,
                "tanggal": target_date,
                "waktu_sholat": "dzuhur",
                "status": "alpha",
                "keterangan": f"Testing alpha otomatis hari ke-{3 - day_offset}.",
            }
            data, _audit_log_id = create_manual_absensi(payload, guru)
            created_sp = data.get("surat_peringatan_baru", []) or created_sp
            print(
                f"Alpha tersimpan untuk {target_date.isoformat()} | "
                f"SP baru: {len(data.get('surat_peringatan_baru', []))}"
            )

        print("")
        print("Pengujian selesai.")
        print(f"Email tujuan: {args.recipient_email}")
        if created_sp:
            print("SP yang dibuat:")
            for sp in created_sp:
                print(
                    f"- {sp['jenis']} | status_kirim={sp['status_kirim']} | tanggal={sp['tanggal']}"
                )
        else:
            print("Belum ada SP baru yang terbentuk.")

    return 0


def _detect_client_secret() -> Path:
    matches = sorted(ROOT_DIR.glob("client_secret_*.apps.googleusercontent.com.json"))
    if not matches:
        raise FileNotFoundError("File client secret Gmail tidak ditemukan di root project.")
    return matches[0]


if __name__ == "__main__":
    raise SystemExit(main())
