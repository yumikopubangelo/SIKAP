from typing import List, Optional
from ..models import db, Kelas
import logging

logger = logging.getLogger(__name__)

class KelasServiceError(Exception): 
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def list_kelas() -> List[dict]:
    kelas_list = Kelas.query.all()
    results = []
    for k in kelas_list:
        results.append({
            "id_kelas": k.id_kelas,
            "nama_kelas": k.nama_kelas,
            "tingkat": k.tingkat,
            "jurusan": k.jurusan,
            "id_wali": k.id_wali,
            "tahun_ajaran": k.tahun_ajaran
        })
    return results

def create_kelas(payload: dict) -> dict:
    nama = payload.get("nama_kelas")
    tingkatan = payload.get("tingkat")
    tahun = payload.get("tahun_ajaran")
    
    if not nama or not tingkatan or not tahun:
        raise KelasServiceError("nama_kelas, tingkat, tahun_ajaran wajib diisi")
        
    k = Kelas(
        nama_kelas=nama,
        tingkat=tingkatan,
        jurusan=payload.get("jurusan"),
        id_wali=payload.get("id_wali"),
        tahun_ajaran=tahun
    )
    db.session.add(k)
    db.session.commit()
    return {"id_kelas": k.id_kelas}

def update_kelas(id_kelas: int, payload: dict) -> dict:
    k = Kelas.query.get(id_kelas)
    if not k: raise KelasServiceError("Kelas tidak ditemukan", 404)
        
    if "nama_kelas" in payload: k.nama_kelas = payload["nama_kelas"]
    if "tingkat" in payload: k.tingkat = payload["tingkat"]
    if "jurusan" in payload: k.jurusan = payload["jurusan"]
    if "id_wali" in payload: k.id_wali = payload["id_wali"]
    if "tahun_ajaran" in payload: k.tahun_ajaran = payload["tahun_ajaran"]
        
    db.session.commit()
    return {"id_kelas": k.id_kelas}

def delete_kelas(id_kelas: int):
    k = Kelas.query.get(id_kelas)
    if not k: raise KelasServiceError("Kelas tidak ditemukan", 404)
    db.session.delete(k)
    db.session.commit()
