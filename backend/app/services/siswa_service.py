from typing import List, Optional
from ..models import db, Siswa
import logging

logger = logging.getLogger(__name__)

class SiswaServiceError(Exception): 
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def list_siswa(id_kelas: Optional[int] = None) -> List[dict]:
    query = Siswa.query
    if id_kelas: query = query.filter_by(id_kelas=id_kelas)
    return [s.to_dict() for s in query.all()]

def create_siswa(payload: dict) -> dict:
    nisn = payload.get("nisn")
    if not nisn: raise SiswaServiceError("NISN wajib diisi")
    if Siswa.query.filter_by(nisn=nisn).first(): raise SiswaServiceError("NISN sudah terdaftar")
        
    s = Siswa(
        nisn=nisn,
        nama=payload.get("nama", "Siswa Baru"),
        jenis_kelamin=payload.get("jenis_kelamin"),
        alamat=payload.get("alamat"),
        no_telp_ortu=payload.get("no_telp_ortu"),
        id_card=payload.get("id_card"),
        id_kelas=payload.get("id_kelas")
    )
    db.session.add(s)
    db.session.commit()
    return s.to_dict()

def update_siswa(id_siswa: int, payload: dict) -> dict:
    s = Siswa.query.get(id_siswa)
    if not s: raise SiswaServiceError("Siswa tidak ditemukan", 404)
        
    if "nama" in payload: s.nama = payload["nama"]
    if "jenis_kelamin" in payload: s.jenis_kelamin = payload["jenis_kelamin"]
    if "alamat" in payload: s.alamat = payload["alamat"]
    if "no_telp_ortu" in payload: s.no_telp_ortu = payload["no_telp_ortu"]
    if "id_card" in payload: s.id_card = payload["id_card"]
    if "id_kelas" in payload: s.id_kelas = payload["id_kelas"]
        
    db.session.commit()
    return s.to_dict()

def delete_siswa(id_siswa: int):
    s = Siswa.query.get(id_siswa)
    if not s: raise SiswaServiceError("Siswa tidak ditemukan", 404)
    db.session.delete(s)
    db.session.commit()
