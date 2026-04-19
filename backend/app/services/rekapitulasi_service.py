from sqlalchemy import func

from ..extensions import db
from ..models import Absensi, Kelas, SesiSholat, Siswa


STATUS_KEYS = ("tepat_waktu", "terlambat", "alpha", "izin", "sakit", "haid")


def _calculate_percentage(stats):
    tepat_waktu = stats.get("tepat_waktu", 0)
    terlambat = stats.get("terlambat", 0)
    alpha = stats.get("alpha", 0)

    total_valid = tepat_waktu + terlambat + alpha
    hadir = tepat_waktu + terlambat

    if total_valid > 0:
        return round((hadir / total_valid) * 100, 2)
    return 0.0


def _sum_stats(rows):
    totals = {status: 0 for status in STATUS_KEYS}
    for row in rows:
        for status in STATUS_KEYS:
            totals[status] += int(row.get(status, 0) or 0)
    return totals


def _build_status_breakdown(stats):
    labels = {
        "tepat_waktu": "Tepat Waktu",
        "terlambat": "Terlambat",
        "alpha": "Alpha",
        "izin": "Izin",
        "sakit": "Sakit",
        "haid": "Haid",
    }
    return [
        {"status": status, "label": labels[status], "count": int(stats.get(status, 0) or 0)}
        for status in STATUS_KEYS
    ]


def get_rekap_kelas(id_kelas, start_date=None, end_date=None):
    siswas = Siswa.query.filter_by(id_kelas=id_kelas).all()
    siswa_dict = {
        s.id_siswa: {"id_siswa": s.id_siswa, "nama": s.nama, "nisn": s.nisn, "stats": {}}
        for s in siswas
    }

    if not siswa_dict:
        return []

    query = db.session.query(
        Absensi.id_siswa,
        Absensi.status,
        func.count(Absensi.id_absensi).label("count"),
    ).join(SesiSholat)

    if start_date:
        query = query.filter(SesiSholat.tanggal >= start_date)
    if end_date:
        query = query.filter(SesiSholat.tanggal <= end_date)

    query = query.filter(Absensi.id_siswa.in_(siswa_dict.keys()))
    query = query.group_by(Absensi.id_siswa, Absensi.status)

    results = query.all()
    for row in results:
        siswa_id, status, count = row
        siswa_dict[siswa_id]["stats"][status] = count

    rekap_list = []
    for _, s_data in siswa_dict.items():
        stats = s_data["stats"]
        persentase = _calculate_percentage(stats)
        rekap_list.append(
            {
                "id_siswa": s_data["id_siswa"],
                "nama": s_data["nama"],
                "nisn": s_data["nisn"],
                "tepat_waktu": stats.get("tepat_waktu", 0),
                "terlambat": stats.get("terlambat", 0),
                "alpha": stats.get("alpha", 0),
                "izin": stats.get("izin", 0),
                "sakit": stats.get("sakit", 0),
                "haid": stats.get("haid", 0),
                "persentase": persentase,
            }
        )

    return rekap_list


def get_rekap_siswa(id_siswa, start_date=None, end_date=None):
    query = (
        db.session.query(
            Absensi.status,
            func.count(Absensi.id_absensi).label("count"),
        )
        .join(SesiSholat)
        .filter(Absensi.id_siswa == id_siswa)
    )

    if start_date:
        query = query.filter(SesiSholat.tanggal >= start_date)
    if end_date:
        query = query.filter(SesiSholat.tanggal <= end_date)

    query = query.group_by(Absensi.status)

    results = query.all()
    stats = {row[0]: row[1] for row in results}

    return {
        "id_siswa": id_siswa,
        "tepat_waktu": stats.get("tepat_waktu", 0),
        "terlambat": stats.get("terlambat", 0),
        "alpha": stats.get("alpha", 0),
        "izin": stats.get("izin", 0),
        "sakit": stats.get("sakit", 0),
        "haid": stats.get("haid", 0),
        "persentase": _calculate_percentage(stats),
    }


def get_rekap_sekolah(start_date=None, end_date=None):
    kelas_list = Kelas.query.all()
    kelas_dict = {
        kelas.id_kelas: {
            "id_kelas": kelas.id_kelas,
            "nama_kelas": kelas.nama_kelas,
            "tingkat": kelas.tingkat,
            "jurusan": kelas.jurusan,
            "tahun_ajaran": kelas.tahun_ajaran,
            "stats": {},
            "jumlah_siswa": 0,
        }
        for kelas in kelas_list
    }

    student_counts = (
        db.session.query(
            Siswa.id_kelas,
            func.count(Siswa.id_siswa).label("jumlah_siswa"),
        )
        .group_by(Siswa.id_kelas)
        .all()
    )
    for row in student_counts:
        if row.id_kelas in kelas_dict:
            kelas_dict[row.id_kelas]["jumlah_siswa"] = int(row.jumlah_siswa or 0)

    query = (
        db.session.query(
            Siswa.id_kelas,
            Absensi.status,
            func.count(Absensi.id_absensi).label("count"),
        )
        .select_from(Absensi)
        .join(SesiSholat)
        .join(Siswa, Absensi.id_siswa == Siswa.id_siswa)
    )

    if start_date:
        query = query.filter(SesiSholat.tanggal >= start_date)
    if end_date:
        query = query.filter(SesiSholat.tanggal <= end_date)

    query = query.group_by(Siswa.id_kelas, Absensi.status)
    results = query.all()

    for row in results:
        kelas_id, status, count = row
        if kelas_id in kelas_dict:
            kelas_dict[kelas_id]["stats"][status] = count

    rekap_list = []
    for _, kelas_data in kelas_dict.items():
        stats = kelas_data["stats"]
        total_hadir = stats.get("tepat_waktu", 0) + stats.get("terlambat", 0)
        total_valid = total_hadir + stats.get("alpha", 0)
        total_absensi = sum(int(stats.get(status, 0) or 0) for status in STATUS_KEYS)
        rekap_list.append(
            {
                "id_kelas": kelas_data["id_kelas"],
                "nama_kelas": kelas_data["nama_kelas"],
                "tingkat": kelas_data["tingkat"],
                "jurusan": kelas_data["jurusan"],
                "tahun_ajaran": kelas_data["tahun_ajaran"],
                "jumlah_siswa": int(kelas_data["jumlah_siswa"] or 0),
                "tepat_waktu": stats.get("tepat_waktu", 0),
                "terlambat": stats.get("terlambat", 0),
                "alpha": stats.get("alpha", 0),
                "izin": stats.get("izin", 0),
                "sakit": stats.get("sakit", 0),
                "haid": stats.get("haid", 0),
                "total_hadir": total_hadir,
                "total_valid": total_valid,
                "total_absensi": total_absensi,
                "persentase": _calculate_percentage(stats),
            }
        )

    rekap_list.sort(key=lambda row: (row["tingkat"], row["nama_kelas"]))
    global_stats = _sum_stats(rekap_list)
    total_hadir = global_stats.get("tepat_waktu", 0) + global_stats.get("terlambat", 0)
    total_valid = total_hadir + global_stats.get("alpha", 0)
    total_absensi = sum(row["total_absensi"] for row in rekap_list)
    total_siswa = db.session.query(func.count(Siswa.id_siswa)).scalar() or 0
    siswa_berkartu = (
        db.session.query(func.count(Siswa.id_siswa))
        .filter(Siswa.id_card.isnot(None), Siswa.id_card != "")
        .scalar()
        or 0
    )

    perangkat_online = 0
    try:
        from ..models import Perangkat

        perangkat_online = (
            db.session.query(func.count(Perangkat.device_id))
            .filter(Perangkat.status == "online")
            .scalar()
            or 0
        )
    except Exception:
        perangkat_online = 0

    ranked = sorted(
        rekap_list,
        key=lambda row: (row["persentase"], row["total_hadir"], row["jumlah_siswa"]),
        reverse=True,
    )
    top_kelas = ranked[:3]
    bottom_kelas = list(reversed(ranked[-3:])) if ranked else []
    rata_rata_persentase = (
        round(sum(row["persentase"] for row in rekap_list) / len(rekap_list), 2)
        if rekap_list
        else 0.0
    )

    return {
        "summary": {
            "tepat_waktu": global_stats.get("tepat_waktu", 0),
            "terlambat": global_stats.get("terlambat", 0),
            "alpha": global_stats.get("alpha", 0),
            "izin": global_stats.get("izin", 0),
            "sakit": global_stats.get("sakit", 0),
            "haid": global_stats.get("haid", 0),
            "total_hadir": total_hadir,
            "total_valid": total_valid,
            "total_absensi": total_absensi,
            "persentase": _calculate_percentage(global_stats),
        },
        "metadata": {
            "total_kelas": len(kelas_list),
            "total_siswa": int(total_siswa),
            "total_tap": int(total_absensi),
            "perangkat_online": int(perangkat_online),
            "siswa_berkartu": int(siswa_berkartu),
            "siswa_tanpa_kartu": int(max(int(total_siswa) - int(siswa_berkartu), 0)),
            "rata_rata_persentase_kelas": rata_rata_persentase,
        },
        "period": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "filter_applied": bool(start_date or end_date),
        },
        "status_breakdown": _build_status_breakdown(global_stats),
        "top_kelas": top_kelas,
        "bottom_kelas": bottom_kelas,
        "kelas": rekap_list,
    }
