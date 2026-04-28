import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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


def _get_app_timezone() -> ZoneInfo:
    timezone_name = os.getenv("APP_TIMEZONE", "Asia/Jakarta")
    return ZoneInfo(timezone_name)


def _parse_reference_timestamp(raw_value: str | None) -> tuple[datetime, str]:
    if not raw_value:
        return datetime.now(_get_app_timezone()).replace(tzinfo=None), "server_clock"

    normalized = raw_value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(
            "Parameter timestamp harus berformat ISO 8601, misalnya 2026-04-28T12:05:00."
        ) from exc

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(_get_app_timezone()).replace(tzinfo=None)

    return parsed, "query_timestamp"


def _serialize_status_item(item: WaktuSholat) -> dict:
    return item.to_dict()


def _build_waktu_sholat_status(reference_timestamp: datetime, timestamp_source: str) -> dict:
    items = (
        WaktuSholat.query.order_by(WaktuSholat.waktu_adzan.asc(), WaktuSholat.id_waktu.asc()).all()
    )
    current_time = reference_timestamp.time()

    active_item = None
    next_item = None
    next_date = reference_timestamp.date()

    for item in items:
        if active_item is None and item.waktu_adzan <= current_time <= item.waktu_selesai:
            active_item = item
        if next_item is None and item.waktu_adzan > current_time:
            next_item = item

    if next_item is None and items:
        next_item = items[0]
        next_date = reference_timestamp.date() + timedelta(days=1)

    active_payload = None
    if active_item is not None:
        iqamah_at = datetime.combine(reference_timestamp.date(), active_item.waktu_iqamah)
        selesai_at = datetime.combine(reference_timestamp.date(), active_item.waktu_selesai)
        active_payload = {
            **_serialize_status_item(active_item),
            "phase": "menuju_iqamah"
            if current_time <= active_item.waktu_iqamah
            else "sesi_berjalan",
            "seconds_until_iqamah": max(0, int((iqamah_at - reference_timestamp).total_seconds())),
            "seconds_until_end": max(0, int((selesai_at - reference_timestamp).total_seconds())),
        }

    next_payload = None
    if next_item is not None:
        next_at = datetime.combine(next_date, next_item.waktu_adzan)
        next_payload = {
            **_serialize_status_item(next_item),
            "reference_date": next_date.isoformat(),
            "seconds_until_start": max(0, int((next_at - reference_timestamp).total_seconds())),
        }

    return {
        "timestamp_source": timestamp_source,
        "reference_timestamp": reference_timestamp.isoformat(timespec="seconds"),
        "is_active": active_payload is not None,
        "active_prayer": active_payload,
        "next_prayer": next_payload,
    }


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


@waktu_sholat_bp.get("/status")
@inject_current_user
def get_waktu_sholat_status(current_user):
    _ = current_user

    try:
        reference_timestamp, timestamp_source = _parse_reference_timestamp(
            request.args.get("timestamp")
        )
    except ValueError as exc:
        return error_response(str(exc), 400)

    return success_response(
        data=_build_waktu_sholat_status(reference_timestamp, timestamp_source),
        message="Status waktu sholat berhasil diambil.",
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
