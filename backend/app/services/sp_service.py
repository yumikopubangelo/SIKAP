from typing import List
from datetime import date
from ..models import db, SuratPeringatan, Siswa, Absensi
import logging

logger = logging.getLogger(__name__)

class SPServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def list_sp() -> List[dict]:
    sps = SuratPeringatan.query.all()
    results = []
    for s in sps:
        results.append({
            "id_sp": s.id_sp,
            "id_siswa": s.id_siswa,
            "sp_ke": s.sp_ke,
            "tanggal": s.tanggal.isoformat() if s.tanggal else None,
            "jenis": s.jenis,
            "status_kirim": s.status_kirim,
            "alasan": s.alasan
        })
    return results

def generate_auto_sp(current_user) -> dict:
    siswa_all = Siswa.query.all()
    generated_count = 0
    for s in siswa_all:
        alpha_count = Absensi.query.filter_by(id_siswa=s.id_siswa, status="alpha").count()
        last_sp = SuratPeringatan.query.filter_by(id_siswa=s.id_siswa).order_by(SuratPeringatan.sp_ke.desc()).first()
        current_sp_level = last_sp.sp_ke if last_sp else 0
        
        target_sp_level = 0
        if alpha_count >= 9: target_sp_level = 3
        elif alpha_count >= 6: target_sp_level = 2
        elif alpha_count >= 3: target_sp_level = 1
            
        if target_sp_level > current_sp_level:
            new_sp = SuratPeringatan(
                id_siswa=s.id_siswa,
                sp_ke=target_sp_level,
                tanggal=date.today(),
                jenis=f"SP{target_sp_level}",
                id_pengirim=current_user.id_user,
                alasan=f"Akumulasi {alpha_count} kali Alpha tanpa keterangan."
            )
            db.session.add(new_sp)
            generated_count += 1
            
    try:
        db.session.commit()
        return {"generated_count": generated_count}
    except Exception as e:
        db.session.rollback()
        logger.error(f"Generate SP error: {e}")
        raise SPServiceError("Gagal menjalankan automasi SP", 500)
