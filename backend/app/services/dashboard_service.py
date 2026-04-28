from datetime import date, datetime, timedelta

from sqlalchemy import case, distinct, func
from sqlalchemy.orm import joinedload

from ..models import Absensi, Kelas, Perangkat, SesiSholat, Siswa, User, IzinPengajuan, SengketaAbsensi


STATUS_CHART_ORDER = (
    "tepat_waktu",
    "terlambat",
    "izin",
    "sakit",
    "alpha",
    "haid",
)

STATUS_CHART_LABELS = {
    "tepat_waktu": "Tepat Waktu",
    "terlambat": "Terlambat",
    "izin": "Izin",
    "sakit": "Sakit",
    "alpha": "Alpha",
    "haid": "Haid",
}


def _today() -> date:
    return date.today()


def _month_start(day: date) -> date:
    return day.replace(day=1)


def _recent_absensi(limit: int = 10):
    return (
        Absensi.query.options(
            joinedload(Absensi.siswa).joinedload(Siswa.kelas),
            joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat),
            joinedload(Absensi.perangkat),
        )
        .order_by(Absensi.timestamp.desc())
        .limit(limit)
        .all()
    )


def _serialize_absensi_row(absensi: Absensi) -> dict:
    kelas = absensi.siswa.kelas.nama_kelas if absensi.siswa and absensi.siswa.kelas else None
    waktu_sholat = (
        absensi.sesi.waktu_sholat.nama_sholat
        if absensi.sesi and absensi.sesi.waktu_sholat
        else None
    )
    return {
        "id_absensi": absensi.id_absensi,
        "timestamp": absensi.timestamp.isoformat() if absensi.timestamp else None,
        "nama_siswa": absensi.siswa.nama if absensi.siswa else None,
        "nisn": absensi.siswa.nisn if absensi.siswa else None,
        "kelas": kelas,
        "waktu_sholat": waktu_sholat,
        "status": absensi.status,
        "device_id": absensi.device_id,
    }


def _today_absensi():
    return Absensi.query.join(Absensi.sesi).filter(SesiSholat.tanggal == _today())


def _empty_dashboard(note: str, title: str = "Tabel Utama", columns: list[str] | None = None):
    return {
        "cards": [],
        "charts": {
            "attendance_trend": {
                "title": "Trend Kehadiran 7 Hari Terakhir",
                "rows": [],
                "note": note,
            },
            "status_distribution": {
                "title": "Distribusi Status 7 Hari Terakhir",
                "rows": [],
                "note": note,
            },
        },
        "primary_table": {
            "title": title,
            "columns": columns or [],
            "rows": [],
            "note": note,
        },
    }


def _chart_window(days: int = 7) -> tuple[date, date]:
    end_date = _today()
    start_date = end_date - timedelta(days=days - 1)
    return start_date, end_date


def _iter_dates(start_date: date, end_date: date):
    current = start_date
    while current <= end_date:
        yield current
        current += timedelta(days=1)


def _build_chart_payload(
    base_query,
    *,
    trend_title: str = "Trend Kehadiran 7 Hari Terakhir",
    status_title: str = "Distribusi Status 7 Hari Terakhir",
) -> dict:
    start_date, end_date = _chart_window()
    scoped_query = base_query.join(Absensi.sesi).filter(
        SesiSholat.tanggal >= start_date,
        SesiSholat.tanggal <= end_date,
    )

    trend_rows = (
        scoped_query.with_entities(
            SesiSholat.tanggal.label("tanggal"),
            func.count(Absensi.id_absensi).label("total"),
            func.sum(case((Absensi.status == "tepat_waktu", 1), else_=0)).label("tepat_waktu"),
            func.sum(case((Absensi.status == "terlambat", 1), else_=0)).label("terlambat"),
        )
        .group_by(SesiSholat.tanggal)
        .order_by(SesiSholat.tanggal.asc())
        .all()
    )
    trend_lookup = {
        row.tanggal: {
            "total": int(row.total or 0),
            "tepat_waktu": int(row.tepat_waktu or 0),
            "terlambat": int(row.terlambat or 0),
        }
        for row in trend_rows
    }

    status_rows = (
        scoped_query.with_entities(
            Absensi.status.label("status"),
            func.count(Absensi.id_absensi).label("value"),
        )
        .group_by(Absensi.status)
        .all()
    )
    status_lookup = {row.status: int(row.value or 0) for row in status_rows}

    return {
        "attendance_trend": {
            "title": trend_title,
            "rows": [
                {
                    "date": day.isoformat(),
                    "label": f"{day.day}/{day.month}",
                    "total": trend_lookup.get(day, {}).get("total", 0),
                    "tepat_waktu": trend_lookup.get(day, {}).get("tepat_waktu", 0),
                    "terlambat": trend_lookup.get(day, {}).get("terlambat", 0),
                }
                for day in _iter_dates(start_date, end_date)
            ],
            "note": "Belum ada absensi pada rentang 7 hari terakhir.",
        },
        "status_distribution": {
            "title": status_title,
            "rows": [
                {
                    "status": status,
                    "label": STATUS_CHART_LABELS[status],
                    "value": status_lookup[status],
                }
                for status in STATUS_CHART_ORDER
                if status_lookup.get(status, 0) > 0
            ],
            "note": "Belum ada distribusi status untuk ditampilkan.",
        },
    }


def _admin_payload() -> dict:
    today_query = _today_absensi()
    now = datetime.utcnow()
    perangkat_list = []
    for p in Perangkat.query.all():
        is_online = p.last_ping and p.last_ping >= (now - timedelta(minutes=3))
        perangkat_list.append({
            "device_id": p.device_id,
            "nama": p.nama_device,
            "status": "online" if is_online else "offline",
            "last_ping": p.last_ping.isoformat() if p.last_ping else None
        })
    online_count = sum(1 for p in perangkat_list if p["status"] == "online")
    return {
        "cards": [
            {"key": "total_users", "label": "Total User", "value": User.query.count()},
            {"key": "total_siswa", "label": "Total Siswa", "value": Siswa.query.count()},
            {"key": "tap_hari_ini", "label": "Tap Hari Ini", "value": today_query.count()},
            {
                "key": "perangkat_online",
                "label": "Perangkat Online",
                "value": online_count,
            },
        ],
        "perangkat_list": perangkat_list,
        "charts": _build_chart_payload(
            Absensi.query,
            trend_title="Trend Kehadiran Sekolah",
            status_title="Distribusi Status Sekolah",
        ),
        "primary_table": {
            "title": "Aktivitas Absensi Terkini",
            "columns": ["timestamp", "nama_siswa", "kelas", "waktu_sholat", "status", "device_id"],
            "rows": [_serialize_absensi_row(item) for item in _recent_absensi()],
        },
    }


def _kepsek_payload() -> dict:
    today_query = _today_absensi()
    class_rows = (
        today_query.join(Absensi.siswa)
        .join(Siswa.kelas)
        .with_entities(
            Kelas.nama_kelas.label("kelas"),
            func.count(Absensi.id_absensi).label("total_tap"),
            func.count(distinct(Absensi.id_siswa)).label("siswa_hadir"),
            func.sum(case((Absensi.status == "terlambat", 1), else_=0)).label("terlambat"),
        )
        .group_by(Kelas.id_kelas, Kelas.nama_kelas)
        .order_by(func.count(Absensi.id_absensi).desc())
        .all()
    )

    zona_merah_query = (
        Absensi.query.join(Absensi.siswa).join(Siswa.kelas)
        .filter(Absensi.status == "alpha")
        .with_entities(Siswa.nama.label("nama"), Kelas.nama_kelas.label("kelas"), func.count(Absensi.id_absensi).label("jumlah"))
        .group_by(Siswa.id_siswa, Siswa.nama, Kelas.nama_kelas)
        .having(func.count(Absensi.id_absensi) >= 2)
        .all()
    )
    zona_merah = [{"nama": r.nama, "kelas": r.kelas, "jumlah": int(r.jumlah)} for r in zona_merah_query]
    return {
        "cards": [
            {"key": "total_kelas", "label": "Total Kelas", "value": Kelas.query.count()},
            {"key": "total_siswa", "label": "Total Siswa", "value": Siswa.query.count()},
            {
                "key": "siswa_hadir_hari_ini",
                "label": "Siswa Hadir Hari Ini",
                "value": today_query.with_entities(func.count(distinct(Absensi.id_siswa))).scalar() or 0,
            },
            {
                "key": "terlambat_hari_ini",
                "label": "Terlambat Hari Ini",
                "value": today_query.filter(Absensi.status == "terlambat").count(),
            },
        ],
        "charts": _build_chart_payload(
            Absensi.query,
            trend_title="Trend Kehadiran Sekolah",
            status_title="Distribusi Status Sekolah",
        ),
        "primary_table": {
            "title": "Ringkasan Kelas Hari Ini",
            "columns": ["kelas", "siswa_hadir", "total_tap", "terlambat"],
            "rows": [
                {
                    "kelas": row.kelas,
                    "siswa_hadir": int(row.siswa_hadir or 0),
                    "total_tap": int(row.total_tap or 0),
                    "terlambat": int(row.terlambat or 0),
                }
                for row in class_rows
            ],
        },
        "secondary_table": {
            "title": "Top Offender (Sekolah)",
            "columns": ["nama", "kelas", "jumlah"],
            "rows": [
                {
                    "nama": row.nama,
                    "kelas": row.kelas_nama,
                    "jumlah": int(row.jumlah or 0)
                }
                for row in Absensi.query.join(Absensi.siswa).join(Siswa.kelas).filter(Absensi.status == "terlambat").with_entities(Siswa.nama.label("nama"), Kelas.nama_kelas.label("kelas_nama"), func.count(Absensi.id_absensi).label("jumlah")).group_by(Siswa.id_siswa, Siswa.nama, Kelas.nama_kelas).order_by(func.count(Absensi.id_absensi).desc()).limit(3).all()
            ],
        },
        "zona_merah": zona_merah,
    }


def _wali_payload(current_user: User) -> dict:
    kelas_diampu = Kelas.query.filter_by(id_wali=current_user.id_user).all()
    if not kelas_diampu:
        return _empty_dashboard(
            "Belum ada kelas yang dihubungkan ke wali kelas ini.",
            title="Rekap Siswa Kelas",
            columns=["nisn", "nama", "kelas", "total_hadir", "total_terlambat"],
        ) | {
            "cards": [
                {"key": "jumlah_kelas", "label": "Kelas Diampu", "value": 0},
                {"key": "jumlah_siswa", "label": "Total Siswa", "value": 0},
            ]
        }

    kelas_ids = [kelas.id_kelas for kelas in kelas_diampu]
    siswa_list = Siswa.query.options(joinedload(Siswa.kelas)).filter(Siswa.id_kelas.in_(kelas_ids)).all()
    student_ids = [item.id_siswa for item in siswa_list]
    aggregates = {}
    if student_ids:
        for row in (
            Absensi.query.with_entities(
                Absensi.id_siswa,
                func.count(Absensi.id_absensi).label("total_hadir"),
                func.sum(case((Absensi.status == "terlambat", 1), else_=0)).label("total_terlambat"),
            )
            .filter(Absensi.id_siswa.in_(student_ids))
            .group_by(Absensi.id_siswa)
            .all()
        ):
            aggregates[row.id_siswa] = {
                "total_hadir": int(row.total_hadir or 0),
                "total_terlambat": int(row.total_terlambat or 0),
            }

    hadir_hari_ini = (
        _today_absensi()
        .join(Absensi.siswa)
        .filter(Siswa.id_kelas.in_(kelas_ids))
        .with_entities(func.count(distinct(Absensi.id_siswa)))
        .scalar()
        or 0
    )
    terlambat_hari_ini = (
        _today_absensi()
        .join(Absensi.siswa)
        .filter(Siswa.id_kelas.in_(kelas_ids), Absensi.status == "terlambat")
        .count()
    )

    pending_sengketa = SengketaAbsensi.query.join(Siswa).filter(
        Siswa.id_kelas.in_(kelas_ids), SengketaAbsensi.status == "pending"
    ).count()
    pending_izin = IzinPengajuan.query.join(Siswa).filter(
        Siswa.id_kelas.in_(kelas_ids), IzinPengajuan.status == "pending"
    ).count()
    pending_tasks = {
        "sengketa": pending_sengketa,
        "izin": pending_izin,
        "total": pending_sengketa + pending_izin
    }

    zona_merah_query = (
        Absensi.query.join(Absensi.siswa).join(Siswa.kelas)
        .filter(Absensi.status == "alpha", Siswa.id_kelas.in_(kelas_ids))
        .with_entities(Siswa.nama.label("nama"), Kelas.nama_kelas.label("kelas"), func.count(Absensi.id_absensi).label("jumlah"))
        .group_by(Siswa.id_siswa, Siswa.nama, Kelas.nama_kelas)
        .having(func.count(Absensi.id_absensi) >= 2)
        .all()
    )
    zona_merah = [{"nama": r.nama, "kelas": r.kelas, "jumlah": int(r.jumlah)} for r in zona_merah_query]

    return {
        "cards": [
            {"key": "jumlah_kelas", "label": "Kelas Diampu", "value": len(kelas_diampu)},
            {"key": "jumlah_siswa", "label": "Total Siswa", "value": len(siswa_list)},
            {"key": "hadir_hari_ini", "label": "Hadir Hari Ini", "value": int(hadir_hari_ini)},
            {"key": "terlambat_hari_ini", "label": "Terlambat Hari Ini", "value": int(terlambat_hari_ini)},
        ],
        "charts": _build_chart_payload(
            Absensi.query.join(Absensi.siswa).filter(Siswa.id_kelas.in_(kelas_ids)),
            trend_title="Trend Kehadiran Kelas",
            status_title="Distribusi Status Kelas",
        ),
        "primary_table": {
            "title": "Rekap Siswa Kelas",
            "columns": ["nisn", "nama", "kelas", "total_hadir", "total_terlambat"],
            "rows": [
                {
                    "nisn": siswa.nisn,
                    "nama": siswa.nama,
                    "kelas": siswa.kelas.nama_kelas if siswa.kelas else None,
                    "total_hadir": aggregates.get(siswa.id_siswa, {}).get("total_hadir", 0),
                    "total_terlambat": aggregates.get(siswa.id_siswa, {}).get("total_terlambat", 0),
                }
                for siswa in siswa_list
            ],
        },
        "secondary_table": {
            "title": "Top Offender (Kelas Anda)",
            "columns": ["nama", "jumlah"],
            "rows": [
                {
                    "nama": row.nama,
                    "jumlah": int(row.jumlah or 0)
                }
                for row in Absensi.query.join(Absensi.siswa).filter(Siswa.id_kelas.in_(kelas_ids), Absensi.status == "terlambat").with_entities(Siswa.nama.label("nama"), func.count(Absensi.id_absensi).label("jumlah")).group_by(Siswa.id_siswa, Siswa.nama).order_by(func.count(Absensi.id_absensi).desc()).limit(3).all()
            ],
        },
        "zona_merah": zona_merah,
        "pending_tasks": pending_tasks,
    }


def _guru_piket_payload() -> dict:
    today_query = _today_absensi()
    now = datetime.utcnow()
    perangkat_list = []
    for p in Perangkat.query.all():
        is_online = p.last_ping and p.last_ping >= (now - timedelta(minutes=3))
        perangkat_list.append({
            "device_id": p.device_id,
            "nama": p.nama_device,
            "status": "online" if is_online else "offline",
            "last_ping": p.last_ping.isoformat() if p.last_ping else None
        })
    online_count = sum(1 for p in perangkat_list if p["status"] == "online")
    return {
        "cards": [
            {"key": "tap_hari_ini", "label": "Tap Hari Ini", "value": today_query.count()},
            {"key": "tepat_waktu", "label": "Tepat Waktu", "value": today_query.filter(Absensi.status == "tepat_waktu").count()},
            {"key": "terlambat", "label": "Terlambat", "value": today_query.filter(Absensi.status == "terlambat").count()},
            {"key": "perangkat_online", "label": "Perangkat Online", "value": online_count},
        ],
        "perangkat_list": perangkat_list,
        "charts": _build_chart_payload(
            Absensi.query,
            trend_title="Trend Tap Kehadiran",
            status_title="Distribusi Status Kehadiran",
        ),
        "primary_table": {
            "title": "Tap RFID Terkini",
            "columns": ["timestamp", "nama_siswa", "kelas", "waktu_sholat", "status", "device_id"],
            "rows": [_serialize_absensi_row(item) for item in _recent_absensi()],
        },
    }


def _siswa_payload(student: Siswa | None) -> dict:
    if student is None:
        return _empty_dashboard(
            "Akun ini belum terhubung ke data siswa.",
            title="Riwayat Absensi Pribadi",
            columns=["tanggal", "timestamp", "waktu_sholat", "status"],
        )

    today = _today()
    month_start = _month_start(today)
    base_query = (
        Absensi.query.join(Absensi.sesi)
        .options(joinedload(Absensi.sesi).joinedload(SesiSholat.waktu_sholat))
        .filter(Absensi.id_siswa == student.id_siswa)
    )
    monthly_query = base_query.filter(SesiSholat.tanggal >= month_start, SesiSholat.tanggal <= today)
    latest = base_query.order_by(Absensi.timestamp.desc()).first()
    rows = []
    for absensi in base_query.order_by(Absensi.timestamp.desc()).limit(10).all():
        rows.append(
            {
                "tanggal": absensi.sesi.tanggal.isoformat() if absensi.sesi and absensi.sesi.tanggal else None,
                "timestamp": absensi.timestamp.isoformat() if absensi.timestamp else None,
                "waktu_sholat": absensi.sesi.waktu_sholat.nama_sholat if absensi.sesi and absensi.sesi.waktu_sholat else None,
                "status": absensi.status,
            }
        )
        
    absensi_bulan_ini_count = monthly_query.count()
    tepat_waktu_count = monthly_query.filter(Absensi.status == "tepat_waktu").count()
    persentase_tepat_waktu = round((tepat_waktu_count / absensi_bulan_ini_count) * 100) if absensi_bulan_ini_count > 0 else 0
    total_izin = monthly_query.filter(Absensi.status == "izin").count()

    milestone = {
        "persentase_tepat": persentase_tepat_waktu,
        "total_izin": total_izin
    }
    
    return {
        "cards": [
            {"key": "absensi_bulan_ini", "label": "Absensi Bulan Ini", "value": absensi_bulan_ini_count},
            {"key": "tepat_waktu", "label": "Tepat Waktu", "value": tepat_waktu_count},
            {"key": "terlambat", "label": "Terlambat", "value": monthly_query.filter(Absensi.status == "terlambat").count()},
            {"key": "status_terakhir", "label": "Status Terakhir", "value": latest.status if latest else "belum_ada"},
        ],
        "charts": _build_chart_payload(
            Absensi.query.filter(Absensi.id_siswa == student.id_siswa),
            trend_title="Trend Kehadiran Pribadi",
            status_title="Distribusi Status Pribadi",
        ),
        "primary_table": {
            "title": "Riwayat Absensi Pribadi",
            "columns": ["tanggal", "timestamp", "waktu_sholat", "status"],
            "rows": rows,
        },
        "milestone": milestone,
    }


def _orangtua_payload(current_user: User) -> dict:
    parent_relation = getattr(current_user, "orangtua_profile", None)
    if parent_relation is not None:
        student = Siswa.query.options(joinedload(Siswa.kelas)).filter_by(id_siswa=parent_relation.id_siswa).first()
    else:
        student = (
            Siswa.query.options(joinedload(Siswa.kelas)).filter_by(no_telp_ortu=current_user.no_telp).first()
            if current_user.no_telp
            else None
        )
    payload = _siswa_payload(student)
    payload["student"] = {
        "id_siswa": student.id_siswa,
        "nisn": student.nisn,
        "nama": student.nama,
        "kelas": student.kelas.nama_kelas if student.kelas else None,
    } if student else None
    if student is None:
        payload["primary_table"]["note"] = "Akun orang tua belum terhubung ke data siswa melalui nomor telepon."
    return payload


def build_dashboard_payload(current_user: User) -> dict:
    role = current_user.role
    if role == "admin":
        payload = _admin_payload()
    elif role == "kepsek":
        payload = _kepsek_payload()
    elif role == "wali_kelas":
        payload = _wali_payload(current_user)
    elif role == "guru_piket":
        payload = _guru_piket_payload()
    elif role == "siswa":
        payload = _siswa_payload(current_user.siswa_profile)
    elif role == "orangtua":
        payload = _orangtua_payload(current_user)
    else:
        payload = _empty_dashboard("Role belum didukung.")

    payload["role"] = role
    payload["generated_at"] = datetime.utcnow().isoformat() + "Z"
    return payload
