from typing import Optional
from ..models import db, SekolahInfo
import logging

logger = logging.getLogger(__name__)

class SekolahServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def get_sekolah_info() -> dict:
    info = SekolahInfo.query.first()
    if not info:
        info = SekolahInfo(nama_sekolah="Sekolah Bawaan", alamat="-")
        db.session.add(info)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            return {}
    
    return {
        "id_sekolah": info.id_sekolah,
        "nama_sekolah": info.nama_sekolah,
        "alamat": info.alamat,
        "no_telp": info.no_telp,
        "email": info.email,
        "logo_path": info.logo_path,
        "foto_masjid_path": info.foto_masjid_path,
    }

def update_sekolah_info(payload: dict) -> dict:
    info = SekolahInfo.query.first()
    if not info:
        info = SekolahInfo(nama_sekolah="Sekolah Bawaan")
        db.session.add(info)
        
    for k, v in payload.items():
        if hasattr(info, k) and k != "id_sekolah":
            setattr(info, k, v)
            
    try:
        db.session.commit()
        return get_sekolah_info()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error update sekolah: {e}")
        raise SekolahServiceError("Gagal update profil sekolah", 500)
