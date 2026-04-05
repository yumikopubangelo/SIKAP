from typing import List, Optional
from ..models import db, WaktuSholat
import logging

logger = logging.getLogger(__name__)

class WaktuSholatServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def list_waktu_sholat() -> List[dict]:
    waktus = WaktuSholat.query.all()
    if not waktus:
        # Default seeds
        seeds = [
            WaktuSholat(nama_sholat="Dhuhur", waktu_adzan="12:00:00", waktu_iqamah="12:10:00", waktu_selesai="12:30:00"),
            WaktuSholat(nama_sholat="Ashar", waktu_adzan="15:00:00", waktu_iqamah="15:10:00", waktu_selesai="15:30:00")
        ]
        db.session.add_all(seeds)
        db.session.commit()
        waktus = WaktuSholat.query.all()
        
    return [{
        "id_waktu": w.id_waktu,
        "nama_sholat": w.nama_sholat,
        "waktu_adzan": str(w.waktu_adzan),
        "waktu_iqamah": str(w.waktu_iqamah),
        "waktu_selesai": str(w.waktu_selesai)
    } for w in waktus]

def update_waktu_sholat(id_waktu: int, payload: dict) -> dict:
    w = WaktuSholat.query.get(id_waktu)
    if not w:
        raise WaktuSholatServiceError("Jadwal tidak ditemukan", 404)
        
    w.waktu_adzan = payload.get("waktu_adzan", w.waktu_adzan)
    w.waktu_iqamah = payload.get("waktu_iqamah", w.waktu_iqamah)
    w.waktu_selesai = payload.get("waktu_selesai", w.waktu_selesai)
    
    try:
        db.session.commit()
        return {
            "id_waktu": w.id_waktu,
            "nama_sholat": w.nama_sholat,
            "waktu_adzan": str(w.waktu_adzan),
            "waktu_iqamah": str(w.waktu_iqamah),
            "waktu_selesai": str(w.waktu_selesai)
        }
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update waktu sholat: {e}")
        raise WaktuSholatServiceError("Gagal merubah waktu sholat.", 500)
