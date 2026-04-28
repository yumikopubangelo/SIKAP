from datetime import datetime

from flask import Blueprint, jsonify, request

from ..models import Absensi, Perangkat, SesiSholat, db

perangkat_bp = Blueprint("perangkat_bp", __name__, url_prefix="/api/v1/perangkat")

@perangkat_bp.route("/ping", methods=["POST"])
def ping_perangkat():
    """Endpoint heartbeat untuk perangkat IoT."""
    device_id = request.headers.get("X-Device-Id")
    api_key = request.headers.get("X-Api-Key")

    if not device_id or not api_key:
        return jsonify({"success": False, "message": "Missing device credentials"}), 401

    perangkat = db.session.get(Perangkat, device_id)
    if not perangkat or perangkat.api_key != api_key:
        return jsonify({"success": False, "message": "Invalid device credentials"}), 401

    # Update heartbeat
    perangkat.last_ping = datetime.utcnow()
    # Pastikan status tertulis online
    perangkat.status = "online"
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Database error"}), 500

    return jsonify({"success": True, "message": "Ping acknowledged"}), 200
