from sqlalchemy import func
from ..extensions import db
from ..models import Absensi, Siswa, Kelas, SesiSholat

def _calculate_percentage(stats):
    tepat_waktu = stats.get('tepat_waktu', 0)
    terlambat = stats.get('terlambat', 0)
    alpha = stats.get('alpha', 0)
    
    total_valid = tepat_waktu + terlambat + alpha
    hadir = tepat_waktu + terlambat
    
    if total_valid > 0:
        return round((hadir / total_valid) * 100, 2)
    return 0.0

def get_rekap_kelas(id_kelas, start_date=None, end_date=None):
    siswas = Siswa.query.filter_by(id_kelas=id_kelas).all()
    siswa_dict = {s.id_siswa: {"id_siswa": s.id_siswa, "nama": s.nama, "nisn": s.nisn, "stats": {}} for s in siswas}
    
    if not siswa_dict:
        return []

    query = db.session.query(
        Absensi.id_siswa,
        Absensi.status,
        func.count(Absensi.id_absensi).label('count')
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
    for s_id, s_data in siswa_dict.items():
        stats = s_data["stats"]
        persentase = _calculate_percentage(stats)
        rekap_list.append({
            "id_siswa": s_data["id_siswa"],
            "nama": s_data["nama"],
            "nisn": s_data["nisn"],
            "tepat_waktu": stats.get('tepat_waktu', 0),
            "terlambat": stats.get('terlambat', 0),
            "alpha": stats.get('alpha', 0),
            "izin": stats.get('izin', 0),
            "sakit": stats.get('sakit', 0),
            "haid": stats.get('haid', 0),
            "persentase": persentase
        })
        
    return rekap_list

def get_rekap_siswa(id_siswa, start_date=None, end_date=None):
    query = db.session.query(
        Absensi.status,
        func.count(Absensi.id_absensi).label('count')
    ).join(SesiSholat).filter(Absensi.id_siswa == id_siswa)
    
    if start_date:
        query = query.filter(SesiSholat.tanggal >= start_date)
    if end_date:
        query = query.filter(SesiSholat.tanggal <= end_date)
        
    query = query.group_by(Absensi.status)
    
    results = query.all()
    stats = {row[0]: row[1] for row in results}
    
    return {
        "id_siswa": id_siswa,
        "tepat_waktu": stats.get('tepat_waktu', 0),
        "terlambat": stats.get('terlambat', 0),
        "alpha": stats.get('alpha', 0),
        "izin": stats.get('izin', 0),
        "sakit": stats.get('sakit', 0),
        "haid": stats.get('haid', 0),
        "persentase": _calculate_percentage(stats)
    }

def get_rekap_sekolah(start_date=None, end_date=None):
    kelas_list = Kelas.query.all()
    kelas_dict = {k.id_kelas: {"id_kelas": k.id_kelas, "nama_kelas": k.nama_kelas, "stats": {}} for k in kelas_list}
    
    query = db.session.query(
        Siswa.id_kelas,
        Absensi.status,
        func.count(Absensi.id_absensi).label('count')
    ).select_from(Absensi).join(SesiSholat).join(Siswa, Absensi.id_siswa == Siswa.id_siswa)
    
    if start_date:
        query = query.filter(SesiSholat.tanggal >= start_date)
    if end_date:
        query = query.filter(SesiSholat.tanggal <= end_date)
        
    query = query.group_by(Siswa.id_kelas, Absensi.status)
    results = query.all()
    
    for row in results:
        k_id, status, count = row
        if k_id in kelas_dict:
            kelas_dict[k_id]["stats"][status] = count
            
    rekap_list = []
    for k_id, k_data in kelas_dict.items():
        stats = k_data["stats"]
        rekap_list.append({
            "id_kelas": k_data["id_kelas"],
            "nama_kelas": k_data["nama_kelas"],
            "tepat_waktu": stats.get('tepat_waktu', 0),
            "terlambat": stats.get('terlambat', 0),
            "alpha": stats.get('alpha', 0),
            "izin": stats.get('izin', 0),
            "sakit": stats.get('sakit', 0),
            "haid": stats.get('haid', 0),
            "persentase": _calculate_percentage(stats)
        })
        
    global_stats = {}
    for r in rekap_list:
        for status in ['tepat_waktu', 'terlambat', 'alpha', 'izin', 'sakit', 'haid']:
            global_stats[status] = global_stats.get(status, 0) + r[status]
            
    return {
        "summary": {
            "tepat_waktu": global_stats.get('tepat_waktu', 0),
            "terlambat": global_stats.get('terlambat', 0),
            "alpha": global_stats.get('alpha', 0),
            "izin": global_stats.get('izin', 0),
            "sakit": global_stats.get('sakit', 0),
            "haid": global_stats.get('haid', 0),
            "persentase": _calculate_percentage(global_stats)
        },
        "kelas": rekap_list
    }
