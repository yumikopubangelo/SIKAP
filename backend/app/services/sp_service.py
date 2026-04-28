from datetime import date

from flask import current_app
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Absensi, OrangTua, SesiSholat, Siswa, SuratPeringatan
from .email_service import EmailServiceError, send_gmail_email
from .notifikasi_service import create_notifikasi


def _serialize_surat_peringatan(sp: SuratPeringatan) -> dict:
    return {
        "id_sp": sp.id_sp,
        "id_siswa": sp.id_siswa,
        "sp_ke": sp.sp_ke,
        "jenis": sp.jenis,
        "tanggal": sp.tanggal.isoformat() if sp.tanggal else None,
        "status_kirim": sp.status_kirim,
        "alasan": sp.alasan,
        "id_pengirim": sp.id_pengirim,
        "created_at": sp.created_at.isoformat() if sp.created_at else None,
    }


def _get_thresholds() -> tuple[int, ...]:
    thresholds = tuple(current_app.config.get("SP_CONSECUTIVE_ALPHA_THRESHOLDS") or ())
    return thresholds or (3, 6, 9)


def _current_alpha_streak(student_id: int) -> tuple[int, date | None]:
    rows = (
        db.session.query(Absensi.status, SesiSholat.tanggal)
        .join(Absensi.sesi)
        .filter(Absensi.id_siswa == student_id)
        .order_by(SesiSholat.tanggal.desc(), Absensi.timestamp.desc(), Absensi.id_absensi.desc())
        .all()
    )

    streak = 0
    latest_date = rows[0].tanggal if rows else None
    for row in rows:
        if row.status != "alpha":
            break
        streak += 1
    return streak, latest_date


def _load_student(student_id: int) -> Siswa | None:
    return (
        Siswa.query.options(
            joinedload(Siswa.kelas),
            joinedload(Siswa.user),
            joinedload(Siswa.orangtua).joinedload(OrangTua.user),
        )
        .filter_by(id_siswa=student_id)
        .first()
    )


def _next_surat_peringatan_levels(student_id: int, streak: int) -> list[int]:
    existing_levels = {
        sp_ke
        for (sp_ke,) in db.session.query(SuratPeringatan.sp_ke)
        .filter(SuratPeringatan.id_siswa == student_id)
        .all()
    }

    levels: list[int] = []
    for index, threshold in enumerate(_get_thresholds(), start=1):
        if streak >= threshold and index not in existing_levels:
            levels.append(index)
    return levels


def _email_subject(sp: SuratPeringatan, student: Siswa) -> str:
    return f"{sp.jenis} SIKAP - {student.nama}"


def _email_body(sp: SuratPeringatan, student: Siswa, streak: int) -> str:
    class_name = student.kelas.nama_kelas if student.kelas else "-"
    return (
        "Yth. Orang Tua/Wali,\n\n"
        f"Sistem SIKAP mencatat bahwa {student.nama} (NISN: {student.nisn}) dari kelas {class_name} "
        f"telah mencapai {streak} alpha berturut-turut.\n\n"
        f"Surat peringatan yang diterbitkan: {sp.jenis}\n"
        f"Tanggal penerbitan: {sp.tanggal.isoformat() if sp.tanggal else '-'}\n"
        f"Alasan: {sp.alasan or '-'}\n\n"
        "Mohon lakukan tindak lanjut bersama pihak sekolah.\n\n"
        "Pesan ini dikirim otomatis oleh SIKAP."
    )


def issue_surat_peringatan_for_student(*, student_id: int, actor_id: int | None = None) -> list[dict]:
    if not current_app.config.get("SP_AUTO_ENABLED", True):
        return []

    streak, latest_date = _current_alpha_streak(student_id)
    if streak <= 0:
        return []

    levels = _next_surat_peringatan_levels(student_id, streak)
    if not levels:
        return []

    student = _load_student(student_id)
    if student is None:
        return []

    parent_user = student.orangtua.user if getattr(student, "orangtua", None) and student.orangtua.user else None
    created: list[SuratPeringatan] = []

    for level in levels:
        threshold = _get_thresholds()[level - 1]
        sp = SuratPeringatan(
            id_siswa=student.id_siswa,
            sp_ke=level,
            tanggal=latest_date or date.today(),
            jenis=f"SP{level}",
            status_kirim="diproses",
            id_pengirim=actor_id,
            alasan=(
                f"Siswa tercatat alpha {streak} kali berturut-turut. "
                f"Threshold {threshold} terpenuhi untuk penerbitan SP{level}."
            ),
        )
        db.session.add(sp)
        db.session.flush()

        if parent_user is not None:
            create_notifikasi(
                user_id=parent_user.id_user,
                judul=f"{sp.jenis} untuk {student.nama}",
                pesan=(
                    f"{student.nama} telah menerima {sp.jenis} karena mencapai {streak} alpha berturut-turut."
                ),
                tipe="peringatan",
            )
        created.append(sp)

    db.session.commit()

    if not current_app.config.get("SP_EMAIL_ENABLED", True):
        for sp in created:
            sp.status_kirim = "nonaktif"
        db.session.commit()
        return [_serialize_surat_peringatan(sp) for sp in created]

    if parent_user is None or not parent_user.email:
        for sp in created:
            sp.status_kirim = "tanpa_email"
        db.session.commit()
        return [_serialize_surat_peringatan(sp) for sp in created]

    for sp in created:
        try:
            send_gmail_email(
                recipient_email=parent_user.email,
                subject=_email_subject(sp, student),
                body=_email_body(sp, student, streak),
            )
        except EmailServiceError as exc:
            current_app.logger.warning(
                "Pengiriman email %s untuk siswa %s gagal: %s",
                sp.jenis,
                student.id_siswa,
                exc.message,
            )
            sp.status_kirim = "gagal"
        else:
            sp.status_kirim = "terkirim"

    db.session.commit()
    return [_serialize_surat_peringatan(sp) for sp in created]
