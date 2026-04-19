import base64
import binascii
from datetime import datetime, timezone
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, ed448, padding, rsa
from flask import current_app


class RfidSecurityError(Exception):
    def __init__(self, message: str, status_code: int = 401, errors: dict | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.errors = errors


def build_rfid_signature_message(payload: dict, request_timestamp: datetime) -> bytes:
    event_timestamp = payload.get("timestamp")
    if hasattr(event_timestamp, "isoformat"):
        event_iso = event_timestamp.isoformat()
    else:
        event_iso = str(event_timestamp or "")
    canonical = "\n".join(
        [
            payload["device_id"],
            payload["uid_card"],
            event_iso,
            request_timestamp.astimezone(timezone.utc).isoformat(),
        ]
    )
    return canonical.encode("utf-8")


def _parse_signature_timestamp(value: str | None) -> datetime:
    if not value:
        raise RfidSecurityError(
            "Timestamp tanda tangan RFID wajib disertakan.",
            401,
            errors={"X-RFID-Signature-Timestamp": "Header wajib diisi."},
        )

    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RfidSecurityError(
            "Timestamp tanda tangan RFID tidak valid.",
            401,
            errors={"X-RFID-Signature-Timestamp": "Gunakan format ISO 8601."},
        ) from exc

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _load_device_public_key(device_id: str, perangkat=None):
    public_key_pem = getattr(perangkat, "public_key", None)
    if public_key_pem:
        try:
            return serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
        except ValueError as exc:
            raise RfidSecurityError(
                "Public key perangkat tidak valid.",
                500,
                errors={"device_id": f"Public key database untuk '{device_id}' tidak valid."},
            ) from exc

    key_dir = Path(current_app.config["RFID_PUBLIC_KEY_DIR"])
    key_path = key_dir / f"{device_id}.pem"
    if not key_path.exists():
        raise RfidSecurityError(
            "Public key perangkat belum terdaftar di server.",
            401,
            errors={"device_id": f"File public key tidak ditemukan untuk device '{device_id}'."},
        )

    try:
        return serialization.load_pem_public_key(key_path.read_bytes())
    except ValueError as exc:
        raise RfidSecurityError(
            "Public key perangkat tidak valid.",
            500,
            errors={"device_id": f"Gagal membaca file public key untuk '{device_id}'."},
        ) from exc


def _verify_signature(public_key, signature: bytes, message: bytes) -> None:
    if isinstance(public_key, ed25519.Ed25519PublicKey):
        public_key.verify(signature, message)
        return

    if isinstance(public_key, ed448.Ed448PublicKey):
        public_key.verify(signature, message)
        return

    if isinstance(public_key, rsa.RSAPublicKey):
        public_key.verify(signature, message, padding.PKCS1v15(), hashes.SHA256())
        return

    if isinstance(public_key, ec.EllipticCurvePublicKey):
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return

    raise RfidSecurityError("Jenis public key perangkat belum didukung.", 500)


def verify_rfid_signature(payload: dict, headers, perangkat=None) -> dict:
    require_signature = bool(current_app.config.get("RFID_REQUIRE_SIGNATURE"))
    signature_b64 = headers.get("X-RFID-Signature")
    signature_timestamp_raw = headers.get("X-RFID-Signature-Timestamp")

    if not signature_b64 and not signature_timestamp_raw:
        if require_signature:
            raise RfidSecurityError(
                "Tanda tangan RFID wajib disertakan.",
                401,
                errors={
                    "X-RFID-Signature": "Header wajib diisi.",
                    "X-RFID-Signature-Timestamp": "Header wajib diisi.",
                },
            )
        return {"verified": False, "nonce": None}

    if not signature_b64:
        raise RfidSecurityError(
            "Tanda tangan RFID wajib disertakan.",
            401,
            errors={"X-RFID-Signature": "Header wajib diisi."},
        )

    request_timestamp = _parse_signature_timestamp(signature_timestamp_raw)
    tolerance = int(current_app.config.get("RFID_SIGNATURE_TOLERANCE_SECONDS", 120))
    drift = abs((datetime.now(timezone.utc) - request_timestamp).total_seconds())
    if drift > tolerance:
        raise RfidSecurityError(
            "Tanda tangan RFID sudah kedaluwarsa atau timestamp terlalu jauh.",
            401,
            errors={"X-RFID-Signature-Timestamp": f"Maksimal selisih {tolerance} detik."},
        )

    try:
        signature = base64.b64decode(signature_b64, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise RfidSecurityError(
            "Format tanda tangan RFID tidak valid.",
            401,
            errors={"X-RFID-Signature": "Gunakan base64 yang valid."},
        ) from exc

    nonce = int(request_timestamp.timestamp())
    last_nonce = getattr(perangkat, "last_nonce", None)
    if last_nonce is not None and nonce <= int(last_nonce):
        raise RfidSecurityError(
            "Permintaan RFID terdeteksi sebagai replay atau urutan timestamp mundur.",
            401,
            errors={"X-RFID-Signature-Timestamp": "Gunakan timestamp yang selalu lebih baru."},
        )

    public_key = _load_device_public_key(payload["device_id"], perangkat=perangkat)
    message = build_rfid_signature_message(payload, request_timestamp)

    try:
        _verify_signature(public_key, signature, message)
    except InvalidSignature as exc:
        raise RfidSecurityError(
            "Verifikasi tanda tangan RFID gagal.",
            401,
            errors={"X-RFID-Signature": "Signature tidak cocok dengan payload."},
        ) from exc

    return {"verified": True, "nonce": nonce}
