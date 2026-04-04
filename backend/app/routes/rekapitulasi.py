from flask import Blueprint, request
from datetime import datetime

from ..middleware.auth_middleware import inject_current_user
from ..services.rekapitulasi_service import (
    get_rekap_kelas,
    get_rekap_siswa,
    get_rekap_sekolah,
)
from ..utils.response import success_response, error_response

rekapitulasi_bp = Blueprint("rekapitulasi", __name__, url_prefix="/api/v1/rekapitulasi")

def _parse_dates():
    start_date_str = request.args.get("start_date")
    end_date_str = request.args.get("end_date")
    start_date = None
    end_date = None
    
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Format tanggal tidak valid. Gunakan YYYY-MM-DD.")
        
    return start_date, end_date

@rekapitulasi_bp.get("/kelas/<int:id_kelas>")
@inject_current_user
def rekap_kelas(current_user, id_kelas):
    try:
        start_date, end_date = _parse_dates()
    except ValueError as e:
        return error_response(str(e), 400)
        
    try:
        data = get_rekap_kelas(id_kelas, start_date, end_date)
        return success_response(data=data, message="Berhasil mendapatkan rekap kelas.")
    except Exception as e:
        return error_response(f"Terjadi kesalahan: {str(e)}", 500)

@rekapitulasi_bp.get("/siswa/<int:id_siswa>")
@inject_current_user
def rekap_siswa(current_user, id_siswa):
    try:
        start_date, end_date = _parse_dates()
    except ValueError as e:
        return error_response(str(e), 400)
        
    try:
        data = get_rekap_siswa(id_siswa, start_date, end_date)
        return success_response(data=data, message="Berhasil mendapatkan rekap siswa.")
    except Exception as e:
        return error_response(f"Terjadi kesalahan: {str(e)}", 500)

@rekapitulasi_bp.get("/sekolah")
@inject_current_user
def rekap_sekolah(current_user):
    try:
        start_date, end_date = _parse_dates()
    except ValueError as e:
        return error_response(str(e), 400)
        
    try:
        data = get_rekap_sekolah(start_date, end_date)
        return success_response(data=data, message="Berhasil mendapatkan rekap sekolah.")
    except Exception as e:
        return error_response(f"Terjadi kesalahan: {str(e)}", 500)
