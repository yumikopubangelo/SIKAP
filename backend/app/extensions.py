from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import os
import json

# Core extensions

db = SQLAlchemy()
migrate = Migrate(compare_type=True)
jwt = JWTManager()
cors = CORS()

token_blocklist = set()

# JWT key‑rotation support
_JWT_KEYS = {
    os.getenv('JWT_ACTIVE_KID', 'v1'): os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-ganti-di-production'),
}
# Load any additional keys supplied as JSON string
_additional = os.getenv('JWT_ADDITIONAL_SECRET_KEYS')
if _additional:
    try:
        _JWT_KEYS.update(json.loads(_additional))
    except Exception:
        pass

def get_jwt_secret(kid: str) -> str:
    """Return the secret for the given ``kid``. Fallback to active key."""
    return _JWT_KEYS.get(kid) or _JWT_KEYS.get(os.getenv('JWT_ACTIVE_KID'))

# RFID configuration
RFID_REQUIRE_SIGNATURE = bool(int(os.getenv('RFID_REQUIRE_SIGNATURE', '0')))
RFID_SIGNATURE_TOLERANCE_SECONDS = int(os.getenv('RFID_SIGNATURE_TOLERANCE_SECONDS', '120'))
RFID_PUBLIC_KEY_DIR = os.getenv('RFID_PUBLIC_KEY_DIR', '/app/keys/rfid_public')
