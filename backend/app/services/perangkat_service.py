from typing import List, Optional
from ..models import db, Perangkat
import logging

logger = logging.getLogger(__name__)

class PerangkatServiceError(Exception): 
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

def list_perangkat() -> List[dict]:
    perangkat = Perangkat.query.all()
    results = []
    for p in perangkat:
        results.append({
            "device_id": p.device_id,
            "nama_device": p.nama_device,
            "lokasi": p.lokasi,
            "api_key": p.api_key,
            "status": p.status,
            "last_ping": p.last_ping.isoformat() if p.last_ping else None
        })
    return results

def create_perangkat(payload: dict) -> dict:
    device_id = payload.get("device_id")
    api_key = payload.get("api_key")
    if not device_id or not api_key:
        raise PerangkatServiceError("device_id dan api_key wajib diisi")
        
    if Perangkat.query.filter_by(device_id=device_id).first():
        raise PerangkatServiceError("device_id sudah terdaftar")
        
    p = Perangkat(
        device_id=device_id,
        nama_device=payload.get("nama_device", "New Device"),
        lokasi=payload.get("lokasi", ""),
        api_key=api_key
    )
    db.session.add(p)
    db.session.commit()
    return {"device_id": p.device_id}

def update_perangkat(device_id: str, payload: dict) -> dict:
    p = Perangkat.query.get(device_id)
    if not p:
        raise PerangkatServiceError("Perangkat tidak ditemukan", 404)
        
    if "nama_device" in payload:
        p.nama_device = payload["nama_device"]
    if "lokasi" in payload:
        p.lokasi = payload["lokasi"]
    if "api_key" in payload:
        p.api_key = payload["api_key"]
    if "status" in payload:
        p.status = payload["status"]
        
    db.session.commit()
    return {"device_id": p.device_id}

def delete_perangkat(device_id: str):
    p = Perangkat.query.get(device_id)
    if not p: raise PerangkatServiceError("Perangkat tidak ditemukan", 404)
    db.session.delete(p)
    db.session.commit()
