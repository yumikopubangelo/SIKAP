from typing import List, Optional
from ..models import db, SengketaAbsensi
from .absensi_service import create_manual_absensi, AbsensiServiceError
import logging

logger = logging.getLogger(__name__)

class SengketaServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400, errors: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors

def list_sengketa(status: Optional[str] = None) -> List[dict]:
    query = SengketaAbsensi.query
    if status:
        query = query.filter(SengketaAbsensi.status == status)
    sengketa = query.all()
    results = []
    for s in sengketa:
        results.append({
            "id_sengketa": s.id_sengketa,
            "id_siswa": s.id_siswa,
            "id_sesi": s.id_sesi,
            "alasan": s.alasan,
            "status": s.status,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "verified_at": s.verified_at.isoformat() if s.verified_at else None,
            "id_verifikator": s.id_verifikator,
            "catatan_verifikator": s.catatan_verifikator
        })
    return results

def create_sengketa(payload: dict, current_user) -> dict:
    if current_user.role != "siswa" or not current_user.siswa_profile:
        raise SengketaServiceError("Hanya siswa yang dapat membuat sengketa.", 403)
        
    if not payload.get("id_sesi") or not payload.get("alasan"):
        raise SengketaServiceError("Field id_sesi dan alasan wajib diisi.", 400)
        
    sengketa = SengketaAbsensi(
        id_siswa=current_user.siswa_profile.id_siswa,
        id_sesi=payload.get("id_sesi"),
        alasan=payload.get("alasan")
    )
    db.session.add(sengketa)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create sengketa: {str(e)}")
        raise SengketaServiceError("Gagal membuat klaim.", 500)
    
    return {"id_sengketa": sengketa.id_sengketa, "status": sengketa.status}

def resolve_sengketa(sengketa_id: int, action: str, catatan: str, current_user) -> dict:
    if current_user.role != "guru_piket":
        raise SengketaServiceError("Hanya guru piket yang dapat memproses sengketa.", 403)

    sengketa = db.session.get(SengketaAbsensi, sengketa_id)
    if not sengketa:
        raise SengketaServiceError("Sengketa tidak ditemukan.", 404)
        
    if sengketa.status != "pending":
        raise SengketaServiceError(f"Sengketa sudah memiliki status {sengketa.status}.", 400)

    if action == "approve":
        sengketa.status = "disetujui"
        
        absensi_payload = {
            "id_siswa": sengketa.id_siswa,
            "id_sesi": sengketa.id_sesi,
            "status": "tepat_waktu", 
            "keterangan": f"[SENGKETA] ID: {sengketa.id_sengketa} - {catatan}"
        }
        
        try:
            create_manual_absensi(absensi_payload, current_user)
        except AbsensiServiceError as e:
            # We skip throwing error here if absensi exists since the manual absensi create might throw duplicate error
            # Or we could just catch Duplicate and update it.
            logger.warning(f"Auto-absensi failed or duplicate: {e.message}")
            if "UNIQUE constraint" not in str(e.message) and "Duplicate" not in str(e.message):
                raise SengketaServiceError(f"Gagal menyetujui sengketa saat update absensi: {e.message}", e.status_code)
            
    elif action == "reject":
        sengketa.status = "ditolak"
    else:
        raise SengketaServiceError("Action harus 'approve' atau 'reject'.", 400)
        
    sengketa.id_verifikator = current_user.id_user
    sengketa.catatan_verifikator = catatan
    sengketa.verified_at = db.func.now()
    
    try:
        db.session.commit()
        return {"id_sengketa": sengketa.id_sengketa, "status": sengketa.status}
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to resolve sengketa: {str(e)}")
        raise SengketaServiceError("Gagal menyimpan verifikasi sengketa.", 500)
