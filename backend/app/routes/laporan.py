import os
from datetime import datetime

from flask import Blueprint, request, send_file

from ..extensions import db
from ..middleware.auth_middleware import inject_current_user
from ..services.laporan_service import REPORT_DIR, generate_laporan
from ..utils.response import error_response, success_response

laporan_bp = Blueprint("laporan", __name__, url_prefix="/api/v1/laporan")


@laporan_bp.post("/generate")
@inject_current_user
def generate(current_user):
    data = request.get_json(silent=True) or {}

    jenis = data.get("jenis")
    format_laporan = data.get("format")
    filter_id = data.get("filter_id")
    tanggal_mulai_str = data.get("tanggal_mulai")
    tanggal_selesai_str = data.get("tanggal_selesai")

    if jenis not in ("kelas", "siswa", "sekolah"):
        return error_response(
            "Jenis laporan harus 'kelas', 'siswa', atau 'sekolah'.",
            400,
        )
    if format_laporan not in ("pdf", "excel"):
        return error_response("Format laporan harus 'pdf' atau 'excel'.", 400)
    if jenis in ("kelas", "siswa") and not filter_id:
        return error_response(f"filter_id wajib diisi untuk jenis {jenis}.", 400)

    tanggal_mulai = None
    tanggal_selesai = None
    try:
        if tanggal_mulai_str:
            tanggal_mulai = datetime.strptime(tanggal_mulai_str, "%Y-%m-%d").date()
        if tanggal_selesai_str:
            tanggal_selesai = datetime.strptime(tanggal_selesai_str, "%Y-%m-%d").date()
    except ValueError:
        return error_response("Format tanggal harus YYYY-MM-DD.", 400)

    try:
        laporan = generate_laporan(
            jenis=jenis,
            format_laporan=format_laporan,
            filter_id=filter_id,
            tanggal_mulai=tanggal_mulai,
            tanggal_selesai=tanggal_selesai,
            user_id=current_user.id_user,
        )
        return success_response(
            data={
                "id_laporan": laporan.id_laporan,
                "jenis": laporan.jenis,
                "format": laporan.format,
                "created_at": laporan.created_at.isoformat(),
            },
            message="Laporan berhasil digenerate.",
            status_code=201,
        )
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Gagal generate laporan: {str(e)}", 500)


@laporan_bp.get("/download/<int:id_laporan>")
@inject_current_user
def download(current_user, id_laporan):
    from ..models import Laporan

    laporan = db.session.get(Laporan, id_laporan)
    if not laporan:
        return error_response("Laporan tidak ditemukan.", 404)

    if not os.path.exists(laporan.file_path):
        return error_response("File laporan sudah tidak tersedia di server.", 404)

    return send_file(
        laporan.file_path,
        as_attachment=True,
        download_name=os.path.basename(laporan.file_path),
    )
