from flask import Blueprint, request

from ..extensions import db
from ..middleware.auth_middleware import inject_current_user
from ..models import WaktuSholat
from ..utils.response import error_response, success_response
from ..utils.validators import validate_waktu_sholat_update_payload


waktu_sholat_bp = Blueprint("waktu_sholat", __name__, url_prefix="/api/v1/waktu-sholat")


def _ensure_admin(current_user):
    if current_user.role != "admin":
        return error_response("Hanya admin yang dapat mengubah waktu sholat.", 403)
    return None


@waktu_sholat_bp.get("")
@inject_current_user
def list_waktu_sholat(current_user):
    _ = current_user
    data = [
        item.to_dict()
        for item in WaktuSholat.query.order_by(WaktuSholat.id_waktu.asc()).all()
    ]
    return success_response(
        data=data,
        message="Daftar waktu sholat berhasil diambil.",
    )


@waktu_sholat_bp.put("/<int:waktu_id>")
@inject_current_user
def update_waktu_sholat(current_user, waktu_id: int):
    forbidden_response = _ensure_admin(current_user)
    if forbidden_response is not None:
        return forbidden_response

    payload, errors = validate_waktu_sholat_update_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload waktu sholat tidak valid.", 400, errors=errors)

    waktu_sholat = WaktuSholat.query.filter_by(id_waktu=waktu_id).first()
    if waktu_sholat is None:
        return error_response("Data waktu sholat tidak ditemukan.", 404)

    try:
        waktu_sholat.waktu_adzan = payload["waktu_adzan"]
        waktu_sholat.waktu_iqamah = payload["waktu_iqamah"]
        waktu_sholat.waktu_selesai = payload["waktu_selesai"]
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return success_response(
        data=waktu_sholat.to_dict(),
        message="Waktu sholat berhasil diupdate.",
    )
