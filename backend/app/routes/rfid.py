from flask import Blueprint, request, jsonify
from ..extensions import db, RFID_REQUIRE_SIGNATURE, RFID_SIGNATURE_TOLERANCE_SECONDS, RFID_PUBLIC_KEY_DIR
from ..models.perangkat import Perangkat
from ..services.rfid_capture_service import RfidCaptureServiceError, record_capture_tap
from ..utils.response import error_response, success_response
from ..utils.validators import validate_rfid_absensi_payload
import os
import time
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

rfid_bp = Blueprint('rfid', __name__, url_prefix='/api/v1/rfid')

def _load_public_key(device_id: str):
    """Load PEM public key for a device from the configured directory."""
    key_path = os.path.join(RFID_PUBLIC_KEY_DIR, f"{device_id}.pem")
    if not os.path.isfile(key_path):
        return None
    with open(key_path, 'rb') as f:
        return serialization.load_pem_public_key(f.read())

@rfid_bp.post('/verify')
def verify():
    """Verify RFID payload signature and replay protection.
    Expected JSON body:
    {
        "device_id": "string",
        "payload": "base64url-encoded JSON string",
        "signature": "base64url-encoded signature",
        "timestamp": integer (unix epoch seconds)
    }
    """
    data = request.get_json(silent=True) or {}
    device_id = data.get('device_id')
    payload_b64 = data.get('payload')
    signature_b64 = data.get('signature')
    timestamp = data.get('timestamp')

    if not all([device_id, payload_b64, signature_b64, timestamp]):
        return jsonify({"success": False, "message": "Missing required fields."}), 400

    # Replay protection
    now = int(time.time())
    if abs(now - int(timestamp)) > RFID_SIGNATURE_TOLERANCE_SECONDS:
        return jsonify({"success": False, "message": "Timestamp out of tolerance window."}), 400

    device = Perangkat.query.filter_by(device_id=device_id).first()
    if not device:
        return jsonify({"success": False, "message": "Device not found."}), 404

    # If signature verification is disabled, fall back to API key check
    if not RFID_REQUIRE_SIGNATURE:
        api_key = request.headers.get('X-API-KEY')
        if api_key != device.api_key:
            return jsonify({"success": False, "message": "Invalid API key."}), 401
        # Update last_nonce for replay safety
        device.last_nonce = int(timestamp)
        db.session.commit()
        return jsonify({"success": True, "message": "Verified via API key."}), 200

    # Verify signature using stored public key
    public_key = _load_public_key(device_id) or (device.public_key and serialization.load_pem_public_key(device.public_key.encode()))
    if not public_key:
        return jsonify({"success": False, "message": "Public key not available for device."}), 500

    try:
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + '==')
        signature_bytes = base64.urlsafe_b64decode(signature_b64 + '==')
        public_key.verify(signature_bytes, payload_bytes, ec.ECDSA(hashes.SHA256()))
    except (InvalidSignature, ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid signature."}), 401

    # Replay check using stored nonce
    if device.last_nonce and int(timestamp) <= device.last_nonce:
        return jsonify({"success": False, "message": "Replay attack detected."}), 401

    # All good – update nonce
    device.last_nonce = int(timestamp)
    db.session.commit()
    return jsonify({"success": True, "message": "Signature verified."}), 200


@rfid_bp.post('/capture')
def capture():
    payload, errors = validate_rfid_absensi_payload(request.get_json(silent=True))
    if errors:
        return error_response("Payload capture RFID tidak valid.", 400, errors=errors)

    try:
        data = record_capture_tap(payload, request.headers)
    except RfidCaptureServiceError as exc:
        return error_response(exc.message, exc.status_code, errors=exc.errors)

    return success_response(
        data=data,
        message="Tap RFID untuk konfirmasi UID berhasil direkam.",
        status_code=201,
    )
