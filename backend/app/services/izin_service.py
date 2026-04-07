from typing import List, Optional
from datetime import datetime
from ..models import db, IzinPengajuan, SesiSholat
from .absensi_service import create_manual_absensi, AbsensiServiceError
import logging

logger = logging.getLogger(__name__)

class IzinServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400, errors: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors

def list_izin(status: Optional[str] = None) -> List[dict]:
    query = IzinPengajuan.query
    if status:
        query = query.filter(IzinPengajuan.status == status)
    izin_list = query.all()
    results = []
    for s in izin_list:
        results.append({
            "id_izin": s.id_izin,
            "id_siswa": s.id_siswa,
            "tanggal_mulai": s.tanggal_mulai.isoformat() if s.tanggal_mulai else None,
            "tanggal_selesai": s.tanggal_selesai.isoformat() if s.tanggal_selesai else None,
            "alasan": s.alasan,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "id_verifikator": s.id_verifikator,
            "catatan_verifikator": s.catatan_verifikator
        })
    return results

def create_izin(payload: dict, current_user) -> dict:
    if current_user.role != "siswa" or not current_user.siswa_profile:
        raise IzinServiceError("Hanya siswa yang dapat membuat izin.", 403)
        
    try:
        tgl_mulai = datetime.strptime(payload.get("tanggal_mulai", ""), "%Y-%m-%d").date()
        tgl_selesai = datetime.strptime(payload.get("tanggal_selesai", ""), "%Y-%m-%d").date()
    except ValueError:
        raise IzinServiceError("Format tanggal tidak valid. Gunakan YYYY-MM-DD", 400)
    
    alasan = payload.get("alasan")
    if not alasan:
        raise IzinServiceError("Alasan izin wajib diisi.", 400)
        
    izin = IzinPengajuan(
        id_siswa=current_user.siswa_profile.id_siswa,
        tanggal_mulai=tgl_mulai,
        tanggal_selesai=tgl_selesai,
        alasan=alasan
    )
    db.session.add(izin)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create izin: {str(e)}")
        raise IzinServiceError("Gagal membuat pengajuan izin.", 500)
    
    return {"id_izin": izin.id_izin, "status": izin.status}

def resolve_izin(izin_id: int, action: str, catatan: str, current_user) -> dict:
    if current_user.role != "wali_kelas" and current_user.role != "kepsek":
        raise IzinServiceError("Hanya Wali Kelas/Kepsek yang dapat memproses izin.", 403)

    izin = IzinPengajuan.query.get(izin_id)
    if not izin:
        raise IzinServiceError("Pengajuan izin tidak ditemukan.", 404)
        
    if izin.status != "pending":
        raise IzinServiceError(f"Izin sudah memiliki status {izin.status}.", 400)

    if action == "approve":
        izin.status = "disetujui"
        
        # Check active sesi_sholat in that date range
        sesi_list = SesiSholat.query.filter(
            SesiSholat.tanggal >= izin.tanggal_mulai,
            SesiSholat.tanggal <= izin.tanggal_selesai
        ).all()
        
        # We auto generate absent status "izin" or "haid" based on the reason text
        auto_status = "haid" if "haid" in izin.alasan.lower() else "izin"
        
        for sesi in sesi_list:
            absensi_payload = {
                "id_siswa": izin.id_siswa,
                "id_sesi": sesi.id_sesi,
                "status": auto_status, 
                "keterangan": f"[IZIN AUTO] ID: {izin.id_izin}"
            }
            try:
                create_manual_absensi(absensi_payload, current_user)
            except AbsensiServiceError as e:
                logger.warning(f"Izin auto-absensi issue for sesi {sesi.id_sesi}: {e.message}")
            
    elif action == "reject":
        izin.status = "ditolak"
    else:
        raise IzinServiceError("Action harus 'approve' atau 'reject'.", 400)
        
    izin.id_verifikator = current_user.id_user
    izin.catatan_verifikator = catatan
    
    try:
        db.session.commit()
        return {"id_izin": izin.id_izin, "status": izin.status}
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to resolve izin: {str(e)}")
        raise IzinServiceError("Gagal menyimpan verifikasi izin.", 500)
